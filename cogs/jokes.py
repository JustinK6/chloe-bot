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
    await ctx.send('RIP Flan RIP Flidica RIP Spez RIP SBA')

  @commands.command()
  async def goku(self, ctx):
    await ctx.send('COUNTER CITY BABY')
  
  @commands.command()
  async def kas(self, ctx):
    await ctx.send('Kas is a TRAITOR :frowning:')

  @commands.command()
  async def boba(self, ctx):
    await ctx.send('Someone get this man to join a tourny already')
  
  @commands.command()
  async def sonic(self, ctx):
    await ctx.send('<:_Pepe_ludwig:777967949612056576> <:jerry:837176892385001544> <:ravicreep:795478988100468756> <:ravi:795478986737319937> <:OPsig:837178265109004308> <:0_haha:730932492768509972> <:0_smug:730931683364306957>')

def setup(client):
  client.add_cog(Jokes(client))