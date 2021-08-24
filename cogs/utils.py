import discord
import random

from discord.ext import commands
from .db import db
from discord.ext.commands import has_permissions, CheckFailure

class Utils(commands.Cog):
  def __init__(self, client):
    self.client = client

  #Events
  @commands.Cog.listener()
  async def on_ready(self):
    await self.client.change_presence(status=discord.Status.online, activity=discord.Game('Bully zZoNe'))
    print('Bot is ready.')

  @commands.Cog.listener()
  async def on_member_join(self, member):
    # Fetch welcome channel
    channel = self.client.get_channel(775185721182388275)

    await channel.send(f"Welcome {member.mention}! Please make sure the read the rules, and one of our mods will be with you shortly to give you roles that will grant you access to the rest of the channels in the server!")
    await channel.send("https://cdn.discordapp.com/attachments/865877909662859264/865877933180190720/Tamarinne252C2BKarin252C2Band2BArky2Bare2Bhere2Bto2Bwelcome2Bour2BHeirs2521.png")

  @commands.Cog.listener()
  async def on_member_remove(self, member):
    print(f'{member} has left the server.')

  #Commands
  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

  @commands.command()
  async def cr(self, ctx, one, two):
    await ctx.send(f'Your fastest unit: {one}\n Enemy fastest CR: {two}\n Enemy fastest speed: {float(two) * float(one)}')

  @commands.command(aliases = ['coin', 'cf', 'c'])
  async def coinFlip(self, ctx):
    await ctx.send(f'{random.choice(["Heads", "Tails"])}')

  @commands.command()
  @has_permissions(administrator = True, manage_messages = True, manage_roles = True)
  async def kick(self, ctx, member : discord.Member, *, reason = None):
    try:
      await member.kick(reason = reason)
      await ctx.send(f'{str(member)} has been kicked.')
    except Exception as error:
      await ctx.send(f"Can't kick {str(member)} : {error}")

  @commands.command()
  @has_permissions(administrator = True, manage_messages = True, manage_roles = True)
  async def ban(self, ctx, member : discord.Member, *, reason = None):
    try:
      await member.ban(reason = reason)
      await ctx.send(f'{str(member)} has been banned.')
    except Exception as error:
      await ctx.send(f"Can't ban {str(member)} : {error}")

  @commands.command()
  async def clear(self, ctx, amount = 1):
    try:
      await ctx.channel.purge(limit = amount + 1)
      print(amount)
    except Exception as error:
      await ctx.send(f"Can't clear messages : {error}")

  @commands.command()
  async def query(self, ctx, *, query):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    db.execute(query)

  @commands.command(aliases = ['t'])
  async def trepid(self, ctx):
     await ctx.send("TREPID SUPREMACY!")

  @commands.command(aliases = ['f'])
  async def fathom(self, ctx):
     await ctx.send("FATHOM SUPREMACY!")

  @commands.command(aliases = ['j'])
  async def jinxed(self, ctx):
     await ctx.send("JINXED SUPREMACY!")

def setup(client):
  client.add_cog(Utils(client))