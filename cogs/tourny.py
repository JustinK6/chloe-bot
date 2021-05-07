import discord

from discord.ext import commands

class Tourny(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.roster = []
    self.tournyStarted = False
    self.tournyMessageID = None
    self.tourny = Tournament(self.roster)

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

    # Set the tourny message ID to the message sent
    self.tournyMessageID = tournyMessage.id

  # If a reaction is added to the tourny message, add player to tourny roster
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    if payload.message_id == self.tournyMessageID:
      name = payload.member.display_name

      # Make sure player is not already in roster before adding
      if not name in self.roster:
        self.roster.append(name)
    else:
      pass

  # Displays the roster of those added to the tourny
  @commands.command(aliases = ['roster'])
  async def _roster(self, ctx):
    resultString = "```Current tournament roster:"

    # Iterate over each player in the roster and add to string
    for player in self.roster:
      resultString += '\n'
      resultString += player

    resultString += "```"
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