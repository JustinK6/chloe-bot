import discord
import random

from discord.ext import commands

class Misc(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(aliases = ['t'])
  async def trepid(self, ctx):
    if ctx.guild.id == 524067267730735107:
      await ctx.send("TREPID SUPREMACY!")

  @commands.command(aliases = ['f'])
  async def fathom(self, ctx):
    if ctx.guild.id == 524067267730735107:
      await ctx.send("FATHOM SUPREMACY!")

  @commands.command(aliases = ['j'])
  async def jinxed(self, ctx):
    if ctx.guild.id == 524067267730735107:
      await ctx.send("JINXED SUPREMACY!")

  @commands.command()
  async def cr(self, ctx, one, two):
    await ctx.send(f'Your fastest unit: {one}\n Enemy fastest CR: {two}\n Enemy fastest speed: {float(two) * float(one)}')

  @commands.command(aliases = ['coin', 'cf', 'c'])
  async def coinFlip(self, ctx):
    await ctx.send(f'{random.choice(["Heads", "Tails"])}')

  @commands.command(aliases = ['8ball'])
  async def _8ball(self, ctx, *, question):
    responses = ['It is certain.',
                'It is decidedly so.',
                'Without a doubt.',
                'Yes - definitely.',
                'You may rely on it.',
                'As I see it, yes.',
                'Most likely.',
                'Outlook good.',
                'Yes.',
                'Signs point to yes.',
                'Reply hazy, try again.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                "Don't count on it.",
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good',
                'Very doubtful']

    await ctx.send(f'{random.choice(responses)}')

def setup(client):
  client.add_cog(Misc(client))