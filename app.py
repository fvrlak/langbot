###############[Imports]#####################
import os
from dotenv import load_dotenv
from datetime import datetime
import openai
import discord 
from discord import app_commands
from discord.ext import commands
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import initialize_app, delete_app, get_app
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate)
from langchain.memory import ChatMessageHistory
from langchain.output_parsers import (StructuredOutputParser, ResponseSchema)
from langchain.schema import OutputParserException
from langchain.chat_models import ChatOpenAI
###############[/Imports]####################

################[API keys]#####################
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
################[/API keys]####################

################[Bot]#####################
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()
intents.presences = True
intents.typing = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
client = commands.Bot(command_prefix="/", intents=intents, description="Working on it")
################[/Bot]####################

################[DB]####################
# Firebase
try:
    default_app = get_app()
except ValueError:
    default_app = initialize_app()

db = default_app
db._credential = credentials.Certificate('./db.json')
db._client = firestore.client(db)
d = db._client

try:
    delete_app(default_app)
except ValueError:
    pass
################[/DB]####################

##############################################################################
#                                Functions                                   #           
##############################################################################
def generate_image(prompt:str):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

def language_schema(attr, variant=None):
    schemas = {
        'register': {1: 'concise', 'concise': 'Answer in summary, always just answer on question, no need to explaining into detail. be concise. Save words.',
                     2: 'elaborate', 'elaborate': 'Provide detailed explanations, answer beyond the immediate question, elaborate extensively. Use more words.'},
        'formality': {1: 'standard', 'standard': 'Standard language, no slang, no jargon. Use formal language.',
                      2: 'official', 'official': 'Official language, no slang, no jargon. Use formal language.'},
        'emotiveness': {1: 'neutral', 'neutral': 'Neutral, no emotion.',
                        2: 'emotional', 'emotional': 'Emotional, express feelings.'},
        'ambiguity': {1: 'low', 'low': 'Low ambiguity, single meaning.',
                      2: 'high', 'high': 'High ambiguity, multiple possible meanings.'},
        'jargon': {1: 'low', 'low': 'Low jargon, no specialized industry terms.',
                   2: 'high', 'high': 'High jargon, specialized industry terms.'}
    }
    
    if type(attr) == list:
        print("ATTR", attr)
        return [ResponseSchema(name='text', description="Answer with following modalities " + " ".join(attr))]

    return schemas.get(attr, {}).get(variant, None)

def clamp_values(register, formality, emotiveness, ambiguity, jargon):
    def clamp(val):
        return 0 if val == 0 else min(max(val, 1), 2)
        
    return {
        "register": clamp(register),
        "formality": clamp(formality),
        "emotiveness": clamp(emotiveness),
        "ambiguity": clamp(ambiguity),
        "jargon": clamp(jargon),
    }

def get_language_settings(user):
    settings_ref = d.collection(u"Settings")
    docs = settings_ref.stream()
    is_empty = not any(docs)
    if is_empty:
        generate_db_schema(user)
        

    settings_ref = d.collection(u"Settings").document("language")
    settings = settings_ref.get().to_dict()

    return [
        language_schema("register", settings["register"]),
        language_schema("formality", settings["formality"]),
        language_schema("emotiveness", settings["emotiveness"]),
        language_schema("ambiguity", settings["ambiguity"]),
        language_schema("jargon", settings["jargon"]),
    ]

def get_model_settings():
    settings_ref = d.collection(u"Settings").document("model")
    settings = settings_ref.get().to_dict()

    return ChatOpenAI(temperature=settings["temperature"], model_name=settings["model"], max_tokens=settings["max_tokens"], openai_api_key=OPENAI_API_KEY)

def generate_db_schema(user):
    """ Default Schema for database  

    Account -> User -> {UserId, username}

    Settings -> Language -> {register, formality, emotiveness, ambiguity, jargon}
             -> Model    -> {model, temperature, max_tokens}

    Images -> time_created -> {url, prompt, timestamp}

    """
    # Account
    account_ref = d.collection(u"Account").document("profile")
    account_ref.set({
        u"username": user.name,
        u"userId": user.id,
    })


    # Settings
    ## Language
    settings_lang_ref = d.collection(u"Settings").document("language")
    settings_lang_ref.set({
        "register": "concise",
        "formality": "standard",
        "emotiveness": "neutral",
        "ambiguity": "low",
        "jargon": "low"
    })

    ## Model
    settings_model_ref = d.collection(u"Settings").document("model")
    settings_model_ref.set({
        "model": "gpt-3.5-turbo-16k",
        "temperature": 0.7,
        "max_tokens": 200,
    })

async def messages(interaction, system_template, user_input):
    async def h():
        history =  interaction.channel.history(limit=50)
        channel_messages = ChatMessageHistory()
        async for msg in history:
            if msg.id == interaction.id:
                continue
            if msg.author.bot:
                channel_messages.add_ai_message(msg.content)
            if not msg.author.bot:
                channel_messages.add_user_message(msg.content)
        return channel_messages
    
    m = await h()
    k = m.messages[::-1]
    k.insert(0, SystemMessagePromptTemplate.from_template(system_template))
    k.append(HumanMessagePromptTemplate.from_template(user_input))
    return k

time_id = lambda: datetime.now().strftime("%Y%m%d%H%M%S%f")
timestamp = lambda: datetime.now().strftime("%d/%m/%Y %H:%M:%S")
##############################################################################
#                                Commands                                    #           
##############################################################################
@client.tree.command(name="image", description="Image generation")
@app_commands.describe(prompt="Generate image from prompt")
async def image(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    if prompt == "":
        return

    url = generate_image(prompt)
    description = "*" + prompt + "*"

    # save to firebase
    image_ref = d.collection(u"Image").document(time_id())
    image_ref.set({
        "prompt": prompt,
        "url": url,
        "timestamp": timestamp(),
    })
    if interaction is not None and interaction.user is None:  
        await interaction.edit_original_response(embed=embed)
    embed = discord.Embed(description=description, color=0x000000).set_image(url=url)
    await interaction.edit_original_response(embed=embed)

@client.tree.command(name="language", description="Set language attributes. To see current settings, use command `/settings`.")
@app_commands.describe(register = "Balance between conciseness and verbosity. (0)no-change (1)concise (2)elaborate")
@app_commands.describe(formality = "Standard or official language. (0)no-change (1)standard (2)official")
@app_commands.describe(emotiveness = "Expression of feelings. (0)no-change (1)neutral (2)emotional")
@app_commands.describe(ambiguity = "Multiple possible meanings. (0)no-change (1)low, (2)high")
@app_commands.describe(jargon = "Specialized industry terms. (0)no-change (1)low (2)high")
async def language(interaction: discord.Interaction, register: int, formality: int, emotiveness: int, ambiguity: int, jargon: int):
    
    settings_ref = d.collection(u"Settings").document("language")
    settings = settings_ref.get().to_dict()
    variants = clamp_values(register, formality, emotiveness, ambiguity, jargon)
    
    results = {}

    for name, value in variants.items():
        if value != 0:
            results[name] = language_schema(name, value)

    print("RESULTS", results)

    if results:
        settings_ref.update(results)

        updated_settings = settings_ref.get().to_dict()
        print("UPDATED SETTINGS", updated_settings)

        description = '**Language attributes updated**\n'

        if 'register' in results:
            description += f"Register:  {results['register']}\n"
        if 'formality' in results:
            description += f"Formality: {results['formality']}\n"
        if 'emotiveness' in results:
            description += f"Emotiveness: {results['emotiveness']}\n"
        if 'ambiguity' in results:
            description += f"Ambiguity: {results['ambiguity']}\n"
        if 'jargon' in results:
            description += f"Jargon: {results['jargon']}\n"
        
        embed = discord.Embed(title="Settings updated", description=description, color=0x000000)
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return

    embed = discord.Embed(title="Settings", description="No change", color=0x000000)
    await interaction.response.send_message(embed = embed, ephemeral=True)

@client.tree.command(name="model", description="Set language model. To see current settings, use command `/settings`.")
@app_commands.describe(model = "Set language model. (0)no-change (1)gpt-3.5-turbo-16k (2)gpt-4")
@app_commands.describe(temperature = "Set temperature of model. Type number between 0 and 2. For math use 0, for poetry use 2.")
@app_commands.describe(max_tokens = "Set amount of tokens for model to return. [Max 4000 tokens]")
async def model(interaction: discord.Interaction, model: int, temperature: float, max_tokens: int):
    
    settings_ref = d.collection(u"Settings").document("model")
    settings = settings_ref.get().to_dict()
    if model == 0:
        model = settings["model"]
    if model == 1:
        model = "gpt-3.5-turbo-16k"
    if model == 2:
        model = "gpt-4"
    
    if temperature > 2.0 or temperature < 0:
        embed = discord.Embed(title="Temperature is out of range", description="Please choose number between 0 and 2", color=0x000000)
        await interaction.response.send_message(embed=embed)
        return
    if max_tokens > 4000 or max_tokens < 1:
        embed = discord.Embed(title="Max tokens is out of range", description="Please choose number between 1 and 4000", color=0x000000)
        await interaction.response.send_message(embed=embed)
        return

    settings_ref.update({
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    })

    description= '''
    **Language model updated**
    Model: {model}
    Temperature: {temperature}
    Max tokens: {max_tokens}
    '''.format(model=model, temperature=temperature, max_tokens=max_tokens)

    embed = discord.Embed(title="Settings updated", description=description, color=0x000000)
    await interaction.response.send_message(embed = embed, ephemeral=True)

@client.tree.command(name="account", description="Check your account")
async def account(interaction: discord.Interaction):
    account_ref = d.collection(u"Account").document("profile")
    account = account_ref.get().to_dict()

    embed = discord.Embed(title="",color=0x00ff00)
    embed.add_field(name="Name", value=account["username"], inline=True)
    embed.add_field(name="ID", value=account["userId"], inline=False)

    return await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="settings", description="Show settings of bot")
async def settings(interaction: discord.Interaction):
    
    embed = discord.Embed(title="",color=0x00ff00)

    model_ref = d.collection(u"Settings").document("model")
    model = model_ref.get().to_dict()
    embed.add_field(name="Model", value=f"{model['model']}\n*Temperature* {model['temperature']}\n*Max tokens* {model['max_tokens']}", inline=True)

    language_ref = d.collection(u"Settings").document("language")
    language = language_ref.get().to_dict()
    embed.add_field(name="Language", value=f"*Register* {language['register']}\n*Formality* {language['formality']}\n*Emotiveness* {language['emotiveness']}\n*Ambiguity* {language['ambiguity']}\n*Jargon* {language['jargon']}", inline=False)

    return await interaction.response.send_message(embed=embed, ephemeral=True)

##############################################################################
#                                Events                                      #           
##############################################################################
@client.event
async def on_member_join(member):
    print("Member joined {0}".format(member))

@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
    except Exception as e:
        print(e)

@client.event
async def on_message(interaction: discord.Interaction):
    
    is_pass = interaction.author.bot == True  or interaction.content.startswith("/") 
    if is_pass:
        return

    system_template = """
    Answer to user input based on instructions:
    {format_instructions}
    """

    language = get_language_settings(interaction.author)
    model = get_model_settings()
    user_input = interaction.content

    output_parser = StructuredOutputParser.from_response_schemas(language_schema(language))
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate(
        messages=await messages(interaction, system_template, user_input),
        input_variables=["user_input"],
        partial_variables={"format_instructions": format_instructions}
    )

    query = prompt.format_prompt(user_input=user_input)
    pre_output = model(query.to_messages())
    print("PREOUTPUT", pre_output.content)

    try:
        output = output_parser.parse(pre_output.content)
        print("OUTPUT", output)
        await interaction.channel.send(output["text"])
    
    except OutputParserException as e:
        full_string = str(e)
        remove_string = "Got invalid return object. Expected markdown code snippet with JSON object, but got:"
        output = full_string.replace(remove_string, "")

        await interaction.channel.send(output)

if __name__ == "__main__":
    client.run(BOT_TOKEN)
