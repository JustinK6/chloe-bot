import discord
import random

from discord.ext import commands
from .db import db
from discord.ext.commands import has_permissions

class Utils(commands.Cog):
  def __init__(self, client):
    self.client = client

  #Events
  @commands.Cog.listener()
  async def on_ready(self):
    await self.client.change_presence(status=discord.Status.online, activity=discord.Game('Bonking heirs!'))
    print('Bot is ready.')

  @commands.Cog.listener()
  async def on_member_join(self, member):
    # Fetch welcome channel of guild from the database if there is one
    query = "SELECT welcome_id FROM Guilds WHERE guild_id = ?"
    welcomeChannel = db.fetch(query, member.guild.id)

    # Make sure guild has a welcome channel
    if len(welcomeChannel) == 0:
      return

    channel = self.client.get_channel(welcomeChannel[0][0])

    await channel.send(f"Welcome {member.mention}! Please make sure the read the rules, and one of our mods will be with you shortly to give you roles that will grant you access to the rest of the channels in the server!")
    await channel.send("https://cdn.discordapp.com/attachments/865877909662859264/865877933180190720/Tamarinne252C2BKarin252C2Band2BArky2Bare2Bhere2Bto2Bwelcome2Bour2BHeirs2521.png")

  #Commands
  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

  @commands.command(aliases = ['w'])
  async def welcome(self, ctx):
    # Add new row or replace row with guild id of the server
    query = "INSERT OR REPLACE INTO Guilds VALUES (?, ?)"
    db.execute(query, ctx.guild.id, ctx.channel.id)

    await ctx.send("Channel set as welcome channel!")

  @commands.command()
  async def clear(self, ctx, amount = 1):
    try:
      await ctx.channel.purge(limit = amount + 1)
      print(amount)
    except Exception as error:
      await ctx.send(f"Can't clear messages : {error}")

def setup(client):
  client.add_cog(Utils(client))