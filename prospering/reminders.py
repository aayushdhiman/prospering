import re
from datetime import datetime

import pytz
from discord.ext import commands, tasks


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @commands.command(name="remindme")
    async def set_reminder(self, ctx, *, reminder_text: str):
        """
        Set a reminder with the format: !remindme <task name> <date> <time>
        Example: !remindme Pay bills 2024-12-25 14:30
        """
        try:
            # Parse input
            pattern = r"^(.+?)\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})$"
            match = re.match(pattern, reminder_text)

            if not match:
                await ctx.send(
                    "Invalid format! Please use: !remindme <task name> <YYYY-MM-DD> <HH:MM>"
                )
                return

            task_name, date_str, time_str = match.groups()

            reminder_time = datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )
            reminder_time = pytz.UTC.localize(reminder_time)

            # Store in db
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO reminders (user_id, channel_id, task_name, reminder_time)
                    VALUES ($1, $2, $3, $4)
                """,
                    ctx.author.id,
                    ctx.channel.id,
                    task_name,
                    reminder_time,
                )

            await ctx.send(
                f"✅ I'll remind you about '{task_name}' on {date_str} at {time_str}"
            )

        except ValueError:
            await ctx.send(
                "Invalid date or time format! Please use YYYY-MM-DD for date and HH:MM for time."
            )
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        """Check for due reminders every minute"""
        current_time = datetime.now(pytz.UTC)

        async with self.bot.db_pool.acquire() as conn:
            # Fetch reminders
            due_reminders = await conn.fetch(
                """
                SELECT * FROM reminders 
                WHERE reminder_time <= $1
            """,
                current_time,
            )

            for reminder in due_reminders:
                # Get channel + send message
                channel = self.bot.get_channel(reminder["channel_id"])
                if channel:
                    user = await self.bot.fetch_user(reminder["user_id"])
                    await channel.send(
                        f"🔔 Hey {user.mention}, reminder for: {reminder['task_name']}"
                    )

                # Delete the reminder
                await conn.execute(
                    """
                    DELETE FROM reminders WHERE id = $1
                """,
                    reminder["id"],
                )

    @commands.command(name="myreminders")
    async def list_reminders(self, ctx):
        """List all pending reminders for the user"""
        async with self.bot.db_pool.acquire() as conn:
            reminders = await conn.fetch(
                """
                SELECT * FROM reminders 
                WHERE user_id = $1 
                ORDER BY reminder_time
            """,
                ctx.author.id,
            )

            if not reminders:
                await ctx.send("You have no pending reminders!")
                return

            reminder_list = "Your pending reminders:\n"
            for i, rem in enumerate(reminders, 1):
                reminder_list += f"{i}. {rem['task_name']} - {rem['reminder_time'].strftime('%Y-%m-%d %H:%M UTC')}\n"

            await ctx.send(reminder_list)

    @commands.command(name="cancelreminder")
    async def cancel_reminder(self, ctx, reminder_id: int):
        """Cancel a specific reminder by its number from the list"""
        async with self.bot.db_pool.acquire() as conn:
            # Get user's reminders
            reminders = await conn.fetch(
                """
                SELECT * FROM reminders 
                WHERE user_id = $1 
                ORDER BY reminder_time
            """,
                ctx.author.id,
            )

            if not reminders or reminder_id < 1 or reminder_id > len(reminders):
                await ctx.send("Invalid reminder ID!")
                return

            reminder_to_delete = reminders[reminder_id - 1]

            # Delete the reminder
            await conn.execute(
                """
                DELETE FROM reminders WHERE id = $1 AND user_id = $2
            """,
                reminder_to_delete["id"],
                ctx.author.id,
            )

            await ctx.send(f"Cancelled reminder: {reminder_to_delete['task_name']}")

    @check_reminders.before_loop
    async def before_reminder_check(self):
        await self.bot.wait_until_ready()


async def setup_reminder_commands(bot):
    await bot.add_cog(ReminderCog(bot))
