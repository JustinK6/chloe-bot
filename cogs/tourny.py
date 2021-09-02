import discord
import random
from discord import client

from discord.ext import commands
from .db import db

class Tourny(commands.Cog):
  def __init__(self, client):
    self.client = client

  # Resets the tournament
  @commands.has_permissions(administrator=True)
  @commands.command(aliases = ['rt'])
  async def resettourny(self, ctx):
    self.roster = []
    self.tournyStarted = False
    await ctx.send("Tournament has been reset!")

  # Creates a message to notify the initialization of tourny, upon reactions players will be added to the tourny
  @commands.command(aliases = ['it'])
  async def initializeTourny(self, ctx, *, date):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return

    tournyMessage = await ctx.send(f"React to this message to be added to the tourny roster on {date}! \n<a:maidbonk:855548328108228609> to be added to the tourny \n<:_Pepe_ludwig:840158099091226664> if you would like to not join, but still be given a role to be pinged when matches occur")
    await tournyMessage.add_reaction("<a:maidbonk:855548328108228609>")
    await tournyMessage.add_reaction("<:_Pepe_ludwig:840158099091226664>")
    
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
    reactMessageID = (0)

    # Fetch react message id from database
    query = "SELECT react_message_id FROM Tournaments WHERE guild_id = ?;"
    for value in db.fetch(query, guild_id):
      (reactMessageID) = value

    # Check if reaction is on reaction message
    if payload.message_id == int(reactMessageID[0] and not payload.user_id == 171782191188017152):
      name = payload.member.display_name
      id = payload.member.id
      role = discord.utils.get(payload.member.guild.roles, name = "Tourny")

      # Add tournament role
      if str(payload.emoji) == "<a:maidbonk:855548328108228609>" or  str(payload.emoji) == "<:_Pepe_ludwig:840158099091226664>":
        await payload.member.add_roles(role)

      if str(payload.emoji) == "<a:maidbonk:855548328108228609>":
        # Make sure player is not already in roster before adding
        query = "INSERT INTO Roster VALUES (?,?,?);"
        db.execute(query, id, name, guild_id)
    else:
      pass

  # Displays the roster of those added to the tourny
  @commands.command(aliases = ['roster'])
  async def _roster(self, ctx):
    resultString = "Current tournament roster:```"

    # Get roster from database
    guildID = ctx.channel.guild.id
    query = "SELECT nick FROM ROSTER WHERE guild_id = ?;"
    roster = db.fetch(query, guildID)

    for player in roster:
      resultString += '\n'
      resultString += player[0]

    resultString += "```"
    await ctx.send(resultString)

  @commands.has_permissions(administrator=True)
  @commands.command(aliases = ['ar'])
  async def addToRoster(self, ctx, id, nick, guildID):
    query = "INSERT INTO Roster VALUES (?,?,?);"
    db.execute(query, id, nick, guildID)

  # Generates tournament brackets
  @commands.has_permissions(administrator=True)
  @commands.command(aliases = ['gb'])
  async def generateBracket(self, ctx):
    # Remove any previous bracket information
    guildID = ctx.channel.guild.id
    query = "DELETE FROM Matches WHERE guild_id = ?"
    db.execute(query, guildID)

    # Fetch the roster from database
    query = "SELECT nick FROM Roster WHERE guild_id = ?;"
    roster = db.fetch(query, guildID)

    # Shuffle bracket
    random.shuffle(roster)

    # Generate round one brackets
    matchNum = 1
    round = 1
    matches = []
    for i in range(0, len(roster), 2):
      query = "INSERT INTO Matches VALUES (?, ?, ?, ?, ?, ?)"
      if i + 1 == len(roster):
        db.execute(query, guildID, matchNum, round, roster[i][0], "Bye", "N/A")
      else:
        db.execute(query, guildID, matchNum, round, roster[i][0], roster[i + 1][0], "N/A")
      matches.append(matchNum)
      matchNum += 1

    # Shuffle again
    random.shuffle(matches)

    # Generate other rounds
    while len(matches) > 1:
      round += 1
      next_matches = []
      
      for i in range(0, len(matches), 2):
        query = "INSERT INTO Matches VALUES (?, ?, ?, ?, ?, ?)"
        if i + 1 == len(matches):
          db.execute(query, guildID, matchNum, round, "Winner of Match " + str(matches[i]), "Bye", "N/A")
        else:
          db.execute(query, guildID, matchNum, round, "Winner of Match " + str(matches[i]), "Winner of Match " + str(matches[i + 1]), "N/A")
        next_matches.append(matchNum)
        matchNum += 1

      matches = next_matches

  @commands.command(aliases = ['br'])
  async def bracket(self, ctx):
    # Fetch the roster from database
    guildID = ctx.channel.guild.id
    query = "SELECT match_num, player_one, player_two, round, winner FROM Matches WHERE guild_id = ?;"
    bracket = db.fetch(query, guildID)

    # Sort bracket list by round
    bracket.sort(key=lambda tup: tup[3])

    curRound = 1
    resultString = "MATCHES:\n\nROUND 1:\n"
    for match in bracket:
      if curRound != match[3]:
        curRound = match[3]
        resultString += "\nROUND " + str(curRound) + "\n"
      resultString += "Match " + str(match[0]) + ": " + match[1] + " vs " + match[2] + "\t Winner: " + match[4]
      resultString += "\n"

    await ctx.send(resultString)

  @commands.has_permissions(administrator=True)
  @commands.command(aliases = ['ub'])
  async def updateBracket(self, ctx, match, winner):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    # Fetch match winner from database
    try:
      match = int(match)
      winner = int(winner)
    except:
      await ctx.send("Error with the parameters!")
      return

    guildID = ctx.channel.guild.id

    query = ""
    if winner == 1:
      query = "SELECT player_one FROM Matches WHERE match_num = ? AND guild_id = ?"
    elif winner == 2:
      query = "SELECT player_two FROM Matches WHERE match_num = ? AND guild_id = ?"
    else:
      await ctx.send("Enter '1' or '2' for the match winner parameter!")
      return
    
    winnerName = db.fetch(query, match, guildID)

    # Update match number inputted
    query = "UPDATE Matches SET winner = ? WHERE match_num = ? AND guild_id = ?"
    db.execute(query, winnerName[0][0], match, guildID)

    # Update matches in future rounds
    query = "UPDATE Matches SET player_one = ? WHERE player_one LIKE ? AND guild_id = ?"
    db.execute(query, winnerName[0][0], "________________" + str(match) + "%", guildID)

    query = "UPDATE Matches SET player_two = ? WHERE player_two LIKE ? AND guild_id = ?"
    db.execute(query, winnerName[0][0], "________________" + str(match) + "%", guildID)
      
def setup(client):
  client.add_cog(Tourny(client))