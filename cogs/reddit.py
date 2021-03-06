import discord
import random
import asyncpraw
import os

from discord.ext import commands
from dotenv import load_dotenv

class Reddit(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.reddit = asyncpraw.Reddit(
      client_id = os.getenv("REDDIT_CLIENT"),
      client_secret = os.getenv("REDDIT_SECRET"),
      user_agent = os.getenv("REDDIT_USER_AGENT"),
    )

  @commands.command()
  async def art(self, ctx):
    subreddit = await self.reddit.subreddit("EpicSeven")
    submissions = []

    async for submission in subreddit.search("flair:Art", 'new'):
      if not "gallery" in submission.url:
        submissions.append(submission)

    chosen =  random.choice(submissions)
    await ctx.send(chosen.url)

  @commands.command()
  async def cat(self, ctx):
    subreddit = await self.reddit.subreddit("cats")
    submissions = []

    async for submission in subreddit.search("flair:Cat Picture", 'new'):
      if not "gallery" in submission.url:
        submissions.append(submission)

    chosen =  random.choice(submissions)
    await ctx.send(chosen.url)

async def setup(client):
  await client.add_cog(Reddit(client), guilds = [discord.Object(id = 437118873150685194)])