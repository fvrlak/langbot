# LangBot

## Overview
LangBot is a Discord bot powered by generative AI and offers versatile communication assistance. Similar to Antropic Clyde, it adapts to both casual and formal conversational tones. Featuring database queries via Firebase and real-time event updates, LangBot serves as a reliable, context-aware communication companion.

![1](https://github.com/artificialarts/LangBot/assets/145310115/6b6cfc30-1faf-4f2c-afaa-d90f0bbfcaf4)


## Bot Commands
Shows user's account
```bash
/account
```
![3](https://github.com/artificialarts/LangBot/assets/145310115/318d9015-f0f4-47bd-ac17-06c1cdb50951)

Shows user's settings
```bash
/settings
```
![4](https://github.com/artificialarts/LangBot/assets/145310115/51ce3468-dadc-45a8-b655-784216381b4c)

Adjusts language modalities
```bash
/language
```
![6](https://github.com/artificialarts/LangBot/assets/145310115/16ad1cc0-27f3-4872-862e-450085a8e07d)

Change AI model
```bash
/model
```
![5](https://github.com/artificialarts/LangBot/assets/145310115/246a748d-73ae-4fb1-ad51-58ebf01b5eda)

Generate Image
```bash
/image
```
![2](https://github.com/artificialarts/LangBot/assets/145310115/72675197-98ee-4959-a87c-631d2fa3387f)


## Installation

To install LangBot, you can clone the repository using the following command:

```bash
git clone https://github.com/artificialarts/langbot.git
```

Install requirements

```bash
pip install -r requirements.txt
```

Setup Firebase database according to file

```bash
./firebase_setup.md
```

Setup Bot according to file

```bash
./discord_setup.md
```

Launch the bot

```bash
py app.py
```

