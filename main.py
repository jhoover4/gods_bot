import os
import traceback

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from db import Database

load_dotenv()

TASK_SECONDS = int(os.getenv("REMINDER_SECONDS_WAIT"))
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        description = "God's bot doing God's work"
        super().__init__(description=description, intents=intents)

        self.tree = app_commands.CommandTree(self)

    @tasks.loop(seconds=TASK_SECONDS)
    async def send_info(self):
        database = Database()
        try:
            msg = database.get_all_meetings_formatted()
        except:
            # TODO: Better error handling here
            msg = "I'm sorry, I've had trouble communing with The Father in getting all the meetings"

        channel = self.get_channel(CHANNEL_ID)
        await channel.send(msg)

    @send_info.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def setup_hook(self) -> None:
        self.send_info.start()
        await self.tree.sync()


class AddMeeting(discord.ui.Modal, title='Add Meeting'):
    meeting_date = discord.ui.TextInput(
        label='Meeting Date',
        placeholder='mm/dd/yy'
    )

    leader = discord.ui.TextInput(
        label='Leader',
        required=False
    )

    topic = discord.ui.TextInput(
        label='Topic',
        required=False
    )

    notes = discord.ui.TextInput(
        label='Notes',
        style=discord.TextStyle.long,
        placeholder='Type your note here...',
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        database = Database()

        passed = database.insert_meeting(self.meeting_date.value, self.leader.value.lower(), self.topic.value, self.notes.value)
        if passed:
            msg = f"I've prayed for a meeting to be added on {self.meeting_date.value}, let's only hope that the " \
                  f"spirit can guide us towards it {interaction.user.name}"
        else:
            msg = "I'm sorry, I've had trouble communing with The Father in creating this meeting"

        await interaction.response.send_message(msg, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("I'm sorry, I've had trouble communing with The Father", ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)


client = MyClient()


@client.tree.command()
async def add_meeting(interaction: discord.Interaction) -> None:
    await interaction.response.send_modal(AddMeeting())


@client.tree.command()
async def info(interaction: discord.Interaction) -> None:
    database = Database()
    try:
        msg = database.get_all_meetings_formatted()
    except:
        # TODO: Better error handling here
        msg = "I'm sorry, I've had trouble communing with The Father in getting all the meetings"

    await interaction.response.send_message(msg)


client.run(TOKEN)
