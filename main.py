import os
import traceback

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

ONE_WEEK = 604800  # 604800 seconds = 1 week
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GUILD_ID = discord.Object(int(os.getenv("GUILD_ID")))


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=GUILD_ID)

    @tasks.loop(seconds=ONE_WEEK)
    async def post_upcoming_meetings(self):
        channel = self.get_channel(CHANNEL_ID)

        # TODO: Flesh this out with grabbing dates from db
        await channel.send("test")


class AddMeeting(discord.ui.Modal, title='Feedback'):
    meeting_date = discord.ui.TextInput(
        label='Meeting Date',
    )

    leader = discord.ui.TextInput(
        label='Leader',
        required=False
    )

    topic = discord.ui.TextInput(
        label='Topic',
        required=False
    )

    feedback = discord.ui.TextInput(
        label='Notes',
        style=discord.TextStyle.long,
        placeholder='Type your comment here...',
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Meeting added, thanks for doing that {interaction.user.name}!',
                                                ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)


client = MyClient()


@client.tree.command(name='add', description="Add a new meeting")
async def add_meeting(interaction: discord.Interaction):
    await interaction.response.send_modal(AddMeeting())


client.run(TOKEN)
