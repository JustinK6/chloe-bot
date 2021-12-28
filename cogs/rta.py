import discord
import asyncio

from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(aliases = ['rs'])
  async def rtastats(self, ctx, *, input):
    # Check if the character being searched for is valid
    namequery = "SELECT name FROM Names WHERE alias = ?"

    name = db.fetch(namequery, input)
    if len(name) == 0:
      await ctx.send("No such character found.")
      return

    # Get string from query results
    nameString = name[0][0]

    

def setup(client):
  client.add_cog(Builds(client)) 