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
  async def addbuild(self, ctx, link, set, *, character):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    query = "INSERT INTO Builds VALUES (?, ?, ?)"
    db.execute(query, character, link, set)

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
  async def build(self, ctx, *, input):
    checkSet = input.split()[0]
    buildquery = ""
    namequery = "SELECT name FROM Names WHERE alias = ?"

    validSets = [
      'speed', 
      'hit', 
      'crit', 
      'attack', 
      'health', 
      'defense', 
      'resist', 
      'destruction', 
      'lifesteal', 
      'counter', 
      'immunity', 
      'rage', 
      'unity', 
      'revenge', 
      'injury', 
      'penetration'
    ]

    if not (checkSet in validSets):
      buildquery = "SELECT ImageLink FROM Builds WHERE CharacterName = ? ORDER BY RANDOM() LIMIT 1"
      character = input
    else:
      buildquery = "SELECT ImageLink FROM Builds WHERE CharacterName = ? AND MainSet = ? ORDER BY RANDOM() LIMIT 1"
      character = input[len(checkSet) + 1:]

    name = db.fetch(namequery, character)
    if len(name) == 0:
      await ctx.send("No such character found.")
      return

    if checkSet in validSets:
      build = db.fetch(buildquery, name[0][0], set)
    else:
      build = db.fetch(buildquery, name[0][0])
    if len(build) == 0:
      await ctx.send("No builds found.")
      return
    
    await ctx.send(build[0][0])

  # Gets list of available characters and aliases
  @commands.command()
  async def builds(self, ctx):
    resultString = "Current available chracter builds: \n"

    namequery = "SELECT DISTINCT name FROM Names"
    names = db.fetch(namequery)

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
 
    print(resultString)

  # Gets a count of the number of builds each character has
  @commands.command(aliases = ['bc', 'buildcount'])
  async def buildCount(self, ctx):
    query = "SELECT CharacterName, Count(ImageLink) FROM Builds GROUP BY CharacterName"
    counts = db.fetch(query)

    resultString = "Number of builds for each character: ```\n"
    for count in counts:
      resultString += count[0] # character name
      resultString += ": "
      resultString += str(count[1]) # build count
      resultString += "\n"

    resultString += "```"

    await ctx.send(resultString)

def setup(client):
  client.add_cog(Builds(client))