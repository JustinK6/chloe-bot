import discord

from discord.ext import commands
from .db import db

CURRENT_SEASON = 6

class RTA(commands.Cog):
  def __init__(self, client):
    self.client = client

  # Fetch absolute name from database using nickname input
  def getName(self, name):
    # Check if the character being searched for is valid
    namequery = "SELECT name FROM Names WHERE alias = ?"

    n = db.fetch(namequery, name)
    return n

  # Get the overall win rate of unit
  def getOverallWinrate(self, name, season = CURRENT_SEASON):
    query = "SELECT * FROM RTAStats WHERE name = ? AND season = ?"

    data = db.fetch(query, name, season)
    if len(data) == 0:
      return 0

    return data[0][4] / (data[0][2] - data[0][3])

  # Get the overall preban rate of unit
  def getOverallPrebanRate(self, name, totalCount):
    # Overall count of matches with unit prebanned
    query = """SELECT COUNT(match_id)
               FROM RTA
               WHERE preban_p1 = ? OR preban_p2 = ?"""

    prebans = db.fetch(query, name, name)[0][0]

    return prebans / totalCount

  # Get the general postban rate of unit
  def getOverallPostbanRate(self, name, season = CURRENT_SEASON):
    query = "SELECT * FROM RTAStats WHERE name = ? AND season = ?"

    data = db.fetch(query, name, season)
    if len(data) == 0:
      return 0

    return data[0][3] / data[0][2]

  # Get the first pick rate of unit
  def getFirstPickRate(self, name, totalCount, season = CURRENT_SEASON):
    query = "SELECT * FROM RTAStats WHERE name = ? AND season = ?"

    data = db.fetch(query, name, season)
    if len(data) == 0:
      return 0

    return data[0][5] / totalCount

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

  # Calculates winrates against characters
  def calculateWinRates(self, name):
    # Get number of wins/losses vs other chars
    data = self.getWinLoss(name)

    wins = data[0]
    losses = data[1]

    # Calculate winrates for each character
    winrates = {}
    for unit in wins:
      numWins = wins[unit]
      numLosses = losses[unit]

      if numWins == 0 and numLosses == 0:
        continue

      winRate = numWins / (numWins + numLosses)
      if winRate > 0.0:
        winrates[unit] = numWins / (numWins + numLosses)

    return dict(sorted(winrates.items(), key=lambda item: item[1]))

  # Gets the units the character has the lowest winrates against (at most 3)
  def worstMatchups(self, name):
    winRates = self.calculateWinRates(name)
    result = {}

    for index, wr in enumerate(winRates):
      if index > 2:
        break

      result[wr] = winRates[wr]

    return result
  
  # Create embed to send based on data
  def getEmbed(self, name, overallWinrate, prebanRate, postbanRate, firstPickRate, worstMatchups):
    embed = discord.Embed(
      title = f"RTA Stats for {name}",
    )

    query = "SELECT image_link from CharacterImages WHERE name = ?"
    imageLink = db.fetch(query, name)[0][0]

    embed.set_thumbnail(url=imageLink)
    embed.add_field(name = "Winrate:", value = f"{overallWinrate}%", inline = False)
    embed.add_field(name = "Preban Rate:", value = f"{prebanRate}%", inline = True)
    embed.add_field(name = "Postban Rate:", value = f"{postbanRate}%", inline = True)
    embed.add_field(name = "First Pick Rate:", value = f"{firstPickRate}%", inline = True)

    # Worst matchup info
    matchupString = ""
    if len(worstMatchups) == 0:
      matchupString = "N/A"
      
    for matchup in worstMatchups:
      matchupString += f"{matchup} ({round(worstMatchups[matchup] * 100, 2)}%)\n"

    embed.add_field(name = "Struggles against (Win%):", value = matchupString, inline = False)

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

    # Get total number of matches
    query = "SELECT COUNT(match_id) FROM RTA"
    totalCount = db.fetch(query)[0][0]

    # Get overall winrate of character
    overallWinrate = round(self.getOverallWinrate(nameString) * 100, 2)

    # Get postban rate of character
    postbanRate = round(self.getOverallPostbanRate(nameString) * 100, 2)

    # Get preban rate of character
    prebanRate = round(self.getOverallPrebanRate(nameString, totalCount) * 100, 2)

    # Get the first pick rate of the character
    firstPickRate = round(self.getFirstPickRate(nameString, totalCount) * 100, 2)

    # Get worst matchups
    worstMatchups = self.worstMatchups(nameString)

    await ctx.send(embed = self.getEmbed(nameString, overallWinrate, prebanRate, postbanRate, firstPickRate, worstMatchups)) 

def setup(client):
  client.add_cog(RTA(client)) 