import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from utils.functions import fetch_random_panel as frp
from utils.functions import is_valid
import time
# welcome dMahra
#  global dict to keep track of user score in every server
#  key: (username, server id), value: user score in that server
scores = {}

with open('config.txt', 'r') as f:
    TOKEN = f.readline().strip()

bot = commands.Bot(command_prefix='', case_insensitive=True, help_command=None)


def update_scores(message, score_update):
    global scores  # update dictionary globally
    if (message.author, message.guild.id) not in scores and score_update > 0:
        scores[(message.author, message.guild.id)] = score_update
    else:
        if scores[(message.author, message.guild.id)] + score_update < 0:
            scores[(message.author, message.guild.id)] = 0
        else:
            scores[(message.author, message.guild.id)] += score_update
 

@bot.event
async def on_ready():
    print('Bot online')
    print('Name: {}'.format(bot.user.name))
    print('ID: {}'.format(bot.user.id))


# ignore CommandNotFound Errors !
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.event
async def on_message(message):
    if message.content == 'host?':
        await message.channel.send("Hi. I'm your host!")
    await bot.process_commands(message)


# now displays the score in descending order
@bot.command(name='t.top')
async def display_server_scores(ctx):
    print(str(ctx.message.author)+" requested scoreboard.")  # print check to console
    embed = discord.Embed(title=f'Top Scores on {ctx.message.guild.name}:', inline=False)
    sort_orders = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # sorts dict in descending order
    for i in sort_orders:
        username = str(i[0][0])
        embed.add_field(name=username[:-5], value="$" + str(i[1]), inline=False)
    await ctx.send(embed=embed)


@bot.command(name='t.q', aliases=['Random'])
async def await_rand_question(ctx):
    # makes sure bot doesn't respond to itself
    if ctx.author.bot:
        return
    panel = frp()
    await ctx.send(embed=panel.get_embed())  # display panel
    # question/answer logic + time
    t_end = time.time() + 60
    while time.time() < t_end:
        try:
            attempt = await bot.wait_for('message')
            print('\"{}\" was sent by {}'.format(attempt.content, attempt.author))  # print to console
            if attempt.content in ['t.q', 't.top']:
                break
            elif attempt.content in ctx.bot.commands:
                break
            elif is_valid(attempt.content, panel.get_answer()):
                await ctx.send('Correct {}! You get ${}'.format(str(attempt.author)[:-5], panel.get_value()))
                update_scores(attempt, panel.get_value())  # increase score here
                return
            elif attempt.content != panel.get_answer():
                await ctx.send('That is incorrect {}. You lost ${}'.format(str(attempt.author)[:-5], panel.get_value()))
                update_scores(attempt, -1*panel.get_value())  # decrease score here
                continue
        except Exception as e:
            print(e)
    await ctx.send('Times up! The correct answer was \'{}\''.format(panel.get_answer()))

bot.run(TOKEN.strip())
