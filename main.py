import os

import discord
import sqlite3
import datetime
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

ONE_WEEK = 604800  # 604800 seconds = 1 week
DATABASE = "meetings.db"
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

conn = sqlite3.connect(DATABASE)

conn.execute(
    """CREATE TABLE IF NOT EXISTS meetings
             (id INTEGER PRIMARY KEY,
             date TEXT NOT NULL)"""
)


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    weekly_reminder.start()


@tasks.loop(
    count=None, seconds=ONE_WEEK
)
async def weekly_reminder():
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM meetings ORDER BY date ASC LIMIT 1")
    result = cursor.fetchone()
    if result:
        meeting_date = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()
        days_until = (meeting_date - datetime.date.today()).days
        if days_until == 1:
            response = "The next meeting is tomorrow!"
        elif days_until == 7:
            response = "The next meeting is in one week!"
        else:
            response = "There are no meetings scheduled."
    else:
        response = "There are no meetings scheduled."
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(response)


@client.event
async def on_message(message):
    if message.content.startswith("!schedule"):
        await message.channel.send(get_all_meetings())
    elif message.content.startswith("!addmeeting"):
        date_str = message.content.split(" ")[1]
        return add_meeting(date_str)
    else:
        return "I don't have any more commands. Pray to god that I have the strength to find more."


def get_all_meetings():
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM meetings ORDER BY date ASC")
    result = cursor.fetchone()
    if result:
        # TODO: List all meetings
        for meeting in result:
            response += "The next meeting is in {} days on {}.".format(
                days_until, meeting_date.strftime("%A, %B %d")
            )
    else:
        response = "There are no meetings scheduled."

    return response


def add_meeting(date):
    # TODO: Evaluate date, if bad error
    meeting_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    try:
        conn.execute("INSERT INTO meetings (date) VALUES (?)", (meeting_date,))
        conn.commit()
        response = "Meeting scheduled for {}.".format(
            meeting_date.strftime("%A, %B %d")
        )
    except (IndexError, ValueError):
        response = "Invalid date format. Please use YYYY-MM-DD."

    return response


client.run(TOKEN)
