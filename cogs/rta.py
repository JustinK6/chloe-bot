import discord

from discord.ext import commands
from .db import db

class Builds(commands.Cog):
  def __init__(self, client):
    self.client = client

  # Fetch absolute name from database using nickname input
  def getName(self, name):
    # Check if the character being searched for is valid
    namequery = "SELECT name FROM Names WHERE alias = ?"

    n = db.fetch(namequery, name)
    return n

  # Get the overall win rate of unit
  def getOverallWinrate(self, name, count):
    # Overall count of matches won with unit
    query = """SELECT COUNT(match_id)
               FROM RTA
               WHERE NOT (p1_ban = ? OR p2_ban = ?) AND
                     (((p1_pick1 = ? OR p1_pick2 = ? OR p1_pick3 = ? OR p1_pick4 = ? OR p1_pick5 = ?) AND match_winner = 1) OR 
                     ((p2_pick1 = ? OR p2_pick2 = ? OR p2_pick3 = ? OR p2_pick4 = ? OR p2_pick5 = ?) AND match_winner = 2))"""

    won = db.fetch(query, name, name, name, name, name, name, name, name, name, name, name, name)[0][0]
    return won / count

  # Get the overall preban rate of unit
  def getOverallPrebanRate(self, name, count):
    # Overall count of matches with unit prebanned
    query = """SELECT COUNT(match_id)
               FROM RTA
               WHERE preban_p1 = ? OR preban_p2 = ?"""

    prebans = db.fetch(query, name, name)[0][0]

    query = "SELECT COUNT(match_id) FROM RTA"

    totalCount = db.fetch(query)[0][0]

    return prebans / totalCount

  # Get the general postban rate of unit
  def getOverallPostbanRate(self, name):
    # Overall count of matches with character chosen
    query = """SELECT COUNT(match_id)
               FROM RTA
               WHERE (p1_pick1 = ? OR p1_pick2 = ? OR p1_pick3 = ? OR p1_pick4 = ? OR p1_pick5 = ?) OR 
                     (p2_pick1 = ? OR p2_pick2 = ? OR p2_pick3 = ? OR p2_pick4 = ? OR p2_pick5 = ?)"""

    count = db.fetch(query, name, name, name, name, name, name, name, name, name, name)[0][0]

    # Overall count of matches with unit postbanned
    query = """SELECT COUNT(match_id)
               FROM RTA
               WHERE p1_ban = ? OR p2_ban = ?"""

    postbans = db.fetch(query, name, name)[0][0]

    return postbans / count

  # Gets wins and losses
  def getWinLoss(self, name):
    # Get match data for matches character has played in
    query = """SELECT p1_pick1, p1_pick2, p1_pick3, p1_pick4, p1_pick5, p2_pick1, p2_pick2, p2_pick3, p2_pick4, p2_pick5, p1_ban, p2_ban, match_winner
               FROM RTA
               WHERE NOT (p1_ban = ? OR p2_ban = ?) AND
                     ((p1_pick1 = ? OR p1_pick2 = ? OR p1_pick3 = ? OR p1_pick4 = ? OR p1_pick5 = ?) OR 
                     (p2_pick1 = ? OR p2_pick2 = ? OR p2_pick3 = ? OR p2_pick4 = ? OR p2_pick5 = ?))"""

    data = db.fetch(query, name, name, name, name, name, name, name, name, name, name, name, name)

    # Dictionaries keeping track of count of won and lost matches
    wins = {}
    losses = {}

    for match in data:
      playerOne = []
      playerTwo = []
      characterTeam = -1

      for index, unit in enumerate(match):
        # Ignore banned units
        if index > 9 or unit == match[10] or unit == match[11]:
          continue
        elif not unit == name:
          if not unit in wins:
            wins[unit] = 0
          
          if not unit in losses:
            losses[unit] = 0

        # If unit is player, note index
        if unit == name:
          if index <= 4:
            characterTeam = 1
          else:
            characterTeam = 2
        else:
          if index <= 4:
            playerOne.append(unit)
          else:
            playerTwo.append(unit)

      # Update wins and losses
      if characterTeam == 1:
        if match[12] == 1:
          # Player wins
          for unit in playerTwo:
            wins[unit] += 1
        else:
          # Player loses
          for unit in playerTwo:
            losses[unit] += 1
      else:
        if match[12] == 2:
          # Player wins
          for unit in playerOne:
            wins[unit] += 1
        else:
          # Player loses
          for unit in playerOne:
            losses[unit] += 1

    return (wins,losses)

  # Gets the units the character has the lowest winrates against
  def getLosesAgainst(self, name):
    return self.getWinLoss(name)
  
  # Create embed to send based on data
  def getEmbed(self, name, overallWinrate, prebanRate, postbanRate):
    embed = discord.Embed(
      title = f"RTA Stats for {name}",
    )

    query = "SELECT image_link from CharacterImages WHERE name = ?"
    imageLink = db.fetch(query, name)[0][0]

    embed.set_thumbnail(url=imageLink)

    embed.add_field(name = "Overall Win Rate:", value = f"{overallWinrate}%", inline = False)
    embed.add_field(name = "Overall Preban Rate:", value = f"{prebanRate}%", inline = False)
    embed.add_field(name = "Overall Postban Rate:", value = f"{postbanRate}%", inline = False)

    return embed

  # Get the rta stats of a specific character (input)
  @commands.command(aliases = ['rs'])
  async def rtastats(self, ctx, *, input):
    # Get actual name of character
    name = self.getName(input)
    if len(name) == 0:
      await ctx.send("No such character found.")
      return

    nameString = name[0][0]

    # Overall count of matches done with character
    query = """SELECT COUNT(match_id)
               FROM RTA
               WHERE NOT (p1_ban = ? OR p2_ban = ?) AND
                     ((p1_pick1 = ? OR p1_pick2 = ? OR p1_pick3 = ? OR p1_pick4 = ? OR p1_pick5 = ?) OR 
                     (p2_pick1 = ? OR p2_pick2 = ? OR p2_pick3 = ? OR p2_pick4 = ? OR p2_pick5 = ?))"""

    count = db.fetch(query, nameString, nameString, nameString, nameString, nameString, nameString, nameString, nameString, nameString, nameString, nameString, nameString)[0][0]

    overallWinrate = 0.0
    postbanRate = 0.0

    if count != 0:
      # Get overall winrate of character
      overallWinrate = round(self.getOverallWinrate(nameString, count) * 100, 2)

      # Get postban rate of character
      postbanRate = round(self.getOverallPostbanRate(nameString) * 100, 2)

    # Get preban rate of character
    prebanRate = round(self.getOverallPrebanRate(nameString, count) * 100, 2)

    # Get loss rate of character
    lossRate = self.getLosesAgainst(nameString)
    print(f"Wins: {lossRate[0]}\nLosses: {lossRate[1]}")

    await ctx.send(embed = self.getEmbed(nameString, overallWinrate, prebanRate, postbanRate)) 

def setup(client):
  client.add_cog(Builds(client)) 