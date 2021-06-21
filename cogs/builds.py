import discord
import random

from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

  # DEVELOPER ONLY COMMANDS

  @commands.command()
  async def addbuild(self, ctx, link, set, immunity, attack, defense, health, speed, cchance, cdamage, effectiveness, effectresist, *, character):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    query = "INSERT INTO Builds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    db.execute(query, character, link, set, attack, defense, health, speed, cchance, cdamage, effectiveness, effectresist, immunity)

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
  async def removeopbuild(self, ctx, link):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    query = "DELETE FROM OPBuilds WHERE ImageLink = ?"
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
  @commands.command(aliases = ['b'])
  async def build(self, ctx, *, input):
    input = input.lower()
    print(self.fetchBuildQuery(input))

    checkSet = input.split()[0]
    buildquery = ""

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

    # Check if the character being searched for is valid
    namequery = "SELECT name FROM Names WHERE alias = ?"

    name = db.fetch(namequery, character)
    if len(name) == 0:
      await ctx.send("No such character found.")
      return

    # Attempt to fetch a build for specified character from the database
    if checkSet in validSets:
      build = db.fetch(buildquery, name[0][0], checkSet)
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
  @commands.command(aliases = ['bc'])
  async def buildcount(self, ctx):
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

  # HELPER METHODS

  # Converts a flag to an appropriate query piece as necessary
  def convertFlagToQuery(self, flag):
    # Check that flag is formatted properly
    tokens = flag.split('=')
    if not len(tokens) == 2:
      return None

    textFlag = tokens[0]
    value = tokens[1]

    # Dictionary of flags to query pieces
    flagToQuery = {
      "-mainset" : "MainSet = "
    }

    # Check if the flag is proper
    if not textFlag in flagToQuery.keys():
      return None

    query = flagToQuery[textFlag] + tokens[1]

    return query

  # Returns a query based on specified inputs
  def fetchBuildQuery(self, input):
    character = [] # Represents list of tokens representing the character
    flags = [] # Represents list of tokens representing flags

    for token in input.split():
      # Check if each token is a flag
      if token.startswith('-'):
        flags.append(token)
      else:
        character.append(token)

    # Build the character string
    count = 0
    characterString = ""
    for token in character:
      if count == 0:
        characterString += token
      else:
        characterString += " "
        characterString += token

      count += 1

    # Initial query
    query = f"SELECT ImageLink FROM Builds WHERE CharacterName = {characterString}"

    # Add onto query for each flag
    for flag in flags:
      query += "AND "
      convertedFlag = self.convertFlagToQuery(flag)

      # Check that flag was successfully converted
      if convertedFlag == None:
        return None

      query += convertedFlag

    return query



def setup(client):
  client.add_cog(Builds(client))