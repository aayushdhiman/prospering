import datetime
import json
import pytz
import asyncio

reminders = {}
REMINDERS_FILE = 'reminders.json'
LOCAL_TIMEZONE = 'America/New_York'

async def remindme(ctx, task, time_value: int, time_unit: str):
    time_value = abs(time_value)
    current_time = datetime.datetime.now(datetime.timezone.utc)

    if time_unit.lower() in ['second', 'seconds']:
        reminder_time = current_time + datetime.timedelta(seconds=time_value)
    elif time_unit.lower() in ['minute', 'minutes']:
        reminder_time = current_time + datetime.timedelta(minutes=time_value)
    elif time_unit.lower() in ['hour', 'hours']:
        reminder_time = current_time + datetime.timedelta(hours=time_value)
    elif time_unit.lower() in ['day', 'days']:
        reminder_time = current_time + datetime.timedelta(days=time_value)
    else:
        await ctx.send("Invalid time unit. Please use 'seconds', 'minutes', 'hours', or 'days'.")
        return

    user = ctx.author
    reminder_data = {'user_id': user.id, 'task': task}
    reminders[str(reminder_time)] = reminder_data

    # Save reminders to the JSON file
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f)

    reminder_time = reminder_time.astimezone(pytz.timezone(LOCAL_TIMEZONE))
    await ctx.send(f"I'll remind you to {task} at {str(reminder_time)}.")

    remove_past_reminders()  # Call the function to remove past reminders
    await asyncio.sleep((reminder_time - current_time).total_seconds())
    await ctx.send(f"{user.mention}, don't forget to: {task}")

async def listreminders(ctx):
    current_time = datetime.datetime.now(datetime.timezone.utc)
    local_timezone = pytz.timezone(LOCAL_TIMEZONE)
    active_reminders = []

    for reminder_time_str, reminder_data in reminders.items():
        reminder_time = datetime.datetime.fromisoformat(reminder_time_str).replace(tzinfo=datetime.timezone.utc)
        if reminder_time > current_time:
            reminder_time = reminder_time.astimezone(local_timezone)
            active_reminders.append((reminder_time, reminder_data))

    if active_reminders:
        reminder_list = '\n'.join([f"{str(reminder_time)}: {reminder_data['task']}" for reminder_time, reminder_data in active_reminders])
        await ctx.send("Active reminders:\n" + reminder_list)
    else:
        await ctx.send("No active reminders.")

def remove_past_reminders():
    current_time = datetime.datetime.now(datetime.timezone.utc)
    reminders_to_remove = []

    for reminder_time_str in list(reminders.keys()):
        reminder_time = datetime.datetime.fromisoformat(reminder_time_str).replace(tzinfo=datetime.timezone.utc)
        if reminder_time < current_time:
            reminders_to_remove.append(reminder_time_str)

    for reminder_time_str in reminders_to_remove:
        del reminders[reminder_time_str]

    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f)

def load_reminders():
    # Load existing reminders from the JSON file
    try:
        with open(REMINDERS_FILE, 'r') as f:
            data = f.read()
            reminders = json.loads(data)
    except (FileNotFoundError, json.JSONDecodeError):
        reminders = {}