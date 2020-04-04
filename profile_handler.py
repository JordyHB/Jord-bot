import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('profile_auth_secret.json', scope)
client = gspread.authorize(creds)

profile_sheet = client.open('dnd_profiles').sheet1
user_sheet = client.open('dnd_profiles').get_worksheet(1)


class PHandler():
    """The class that handles fetching profiles from the google doc"""

    def __init__(self):
        """initializes self"""

        # Creates an empty flag that allows printing errors to the user
        self.error = ''
        # Creates an empty dict to temp store profiles for
        self.unclaimed_profiles = {}
        # Creates an empty list to temp store formatted profiles to show user
        self.unclaimed_profiles_list = []

    def fetch_empty_col(self, user_location):
        """Find an empty colom to write the profiles in"""

        occupied_col = user_sheet.row_values(user_location)
        empty_col = len(occupied_col) + 1

        while user_sheet.cell(user_location, empty_col).value != '':
            empty_col = empty_col + 1
            print("I'm stuck, help me")

        return empty_col

    def fetch_unclaimed_profiles(self):
        """Shows all unclaimed profiles on the google sheet"""

        # Creates a list with all the unclaimed profiles
        raw_unclaimed_profiles = profile_sheet.col_values(2)
        # Clears all the flags before proceeding
        self.unclaimed_profiles.clear()
        self.unclaimed_profiles_list = []
        self.error = ''
        self.print_back = ''

        # Fills a dict and assigns all the profile names a numerical key
        for profile in range(1, len(raw_unclaimed_profiles)):

            # Checks the status for each profile
            current_profile = profile_sheet.cell(profile + 1, 15).value
            # Sets the new empty statusses to unclaimed
            if current_profile == '':
                profile_sheet.update_cell(profile + 1, 15, 'unclaimed')
                current_profile = 'unclaimed'

            # Checks for claimed profiles moving on if they are
            if current_profile == 'claimed':
                pass

            # Adds unclaimed profiles to the unclaimed profile dict
            elif current_profile == 'unclaimed':
                self.unclaimed_profiles_list.append(
                    (str(profile + 1) + ": " + str(raw_unclaimed_profiles[profile]))
                    )
                # Adds entry to the dict
                self.unclaimed_profiles[str(profile + 1)] = \
                    str(raw_unclaimed_profiles[profile])

            # Sets corrupted files to unclaimed
            else:
                profile_sheet.update_cell(profile, 15, 'unclaimed')

        # Gets the dict out of the global flag so quick inputs dont break it
        d_unclaimed_profiles = self.unclaimed_profiles
        return d_unclaimed_profiles

    def fetch_claimed_profiles(self, user):
        """Fetches all profiles linked to a specific user"""

        # empty flags to store data in
        self.error = ''
        self.claimed_profiles = {}
        self.claimed_profiles_list = []

        # Fetches the users location from the database
        user_location = self.check_user_sheet(user)

        # Gets all the values connected to the user in a list
        raw_claimed_profiles = user_sheet.row_values(user_location)
        # Removes the user ID from the list
        del raw_claimed_profiles[0:2]

        # Reads all the user profiles adding them to a dictionary
        for claimed_profiles in raw_claimed_profiles:

            # Find the location of the profile on the profile sheet
            prof_location = profile_sheet.find(claimed_profiles).row
            # Adds the profile name to the list with the right key
            self.claimed_profiles[str(prof_location)] = str(claimed_profiles)
            # Neatly adds it to the list for printing back to the user
            self.claimed_profiles_list.append(
                str(prof_location) + ': ' + str(claimed_profiles)
                    )

        # gets the dict out of the flag so quick inputs dont break it
        d_claimed_profiles = self.claimed_profiles
        return d_claimed_profiles

    def check_active_profile(self, user):
        """Checks which profile the user has active"""

        # Finds the user in the database
        user_location = self.check_user_sheet(user)

        activated_profile = user_sheet.cell(user_location, 2).value
        return activated_profile

    def check_user_sheet(self, user):
        """Checks user sheet for existing profiles"""

        # Fetches all the data from the first colom for user IDs
        raw_user_data = user_sheet.col_values(1)

        # Checks if the user is already on the sheet
        if str(user) in raw_user_data:
            cell = user_sheet.find(str(user))
            user_location = cell.row
            return user_location

        else:
            # Adds the user to sheet if not found before returning the loc
            empty_cell = len(raw_user_data) + 1
            user_sheet.update_cell(empty_cell, 1, str(user))
            user_sheet.update_cell(empty_cell, 2, 'none')
            user_location = empty_cell
            return user_location

    def check_claim_input(self, claim_input, user):
        """Checks wether the input matches anything in dict"""

        # Refreshes the Dict
        d_unclaimed_profiles = self.fetch_unclaimed_profiles()

        try:
            # Sets a filtered input for use further down the process
            filtered_input = d_unclaimed_profiles[str(claim_input)]

            self.claim_printback = filtered_input
            self.claim_profile(claim_input, user, filtered_input)

        except IndexError:
            self.error = 'No unclaimed profile found by that number.'

        except KeyError:
            self.error = 'No unclaimed profile found by that number.'

    def claim_profile(self, claim_input, user, filtered_input):
        """Allows you to claim a profile"""

        # Updates the profile page
        profile_sheet.update_cell(int(claim_input), 15, 'claimed')
        profile_sheet.update_cell(int(claim_input), 16, str(user))

        # Makes this the active profile if user doesnt already have one
        if self.check_active_profile(user) == '' or \
                self.check_active_profile(user) == 'none':

            # sets the profile as active on the profiles sheet
            profile_sheet.update_cell(int(claim_input), 17, 'active')

            # Fetches users location in the database
            user_location = self.check_user_sheet(user)

            # Adds the profile to the user and adds the active tag
            user_sheet.update_cell(user_location, 2, filtered_input)
            # Finds an empty col to add the profile
            empty_col = self.fetch_empty_col(user_location)
            user_sheet.update_cell(user_location, empty_col, filtered_input)

        else:
            # sets the profile as active on the profiles sheet
            profile_sheet.update_cell(int(claim_input), 17, 'inactive')

            # Fetches users location in the database
            user_location = self.check_user_sheet(user)

            # Finds an empty col to add the profile
            empty_col = self.fetch_empty_col(user_location)
            user_sheet.update_cell(user_location, empty_col, filtered_input)

    def show_claimed_profiles(self, user):
        """Shows the claimed profiles to the user"""

        # Fills the profile list to print back to the user
        self.fetch_claimed_profiles(user)

        # Checks if the list isnt empty
        if self.claimed_profiles_list == []:
            self.error = "You have no claimed profiles"

        else:
            pass

    def unclaim_profile(self, profile_number, user):
        """Function that lets you unclaim profiles"""

        # Generates the dict with profile locations

        self.fetch_claimed_profiles(user)

        try:
            # Sets the search name to look for in the profile sheet
            unwanted_profile = self.claimed_profiles[str(profile_number)]

            # Finds the location of the unwanted profile in the profile sheet
            unclaim_loc = profile_sheet.find(unwanted_profile)

            # Updates the cells to unclaim on the profile sheet
            profile_sheet.update_cell(unclaim_loc.row, 15, 'unclaimed')
            profile_sheet.update_cell(unclaim_loc.row, 16, '')
            profile_sheet.update_cell(unclaim_loc.row, 17, 'inactive')

            # gets the location of the user in the user sheet
            user_loc = self.check_user_sheet(user)

            # Checks if the profile being unclaimed was the active one
            if user_sheet.cell(user_loc, 2).value == unwanted_profile:
                user_sheet.update_cell(user_loc, 2, '')

            # Sets the search name to look for in the profile sheet
            unclaim_user_sheet = self.claimed_profiles[profile_number]
            # Finds the location of the unwanted profile in the user sheet
            prof_user_loc = user_sheet.find(unclaim_user_sheet)

            # Updates the cells to unclaim on the profile sheet
            user_sheet.update_cell(user_loc, prof_user_loc.col, '')

            self.print_back = unwanted_profile

        except KeyError:
            self.error = 'You have no claimed profile by that number'

    def find_value(self, user, active_profile, request, request_type):
        """Function that finds associated values on the google sheets"""

        # Finds the active profile name on the profile sheet
        profile_loc = profile_sheet.find(active_profile)
        # Declares the row where it can find all the needed stats
        profile_row = profile_loc.row

        # Lists that help sort skills towards the right modfifiers
        str_skill = ['Athletics']
        dex_skill = ['Acrobatics', 'Sleight Of Hand', 'Stealth']
        int_skill = ['Arcana', 'History', 'Investigation', 'Nature', 'Religion']
        wis_skill = ['Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival']
        cha_skill = ['Deception', 'Intimidation', 'Performance', 'Persuasion']

        if request == 'str' or request in str_skill:

            # Checks if you are asking for a save, skill or a check so that it
            # can apply the correct proficiency bonuses
            if request_type == 'save':

                # Gets the modifier off the sheet
                value = profile_sheet.cell(profile_row, 3).value
                # Checks if you are profficient and adds a bonus if you are
                value = int(value) + int(self.check_save_proficiency(user, active_profile, request))

                # Adds a + or a - to the modifier accordingly
                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Check if you are proficient in the requested skill
            elif request_type == 'skill':

                # Gets the modifier off the sheet
                value = profile_sheet.cell(profile_row, 3).value
                # Checks if you are profficient and adds a bonus if you are
                value = int(value) + int(self.check_skill_proficiency(user, active_profile, request))

                # Adds a + or a - to the modifier accordingly
                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Just does a flat roll without proficiency bonuses
            else:
                value = profile_sheet.cell(profile_row, 3).value
                return value

        elif request == 'dex' or request in dex_skill:

            if request_type == 'save':

                value = profile_sheet.cell(profile_row, 4).value

                value = int(value) + int(self.check_save_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Check if you are proficient in the requested skill
            elif request_type == 'skill':

                value = profile_sheet.cell(profile_row, 4).value

                value = int(value) + int(self.check_skill_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Just does a flat roll without proficiency bonuses
            else:
                value = profile_sheet.cell(profile_row, 4).value
                return value

        elif request == 'con':

            if request_type == 'save':

                value = profile_sheet.cell(profile_row, 5).value
                value = int(value) + int(self.check_save_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Check if you are proficient in the requested skill
            elif request_type == 'skill':
                pass

            # Just does a flat roll without proficiency bonuses
            else:
                value = profile_sheet.cell(profile_row, 5).value
                return value

        elif request == 'wis' or request in wis_skill:

            if request_type == 'save':

                value = profile_sheet.cell(profile_row, 7).value
                value = int(value) + int(self.check_save_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Check if you are proficient in the requested skill
            elif request_type == 'skill':

                value = profile_sheet.cell(profile_row, 7).value
                value = int(value) + int(self.check_skill_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Just does a flat roll without proficiency bonuses
            else:
                value = profile_sheet.cell(profile_row, 7).value
                return value

        elif request == 'int' or request in int_skill:

            if request_type == 'save':

                value = profile_sheet.cell(profile_row, 6).value
                value = int(value) + int(self.check_save_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Check if you are proficient in the requested skill
            elif request_type == 'skill':

                value = profile_sheet.cell(profile_row, 6).value
                value = int(value) + int(self.check_skill_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Just does a flat roll without proficiency bonuses
            else:
                value = profile_sheet.cell(profile_row, 6).value
                return value

        elif request == 'cha' or request in cha_skill:

            if request_type == 'save':

                value = profile_sheet.cell(profile_row, 8).value
                value = int(value) + int(self.check_save_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Check if you are proficient in the requested skill
            elif request_type == 'skill':

                value = profile_sheet.cell(profile_row, 8).value
                value = int(value) + int(self.check_skill_proficiency(user, active_profile, request))

                if value >= 0:
                    value = '+' + str(value)
                else:
                    value = '-' + str(value)

                return value

            # Just does a flat roll without proficiency bonuses
            else:
                value = profile_sheet.cell(profile_row, 8).value
                return value

    def check_save_proficiency(self, user, active_profile, request):
        """Function that checks wether to apply a proficiency bonus or not"""

        # Finds the active profile name on the profile sheet
        profile_loc = profile_sheet.find(active_profile)
        # Declares the row where it can find all the needed stats
        profile_row = profile_loc.row

        # Makes a list with the proficiencies
        s_proficiencies = profile_sheet.cell(profile_row, 10).value.split(',')

        prof_bonus = 0

        for prof in s_proficiencies:

            # Checks if you have proficiency in the requested save
            if request == prof.strip():
                prof_bonus = profile_sheet.cell(profile_row, 12).value
                return int(prof_bonus)
            else:
                pass

        if prof_bonus == 0:
            return prof_bonus

    def check_skill_proficiency(self, user, active_profile, request):
        """Function that checks wether to apply a proficiency bonus or not"""

        # Finds the active profile name on the profile sheet
        profile_loc = profile_sheet.find(active_profile)
        # Declares the row where it can find all the needed stats
        profile_row = profile_loc.row

        # Makes a list with the proficiencies
        s_proficiencies = profile_sheet.cell(profile_row, 11).value.split(',')

        prof_bonus = 0

        for prof in s_proficiencies:

            # Checks if you have proficiency in the requested skill
            if request == prof.lstrip():
                prof_bonus = profile_sheet.cell(profile_row, 12).value
                return int(prof_bonus)
            else:
                pass

        if prof_bonus == 0:
            return prof_bonus


my_handler = PHandler()


