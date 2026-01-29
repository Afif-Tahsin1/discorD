from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Boss!"

def run_web():
    # এই লাইনটা খেয়াল করুন 👇
    port = int(os.environ.get("PORT", 8080))  
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "?", ".", "$"], intents= intents, help_command=None)
token = os.environ.get("TOKEN")
@bot.event
async def on_ready():
    try:
        synched = await bot.tree.sync()
        print(f"Logged in as {bot.user.name}")
        print(f"Successfully loaded {len(synched)} commands")
    except Exception as e:
        print(e)

@bot.command()
async def help(ctx):
    app_info = await bot.application_info()
    if app_info.team:
        embed = discord.Embed()
        embed.color = discord.Colour.blue()
        embed.title = "BLox fruits help"
        embed.description = "help To see help"
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.add_field(name= "commandsPrefix", value="!, ?, . and $ are available command prefix like !help etc...", inline=False)
        embed.add_field(name= "commands", value=f"``kick`` - kick a member\n``ban`` - ban a member\n``unban``-unban a member", inline=False)
        embed.set_footer(text=f"Developed by asma4563")
        await ctx.send(embed=embed)
@bot.command(name="kick", help="kick a member")
@commands.has_permissions(kick_members=True)
async def kick(ctx, Member: discord.Member, *,  reason: str = None, ):
        await Member.kick(reason=reason)
        await ctx.send(f"{Member} has been kicked, reason: {reason}")

@bot.command(name="ban", help="ban a member")
@commands.has_permissions(ban_members=True)
async def ban(ctx, Member: discord.Member, *,  reason: str = None, ):
        await Member.ban(reason=reason)
        await ctx.send(f"{Member} has been banned, reason: {reason}")
@bot.command(name="unban", help="unban a member")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_input ):
        if user.name == user_input or str(user.id) == user_input:
                await ctx.guild.unban(user)
                await ctx.send(f"{user.name} is unbanned from the server")
        else:
            await ctx.send(f"Can't find user {user.name}")
        async for entry in ctx.guild.bans():
              user = entry.user
        

@bot.tree.command(name="help", description="see all commands")
async def help_slash(interaction: discord.Interaction):
    app_info = await bot.application_info()
    if app_info.team:
        embed = discord.Embed()
        embed.color = discord.Colour.blue()
        embed.title = "BLox fruits help"
        embed.description = "help To see help"
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.add_field(name= "commandsPrefix", value="!, ?, . and $ are available command prefix like !help etc...", inline=False)
        embed.add_field(name= "commands", value=f"``kick`` - kick a member\n``ban`` - ban a member\n``unban``-unban a member", inline=False)
        embed.set_footer(text=f"Developed by asma4563")
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="kick", description="kick a member")
@app_commands.describe(member="Select the member", reason="Type the reason")
@commands.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, *,  reason: str = None, ):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member} has been kicked, reason: {reason}")
@bot.tree.command(name="ban", description="ban a member")

@commands.has_permissions(ban_members=True)
@app_commands.describe(member="Select the member", reason="Type the reason")
async def ban_slash(interaction: discord.Interaction, member: discord.Member, *,  reason: str = None, ):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member} has been banned, reason: {reason}")
@bot.tree.command(name="unban", description="unban a member")
@commands.has_permissions(ban_members=True)
@app_commands.describe(user_input="User ID or Name")
async def unban_slash(interaction: discord.Interaction, user_input : str):
        async for entry in interaction.guild.bans():
              user = entry.user
        if user.name == user_input or str(user.id) == user_input:
              await interaction.guild.unban(user)
              await interaction.response.send_message(f"{user.name} is unbanned from the server")
        else:
            await interaction.send(f"Can't find user {user.name}")
@bot.tree.command(name="userinfo", description='show your info')
@app_commands.describe(member="Enter name")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
      embed = discord.Embed(title=f"{member.name}'s info", color = discord.Colour.blue())
      embed.set_thumbnail(url=member.avatar.url)
      embed.add_field(name="member's name", value=f"``Name`` {member.name} ")
      embed.add_field(name="member's id", value=f"``Id`` {member.id}")
      embed.add_field(name="member joined at", value=f"``Joined at {member.joined_at.strftime("%Y-%m-%d")}``")
      embed.set_footer(text=f"Requested by {interaction.user.name}")
      await interaction.response.send_message(embed=embed)
if token:   
    bot.run(token)
else:
      print("Can't found token!")
