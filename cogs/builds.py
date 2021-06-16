import discord
import random

from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def builds(self, ctx):
      await ctx.send("""Current available builds: \n
        aras,\n
        charlotte,\n
        """)

  @commands.command()
  async def addbuild(self, ctx, character, link):
    query = "INSERT INTO Builds VALUES (?, ?)"
    db.execute(query, character, link)

  @commands.command()
  async def charlotte(self, ctx):
    query = "SELECT ImageLink FROM Builds WHERE CharacterName = 'charlotte' ORDER BY RANDOM() LIMIT 1"
    build = db.fetch(query)

    await ctx.send(build[0][0])

  @commands.command(aliases = ['ras'])
  async def aras(self, ctx):
    query = "SELECT ImageLink FROM Builds WHERE CharacterName = 'aras' ORDER BY RANDOM() LIMIT 1"
    build = db.fetch(query)

    await ctx.send(build[0][0])
      
def setup(client):
  client.add_cog(Builds(client))