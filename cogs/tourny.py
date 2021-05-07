import discord

from discord.ext import commands

class Tourny(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.roster = []
    self.tournyStarted = False
    self.tourny = Tournament(self.roster)

  # Resets the tournament
  @commands.command(aliases = ['rt'])
  async def resettourny(self, ctx):
    self.roster = []
    self.tournyStarted = False
    await ctx.send("Tournament has been reset!")

  # Adds a specified player to the tourny
  @commands.command(aliases = ['atp'])
  async def addtournyplayer(self, ctx, player):
    # Make sure the tournament hasn't already started
    if self.tournyStarted == False:
      # Add player to roster
      self.roster.append(player)
      await ctx.send(f'Player {player} has been added to the bracket.')
    else:
      await ctx.send('Tournament has already started, you can no longer add players!')

  # Displays the roster of those added to the tourny
  @commands.command(aliases = ['roster'])
  async def _roster(self, ctx):
    resultString = "Current tournament roster:"

    # Iterate over each player in the roster and add to string
    for player in self.roster:
      resultString += '\n'
      resultString += player

    await ctx.send(resultString)

  # Starts the tourny
  @commands.command(aliases = ['st'])
  async def starttourny(self, ctx):
    await ctx.send('Are you sure you want to start the tourny? You will no longer be able to add or remove members! (Y or N)')

    def check(m):
      return m.author == ctx.author
    
    msg  = await self.client.wait_for('message', check = check)

    if msg.content == 'Y' or msg.content == 'y':
      self.tournyStarted = True
      await ctx.send('Tournament has been started!')
    elif msg.content == 'N' or msg.content == 'n':
      await ctx.send('Cancelled starting tournament.')
    else:
      await ctx.send('Invalid answer!')
    

def setup(client):
  client.add_cog(Tourny(client))

# classes for tournaments
class Tournament:
  def __init__(self, players):
    self.players = players
    self.playerCount = len(players)
    self.games = []