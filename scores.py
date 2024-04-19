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

async def on_message(message):
    content = message.content.strip()
    if content == "+2" or content == "-2":
        author_id = str(message.author.id)
        not_author_id = get_not_author_id(author_id)

        if not_author_id:
            update_score(not_author_id, content)

def update_score(user_id, change):
    with open(SCORES_FILE, "r+") as file:
        scores = json.load(file)
        if change == "+2":
            scores[user_id] += 2
        elif change == "-2":
            scores[user_id] -= 2
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