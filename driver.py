import discord
from discord.ext import commands
import reminders

TOKEN = "YOUR TOKEN HERE"

intents = discord.Intents.all() 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} succesfully logged in!')

@bot.command()
async def remindme(ctx, task, time_value: int, time_unit: str):
    await reminders.remindme(ctx, task, time_value, time_unit)

@bot.command()
async def listreminders(ctx):
    await reminders.listreminders(ctx)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    # Call the function to remove past reminders whenever a message is received
    reminders.load_reminders()
    reminders.remove_past_reminders()

bot.run(TOKEN)
