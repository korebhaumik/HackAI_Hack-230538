# Import necessary modules
import os
from uagents import Agent, Context
import requests
import json
import redis
from dotenv import load_dotenv
load_dotenv()

# Connect to Redis database
# redis_url = "redis://redis-db:6379/0"
redis_url = os.environ.get('REDIS_URL')
redis = redis.Redis.from_url(redis_url)

# Define a function to get the temperature for a given location
async def get_temperature(location) -> float:
    api_key = "a74eebe6704ebe9ae5aed50998769d85"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        return temp
    else:
        return 404

# Define an agent to periodically compute temperature status for users
temp_agent = Agent(
    name="temp_agent",
    seed="top_secret_key",
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Define a function to compute temperature status for users
@temp_agent.on_interval(period=300)
async def compute(ctx: Context):
    global redis
    keys = redis.keys("*")
    # print(keys)
    data = {}
    for key in keys:
        data[key.decode("utf-8")] = json.loads(redis.get(key))

    for user in data:
        temp = await get_temperature(data[user]["location"])
        if temp == 404:
            return

        data[user]["prevStatus"] = data[user]["status"]
        if temp < data[user]["minTemp"]:
            data[user]["status"] = -1
        elif temp > data[user]["maxTemp"]:
            data[user]["status"] = 1
        else:
            data[user]["status"] = 0

    for key, value in data.items():
        redis.set(key, json.dumps(value))

    ctx.logger.info("cycle complete")

# Run the agent
if __name__ == "__main__":
    temp_agent.run()