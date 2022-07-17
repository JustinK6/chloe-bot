from inspect import currentframe
import discord
import asyncio

from discord import app_commands
from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

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

    for build in build:
      await ctx.send(build[0])

  # Help command for the build command
  @commands.command()
  async def flags(self, ctx):
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

    embeds = self.getBuildCountPages(counts)
    buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"]

    if len(embeds) == 0:
      return

    current = 0
    msg = await ctx.send(embed=embeds[current])
    
    for button in buttons:
        await msg.add_reaction(button)
        
    while True:
        try:
            reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=30.0)

        except asyncio.TimeoutError:
            return print("test")

        else:
            previous_page = current
            if reaction.emoji == u"\u23EA":
                current = 0
                
            elif reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1
                    
            elif reaction.emoji == u"\u27A1":
                if current < len(embeds)-1:
                    current += 1

            elif reaction.emoji == u"\u23E9":
                current = len(embeds)-1

            for button in buttons:
                await msg.remove_reaction(button, ctx.author)

            if current != previous_page:
                await msg.edit(embed=embeds[current])

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

  # Get build count embed pages
  def getBuildCountPages(self, counts):
    currentEmbed = None

    embeds = []
    page = 1
    num = 0

    for count in counts:
      if num == 0:
        currentEmbed = discord.Embed(
          title = f"Build Counts {page}",
          description = "Number of builds for each character."
        )

      currentEmbed.add_field(name = count[0], value = f"Number of builds: {count[1]}", inline = True)
      num += 1

      if num == 12:
        embeds.append(currentEmbed)
        currentEmbed = None
        num = 0
        page += 1

    if not currentEmbed == None:
      embeds.append(currentEmbed)

    print(len(embeds))
    return embeds


async def setup(client):
  await client.add_cog(Builds(client), guilds = [discord.Object(id = 437118873150685194)]) 