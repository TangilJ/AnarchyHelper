# AnarchyHelper
AnarchyHelper is a GitHub bot that accepts all pull requests for a repository. It also checks to see if a user has exceeded their line limit for their pull request. This bot is being used for the [TheBlocks/Anarchy](https://github.com/TheBlocks/Anarchy) repository using the [@AnarchyHelper](https://github.com/AnarchyHelper) account (hosted using Heroku).

## Getting started

### Prerequisites

You'll need Python 3.6 or higher to run AnarchyHelper. PostgreSQL is also required.

You'll also need to install its dependencies. The requirements.txt file has all the dependencies listed. Install them with:
```
pip install -r requirements.txt
```

Set up the following environment variables on your system:
* `PORT` - The port at which AnarchyHelper receives its webhooks
* `GITHUB_PASSWORD` - Password of the account running the bot
* `DATABASE_URL` - URL of the PostgreSQL database. This can also be arguments in the form of `user=[Postgres user] password=[Postgress password] host=[Postgres server IP] port=[Postgres server port]`.

Set them up like so:
```
set NAME=value (on Windows)
export NAME="value" (on Linux/Mac)
```

Then, edit the account details for the bot, which can be found at the top of the `anarchyhelper/anarchyhelper.py` file.

Next, create your PostgreSQL database with:

```
createdb.exe (on Windows)
createdb (on Linux/Mac)
```
(You may need to specify the user with `createdb.exe -U postgres` if you get a password authentication error.)

Creating the database is a one time process.

## Running AnarchyHelper

Run AnarchyHelper by typing:

```
python anarchyhelper/anarchyhelper.py
```

## Built with

* [PostgreSQL](https://www.postgresql.org/) - Database to keep track of the users' line usage and its own comments
* [psycopg2](https://github.com/psycopg/psycopg2) - Library to interact with PostgreSQL
* [Pyramid](https://github.com/Pylons/pyramid) - Web framework used to receive webhooks from GitHub
* [PyGithub](https://github.com/PyGithub/PyGithub) - Library to interact with the GitHub API

## License
This project is licensed under the BSD 2-Clause "Simplified" License. See the [LICENSE](https://github.com/TheBlocks/AnarchyHelper/blob/master/LICENSE) file for details.
