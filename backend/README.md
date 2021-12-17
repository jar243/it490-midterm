# IT490 Backend

## Requirements
1. [Python 3.9](https://www.python.org/downloads/)
2. [Poetry (Python package manager)](https://python-poetry.org/docs/master/#installation)

## Setup
1. cd to the backend directory
2. `poetry install`
3. `docker-compose up` (depends on your OS)
4. Configure backend via system env variables or an .env file in the backend directory

## Environment Variables
- IT490_BROKER_HOST (default: 127.0.0.1)
- IT490_BROKER_PORT (default: 5672)
- IT490_BROKER_USER (default: guest)
- IT490_BROKER_PASSWORD (default: guest)
- IT490_MYSQL_HOST (default: 127.0.0.1)
- IT490_MYSQL_PORT (default: 3306)
- IT490_MYSQL_USER (default: devuser)
- IT490_MYSQL_PASSWORD (default: devpassword)
- IT490_EMAIL_ADDR (default: no-reply@movieworld.com)

## Run Application
1. `poetry run python app.py`
