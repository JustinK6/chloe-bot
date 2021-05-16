import discord
import random

from discord.ext import commands

class Jokes(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def zzone(self, ctx):
    await ctx.send('zZoNe is a power abusing bully.')

  @commands.command()
  async def zzonequote(self, ctx):
    responses = ['fk you',
                'fite me',
                'ass',
                'gtfo',
                'shove a cactus up your ass',
                'scrub',
                'Oi',
                'Asssssss']

    await ctx.send(f'{random.choice(responses)}')

  @commands.command()
  async def morvek(self, ctx):
    await ctx.send('RIP Flan RIP Flidica')

  @commands.command()
  async def goku(self, ctx):
    await ctx.send('COUNTER CITY BABY')
  
  @commands.command()
  async def kas(self, ctx):
    await ctx.send('Kas is a TRAITOR :frowning:')

  @commands.command(aliases = ['seal'])
  async def sealsworth(self, ctx):
    await ctx.send('Who\'s that? Never heard of him.')

def setup(client):
  client.add_cog(Jokes(client))