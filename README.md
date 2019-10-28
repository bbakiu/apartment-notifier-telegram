# ImmobilienScout instant notifier

## Purpose

This application is built to send push notifications for new apartments using an ImmobilienScout search query.

This repo is a slighlty modified version of: https://github.com/gavronek/apartment-notifier. The difference is in using Telegram to send notification and not [Pushbullet](https://www.pushbullet.com/)

## External services

The application is built to be hosted free and using the free plan of variaty of services online. In order to host the application yourself you will need an account in the following services:
- [Zeit NOW](https://zeit.co/now) - Serverless hosting platform. Free plan includes 5000 executions per day.
- [kvdb.io](https://kvdb.io/) - Free key-value storage with a simple REST API. We use this to store what apartments has been seen.
- [Telegram Messenger](https://telegram.org/) - Cross-platform messaging application for instant notifications. Use this as a tool to receive push notifications.

Suggested, but not required:
- [Freshping](https://www.freshworks.com/website-monitoring/) - Website monitoring service. Use this to keep an eye if the service fails, moreover it serves as an easy scheduling service. 

## Set up

If you are registered in Zeit NOW, Telegram (and Freshping), you can start setting up the application and try to deploy it.

### Install Zeit CLI

First install on your local machine and login to [Zeit CLI](https://zeit.co/docs#install-now-cli)

### Set up database

We need to create a bucket on kvdb.io secured by a key. It has a handy API, which returns the bucket id. 
Save the bucket id and your secret key for later, the application will need both to run!

```
$ export DB_AUTH_KEY=<YOUR_DB_KEY>
$ export DB_BUCKET=$(curl -d 'email=<YOUR_EMAIL>' -d "secret_key=$DB_AUTH_KEY" https://kvdb.io)
```

Next we need to initialize the key with an empty json array, where the apartment ids will be stored.
```
$ curl -d '[]' https://kvdb.io/$DB_BUCKET/seen_apartments
```

### Store API secrets for deployment in Zeit

In order to not share our secrets with the world, we gonna utilize Zeit's secret injection feature.
Zeit has a secret storage, which during deployment it can use to fill up environment variables (see references in now.json)


### Telegram chat bot
Use BotFather to create a chat bot in telegram. Short explanation is [here](https://core.telegram.org/bots#6-botfather).
Basically find BotFather in Telegram and send the message `/newbot` and follow the instructions.
After you have created the chat bot you should have gotten a token that allows you to control the bot, something like `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`.

```
$ export BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
```

From telegram you are going to need also a chat id, which in the id of your chat with the bot. 
Write a couple of dummy messages to the bot you just created and run this command:
```
$ curl https://api.telegram.org/bot<YourBOTToken>/getUpdates
```

Look for the "chat" object in the message you will get. It is something along the lines:
```
{"update_id":8393,
"message":{"message_id":3,"from":{"id":7474,"first_name":"AAA"},
"chat":{"id":,"title":""},
"date":25497,
"new_chat_participant":{"id":71,"first_name":"NAME","username":"YOUR_BOT_NAME"}}}
```
After you have found the chat id, export it:
```
$ export CHAT_ID=<TELEGRAM_BOT_CHAT_ID>
```
If the response does not look like that write a couple of more messages to the bot.

### Last steps

After it you can fill up the secret storage of Zeit with your keys.
```
$ now secrets add db_bucket $DB_BUCKET
$ now secrets add db_auth_key $DB_AUTH_KEY
$ now secrets add bot_token $BOT_TOKEN
$ now secrets add chat_id $CHAT_ID
```

## Customize and deploy

### Customize ImmobilienScout search link


The variable `IMMO_SEARCH_URL` is just an ImmobilienScout24 URL. 

This URL is used for scraping and for a properly functioning application you should make sure that the URL is having the following properties:
- Apartments are in list view (and not map)
- Sorted by date, so that newest are first. This is expecially important as you only request the first page and looking for new stuff on that page.

After you have copied the URL from the browser run: 
```
$ export IMMO_SEARCH_URL=<YOUR_IMMO_URL>
$ now secrets add immo_search_url $IMMO_SEARCH_URL
```

Feel free to go crazy with search criterias, you just need to update the variable.

If you are interested only in the public companies please read and modify lines 52-57 of the index.py file.

### Deploy

Deploying the application is even easier; just run:

```
$ now
```

### Execute

The application offers a single GET endpoint `/findplaces`. It returns the unseen apartments as a json, but it also sends a notification for each of them via Telegram.
On this same endpoint you can set up a regular execution as well. I use [Freshping](https://www.freshworks.com/website-monitoring/) for this purpose.
