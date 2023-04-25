import discord
import sqlite3
import datetime
from discord.ext import tasks

TOKEN = "your_bot_token_here"
DATABASE = "meetings.db"

client = discord.Client()

# Connect to the SQLite database
conn = sqlite3.connect(DATABASE)

# Create a table to store meeting dates
conn.execute(
    """CREATE TABLE IF NOT EXISTS meetings
             (id INTEGER PRIMARY KEY,
             date TEXT NOT NULL)"""
)


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    weekly_reminder.start()  # Start the weekly reminder task


@tasks.loop(
    count=None, seconds=604800
)  # Run the task every week (604800 seconds = 1 week)
async def weekly_reminder():
    # Retrieve the next meeting date from the database
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM meetings ORDER BY date ASC LIMIT 1")
    result = cursor.fetchone()
    if result:
        meeting_date = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()
        # Calculate the number of days until the next meeting
        days_until = (meeting_date - datetime.date.today()).days
        if days_until == 0:
            response = "The next meeting is today!"
        elif days_until == 1:
            response = "The next meeting is tomorrow!"
        else:
            response = "The next meeting is in {} days on {}.".format(
                days_until, meeting_date.strftime("%A, %B %d")
            )
    else:
        response = "There are no meetings scheduled."
    # Send the reminder message to the channel
    channel = client.get_channel(YOUR_CHANNEL_ID_HERE)
    await channel.send(response)


@client.event
async def on_message(message):
    if message.content.startswith("!schedule"):
        # Retrieve the next meeting date from the database
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM meetings ORDER BY date ASC LIMIT 1")
        result = cursor.fetchone()
        if result:
            meeting_date = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()
            # Calculate the number of days until the next meeting
            days_until = (meeting_date - datetime.date.today()).days
            if days_until == 0:
                response = "The next meeting is today!"
            elif days_until == 1:
                response = "The next meeting is tomorrow!"
            else:
                response = "The next meeting is in {} days on {}.".format(
                    days_until, meeting_date.strftime("%A, %B %d")
                )
        else:
            response = "There are no meetings scheduled."
        await message.channel.send(response)

    elif message.content.startswith("!addmeeting"):
        # Extract the date from the message and insert it into the database
        try:
            date_string = message.content.split(" ")[1]
            meeting_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            conn.execute("INSERT INTO meetings (date) VALUES (?)", (date_string,))
            conn.commit()
            response = "Meeting scheduled for {}.".format(
                meeting_date.strftime("%A, %B %d")
            )
        except (IndexError, ValueError):
            response = "Invalid date format. Please use YYYY-MM-DD."
        await message

        return response
