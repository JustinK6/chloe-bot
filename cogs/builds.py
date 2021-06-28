import discord
import random

from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

  # DEVELOPER ONLY COMMANDS

  @commands.command()
  async def addbuild(self, ctx, link, set, attack, defense, health, speed, cchance, cdamage, effectiveness, effectresist, *, character):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return

    sets = set.split(',')

    for s in sets:
      if not s in ['speed', 'hit', 'crit', 'attack', 'health', 'defense', 'resist', 'destruction', 'lifesteal', 'immunity', 'counter', 'rage', 'unity', 'revenge', 'injury', 'penetration']:
        await ctx.send("Invalid sets.")
        return
        
    query = "INSERT INTO Builds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    db.execute(query, character, link, set, attack, defense, health, speed, cchance, cdamage, effectiveness, effectresist)     

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

    # Process input and separate flag and character name values
    processedInput = self.processBuildInputs(input)

    if processedInput == None:
      await ctx.send("Error with flags. Try ?buildhelp.")
      return

    character = processedInput[0]
    flags = processedInput[1]

    # Check if the character being searched for is valid
    namequery = "SELECT name FROM Names WHERE alias = ?"

    name = db.fetch(namequery, character)
    if len(name) == 0:
      await ctx.send("No such character found.")
      return

    # Build the query for the build
    buildQuery = self.fetchBuildQuery(name[0][0], flags)

    if buildQuery == None:
      await ctx.send("Error with flags. Try ?buildhelp.")
      return

    # Attempt to fetch a build for specified character from the database
    print(buildQuery)
    build = db.fetch(buildQuery)

    if len(build) == 0:
      await ctx.send("No builds found. Try ?buildhelp, or ?bc for a list of characters with builds.")
      return
    
    await ctx.send(build[0][0])

  # Help command for the build command
  @commands.command(aliases=['bh'])
  async def buildhelp(self, ctx):
    resultString = "Build command format: ?build/?b [-flag(s)] [character name/alias]\nExample command: ?b -set=speed -set=crit -minspeed=290 acoli"
    resultString += "\n\nCurrent List of flags:\n```"

    flags = [
      "-set: A set the unit equipped excluding immunity ('speed', 'hit', 'crit', 'attack', 'health', 'defense', 'resist', 'destruction', 'lifesteal', 'immunity', 'counter', 'rage', 'unity', 'revenge', 'injury', 'penetration')",
      "-minspeed: Minimum speed of the build - any number",
      "-maxspeed: Maximum speed of the build - any number",
    ]

    for flag in flags:
      resultString += flag
      resultString += "\n"

    resultString += "```"

    await ctx.send(resultString)

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

  # Processes inputs for the ?build command
  def processBuildInputs(self, input):
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

    return (characterString, flags)

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
      "-set" : f"Sets LIKE \'%{value}%\' ",
      "-minspeed" : f"Speed >= {value} ",
      "-maxspeed" : f"Speed <= {value} ",
      "-immunity" : f"Immunity = \'{value}\'"
    }

    # Check if the flag is proper
    if not textFlag in flagToQuery.keys():
      return None

    query = flagToQuery[textFlag]

    return query

  # Returns a query based on specified inputs
  def fetchBuildQuery(self, characterString, flags):
    # Initial query
    query = f"SELECT ImageLink FROM Builds WHERE CharacterName = \"{characterString}\" "

    # Add onto query for each flag
    for flag in flags:
      query += "AND "
      convertedFlag = self.convertFlagToQuery(flag)

      # Check that flag was successfully converted
      if convertedFlag == None:
        return None

      query += convertedFlag

    query += "ORDER BY RANDOM() LIMIT 3"

    return query


def setup(client):
  client.add_cog(Builds(client))