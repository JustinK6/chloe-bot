import discord
import random

from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

  # DEVELOPER ONLY COMMANDS

  @commands.command()
  async def itbuilds(self, ctx):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return

    query = """CREATE TABLE Builds (
        CharacterName varchar(256),
        ImageLink varchar(256) PRIMARY KEY
        )"""
    
    db.execute(query)

  @commands.command()
  async def itnames(self, ctx):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return

    query = """CREATE TABLE Names (
      alias varchar(256) PRIMARY KEY,
      name varchar(256)
    )"""

    db.execute(query)

  @commands.command()
  async def addbuild(self, ctx, link, *, character):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    query = "INSERT INTO Builds VALUES (?, ?)"
    db.execute(query, character, link)

  @commands.command()
  async def addname(self, ctx, *, combined):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return

    alias = combined.split(',')[0]
    name = combined.split(',')[1]
    
    query = "INSERT INTO Names VALUES (?, ?)"
    db.execute(query, alias, name)

  @commands.command()
  async def removebuild(self, ctx, link):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    query = "DELETE FROM Builds WHERE ImageLink = ?"
    db.execute(query, link)

  @commands.command()
  async def removename(self, ctx, *, alias):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    query = "DELETE FROM Names WHERE alias = ?"
    db.execute(query, alias)

  # REGULAR COMMANDS

  # Gets the build of a specified character
  @commands.command()
  async def build(self, ctx, *, character):
    buildquery = "SELECT ImageLink FROM Builds WHERE CharacterName = ? ORDER BY RANDOM() LIMIT 1"
    namequery = "SELECT name FROM Names WHERE alias = ?"

    name = db.fetch(namequery, character)
    if len(name) == 0:
      await ctx.send("No such character found.")
      return

    build = db.fetch(buildquery, name[0][0])
    if len(build) == 0:
      await ctx.send("No builds found.")
      return
    
    await ctx.send(build[0][0])

  # Gets list of available characters and aliases
  @commands.command()
  async def builds(self, ctx):
    resultString = "Current available chracter builds: \n```"

    namequery = "SELECT DISTINCT name FROM Names"
    names = db.fetch(namequery)
    print(names)

    for name in names:
      aliasquery = "SELECT alias FROM Names WHERE name = ?"
      aliases = db.fetch(aliasquery, name[0])
      
      resultString += name[0]
      resultString += ": ("

      for alias in aliases:
        resultString += alias[0]
        resultString += ", "

      if len(resultString) > 2:
        resultString = resultString[0:len(resultString) - 2] # cut off last comma and space

      resultString += ")\n"

    resultString += "```"  
    await ctx.send(resultString)

def setup(client):
  client.add_cog(Builds(client))