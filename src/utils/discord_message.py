# Import necessary modules
import sys
sys.path.insert(0, './src/agents/temperatures')
from temperatures import temp_agent
import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import requests
import asyncio
import datetime
from temperatures import redis
from temperatures import get_temperature
from dotenv import load_dotenv
import random
import math
load_dotenv()

# Load Discord bot token from environment variable
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# Enable all intents for the Discord bot
intents = discord.Intents.all()

# Create a new Discord bot instance
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Define an event handler for when the bot is ready
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# Define a function to schedule temperature alert messages for a user
async def schedule_message(interaction, interval):
    is_active = True
    access_token = math.floor(random.random() * 10000000000000)
    global redis
    rawData = redis.get(str(interaction.user.name))
    userData = json.loads(rawData)

    userData["access_token"] = access_token
    redis.set(str(interaction.user.name), json.dumps(userData))

    while is_active:
        rawData = redis.get(str(interaction.user.name))
        userData = json.loads(rawData)

        is_active = userData["isActive"]

        if userData["status"] == 0:
            message = "Current temperature is inside your threshold. ☺️"
        elif userData["status"] == -1:
            message = "The current temperature is lower than the threshold. 🥶"
        elif userData["status"] == 1:
            message = "The current temperature is higher than the threshold. 🥵"

        if (
            userData["prevStatus"] != userData["status"]
            and userData["access_token"] == access_token
        ):
            embed = discord.Embed(description=message, color=discord.Color.green())
            await interaction.followup.send(embed=embed, ephemeral=True)

        await asyncio.sleep(interval)

# Define a function to write user data to Redis database
async def write_data(user, min_temp, max_temp, location):
    current_temp = await get_temperature(location)
    now = datetime.datetime.now()

    data = {
        "location": location,
        "minTemp": min_temp,
        "maxTemp": max_temp,
        "status": 0,
        "prevStatus": 2,
        "isActive": True,
        "lastUpdated": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    if current_temp < min_temp:
        data["status"] = -1
    elif current_temp > max_temp:
        data["status"] = 1
    else:
        data["status"] = 0

    global redis
    redis.set(str(user), json.dumps(data))

# Define a function to get weather data for a location using OpenWeatherMap API
async def get_weather(location):
    api_key = "a74eebe6704ebe9ae5aed50998769d85"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data = data["main"]
        return data
    else:
        raise Exception(f"Failed to fetch temperature data: {response.text}")

# Load valid locations from a JSON file
with open("location.json", "r") as f:
    valid_loc = json.load(f)

# Define a command to enable temperature alerts for a user
@bot.tree.command(
    name="alert",
    description="Set custom temperature alerts using the power of fetch.ai for the given threshold values!",
)
@app_commands.describe(
    min_temp="Set the minimum temperature threshold for the alert.",
    max_temp="Set the maximum temperature threshold for the alert.",
    location="Set the location for the temperature.",
)
async def enable(
    interaction: discord.Interaction,
    min_temp: float,
    max_temp: float,
    location: str,
):
    location = location.title()
    global valid_loc
    try:
        index = valid_loc.index(location)

        embed = discord.Embed(
            title="Alert Enabled !!",
            description="Your weather agent alert has been enabled. You'll be notified every time temperature drops or exceeds your threshold.",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=f"`🥶 Minimum Temperature Threshold`:  {min_temp} °C",
            value="",
            inline=False,
        )
        embed.add_field(
            name=f"`🥵 Maximum Temperature Threshold`:  {max_temp} °C",
            value="",
            inline=False,
        )
        embed.add_field(name=f"`🌐 Location`:  {location}", value="", inline=False)
        embed.set_footer(text="Use command `/disable_alert` to disable the alerts.")
        if min_temp > max_temp:
            await interaction.response.send_message(
                "Minimum temperature threshold cannot be greater than maximum temperature threshold.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await write_data(interaction.user.name, min_temp, max_temp, location)
            await schedule_message(interaction, 600)

    except ValueError:
        await interaction.response.send_message(
            "This location is not supported by our agent :(", ephemeral=True
        )

# Define a command to get weather updates for a location
@bot.tree.command(
    name="weather_updates", description="Get weather updates for a given location."
)
@app_commands.describe(location="Set the location parameter.")
async def get_updates(interaction: discord.Interaction, location: str):
    location = location.title()
    global valid_loc
    try:
        index = valid_loc.index(location)
        data = await get_weather(location)

        current_temp = data["temp"]
        feels_like = data["feels_like"]
        temp_min = data["temp_min"]
        temp_max = data["temp_max"]
        pressure = data["pressure"]
        humidity = data["humidity"]

        embed = discord.Embed(
            title=f"Weather Updates for {location}",
            description="",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=f"> Current Temperature is: `{current_temp} °C`",
            value="",
            inline=False,
        )
        embed.add_field(
            name=f"> Temp feels like: `{feels_like} °C`", value="", inline=False
        )
        embed.add_field(
            name=f"> Current Pressure: `{pressure} Pa`", value="", inline=False
        )
        embed.add_field(
            name=f"> Current Humidity: `{humidity} %`", value="", inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except ValueError:
        await interaction.response.send_message(
            "This location is not supported by our agent :(", ephemeral=True
        )

# Define a command to disable temperature alerts for a user
@bot.tree.command(
    name="disable_alert", description="Call this command to disable any active alert."
)
async def disable(interaction: discord.Interaction):
    global redis
    rawData = redis.get(str(interaction.user.name))
    print(rawData)
    if rawData is None:
        embed = discord.Embed(
            title="Alert Disabled !!",
            description="Your weather agent alert has been disabled successfully.",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="`/alert`",
            value="Use this command to reactivate the alerts.",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    data = json.loads(rawData)
    if data:
        data["isActive"] = False

    redis.set(str(interaction.user.name), json.dumps(data))

    embed = discord.Embed(
        title="Alert Disabled !!",
        description="Your weather agent alert has been disabled successfully.",
        color=discord.Color.red(),
    )
    embed.add_field(
        name="`/alert`",
        value="Use this command to reactivate the alerts.",
        inline=False,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Start the Discord bot
bot.run(TOKEN)