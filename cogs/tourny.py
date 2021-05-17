import discord
import random

from discord.ext import commands
from .db import db

class Tourny(commands.Cog):
  def __init__(self, client):
    self.client = client

  # Resets the tournament
  @commands.command(aliases = ['rt'])
  async def resettourny(self, ctx):
    self.roster = []
    self.tournyStarted = False
    await ctx.send("Tournament has been reset!")

  # Creates a message to notify the initialization of tourny, upon reactions players will be added to the tourny
  @commands.command(aliases = ['it'])
  async def initializeTourny(self, ctx, *, date):
    tournyMessage = await ctx.send(f"React to this message to be added to the tourny roster on {date}!")
    
    guildID = ctx.channel.guild.id
    reactMessageID = tournyMessage.id
    tournyStarted = 0

    query = "DELETE FROM Tournaments WHERE guild_id = ?;"
    db.execute(query, guildID)

    query = "DELETE FROM Roster WHERE guild_id = ?;"
    db.execute(query, guildID)

    query = "INSERT INTO Tournaments VALUES (?, ?, ?);"
    db.execute(query, guildID, reactMessageID, tournyStarted)

  # If a reaction is added to the tourny message, add player to tourny roster
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    guild_id = payload.guild_id

    # Fetch react message id from database
    query = "SELECT react_message_id FROM Tournaments WHERE guild_id = ?;"
    for value in db.fetch(query, guild_id):
      (reactMessageID) = value

    # Check if reaction is on reaction message
    if payload.message_id == int(reactMessageID[0]):
      name = payload.member.display_name
      id = payload.member.id
      print(name)

      # Make sure player is not already in roster before adding
      query = "INSERT INTO Roster VALUES (?,?,?);"
      db.execute(query, id, name, guild_id)
    else:
      pass

  # Displays the roster of those added to the tourny
  @commands.command(aliases = ['roster'])
  async def _roster(self, ctx):
    resultString = "```Current tournament roster:"

    # Get roster from database
    guildID = ctx.channel.guild.id
    query = "SELECT nick FROM ROSTER WHERE guild_id = ?;"
    roster = db.fetch(query, guildID)

    for player in roster:
      resultString += '\n'
      resultString += player[0]

    resultString += "```"
    await ctx.send(resultString)

  # Generates tournament brackets
  @commands.command(aliases = ['gb'])
  async def generateBracket(self, ctx):
    # Remove any previous bracket information
    guildID = ctx.channel.guild.id
    query = "DELETE FROM Matches WHERE guild_id = ?"
    db.execute(query, guildID)

    # Fetch the roster from database
    query = "SELECT nick FROM ROSTER WHERE guild_id = ?;"
    roster = db.fetch(query, guildID)

    # Shuffle bracket
    random.shuffle(roster)

    # Generate round one brackets
    matchNum = 1
    round = 1
    matches = []
    for i in range(0, len(roster), 2):
      query = "INSERT INTO Matches VALUES (?, ?, ?, ?, ?)"
      if i + 1 == len(roster):
        db.execute(query, guildID, matchNum, round, roster[i][0], "Bye")
      else:
        db.execute(query, guildID, matchNum, round, roster[i][0], roster[i + 1][0])
      matches.append(matchNum)
      matchNum += 1

    # Shuffle again
    random.shuffle(matches)

    # Generate other rounds
    while len(matches) > 1:
      round += 1
      next_matches = []
      
      for i in range(0, len(matches), 2):
        query = "INSERT INTO Matches VALUES (?, ?, ?, ?, ?)"
        if i + 1 == len(matches):
          db.execute(query, guildID, matchNum, round, "Winner of Match " + str(matches[i]), "Bye")
        else:
          db.execute(query, guildID, matchNum, round, "Winner of Match " + str(matches[i]), "Winner of Match " + str(matches[i + 1]))
        next_matches.append(matchNum)
        matchNum += 1

      matches = next_matches

  @commands.command(aliases = ['b'])
  async def bracket(self, ctx):
    # Fetch the roster from database
    guildID = ctx.channel.guild.id
    query = "SELECT match_num, player_one, player_two, round FROM Matches WHERE guild_id = ?;"
    bracket = db.fetch(query, guildID)

    # Sort bracket list by round
    bracket.sort(key=lambda tup: tup[3])

    curRound = 1
    resultString = "MATCHES:\n\nROUND 1:\n"
    for match in bracket:
      if curRound != match[3]:
        curRound = match[3]
        resultString += "\nROUND " + str(curRound) + "\n"
      resultString += "Match " + str(match[0]) + ": " + match[1] + " vs " + match[2]
      resultString += "\n"

    await ctx.send(resultString)
    
def setup(client):
  client.add_cog(Tourny(client))