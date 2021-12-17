# IT490 DMZ

## Requirements
1. [Python 3.9](https://www.python.org/downloads/)
2. [Poetry (Python package manager)](https://python-poetry.org/docs/master/#installation)

## Setup
1. Navigate to the DMZ directory
2. `poetry install`
3. Configure DMZ via system env variables or an .env file in the DMZ directory

## Environment Variables
- IT490_BROKER_HOST (default: 127.0.0.1)
- IT490_BROKER_PORT (default: 5672)
- IT490_BROKER_USER (default: guest)
- IT490_BROKER_PASSWORD (default: guest)
- IT490_TMDB_API_KEY
- IT490_YOUTUBE_API_KEY

## Run Application
1. `poetry run python app.py`
