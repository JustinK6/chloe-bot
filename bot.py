import discord
import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

class ChloeBot(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix = '?', intents = discord.Intents.all()), os.getenv("DISCORD_APPLICATION_ID")

  async def setup_hook(self):
    self.remove_command('help')
    await self.load_extension(f"cogs.utils")
    await self.load_extension(f"cogs.misc")
    await self.load_extension(f"cogs.developer")
    await self.load_extension(f"cogs.rta")
    await self.load_extension(f"cogs.reddit")
    await self.load_extension(f"cogs.builds")
    await bot.tree.sync(guild = discord.Object(id=437118873150685194))

  async def on_ready(self):
    print(f'{self.user} has connected to discord!')

bot = ChloeBot()
bot.run(token)