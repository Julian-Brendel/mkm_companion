# MKM Companion

## Introduction

Managing your growing mtg stock on [Cardmarket](https://www.cardmarket.com/en/Magic) can be
tedious.  
Reacting to changes in the market can prove to be a painfully manual process when updating
potential multiple thousand of articles.

Fear no more, using the mkm companion makes updating your stock great again.

Do you want to quickly adjust to the market?  
Or undercut everyone to sell your collection?

*MKM companion has you covered*

## Setup

The project uses poetry to manage its dependencies. Link here!!.  
Install the required dependencies using `poetry install`.

> Use `poetry install --dev` to install dev packages like jupyter

To be able to connect to the MKM api, following four environment variables must be present:
```.env
MKM_APP_TOKEN=
MKM_APP_SECRET=
MKM_ACCESS_TOKEN=
MKM_ACCESS_TOKEN_SECRET=
```

These can be found in your mkm profile.

As this project comes with `dotenv`, variables contained in the `.env` file will be loaded into the
environment on startup automatically.

## Run the project

The project can be executed through the `master.ipynb` notebook.
