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

  # Overall help command
  @commands.command()
  async def help(self, ctx):
    embed = discord.Embed(
      title = "Queen Chloe Help",
      description = "Commands help for the queen chloe bot."
    )

    # Set thumbnail
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/882867390554210325/882867525925367858/pmtntt4lyys61.png")

    # Add help text/fields for command groups
    embed.add_field(name = "?buildhelp", value = "Use this command for help with commands dealing with builds.", inline = False)
    embed.add_field(name = "?tournyhelp", value = "Use this command for help with commands dealing with tournies.", inline = False)
    embed.add_field(name = "?mischelp", value = "Use this command to explore other misc commands available in the bot.", inline = False)

    await ctx.send(embed = embed)


  # Subcategory help commands
  @commands.command()
  async def buildhelp(self, ctx):
    embed = discord.Embed(
      title = "Queen Chloe Help - Builds",
      description = "Commands help for build commands for the queen chloe bot."
    )

    # Set thumbnail
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/882867390554210325/882867525925367858/pmtntt4lyys61.png")

    # Add help text/fields for commands
    embed.add_field(name = "?build [?b] <FLAG(s)> <HERO NAME>", value = "Command to fetch a build of a character. For info about flags, use ?flags or ?f.", inline = False)
    embed.add_field(name = "?buildcount [?bc]", value = "Command to fetch a count of the number of builds currently stored for each character.", inline = False)
    embed.add_field(name = "?flags", value = "Command to fetch info about current available flags, as well as how to use them.", inline = False)

    await ctx.send(embed = embed)

  @commands.command()
  async def tournyhelp(self, ctx):
    embed = discord.Embed(
      title = "Queen Chloe Help - Tourny",
      description = "COMING SOON!"
    )

    # Set thumbnail
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/882867390554210325/882867525925367858/pmtntt4lyys61.png")

    await ctx.send(embed = embed)

  @commands.command()
  async def mischelp(self, ctx):
    embed = discord.Embed(
      title = "Queen Chloe Help - Misc",
      description = "Commands help for miscellaneous commands for the queen chloe bot."
    )

    # Set thumbnail
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/882867390554210325/882867525925367858/pmtntt4lyys61.png")

    embed.add_field(name = "?coin [?c]", value = "Flip a coin. Heads or tails?", inline = False)
    embed.add_field(name = "?cr <YOUR SPEED> <ENEMY CR>", value = "Calculate approximate enemy speed using your unit's speed and the enemy's position on the CR bar", inline = False)
    embed.add_field(name = "?8ball <QUESTION>", value = "Ask the magic 8 ball a question!", inline = False)
    embed.add_field(name = "?art", value = "Grabs a random image from the Epic Seven subreddit with the art flair.", inline = False)
    embed.add_field(name = "?cat", value = "Grabs a random image from a cat subreddit with the art flair.", inline = False)

    await ctx.send(embed = embed)

def setup(client):
  client.add_cog(Utils(client))