from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os
import random
# --- Flask Server ---
app = Flask('')
channelW = {}
reply = {}
badW = {}

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
intents.members = True

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
@bot.command(name="alert", help="alert a player")
@commands.has_permissions(manage_messages=True)
async def alert(ctx, member: discord.Member):
    
    await ctx.send(f"{member.mention}, You've been warned")
    await member.send(f"You've been warned from {ctx.guild.name}")


# --- Slash Commands (Tree) ---
@bot.tree.command(name="setwelcome", description="set a channel for welcome")
@commands.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    channelW[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"Your welcome channel set for {channel.mention}!")
@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in channelW:
        channel_id = channelW[guild_id]
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"{member.mention} has joined the {member.guild.name} server")
    
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
dice1 = "https://i.postimg.cc/KY6v1Cv3/image1.png"
dice2 = "https://i.postimg.cc/RFwCKGNq/image2.png"
dice3 = "https://i.postimg.cc/nLycXNcq/image3.png"
dice4 = "https://i.postimg.cc/bJ1YkLsG/image4.png"
dice5 = "https://i.postimg.cc/fLYWm5Jt/image5.png"
dice6 = "https://i.postimg.cc/mD7ZCVt1/image6.png"
@bot.tree.command(name="roll", description="roll a number from 1 to 6")
async def roll(interaction: discord.Interaction):
    randomN = random.randint(1,6)
    embed = discord.Embed(title="dice", colour=discord.Color.blue())
    if randomN == 1:
        embed.add_field(name="dice1", value="you've rolled 1 in the dice!")
        embed.set_thumbnail(url=dice1)
        
        interaction.response.send_message(embed=embed)
    elif randomN == 2:
        embed.add_field(name="dice2", value="you've rolled 2 in the dice!")
        embed.set_thumbnail(url=dice2)
        
        interaction.response.send_message(embed=embed)
    elif randomN == 3:
        embed.add_field(name="dice3", value="you've rolled 3 in the dice!")
        embed.set_thumbnail(url=dice3)
        
        interaction.response.send_message(embed=embed)
    elif randomN == 4:
        embed.add_field(name="dice4", value="you've rolled 4 in the dice!")
        embed.set_thumbnail(url=dice4)
        
        interaction.response.send_message(embed=embed)
    elif randomN == 5:
        embed.add_field(name="dice5", value="you've rolled 5 in the dice!")
        embed.set_thumbnail(url=dice5)
        
        interaction.response.send_message(embed=embed)
    elif randomN == 6:
        embed.add_field(name="dice6", value="Congrats! you've rolled 6 in the dice!")
        embed.set_thumbnail(url=dice6)

    embed.set_footer(text=f"requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="ask", description="bot will reply with yes, no or maybe")
@app_commands.describe(ask="pls ask something")
async def ask(interactions: discord.Interaction, ask:str):
    lis = ["yes", "no", "maybe", "ask me later", "I don't think so"]
    ran = random.choice(lis)
    await interactions.response.send_message(ran)
@bot.tree.command(name="setreply", description="set a message for reply")
@commands.has_permissions(administrator=True)
@app_commands.describe(rname="Word to catch", rreply="Bot's answer")
async def replys(interaction: discord.Interaction, rname:str, rreply:str):
    
    # WRONG: reply["trigger"] = rname
    # RIGHT: Use rname as the KEY
    reply[rname] = rreply 
    
    await interaction.response.send_message(f"Added: {rname} -> {rreply}")



@bot.tree.command(name="setword", description="set bad words and I'll delete")
@app_commands.describe(badws= "select bad words")
@commands.has_permissions(manage_messages=True)
async def setwords(interaction: discord.Interaction, badws : str):
    badW[badws] = badws
    await interaction.response.send_message("Setted bad words!")
@bot.tree.command(name="report", description="report this bot about something")
@app_commands.describe(reportabt= "select report reason")
async def setwords(interaction: discord.Interaction, reportabt : str):
    await interaction.response.send_message("reported successfully!", ephemeral=True)
    member = interaction.user.id
    print(f"Someone Reported!\n{member}:{reportabt}")
@bot.event
async def on_message( message):
    if message.author == bot.user: 
        return
    
    # Check if the message exists in our dictionary keys
    if message.content in reply:
        # Get the value using the key (message.content)
        await message.channel.send(reply[message.content])
    if message.content.lower() in badW:   
        await message.channel.send("No bad words allowed!")
        await message.delete()
    
    await bot.process_commands(message)
    
    
    
# --- Run Bot ---
keep_alive()
token = os.environ.get("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Error: TOKEN not found in Environment Variables!")
