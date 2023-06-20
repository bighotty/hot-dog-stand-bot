#created by bighotty ;)

import discord
from discord.ext import commands
import asyncio
import os
import json
from dotenv import load_dotenv
import threading

load_dotenv()

money_generated = 1
price1 = 50
price2 = 200
price3 = 500
price4 = 1500
price5 = 4000
price6 = 6000
price7 = 10000
price8 = 15000

def save_game_data(game_data):
    with open("game_data.json", "w") as file:
        json.dump(game_data, file, indent=4)

def load_game_data():
    game_data = {}
    save_file = "game_data.json"

    if os.path.isfile(save_file):
        try:
            with open(save_file, "r") as file:
                data = file.read()
                if data:
                    game_data = json.loads(data)
        except Exception as e:
            print("An error occurred while loading game data:", e)

    return game_data

client = commands.Bot(command_prefix="-", intents=discord.Intents.all())
client.remove_command("help")
income_task = None
game_data = load_game_data()

@client.event
async def on_connect():
    print("Hot Dog Stand is Online")
    global income_task
    income_task = asyncio.create_task(income_loop())

@client.command()
async def milestones(ctx):
    milestones = [
        (10000, "10k Club", discord.Color.green()),
        (50000, "50k Club", discord.Color.yellow()),
        (100000, "100k Club", discord.Color.dark_red()),
        (200000, "200k Club", discord.Color.dark_purple()),
        (500000, "500k Club", discord.Color.dark_blue()),
        (1000000, "MILLIONAIRE", discord.Color.gold())
    ]

    congrats_messages = []

    embed = discord.Embed(title="Milestones", color=discord.Color.from_str("0x000000"))
    guild = ctx.guild

    for amount, role_name, role_color in milestones:
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            role = await guild.create_role(name=role_name, color=role_color)
        embed.add_field(name=role_name, value=f"Required Amount: ${amount}", inline=False)

        if amount <= game_data.get(str(ctx.author.id), {}).get("money", 0):
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)
                congrats_messages.append(f"Congratulations on reaching the {role_name} milestone!")

    await ctx.send(embed=embed)

    for message in congrats_messages:
        await ctx.send(message)

@client.command()
async def sell(ctx):
    user_id = str(ctx.author.id)
    data = game_data.get(user_id, {})
    money = data.get("money", 0)
    stored_money = data.get("stored_money", 0)
    stand_name = data.get("stand_name", "")
    profile_image = data.get("profile_image", "")
    owned_items = data.get("owned_items", [])

    money += int(stored_money)
    await ctx.send(f"You have sold ${stored_money} in hotdogs at your stand: {stand_name}!")
    stored_money = 0
    data["money"] = money
    data["stored_money"] = stored_money
    game_data[user_id] = data
    save_game_data(game_data)

@client.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    data = game_data.get(user_id, {})
    money = data.get("money", 0)
    stored_money = data.get("stored_money", 0)
    stand_name = data.get("stand_name", "")
    profile_image = data.get("profile_image", "")

    embed = discord.Embed(title="Balance", color=discord.Color.gold())
    embed.set_thumbnail(url=profile_image)
    embed.add_field(name="Stand Name", value=stand_name, inline=False)
    embed.add_field(name="Money", value=f"${money}", inline=False)
    embed.add_field(name="Stored Money", value=f"${stored_money}", inline=False)

    await ctx.send(embed=embed)

@client.command()
async def createstand(ctx):
    user_id = str(ctx.author.id)
    game_data_user = game_data.get(user_id)

    if game_data_user:
        await ctx.send("You have already created a hot dog stand.")
        return

    with open("game_data.json", "r") as file:
        data = json.load(file)
        if user_id in data:
            await ctx.send("You have already created a hot dog stand.")
            return

    await ctx.send("Please enter the name for your hot dog stand:")

    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        stand_name_message = await client.wait_for("message", check=check_author, timeout=30)
        stand_name = stand_name_message.content.strip()

        profile_image = str(ctx.author.avatar.url)

        game_data[user_id] = {
            "money": 0,
            "stored_money": 0,
            "stand_name": stand_name,
            "profile_image": profile_image,
            "owned_items": []
        }
        save_game_data(game_data)
        await ctx.send(f"Congratulations! Your hot dog stand \"{stand_name}\" has been created.")

    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")

@client.command()
async def shop(ctx):
    embed = discord.Embed(title="Hot Dog Stand Shop", description="Welcome to the Hot Dog Stand Shop! Upgrade your stand to increase your earnings.", color=discord.Color.orange())
    embed.add_field(name="1. Ketchup Bottle", value=f"Price: ${price1}\nDoubles your current income.", inline=False)
    embed.add_field(name="2. Mustard", value=f"Price: ${price2}\nDoubles your current income.", inline=False)
    embed.add_field(name="3. Chopped Onions", value=f"Price: ${price3}\nTriples your current income.", inline=False)
    embed.add_field(name="4. Install Soda Machine", value=f"Price: ${price4}\nTriples your current income.", inline=False)
    embed.add_field(name="5. Pretzel Buns", value=f"Price: ${price5}\nTriples your current income.", inline=False)
    embed.add_field(name="6. Chili Dogs", value=f"Price: ${price6}\nMultiplies income by x5!", inline=False)
    embed.add_field(name="7. Sides of Fries", value=f"Price: ${price7}\nTriples your current income.", inline=False)
    embed.add_field(name="8. Meal Discounts", value=f"Price: ${price8}\nTriples your current income.", inline=False)

    await ctx.send(embed=embed)

@client.command()
async def buy(ctx, item_number: int):
    user_id = str(ctx.author.id)
    game_data_user = game_data.get(user_id)

    if not game_data_user:
        await ctx.send("You don't have a hot dog stand. Use the `-createstand` command to create one.")
        return

    items = {
        1: ("Ketchup Bottle", price1, 2),
        2: ("Mustard", price2, 2),
        3: ("Chopped Onions", price3, 3),
        4: ("Install Soda Machine", price4, 3),
        5: ("Pretzel Buns", price5, 3),
        6: ("Chili Dogs", price6, 5),
        7: ("Sides of Fries", price7, 3),
        8: ("Meal Discounts", price8, 3)
    }

    if item_number not in items:
        await ctx.send("Invalid item number. Please choose a valid item number.")
        return

    item_name, item_price, item_multiplier = items[item_number]
    item_price = int(item_price)

    if item_price > int(game_data_user.get("money", 0)):
        await ctx.send("You don't have enough money to buy this item.")
        return

    owned_items = game_data_user.get("owned_items", [])
    if item_name in owned_items:
        await ctx.send("You already own this item.")
        return

    game_data_user["money"] = int(game_data_user.get("money", 0)) - item_price
    owned_items.append(item_name)
    game_data_user["owned_items"] = owned_items
    save_game_data(game_data)

    await ctx.send(f"You have successfully purchased {item_name} for ${item_price}. "
                   f"This item will multiply your earnings by {item_multiplier}.")

@client.command()
async def viewstands(ctx):
    embed = discord.Embed(title="Hot Dog Stand Stats", color=discord.Color.dark_blue())

    if not game_data:
        embed.description = "No hot dog stands found."
    else:
        embed.description = "Here are the stats for all hot dog stands:"
        for user_id, data in game_data.items():
            money = data.get("money", 0)
            stored_money = int(data.get("stored_money", 0))
            stand_name = data.get("stand_name", "")
            user = await client.fetch_user(user_id)
            embed.add_field(
                name=f"Stand: {stand_name}",
                value=f"Owner: {user.mention}\nBalance: ${money}\nStored Money: ${stored_money}",
                inline=False,
            )
            embed.set_thumbnail(url=f"https://cdn.discordapp.com/attachments/1058951545607159915/1120558435407253645/dog.png")

    await ctx.send(embed=embed)

@client.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="All Commands", color = discord.Color.red())

    embed.add_field(name="-createstand", value="Create a hot dog stand. You want to start here", inline=False)
    embed.add_field(name="-sell", value="Sell your hot dogs. Gotta get that money", inline=False)
    embed.add_field(name="-balance", value="View your current earnings.", inline=False)  
    embed.add_field(name="-viewstands", value="View all hot dog stands. Compete to be the best", inline=False)
    embed.add_field(name="-shop", value="View the shop. P.S. chili dogs are really good", inline=False)
    embed.add_field(name="-buy #", value="Buy the specified upgrade. You need to spend money to make money", inline=False)

    embed.set_footer(text=f"thanks for playing :)")

    await ctx.send(embed = embed)


async def income_loop():
    global game_data
    money_generated = 1
    while True:
        for user_id, data in game_data.items():
            money = data.get("money", 0)
            stored_money = data.get("stored_money", 0)
            stand_name = data.get("stand_name", "")
            profile_image = data.get("profile_image", "")
            owned_items = data.get("owned_items", [])

            try:
                stored_money = int(stored_money)
            except ValueError:
                stored_money = 0

            stored_money += money_generated
            game_data[user_id] = {
                "money": money,
                "stored_money": stored_money,
                "stand_name": stand_name,
                "profile_image": profile_image,
                "owned_items": owned_items
            }
        save_game_data(game_data)
        await asyncio.sleep(1)

threading.Thread(target=client.run, args=(os.getenv('BOT_ID'),), daemon=True).start()
asyncio.run(income_loop())
