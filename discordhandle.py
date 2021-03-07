# bot.py
import os
import bot_functions
import name_gen
import profile_handler
from dotenv import load_dotenv
import random

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
ph.load_cache()
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

    # send the results for hidden rolls and stores if no errors came up.
    elif bf.hidden is True and bf.error == '':
        bf.calculate_roll()

        # creates a dict for the user and adds the results if no dict exists
        if not bool(bf.hidden_rolls):

            bf.hidden_rolls[ctx.author.name] = []
            bf.hidden_rolls[ctx.author.name].append(
                bf.input_last_roll +
                ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                str(bf.modifier_number) + ' = ' + str(bf.result))

        # adds up to 5 entries in a users hidden roll list
        elif bool(bf.hidden_rolls):

            # checks if theres already a list for the user
            if ctx.author.name not in bf.hidden_rolls.keys():
                bf.hidden_rolls[ctx.author.name] = []

            # checks how many hidden rolls are saved for the user
            number_of_rolls = len(bf.hidden_rolls[ctx.author.name])

            # Stores a roll if less than 5 are stored
            if number_of_rolls < 5:

                bf.hidden_rolls[ctx.author.name].append(
                    bf.input_last_roll +
                    ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                    str(bf.modifier_number) + ' = ' + str(bf.result))

            # Deletes the oldest entry and stores the newest one
            elif number_of_rolls >= 5:

                bf.hidden_rolls[ctx.author.name].pop(0)

                bf.hidden_rolls[ctx.author.name].append(
                    bf.input_last_roll +
                    ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                    str(bf.modifier_number) + ' = ' + str(bf.result))


        # Private messages the result to the user
        await ctx.author.send(
                bf.input_last_roll +
                ', '.join(bf.last_roll) + ' ' +
                str(bf.modifier) + ' ' +
                str(bf.modifier_number) + ' = ' + str(bf.result))

        # sends a message to the channel the command was called from
        await ctx.send(
                ctx.message.author.mention + " Remember that you can verify your rolls with !verify.")

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
            "The current unclaimed profiles are:\n" + "```" +
            '\n'.join(ph.unclaimed_profiles_list) + "```"
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
            ctx.message.author.mention + ' You have succesfully claimed ' +
            ph.claim_printback
        )


@bot.command(name='myprofiles')
async def com_show_cprofile(ctx):
    """Command that shows your claimed profiles"""

    await ctx.channel.trigger_typing()

    user = ctx.message.author.id
    claimed_profiles = ph.show_claimed_profiles(user)

    if ph.error != '':
        await ctx.channel.send(
            ctx.message.author.mention + ' ' + ph.error
        )

    else:
        await ctx.channel.send(
            ctx.message.author.mention + " Your claimed profiles are:\n" +
            "```" + '\n'.join(claimed_profiles) +
            "```"
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
            ctx.message.author.mention + ' You have succesfully unclaimed ' +
            ph.print_back
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
        await ctx.send(
            ctx.message.author.mention + ' you have succesfully selected: ' +
            ph.cached_users[user]['active_profile']
        )

    else:
        await ctx.send(
            ctx.message.author.mention + ph.error
        )


@bot.command(name='save')
async def save(ctx, save_input, optional_input=''):
    """a command that lets you roll a save with the correct modifiers"""

    await ctx.channel.trigger_typing()

    # Gets the user Id and hands it off to another class
    user = ctx.message.author.id

    mod = ph.request_mod(user, save_input, 'save')
    user_input = '1d20' + str(mod)

    # Makes sure it only rolls the dice if no errors came up with the profile
    if ph.error == '':
        # Rolls the dice with the correct modifiers
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

    # Sends the error for issues in with the profile
    else:
        await ctx.send(
            ctx.message.author.mention + ph.error
        )

@bot.command(name='check')
async def check(ctx, check_input, optional_input=''):
    """a command that lets you roll a check with the correct modifiers"""

    await ctx.channel.trigger_typing()

    # Gets the user Id and hands it off to another class
    user = ctx.message.author.id

    mod = ph.request_mod(user, check_input, 'check')
    user_input = '1d20' + str(mod)

    if ph.error == '':
        # Rolls the dice with the correct modifiers
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

        # send the results for hidden rolls and stores if no errors came up.
        elif bf.hidden is True and bf.error == '':
            bf.calculate_roll()

            # creates a dict for the user and adds the results if no dict exists
            if not bool(bf.hidden_rolls):

                bf.hidden_rolls[ctx.author.name] = []
                bf.hidden_rolls[ctx.author.name].append(
                    bf.input_last_roll +
                    ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                    str(bf.modifier_number) + ' = ' + str(bf.result))

            # adds up to 5 entries in a users hidden roll list
            elif bool(bf.hidden_rolls):

                # checks if theres already a list for the user
                if ctx.author.name not in bf.hidden_rolls.keys():
                    bf.hidden_rolls[ctx.author.name] = []

                # checks how many hidden rolls are saved for the user
                number_of_rolls = len(bf.hidden_rolls[ctx.author.name])

                # Stores a roll if less than 5 are stored
                if number_of_rolls < 5:

                    bf.hidden_rolls[ctx.author.name].append(
                        bf.input_last_roll +
                        ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                        str(bf.modifier_number) + ' = ' + str(bf.result))

                # Deletes the oldest entry and stores the newest one
                elif number_of_rolls >= 5:

                    bf.hidden_rolls[ctx.author.name].pop(0)

                    bf.hidden_rolls[ctx.author.name].append(
                        bf.input_last_roll +
                        ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                        str(bf.modifier_number) + ' = ' + str(bf.result))


            # Private messages the result to the user
            await ctx.author.send(
                    bf.input_last_roll +
                    ', '.join(bf.last_roll) + ' ' +
                    str(bf.modifier) + ' ' +
                    str(bf.modifier_number) + ' = ' + str(bf.result))

            # sends a message to the channel the command was called from
            await ctx.send(
                    ctx.message.author.mention + " Remember that you can verify your rolls with !verify.")

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

    # Sends the error for issues in with the profile
    else:
        await ctx.send(
            ctx.message.author.mention + ph.error
        )


@bot.command(name='skill')
async def skill(ctx, skill_input, optional_input=''):
    """a command that lets you roll a skillcheck with the correct modifiers"""

    await ctx.channel.trigger_typing()

    # Gets the user Id and hands it off to another class
    user = ctx.message.author.id

    mod = ph.request_mod(user, skill_input, 'skill')
    user_input = '1d20' + str(mod)

    if ph.error == '':
        # Rolls the dice with the correct modifiers
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

    # send the results for hidden rolls and stores if no errors came up.
        elif bf.hidden is True and bf.error == '':
            bf.calculate_roll()

            # creates a dict for the user and adds the results if no dict exists
            if not bool(bf.hidden_rolls):

                bf.hidden_rolls[ctx.author.name] = []
                bf.hidden_rolls[ctx.author.name].append(
                    bf.input_last_roll +
                    ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                    str(bf.modifier_number) + ' = ' + str(bf.result))

            # adds up to 5 entries in a users hidden roll list
            elif bool(bf.hidden_rolls):

                # checks if theres already a list for the user
                if ctx.author.name not in bf.hidden_rolls.keys():
                    bf.hidden_rolls[ctx.author.name] = []

                # checks how many hidden rolls are saved for the user
                number_of_rolls = len(bf.hidden_rolls[ctx.author.name])

                # Stores a roll if less than 5 are stored
                if number_of_rolls < 5:

                    bf.hidden_rolls[ctx.author.name].append(
                        bf.input_last_roll +
                        ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                        str(bf.modifier_number) + ' = ' + str(bf.result))

                # Deletes the oldest entry and stores the newest one
                elif number_of_rolls >= 5:

                    bf.hidden_rolls[ctx.author.name].pop(0)

                    bf.hidden_rolls[ctx.author.name].append(
                        bf.input_last_roll +
                        ', '.join(bf.last_roll) + ' ' + str(bf.modifier) + ' ' +
                        str(bf.modifier_number) + ' = ' + str(bf.result))


            # Private messages the result to the user
            await ctx.author.send(
                    bf.input_last_roll +
                    ', '.join(bf.last_roll) + ' ' +
                    str(bf.modifier) + ' ' +
                    str(bf.modifier_number) + ' = ' + str(bf.result))

            # sends a message to the channel the command was called from
            await ctx.send(
                    ctx.message.author.mention + " Remember that you can verify your rolls with !verify.")


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

    # Sends the error for issues in with the profile
    else:
        await ctx.send(
            ctx.message.author.mention + ph.error
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
        ctx.message.author.mention + "".join(formatted_stats) +
        '\nYou have a total of: ' + str(total_stat_point) + ' points.'
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


@bot.command(name='shutdown')
async def shutdown(ctx):
    """the command to shutdown"""

    user = ctx.message.author.id
    shutting_down = ph.shutdown(user)

    if shutting_down is True:
        await ctx.send(ph.print_back)
        exit()

    else:
        await ctx.send(ph.print_back)


@bot.command(name='repair')
async def request_repair(ctx):
    """Fixes the cache after an incorrect shutdown"""

    user = ctx.message.author.id
    ph.repair_cache(user)
    # Sends a msg back with the outcome
    await ctx.send(ph.print_back)

@bot.command(name='art')
async def art(ctx):
    """a command that posts a random piece of art from the art channel"""

    # Sets the location of the art channel
    channel = ctx.guild.get_channel(639622641250074624)

    # fills the dict if empty
    if not bool(bf.art_dict):

        async for old_message in channel.history(limit=1000):
            if old_message.attachments:
                bf.art_dict[old_message.content] = old_message.attachments[0].url

    # Grabs a random piece of art from the dict
    rand_key = random.choice(list(bf.art_dict))

    # sends the random piece of art
    await ctx.send(rand_key + '\n' + bf.art_dict[rand_key])

    del bf.art_dict[rand_key]
    print(len(bf.art_dict))

@bot.command(name='meme')
async def meme(ctx):
    """a command that posts a random meme from the meme channel"""

    # Sets the location of the meme channel
    channel = ctx.guild.get_channel(816849677013876756)

    # fills the dict if empty
    if not bool(bf.meme_dict):

        async for old_message in channel.history(limit=1000):

            if old_message.attachments:

                bf.meme_dict[len(bf.meme_dict)] = old_message.attachments[0].url

    # Grabs a random piece of art from the dict
    rand_key = random.choice(list(bf.meme_dict))

    # sends the random piece of art
    await ctx.send(bf.meme_dict[rand_key])

    del bf.meme_dict[rand_key]
    print(len(bf.meme_dict))


@bot.command(name='verify')
async def verify(ctx, req_user='', optional_input=''):
    """lets you verify the hidden rolls"""

    # sets the name of the person that called the command as user
    user = ctx.message.author.name

    # checks if it is the DM asking for a specific users rolls to verified
    if ctx.message.mentions:
        req_user = ctx.message.mentions[0].name

        # Discord users permitted to use the DM versions
        if user == 'left4twenty':
            # prints the verification publically
            if req_user in bf.hidden_rolls.keys() and optional_input == 'public':

                # prints hidden rolls of the requested user in reverse order so they go from newest to oldest
                await ctx.send('Here are the hidden rolls of ' + ctx.message.mentions[0].mention + ' from newest to oldest:\n' + "\n".join(reversed(bf.hidden_rolls[req_user])))

            elif req_user in bf.hidden_rolls.keys() and optional_input == '':

                # prints hidden rolls of the requested user in reverse order so they go from newest to oldest in a private message
                await ctx.author.send('Here are the hidden rolls of ' + ctx.message.mentions[0].mention + ' from newest to oldest:\n' + "\n".join(reversed(bf.hidden_rolls[req_user])))

            # prints a statement if requested user doesn't have hidden rolls
            elif req_user not in bf.hidden_rolls.keys():
                await ctx.send(ctx.message.mentions[0].mention + " doesn't have any hidden rolls")

            # throws an error
            else:
                await ctx.send(ctx.message.author.mention + " invalid inputs, this command only accepts (all/public)")

        # throws an error incase of an unauthorized person
        else:
            await ctx.send(ctx.message.author.mention + 'Error 420- DM not found')

    # shows DM all the hidden rolls from all users
    elif req_user == 'all':
        # Discord users permitted to use this command
        if user == 'left4twenty':
            # loops through the dict of data
            for key in bf.hidden_rolls.keys():
                await ctx.author.send('Here are the hidden rolls of ' + key + ' from newest to oldest:\n' + "\n".join(reversed(bf.hidden_rolls[key])))

        # throws an error incase of an unauthorized person
        else:
            await ctx.send(ctx.message.author.mention + ' Error 420- DM not found')

    else:

        # checks if user has hidden rolls
        if user in bf.hidden_rolls.keys():

            #prints hidden rolls in reverse order so they go from newest to oldest
            await ctx.send(ctx.message.author.mention + ' here are your hidden rolls from newest to oldest:\n' + "\n".join(reversed(bf.hidden_rolls[user])))

        # prints to the user that they don't have any hidden rolls
        elif user not in bf.hidden_rolls.keys():
            await ctx.send(ctx.message.author.mention + " you don't have any hidden rolls")



@bot.event
async def on_command_error(ctx, error):
    """Catches missing arguements and notifies the user"""

    #if isinstance(error, (ConversionError, commands.MissingRequiredArgument)):
    #    await ctx.send(
    #        ctx.message.author.mention +
    #        ' You are missing some required info please try to add it'
    #        )

    # if isinstance(error, (ConversionError, commands.ValueError)):
    #    await ctx.send(
    #        ctx.message.author.mention + ' Invalid input'
    #        )

    #else:
    #    print(error)

bot.run(token)