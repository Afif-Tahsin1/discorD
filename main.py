from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os

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
bot = commands.Bot(command_prefix=["!", "?", ".", "$"], intents=intents, help_command=None)

@bot.event
async def on_ready():
    try:
        synched = await bot.tree.sync()
        print(f"Logged in as {bot.user.name}")
        print(f"Successfully loaded {len(synched)} commands")
    except Exception as e:
        print(e)

# --- Normal Commands (Prefix) ---

@bot.command()
async def help(ctx):
    # app_info check সরানো হয়েছে কারণ পার্সোনাল বটে team থাকে না
    embed = discord.Embed()
    embed.color = discord.Colour.blue()
    embed.title = "Blox Fruits Help"
    embed.description = "Here are the available commands"
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Command Prefix", value="!, ?, . and $", inline=False)
    embed.add_field(name="Moderation", value="``kick`` - Kick a member\n``ban`` - Ban a member\n``unban`` - Unban a member", inline=False)
    embed.set_footer(text=f"Developed by asma4563")
    await ctx.send(embed=embed)

@bot.command(name="kick", help="kick a member")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} has been kicked, reason: {reason}")

@bot.command(name="ban", help="ban a member")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} has been banned, reason: {reason}")

@bot.command(name="unban", help="unban a member")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_input):
    found = False
    async for entry in ctx.guild.bans():
        user = entry.user
        if (user.name == user_input) or (str(user.id) == user_input):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.name} is unbanned from the server")
            found = True
            break
    if not found:
        await ctx.send(f"Can't find user {user_input}")

# --- Slash Commands (Tree) ---

@bot.tree.command(name="help", description="see all commands")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed()
    embed.color = discord.Colour.blue()
    embed.title = "Blox Fruits Help"
    embed.description = "Here are the available commands"
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Prefixes", value="!, ?, . and $", inline=False)
    embed.add_field(name="Commands", value="``kick``, ``ban``, ``unban``", inline=False)
    embed.set_footer(text="Developed by asma4563")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="kick a member")
@app_commands.describe(member="Select the member", reason="Type the reason")
@commands.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member} has been kicked, reason: {reason}")

@bot.tree.command(name="ban", description="ban a member")
@commands.has_permissions(ban_members=True)
@app_commands.describe(member="Select the member", reason="Type the reason")
async def ban_slash(interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member} has been banned, reason: {reason}")

@bot.tree.command(name="unban", description="unban a member")
@commands.has_permissions(ban_members=True)
@app_commands.describe(user_input="User ID or Name")
async def unban_slash(interaction: discord.Interaction, user_input: str):
    found = False
    # আগে লুপ চালিয়ে ইউজার খুঁজতে হবে
    async for entry in interaction.guild.bans():
        user = entry.user
        if (user.name == user_input) or (str(user.id) == user_input):
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"{user.name} is unbanned from the server")
            found = True
            break
    if not found:
        await interaction.response.send_message(f"Can't find user {user_input}")

@bot.tree.command(name="userinfo", description='show your info')
@app_commands.describe(member="Select a member")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"{member.name}'s info", color=discord.Colour.blue())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    embed.add_field(name="Name", value=f"``{member.name}``", inline=True)
    embed.add_field(name="ID", value=f"``{member.id}``", inline=True)
    
    # ফিক্স: ডবল কোটেশনের ভেতর সিঙ্গেল কোটেশন ব্যবহার করা হয়েছে '%Y-%m-%d'
    formatted_date = member.joined_at.strftime('%Y-%m-%d')
    embed.add_field(name="Joined At", value=f"``{formatted_date}``", inline=False)
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# --- Run Bot ---
keep_alive()
token = os.environ.get("TOKEN")

if token:
    print("Token found! Starting bot...")
    bot.run(token)
else:
    print("❌ Error: TOKEN not found in Environment Variables!")
