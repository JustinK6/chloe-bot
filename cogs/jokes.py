import discord
import random

from discord.ext import commands

class Jokes(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(aliases=['t'])
  async def trepid(self, ctx):
    await ctx.send('TREPID SUPREMACY!')

  @commands.command(aliases=['f'])
  async def fathom(self, ctx):
    await ctx.send('FATHOM SUPREMACY!')
    
def setup(client):
  client.add_cog(Jokes(client))