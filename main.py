from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os
import random

# --- Flask Server ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Boss!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Ensure this is enabled in Discord Developer Portal

bot = commands.Bot(command_prefix=["!", "?", ".", "$"], intents=intents, help_command=None)

# Storage (Note: These reset if the bot restarts)
channelW = {}
reply_map = {}
bad_words = set()

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user.name}")
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Sync Error: {e}")

# --- Events ---

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in channelW:
        channel = bot.get_channel(channelW[guild_id])
        if channel:
            await channel.send(f"Welcome {member.mention} to {member.guild.name}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    # Auto-Reply Check
    if message.content in reply_map:
        await message.channel.send(reply_map[message.content])

    # Bad Word Check (Checks if any registered bad word is in the message)
    if any(word in content for word in bad_words):
        try:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, no bad words allowed!", delete_after=5)
        except discord.Forbidden:
            pass

    await bot.process_commands(message)

# --- Slash Commands ---

@bot.tree.command(name="roll", description="Roll a 6-sided die")
async def roll(interaction: discord.Interaction):
    dice_images = {
        1: "https://i.postimg.cc/KY6v1Cv3/image1.png",
        2: "https://i.postimg.cc/RFwCKGNq/image2.png",
        3: "https://i.postimg.cc/nLycXNcq/image3.png",
        4: "https://i.postimg.cc/bJ1YkLsG/image4.png",
        5: "https://i.postimg.cc/fLYWm5Jt/image5.png",
        6: "https://i.postimg.cc/mD7ZCVt1/image6.png"
    }
    
    num = random.randint(1, 6)
    embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a **{num}**!", color=discord.Color.blue())
    embed.set_thumbnail(url=dice_images[num])
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setword", description="Add a word to the blacklist")
@app_commands.checks.has_permissions(manage_messages=True)
async def setword(interaction: discord.Interaction, word: str):
    bad_words.add(word.lower())
    await interaction.response.send_message(f"Added `{word}` to the blacklist.", ephemeral=True)

@bot.tree.command(name="setwelcome", description="Set the welcome channel")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    channelW[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"Welcome channel set to {channel.mention}")

# --- Run ---
keep_alive()
token = os.environ.get("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Error: TOKEN not found!")
