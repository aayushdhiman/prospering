import json

SCORES_FILE = 'scores.json'

def get_not_author_id(author_id):
    with open(SCORES_FILE, "r") as file:
        scores = json.load(file)
        if author_id in scores:
            for user_id in scores:
                if user_id != author_id:
                    return user_id
    return None

async def on_message(message, bot):
    content = message.content.strip()
    if content == "+2" or content == "-2":
        author_id = str(message.author.id)
        not_author_id = get_not_author_id(author_id)

        if not_author_id:
            await update_score(not_author_id, content, message.channel, bot)

async def update_score(user_id, change, ctx, bot):
    with open(SCORES_FILE, "r+") as file:
        scores = json.load(file)
        if change == "+2":
            scores[user_id] += 2
            await ctx.send(f"{get_friendly_name(user_id, bot)} got 2 social credit.")
        elif change == "-2":
            scores[user_id] -= 2
            await ctx.send(f"{get_friendly_name(user_id, bot)} lost 2 social credit.")
        file.seek(0)
        json.dump(scores, file, indent=4)

def get_friendly_name(user_id, bot):
    user = bot.get_user(int(user_id))
    if user:
        return user.name
    return "Unknown User"

async def scores(ctx, bot):
    with open(SCORES_FILE, "r") as file:
        scores = json.load(file)
        score_list = "\n".join([f"{get_friendly_name(user_id, bot)}: {score}" for user_id, score in scores.items()])
        await ctx.send(f"Current Scores:\n{score_list}")