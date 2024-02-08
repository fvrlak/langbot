## 1
Go to developer portal and create "New Application"
```bash
https://discord.com/developers/applications
```

![1](https://github.com/artificialarts/LangBot/assets/145310115/c36535f1-6696-4ffb-ad9a-815625d46b4e)

## 2
Go to "Bot" section and tick the intents

![7](https://github.com/artificialarts/LangBot/assets/145310115/a6aa968d-fa87-4981-994d-a606433ec15f)

## 3
Go to "General Information" copy "APPLICATION ID", paste it into the URL below, and open in browser
```bash
https://discord.com/api/oauth2/authorize?client_id=APPLICATION_ID&permissions=8&scope=bot
```

If my "APPLICATION ID" is 1153222169438990398 the URL will be
```bash
https://discord.com/api/oauth2/authorize?client_id=1153222169438990398&permissions=8&scope=bot
```

![5](https://github.com/artificialarts/LangBot/assets/145310115/bfcf3a72-3169-461f-af4f-c94f9d0d884c)

## 4
In the browser, set the server where the bot will be living and authorize

![6](https://github.com/artificialarts/LangBot/assets/145310115/160bf697-7dd1-4561-9ca0-a625069a1256)

## 5
Go back to the Bot section in developer portal and copy the token.
If you don't see any, click on "Reset Token" and it will generate a new one.
Paste the token into `BOT_TOKEN` variable in  the `.env` file

![4](https://github.com/artificialarts/LangBot/assets/145310115/65fd08d5-dcd3-423e-a14c-496b7f5990fc)

![8](https://github.com/artificialarts/LangBot/assets/145310115/52e767a4-2426-4b8e-945d-b121854162c1)


