import random
import profile_handler
import re


class RollBot():
    """A class that handles the bulk of functionality"""

    def __init__(self):
        """initializes the attributes of the class"""
        # this is where the procesed user input gets stored for easy readbacks
        self.input_last_roll = ''
        # an empty list to store the results of the roll in
        self.last_roll = []
        # The sum of all the roles inside the last_roll list
        self.result = 0
        self.error = ''
        self.number_of_dice = ''
        self.size_of_dice = ''
        self.modifier = ''
        self.modifier_number = ''
        self.sort = False
        self.adv = False
        # a flag to save the number of the dropped roll on an adv roll
        self.adv_dropped_roll = ''

    def roll_input(self, user_input, optional_input):
        """complicated as fuck function that handles input without breaking"""

        # Resets the status of everything before a new roll
        self.last_roll = []
        self.result = 0
        # An empty error flag to easily throw errors back through discord
        self.error = ''
        self.number_of_dice = ''
        self.size_of_dice = ''
        # The modifier is either a + or a -, stored for easy acces
        self.modifier = ''
        self.modifier_number = ''
        self.adv_dropped_roll = ''

        # this code is run in try to catch atribute errors due to a wrong input
        try:
            # All parts filtered by regex get stored in an object,
            # that then gets split
            split_input = dice_handler.match(user_input)
            # sets the number of dice in the class for use in other functions
            self.number_of_dice = split_input.group(1)
            # sets the size of the dice in the class for use in other functions
            self.size_of_dice = split_input.group(3)
            # sets the +/- in the class for use in other functions
            self.modifier = split_input.group(5)
            # sets the number of the mod in the class to use in other functions
            self.modifier_number = split_input.group(6)

            # An if statements that alows typing 1 for rolling 1 dice to be
            # optional.
            if self.number_of_dice == '':
                self.number_of_dice = 1
            # Makes sure atleast 1 dice is rolled
            if self.number_of_dice == '0':
                self.error = "You can't roll 0 dice"
            # Sets a cap of 200 dice being rolled
            if int(self.number_of_dice) > 200:
                self.error = \
                    'No! Thats to many dice I do not have that many!!!'
                return

            # Meant to catch errors where a none size dice managed to sneak
            # Through.
            if self.size_of_dice == '0' or self.size_of_dice is None:
                self.error = "Please define the dice size."
            # Sets a cap on how large of a dice you can roll.
            if int(self.size_of_dice) > 50000:
                self.error = "Dice too big!" + \
                    " That has gotta be fake nothing goes this high"
                return

            # Checks wether no modifier was entered or if it was incorrectly
            # entered by checking the lenght of the input vs what came through.
            if self.modifier is None and \
                    len(str(user_input)) > \
                    len(str(self.number_of_dice) +
                        str(self.size_of_dice) + 'D'):
                self.error = "Incorrect modifier. Please use + or -"
                return

            # Sets modifier to +0 if no +/- is entered.
            if self.modifier == '' or self.modifier is None:
                self.modifier = '+'
                self.modifier_number = '0'

            # Sets modifier to +0 if no number for it was entered
            if self.modifier_number == '' or self.modifier_number is None:
                self.modifier = '+'
                self.modifier_number = '0'

            # The full input of the user in 1 flag to print back to the user
            # at the end.
            self.input_last_roll =  \
                ' `Rolled ' + \
                str(self.number_of_dice) + \
                'd' + \
                str(self.size_of_dice) + \
                str(self.modifier) + \
                str(self.modifier_number) + \
                ':` '

            if optional_input.lower() == 'adv':
                self.adv = 'adv'
                self.handle_adv()

            # Checks if user asked for disadvantage on a roll and hands it off
            elif optional_input.lower() == 'dadv':
                self.adv = 'dadv'
                self.handle_adv()

            # Checks if user asked for a sorted roll
            elif optional_input.lower() == 'sort':
                # Rolls the dice like normal but sorts the flag after.
                self.sort = True
                self.roll_dice(self.number_of_dice, self.size_of_dice)

            elif optional_input.lower() != '':
                self.error = str(optional_input) + \
                    " is not a valid option. Please try (sort/adv/dadv)"

            else:
                # If everything passed the checks hand offs the proccesed input
                #  to the randomizing and calculating functions.
                self.roll_dice(self.number_of_dice, self.size_of_dice)

        # Catches and attribute error on a wrong input and notifies the user.
        except AttributeError:
            self.error = \
                "Invalid input please follow this format (1)d20(+/-(5))"
        except ValueError:
            self.error = \
                "Invalid input, please Make sure dice size is bigger than 0"

    def roll_dice(self, number_of_dice, size_of_dice):
        """Simple function that rolls dice"""
        # makes a list of random numbers based on the information
        # that was put in
        dice = []
        for roll in range(int(number_of_dice)):
            roll = random.randint(1, int(size_of_dice))
            dice.append(roll)

        # Checks wether the result needs to be sorted or not
        if self.sort is True:
            dice.sort()
            # Turns ints into strings after sorting
            converted_dice = []
            for i in range(len(dice)):
                roll_to_convert = dice[i]
                roll_to_convert = str(roll_to_convert)
                converted_dice.append(roll_to_convert)
            # Sets the last roll flag and returns to sort flag to false
            self.last_roll = converted_dice
            self.sort = False
        # Sets the last roll flag for easy cross function use.
        else:
            # Turns Ints into strings incase it had to be sorted
            converted_dice = []
            for i in range(len(dice)):
                roll_to_convert = dice[i]
                roll_to_convert = str(roll_to_convert)
                converted_dice.append(roll_to_convert)
            self.last_roll = converted_dice

    def calculate_roll(self):
        """Function to calculate the sum of the roll"""
        # Takes all the numbers from the last roll and adds them up.
        for i in self.last_roll:
            self.result = int(self.result) + int(i)
        self.result = self.result + int(self.modifier + self.modifier_number)

    def handle_adv(self):
        """Function that handles the optional advantage options"""

        # This part handles advantage so it takes the highest of the 2 numbers
        # and then drops the lowest number
        if self.adv == 'adv':
            # Checks wether the number that was input is not 1 or 2.
            if str(self.number_of_dice) != '2' and \
                    str(self.number_of_dice) != '1':
                self.error = 'Can only roll advantage with 2 dice, ya dummy!'

            # Checks if number of dice was left blank so automatically set to 1
            if str(self.number_of_dice) != '2' and \
                    str(self.number_of_dice) == '1':
                self.number_of_dice = 2

            # Checks if the number of dice is 2 before moving on
            if str(self.number_of_dice) == '2':
                self.sort = True
                self.roll_dice(self.number_of_dice, self.size_of_dice)
                # Stores the dropped roll before deleting it from last_roll
                self.adv_dropped_roll = self.last_roll[0]
                del self.last_roll[0]
                # Returns flag to default state
                self.adv = False

        # This part handles disadvantage so it takes the lowest of the 2
        # numbers and then drops the highest number
        if self.adv == 'dadv':
            # Checks wether the number that was input is not 1 or 2.
            if str(self.number_of_dice) != '2' and \
                    str(self.number_of_dice) != '1':
                self.error = \
                    'Can only roll disadvantage with 2 dice, ya dummy!'

            # Checks if number of dice was left blank so automatically set to 1
            if str(self.number_of_dice) != '2' and \
                    str(self.number_of_dice) == '1':
                self.number_of_dice = 2

            # Checks if the number of dice is 2 before moving on
            if str(self.number_of_dice) == '2':
                self.sort = True
                self.roll_dice(self.number_of_dice, self.size_of_dice)
                # Stores the dropped roll before deleting it from last_roll
                self.adv_dropped_roll = self.last_roll[1]
                del self.last_roll[1]
                # Returns flag to default state
                self.adv = False

    def check_request_input(self, user, request_input, request_type, optional_input):
        """Function that checks if you gave a valid input"""

        valid_inputs = ['str', 'dex', 'con', 'int', 'wis', 'cha']
        request_input = request_input.lower()

        # Checks wether its a valid input before handing it off
        if request_input in valid_inputs:

            self.roll_request(user, request_input, request_type, optional_input)

        else:
            self.error = \
                ' Please specifiy the type of check or save(str/dex/con/int/wis/cha)'

    def check_skill_input(self, user, request_input, request_type, optional_input):
        """Function that checks if you gave a valid input"""

        valid_inputs = ['Acrobatics', 'Acro', 'Animal Handling', 'Ani', 'Arcana', 'Arc', 'Athletics', 'Ath', 'Deception', 'Dec', 'History', 'His', 'Insight', 'Insi', 'Intimidation', 'Inti', 'Investigation', 'Inv', 'Medicine', 'Med', 'Nature', 'Nat', 'Perception', 'Perc', 'Performance', 'Perf', 'Persuasion', 'Pers', 'Religion', 'Reli', 'Sleight Of Hand', 'Soh', 'Stealth', 'Ste', 'Survival', 'Surv']

        # Dict that stores the abreviations
        abr_dict = {'Acro': 'Acrobatics', 'Ani': 'Animal Handling', 'Arc': 'Arcana', 'Ath': 'Athletics', 'Dec': 'Deception', 'His': 'History', 'Insi': 'Insight', 'Inti': 'Intimidation', 'Inv': 'Investigation', 'Med': 'Medicine', 'Nat': 'Nature', 'Perc': 'Perception', 'Perf': 'Performance', 'Pers': 'Persuasion', 'Reli': 'Religion', 'Soh': 'Sleight Of Hand', 'Ste': 'Stealth', 'Surv': 'Survival'}

        request_input = request_input.lower().title()
        # Checks if you are using an abreviation before updating it
        try:
            request_input = abr_dict[request_input]

        except KeyError:
            pass

        # Checks whether its a valid input before handing it off
        if request_input in valid_inputs:

            self.roll_request(user, request_input, request_type, optional_input)

        else:
            self.error = \
                ' PLACEHOLDER TEXT'

    def roll_request(self, user, save_type, request_type, optional_input):
        """Function that handles rolling the appropriate saves"""

        # Checks wether user has an active profile
        active_profile = ph.check_active_profile(user)

        if active_profile == '' or active_profile == 'none':
            self.error = \
                "You have no active profile, please claim or select one"

        # Moves the process allong if the user has an active profile
        else:
            modified_roll = '1d20' + str(ph.find_value(user, active_profile, save_type, request_type))
            self.roll_input(modified_roll, optional_input)


# The regex that looks through the input for key information.
dice_handler = re.compile(r'(\d*)([dD])(\d*)(([+-])(\d*))?')
ph = profile_handler.PHandler()
