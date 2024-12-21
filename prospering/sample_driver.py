#!/usr/bin/env python3
import discord
from discord.ext import commands
import reminders
import scores

TOKEN = "YOUR TOKEN HERE"

intents = discord.Intents.all() 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    reminders.load_reminders()  # Load reminders from the JSON file
    print(f'{bot.user} succesfully logged in!')

@bot.command()
async def remindme(ctx, task, time_value: int, time_unit: str):
    '''Set a reminder for a task after a specified amount of time.'''
    await reminders.remindme(ctx, task, time_value, time_unit)

@bot.command()
async def listreminders(ctx):
    '''List all active reminders.'''
    await reminders.listreminders(ctx)

@bot.command()
async def listscores(ctx):
    '''List all active scores.'''
    await scores.scores(ctx, bot)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    await scores.on_message(message, bot)
    
    # Call the function to remove past reminders whenever a message is received
    reminders.remove_past_reminders()

bot.run(TOKEN)