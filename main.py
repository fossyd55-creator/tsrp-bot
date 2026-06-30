import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

async def load_cogs():
    """Load all cogs from the cogs folder"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded {filename}")

bot = Bot()

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f"\n{'='*60}")
    print(f"✅ Bot logged in as {bot.user}")
    print(f"🤖 Bot is ready!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    print(f"{'='*60}\n")

async def main():
    """Main function to start the bot"""
    await load_cogs()
    TOKEN = os.getenv("DISCORD_TOKEN")
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
