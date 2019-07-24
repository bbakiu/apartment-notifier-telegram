# ImmobilienScout instant notifier

## Purpose

This application is built to send push notifications for new apartments using an ImmobilienScout search query

## External services

The application is built to be hosted free and using the free plan of variaty of services online. In order to host the application yourself you will need an account in the following services:
- [Zeit NOW](https://zeit.co/now) - Serverless hosting platform. Free plan includes 5000 executions per day.
- [kvdb.io](https://kvdb.io/) - Free key-value storage with a simple REST API. We use this to store what apartments has been seen.
- [Pushbullet](https://www.pushbullet.com/) - Cross-platform application and service for instant notifications. Use this as notification tool.

Suggested, but not required:
- [Freshping](https://www.freshworks.com/website-monitoring/) - Website monitoring service. I use this to keep an eye if the service fails, moreover it serves as an easy scheduling service. 

## Set up

If you are registered in the accounts above, we can start setting up the application and try to deploy it.

### Install Zeit CLI

First install on your local machine and login to [Zeit CLI](https://zeit.co/docs#install-now-cli)

### Set up database

We need to create a bucket on kvdb.io secured by a key. It has a handy API, which returns the bucket id. 
Save the bucket id and your secret key for later, the application will need both to run!

```
$ export DB_AUTH_KEY=my_db_key
$ export DB_BUCKET=$(curl -d "secret_key=$DB_AUTH_KEY" https://kvdb.io/)
```

Next we need to initialize the key with an empty json array, where the apartment ids will be stored.
```
curl -d '[]' https://kvdb.io/$DB_BUCKET/seen_apartments
```

### Store API secrets for deployment in Zeit

In order to not share our secrets with the world, we gonna utilize Zeit's secret injection feature.
Zeit has a secret storage, which during deployment it can use to fill up environment variables (see references in now.json)


First we will need to generate an access token for Pushbullet. See docs [here](https://docs.pushbullet.com/#authentication)

After it we can fill up the secret storage with our keys.
```
$ now secrets add db_bucket $DB_BUCKET
$ now secrets add db_auth_key $DB_AUTH_KEY
$ now secrets add notification_auth_key <PUSHBULLET_API_KEY>
```

## Customize and deploy

### Customize ImmobilienScout search link

Let's start by cloning/fork&clone this repository, so that you have the code locally.

In index.py you can find the variable `IMMO_SEARCH_URL` which is just an ImmobilienScout24 URL. 

This URL is used for scraping and for a properly functioning application you should make sure that the URL is having the following properties:
- Apartments are in list view (and not map)
- Sorted by date, so that newest are first. This is expecially important as we only request the first page and looking for new stuff on that page.

Otherwise feel free to go crazy with search criterias, you just need to update the variable.

### Deploy

Deploying the application is even easier; just run:

```
$ now
```

### Execute

The application offers a single GET endpoint `\findplaces`. It returns the unseen apartments as a json, but it also sends them via Pushbullet.
On this same endpoint you can set up a regular execution as well. I use [Freshping](https://www.freshworks.com/website-monitoring/) for this purpose.
