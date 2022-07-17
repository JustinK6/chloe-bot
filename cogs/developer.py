import discord
import random
import requests
import pytesseract

from PIL import Image
from discord.ext import commands
from .db import db

class Developer(commands.Cog):
  def __init__(self, client):
    self.client = client

  # Check for messages in the builds channel
  @commands.Cog.listener()
  async def on_message(self, message):
    if not message.channel.id == 854616929682849864:
      return

    #result = self.attemptAddBuild(message.attachments[0].url)
    channel = self.client.get_channel(857188035368321034)
    await channel.send(message.attachments[0].url)

  # Manual command to add builds to bot database
  @commands.command()
  async def addbuild(self, ctx, link, set, attack, defense, health, speed, cchance, cdamage, effectiveness, effectresist, *, character):
    author = ctx.message.author.id
    if not (author == 277851099850080258 or author == 171782191188017152 or author == 154848534519218176):
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
    if not (author == 277851099850080258 or author == 171782191188017152 or author == 154848534519218176):
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

  @commands.command()
  async def query(self, ctx, *, query):
    author = ctx.message.author.id
    if author != 277851099850080258:
      return
    
    db.execute(query)

  # Helper command to attempt to read data from build images
  def attemptAddBuild(self, input):
    url = input
    im = Image.open(requests.get(url, stream=True).raw)

    thresh = 65

    width,height = im.size
    im = im.crop((0, 0, width / 3, height))

    newsize = (width, height * 3)
    im = im.resize(newsize)

    fn = lambda x : 255 if x > thresh else 0
    im = im.convert('L').point(fn, mode='1')

    text = pytesseract.image_to_string(im)
    return text
    
async def setup(client):
  await client.add_cog(Developer(client), guilds = [discord.Object(id = 437118873150685194)]) 