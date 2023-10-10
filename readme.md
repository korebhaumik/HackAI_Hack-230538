<a href="/">
    <h1>Temperature Agent</h1>
</a>
<p >
  The temperature agent is a Fetch.ai-based agent that periodically computes the temperature status for users based on their location and temperature thresholds.
</p>

<p >
  <a href="#description"><strong>Description</strong></a> ·
  <a href="#features"><strong>Features</strong></a> ·
  <a href="#key-functionality"><strong>Key functionality</strong></a> ·
  <a href="#running-locally"><strong>Running locally</strong></a> ·
</p>
<br/>

## Description

This project is a temperature agent that periodically computes the temperature status for users based on their location and temperature thresholds. It uses the [Fetch.ai](https://fetch.ai/) framework to define an agent that connects to a [Redis](https://redis.io/docs/getting-started/) database to store user data, and uses the [OpenWeatherMap](https://openweathermap.org/api) API to fetch temperature data for each user's location. The temperature status is computed based on the user's temperature thresholds, and the updated user data is stored back in the Redis database. The agent also sends a message to a Discord channel to notify the user of their temperature status. The agent is deployed on [Docker](https://www.docker.com/) and can be run locally or on a server.

**Link to add the discord bot to your server:** [bot](https://discord.com/api/oauth2/authorize?client_id=1159898199285305395&permissions=8&scope=bot)

<p>Available commands</p>
<img width="1392" alt="Screenshot 2023-10-11 at 12 02 16 AM" src="https://github.com/korebhaumik/hack-ai-temp/assets/106856064/0ed9561e-d73b-458e-8d1f-be26a298169d">

<p>Alert Command</p>
<img width="1392" alt="Screenshot 2023-10-11 at 12 01 43 AM" src="https://github.com/korebhaumik/hack-ai-temp/assets/106856064/007c9886-2038-4fab-ac64-8f0f3a9445a4">

<p>Disable Alerts</p>
<img width="1392" alt="Screenshot 2023-10-11 at 12 02 11 AM" src="https://github.com/korebhaumik/hack-ai-temp/assets/106856064/79b1b2e5-dd80-452d-aae8-482cd87281ad">

<p>Get weather updates</p>
<img width="1392" alt="Screenshot 2023-10-11 at 12 02 42 AM" src="https://github.com/korebhaumik/hack-ai-temp/assets/106856064/5b0465e4-6fd0-4591-8353-cd2a1c7042ef">



## Features

- [Fetch.ai](https://fetch.ai/) for agent development
- [Redis](https://redis.io/docs/getting-started/) for storing user data
- [OpenWeatherMap](https://openweathermap.org/api) for fetching temperature data
- [Docker](https://www.docker.com/) for containerization
- [Discord.py](https://discordpy.readthedocs.io/en/stable/) for creating the discord bot


## Key Functionality

- Ability to set max & min temperature thresholds for each user.
- Ability to get weather updates for any given location.
- Ability to disable active alerts for a given user.
- Notifies users periodically if the temperature for a given location exceeds or enters the threshold.


## Running locally

You will need to have the necessary environment variables setup in your `.env` file.
This includes your Discord bot token, redis-db url. 
    
```bash
DISCORD_BOT_TOKEN =
REDIS_URL =
```

> Note: You should not commit your `.env` file or it will expose secrets that will allow others to control access to your authentication provider accounts.

1. Activate Virtual Environment: `conda activate hack-ai`
2. Make a new `.env` file.
3. Populate the `.env` file with the necessary environment variables.

```bash
pip install -r requirements.txt
python src/main.py
```

Your bot should be active and running.

## Running locally with docker

```bash
docker login
docker pull korebhaumik/temperature-agent-hack-ai
docker pull korebhaumik/amd-redis-db
docker network create my-network
docker run -it -d -p 6379:6379 --network my-network --name amd-redis-db korebhaumik/amd-redis-db
docker run -it -d -v ./:/app -e DISCORD_BOT_TOKEN="" -e REDIS_URL=""  --network my-network --name hack-ai korebhaumik/temperature-agent-hack-ai
```

> Note: If the docker image is not available (repo is privated), you can build it locally by running `docker build -t temperature-agent-hack-ai .` in the root directory of the project.
