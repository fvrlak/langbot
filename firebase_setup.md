## 1
Go to Firebase and click on "Go to console"
```bash
https://firebase.google.com
```


## 2
Click on "Add project"

## 3
Name your project "LangBot", continue and choose "Default Account for Firebase" and click on "Create Project"

## 4
Click on "Cloud Firestore" 

![1](https://github.com/artificialarts/LangBot/assets/145310115/6e8238a1-5c3e-4fb7-b10e-28a67f4de771)

## 5
Click on "Create Database"

## 6
Choose "Start in test mode", click "Next" and "Enable"

![2](https://github.com/artificialarts/LangBot/assets/145310115/097af05f-761e-4820-be41-077cff9b511b)

## 7
You are in the database, click on Settings icon and choose "Project Settings"

![3](https://github.com/artificialarts/LangBot/assets/145310115/da462100-d405-4fad-a6d8-0b557fc5fa88)

## 8
In Project Settings go to "Service Account" choose "Python" and click "Generate new private key" and download.
![4](https://github.com/artificialarts/LangBot/assets/145310115/e2d61b5d-35a8-451a-befd-bd6d47c7e4a5)

## 9
The downloaded private key should have a name something like `langbot-91c25-firebase-adminsdk-ea889-4f618c1331.json`

Rename the private key to `db.json` and move it into this folder, so your folder structure look like this:
```bash
.env
app.py
db.json
discord_setup.md
firebase_setup.md
README.md
requirements.txt
```


