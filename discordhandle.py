# bot.py
import os
import bot_functions
import name_gen
import profile_handler
from dotenv import load_dotenv

# 1
from discord.ext import commands
from discord.ext.commands import ConversionError
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
bf = bot_functions.RollBot()
ng = name_gen.NameGen()
ph = profile_handler.PHandler()
given_stats = []


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='hello')
async def hello_world(ctx):
    await ctx.send("Hello there :)")


@bot.command(name='celebrate')
async def celebrate(ctx):
    """a command that lets you celebrate with some deserved crab rave"""
    await ctx.send(
        ctx.message.author.mention + ' Here have some well deserved crab' +
        ' rave to celebrate your latest succes!!\n' +
        'https://youtu.be/LDU_Txk06tM?t=70'
    )


@bot.command(name='r')
async def roll_dice(ctx, user_input, optional_input=""):
    """Function that gets a user input and passes it along to get processed"""

    # Sends the user input to be processed bot_functions
    bf.roll_input(user_input, optional_input)

    # Prints results for advantage rolls if no errors came up.
    if bf.dropped_roll != '' and bf.error == '':
        bf.calculate_roll()
        await ctx.send(
            ctx.message.author.mention +
            ' `Dropped roll: ' + bf.dropped_roll + ', Result:` ' +
            ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
            str(bf.modifier_number) + ' = ' + str(bf.result)
        )

    # Only outputs the results if no errors came up allong the way and no
    # advantage had to be aplied
    elif bf.error == '':
        bf.calculate_roll()
        await ctx.send(
                ctx.message.author.mention +
                bf.input_last_roll +
                ', '.join(bf.last_roll) + ' ' +
                str(bf.modifier) + ' ' +
                str(bf.modifier_number) + ' = ' + str(bf.result))

    # Send the error message if a specific one did come up
    else:
        await ctx.send(
            ctx.message.author.mention + ' ' + bf.error
        )


@bot.command(name='name')
async def get_name(ctx, race, subtype="", extra=""):
    """Handles getting a random name from a list"""

    ng.handle_input(race, subtype, extra)

    # Sends an error msg in discord if one came up while getting name
    if ng.error is not False:
        await ctx.send(
            ctx.message.author.mention + ' ' + ng.error
        )

    else:
        # Prints back the names
        await ctx.send(
                ctx.message.author.mention + "\n```" + '\n'.join(ng.names) +
                "```"
        )


@bot.command(name='Nhelp')
async def name_help(ctx):
    """Shows you all possible options for !name"""

    # Opens the help text files and puts it in a variable
    with open(os.path.join("textfiles", "name_help.txt")) as f:
        nhelp = f.read()

    # sends the opened text file through discord
    await ctx.send(
        ctx.message.author.mention + "\n" + nhelp
    )


@bot.command(name='showprofiles')
async def com_fetch_unclaimed_profiles(ctx):
    """Command that shows you all unclaimed profiles"""

    await ctx.channel.trigger_typing()

    ph.fetch_unclaimed_profiles()

    if len(ph.unclaimed_profiles) == 0:
        await ctx.send(
            "There are no unclaimed profiles :critfail:"
            )

    else:
        await ctx.send(
            "The current unclaimed profiles are:\n" + "```" + '\n'.join(ph.unclaimed_profiles_list) + "```"
            )


@bot.command(name='claimprofile')
async def com_claim_profile(ctx, profile_name):
    """Command that lets you claim a profile"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    ph.check_claim_input(profile_name, user)

    if ph.error != '':
        await ctx.send(
            ctx.message.author.mention + ' ' + ph.error
        )

    else:
        await ctx.send(
            ctx.message.author.mention + ' You have succesfully claimed ' + ph.claim_printback + " :yeetyeet:"
        )


@bot.command(name='myprofiles')
async def com_show_cprofile(ctx):
    """Command that shows your claimed profiles"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    ph.show_claimed_profiles(user)

    if ph.error != '':
        await ctx.channel.send(
            ctx.message.author.mention + ' ' + ph.error
        )

    else:
        await ctx.channel.send(
            ctx.message.author.mention + " Your claimed profiles are:\n" +
            "```" + '\n'.join(ph.claimed_profiles_list) + "```"
        )


@bot.command(name='unclaimprofile')
async def com_unclaim_profile(ctx, profile_name):
    """Command that lets you unclaim a profile"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    ph.unclaim_profile(profile_name, user)

    if ph.error != '':
        await ctx.send(
            ctx.message.author.mention + ' ' + ph.error
            )

    else:
        await ctx.send(
            ctx.message.author.mention + ' You have succesfully unclaimed ' + ph.print_back
            )


@bot.command(name='addprofile')
async def addprofile(ctx):
    """a command that gives you a link to add a new profile"""
    await ctx.send(
        ctx.message.author.mention + ' Please fill out this google form to ' +
        'add a profile to the profile pool.' +
        '\nhttps://docs.google.com/forms/d/e/1FAIpQLScJpN7TuiklZjTzVhTLJyYXPF_9K2jhIqdwEBbHAiUV5Z1qLg/viewform?usp=sf_link'
    )


@bot.command(name='selectprofile')
async def selectprofile(ctx, request_p):
    """a command that lets you select your active profile"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    ph.select_active_profile(user, request_p)

    if ph.error == '':
        print('complete succes')

    else:
        print(ph.error)



@bot.command(name='save')
async def save(ctx, save_input, optional_input=''):
    """a command that lets you roll a save with the correct modifiers"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    # Gets the user Id and hands it off to another class
    bf.check_request_input(user, save_input, 'save', optional_input)

    # Prints results for advantage rolls if no errors came up.
    if bf.dropped_roll != '' and bf.error == '':
        bf.calculate_roll()
        await ctx.send(
            ctx.message.author.mention +
            ' `Dropped roll: ' + bf.dropped_roll + ', Result:` ' +
            ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
            str(bf.modifier_number) + ' = ' + str(bf.result)
        )

    # prints rolls that didnt get advantage and no errors
    elif bf.error == '':
        bf.calculate_roll()
        await ctx.send(
                ctx.message.author.mention +
                bf.input_last_roll +
                ', '.join(bf.last_roll) + ' ' +
                str(bf.modifier) + ' ' +
                str(bf.modifier_number) + ' = ' + str(bf.result))

    else:
        await ctx.send(
            ctx.message.author.mention + bf.error
        )


@bot.command(name='check')
async def check(ctx, check_input, optional_input=''):
    """a command that lets you roll a check with the correct modifiers"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    # Gets the user Id and hands it off to another class
    bf.check_request_input(user, check_input, 'check', optional_input)

    # Prints results for advantage rolls if no errors came up.
    if bf.dropped_roll != '' and bf.error == '':
        bf.calculate_roll()
        await ctx.send(
            ctx.message.author.mention +
            ' `Dropped roll: ' + bf.dropped_roll + ', Result:` ' +
            ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
            str(bf.modifier_number) + ' = ' + str(bf.result)
        )

    # prints rolls that didnt get advantage and no errors
    elif bf.error == '':
        bf.calculate_roll()
        await ctx.send(
                ctx.message.author.mention +
                bf.input_last_roll +
                ', '.join(bf.last_roll) + ' ' +
                str(bf.modifier) + ' ' +
                str(bf.modifier_number) + ' = ' + str(bf.result))

    else:
        await ctx.send(
            ctx.message.author.mention + bf.error
        )


@bot.command(name='skill')
async def skill(ctx, skill_input, optional_input=''):
    """a command that lets you roll a skillcheck with the correct modifiers"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    # Gets the user Id and hands it off to another class
    bf.check_skill_input(user, skill_input, 'skill', optional_input)

    # Prints results for advantage rolls if no errors came up.
    if bf.dropped_roll != '' and bf.error == '':
        bf.calculate_roll()
        await ctx.send(
            ctx.message.author.mention +
            ' `Dropped roll: ' + bf.dropped_roll + ', Result:` ' +
            ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
            str(bf.modifier_number) + ' = ' + str(bf.result)
        )

    # prints rolls that didnt get advantage and no errors
    elif bf.error == '':
        bf.calculate_roll()
        await ctx.send(
                ctx.message.author.mention +
                bf.input_last_roll +
                ', '.join(bf.last_roll) + ' ' +
                str(bf.modifier) + ' ' +
                str(bf.modifier_number) + ' = ' + str(bf.result))

    else:
        await ctx.send(
            ctx.message.author.mention + bf.error
        )


@bot.command(name='newstats')
async def stat_roller(ctx):
    """Command that gets you all the stats you need for a new char"""

    bf.roll_stats()
    formatted_stats = []

    # A loop that gets the six results for the 6 stats
    for stat in range(6):

        # Combines all the info of what rolls were dropped
        formatted_stat = '```Here is stat: ' + str(stat + 1) + '\n' + \
            ', '.join(bf.d_stats[stat]) + \
            ' = ' + str(bf.result_d_stats[stat]) + \
            '\nDropped: ' + \
            str(bf.dropped_d_stats[stat]) + \
            '```'
        # adds them all to a list for neater printback
        formatted_stats.append(formatted_stat)

        total_stat_point = 0
        for stat in bf.result_d_stats:
            total_stat_point += bf.result_d_stats[stat]

    await ctx.send(
        ctx.message.author.mention + "".join(formatted_stats) + '\nYou have a total of: ' + str(total_stat_point) + ' points.'
    )


@bot.command(name='help')
async def modified_help(ctx):
    """Shows you all possible options"""

    # Opens the help text files and puts it in a variable
    with open(os.path.join("textfiles", "bot_help.txt")) as f:
        help_text = f.read()

    # sends the opened text file through discord
    await ctx.send(
        ctx.message.author.mention + "\n" + help_text
    )


@bot.event
async def on_command_error(ctx, error):
    """Catches missing arguements and notifies the user"""

    if isinstance(error, (ConversionError, commands.MissingRequiredArgument)):
        await ctx.send(
            ctx.message.author.mention + ' You are missing some required info please try to add it'
            )

    else:
        print(error)

bot.run(token)
