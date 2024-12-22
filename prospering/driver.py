#!/usr/bin/env python3

import os

import asyncpg
import discord
from discord.ext import commands
from dotenv import load_dotenv
from reminders import setup_reminder_commands

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")


async def create_pool():
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            return await asyncpg.create_pool(DATABASE_URL)
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                raise Exception(
                    f"Failed to connect to database after {max_retries} attempts: {str(e)}"
                )
            print(f"Database connection attempt {retry_count} failed, retrying...")
            await asyncio.sleep(5)


async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                task_name TEXT NOT NULL,
                reminder_time TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """
        )


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    return commands.Bot(command_prefix="!", intents=intents)


async def setup_bot(bot):
    bot.db_pool = await create_pool()
    await init_db(bot.db_pool)

    await setup_reminder_commands(bot)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")


def main():
    bot = create_bot()

    @bot.event
    async def setup_hook():
        await setup_bot(bot)

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
