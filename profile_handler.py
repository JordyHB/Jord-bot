import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from datetime import timedelta


class PHandler():
    """The class that handles fetching profiles from the google doc"""

    def __init__(self):
        """initializes self"""

        # Sets the start time of the program
        self.program_start_time = datetime.now()
        # Creates an empty flag that allows printing errors to the user
        self.error = ''
        # Creates an empty dict to temp store profiles for
        self.unclaimed_profiles = {}
        # Creates an empty list to temp store formatted profiles to show user
        self.unclaimed_profiles_list = []
        # stores the info of the last user to avoid having to look it up again
        self.cached_users = {}
        # List that stores the required keys for the prof_mods dict
        self.mod_keys = ['str', 'dex', 'con', 'int', 'wis', 'cha', 'ac', 'saves', 'skills', 'prof_b', 'spell_dc', 'spell_a']
        # list that stores valid skill inputs
        self.valid_types = ['str', 'dex', 'con', 'int', 'wis', 'cha']
        # Dicts to get the right modifiers for the right skills
        self.skills = {}
        self.skills['str'] = {'ath': 'Athletics'}
        self.skills['dex'] = {'acro': 'Acrobatics', 'slei': 'Sleight Of Hand', 'stea': 'Stealth'}
        self.skills['int'] = {'arc': 'Arcana', 'his': 'History', 'inv': 'Investigation', 'nat': 'Nature', 'rel': 'Religion'}
        self.skills['wis'] = {'ani': 'Animal Handling', 'insi': 'Insight', 'med': 'Medicine', 'perc': 'Perception', 'surv': 'Survival'}
        self.skills['cha'] = {'dec': 'Deception', 'inti': 'Intimidation', 'perf': 'Performance', 'pers': 'Persuasion'}

    def cache_user(self, user):
        """puts user in the cached_users dict to speed up the requests"""

        # Stores the location of the user and the active profile
        new_user = {}
        new_user['user_loc'] = self.check_user_sheet(user)
        new_user['active_profile'] = self.check_active_profile(user)
        new_user['profile_row'] = \
            profile_sheet.find(new_user['active_profile']).row

        # Stores a dict of profile names + their locations
        new_user['claimed_p_dict'] = self.fetch_claimed_profiles(user)
        if new_user['claimed_p_dict'] is None:
            new_user['claimed_p_dict'] = {}

        # Stores the new user in cache by the user ID
        self.cached_users[user] = new_user
        print(self.cached_users)
        # Caches the mods if the user has an active profile
        if new_user['active_profile'] != '':
            self.cache_cur_mod(user)

    def cache_cur_mod(self, user):
        """Gets all the modifiers for the current profile and adds them"""

        # Empty dict to store the values in
        prof_mods = {}
        # Variable to keep track of the right colom for the key
        mod_col = 3

        # Loops through the modkeys and fills a dict with the correct values
        for key in self.mod_keys:
            prof_mods[key] = profile_sheet.cell(self.cached_users[user]['profile_row'], mod_col).value
            mod_col = mod_col + 1

        # adds the mod dict to the user cache
        self.cached_users[user]['mods'] = prof_mods

    def save_cache(self):
        """Saves the cached_users dict to a Json"""

        with open('cached_data.json', 'w') as f:
            json.dump(self.cached_users, f)

    def load_cache(self):
        """loads cached_users dict"""

        with open('cached_data.json', 'r') as f:
            raw_cached_users = json.load(f)
            # Converts the strings back to ints
            for key in raw_cached_users.keys():
                self.cached_users[int(key)] = raw_cached_users[key]
            print('loaded cache!')

    def fetch_empty_col(self, user_location):
        """Find an empty colom to write the profiles in"""

        occupied_col = user_sheet.row_values(user_location)
        empty_col = len(occupied_col) + 1

        return empty_col

    def fetch_unclaimed_profiles(self):
        """Shows all unclaimed profiles on the google sheet"""

        self.refresh_auth()

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
                # Adds it to the unclaimed List
                self.unclaimed_profiles_list.append(
                    (str(profile + 1) + ": " +
                        str(raw_unclaimed_profiles[profile]))
                    )

            # Checks for claimed profiles moving on if they are
            elif current_profile == 'claimed':
                pass

            # Adds unclaimed profiles to the unclaimed profile dict
            elif current_profile == 'unclaimed':
                self.unclaimed_profiles_list.append(
                    (str(profile + 1) + ": " +
                        str(raw_unclaimed_profiles[profile]))
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

        # Get all the claimed profiles from the user sheet
        raw_c_profiles = user_sheet.row_values(self.check_user_sheet(user))
        claimed_p_list = raw_c_profiles[2:]
        print(claimed_p_list)

        # Finds the profile location adds it to a dict and returns it
        claimed_p_dict = {}

        for profile in claimed_p_list:
            if profile != '':
                claimed_p_dict[str(profile_sheet.find(profile).row)] = profile

        return claimed_p_dict

    def check_active_profile(self, user):
        """Checks which profile the user has active"""

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():

            # Returns the active profile stored in cache
            activated_profile = self.cached_users[user]['active_profile']
            return activated_profile

        else:

            # Finds the user in the database
            user_location = self.check_user_sheet(user)

            activated_profile = user_sheet.cell(user_location, 2).value
            return activated_profile

    def check_user_sheet(self, user):
        """Checks user sheet for existing profiles"""

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            user_location = self.cached_users[user]['user_loc']

        else:
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
                update1 = user_sheet.cell(empty_cell, 1)
                update1.value = str(user)
                update2 = user_sheet.cell(empty_cell, 2)
                update2.value = 'none'
                user_sheet.update_cells([update1, update2])
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

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            self.refresh_auth()

        else:
            self.refresh_auth()
            self.cache_user(user)

        # Gets values ready for a batch update to the profile sheet
        update1 = profile_sheet.cell(int(claim_input), 15)
        update2 = profile_sheet.cell(int(claim_input), 16)
        update1.value = 'claimed'
        update2.value = str(user)

        # Makes this the active profile if user doesnt already have one
        if self.cached_users[user]['active_profile'] == '' or \
                self.cached_users[user]['active_profile'] == 'none':

            # sets the profile as active on the profiles sheet
            update3 = profile_sheet.cell(int(claim_input), 17)
            update3.value = 'active'

            # Fetches users location in the database
            user_location = self.cached_users[user]['user_loc']

            # Adds the profile to batch for user and to set it as active
            update4 = user_sheet.cell(user_location, 2)
            update4.value = filtered_input

            # Adds newly claimed profile to the cache of claimed profiles
            self.cached_users[user]['active_profile'] = filtered_input
            self.cached_users[user]['claimed_p_dict'][str(profile_sheet.find(filtered_input).row)] = filtered_input

            # Finds an empty col to add the profile
            empty_col = self.fetch_empty_col(user_location)
            if empty_col == 2:
                empty_col = empty_col + 1
            update5 = user_sheet.cell(user_location, empty_col)
            update5.value = filtered_input

            # Updates the cell batches for the profile sheet and the user sheet
            profile_sheet.update_cells([update1, update2, update3])
            user_sheet.update_cells([update4, update5])

        else:
            # sets the profile as active on the profiles sheet
            profile_sheet.update_cell(int(claim_input), 17, 'inactive')

            # Fetches users location in the database
            user_location = self.cached_users[user]['user_loc']

            # Finds an empty col to add the profile
            empty_col = self.fetch_empty_col(user_location)
            profile_sheet.update_cells([update1, update2])
            user_sheet.update_cell(user_location, empty_col, filtered_input)

            # Adds newly claimed profile to the cache of claimed profiles
            self.cached_users[user]['claimed_p_dict'][str(profile_sheet.find(filtered_input).row)] = filtered_input

    def select_active_profile(self, user, request_p_loc):
        "Lets you pick which profile you want active"

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            self.refresh_auth()

        else:
            self.refresh_auth()
            self.cache_user(user)

        # Checks if you have actually claimed the requested profile
        try:
            print(self.cached_users[user]['claimed_p_dict'])
            _ = self.cached_users[user]['claimed_p_dict'][request_p_loc]

            # checks wether the profile is already active
            if profile_sheet.cell(request_p_loc, 2).value != \
                    self.cached_users[user]['active_profile']:

                # Handles setting the old active profile to inactive
                old_ap_loc = self.cached_users[user]['profile_row']
                profile_sheet.update_cell(old_ap_loc, 17, 'inactive')

                # Updates the cache and sets new profile to active
                profile_sheet.update_cell(request_p_loc, 17, 'active')
                self.cached_users[user]['profile_row'] = request_p_loc

                # updates the cache and the active profile on the user sheet
                user_loc = self.cached_users[user]['user_loc']
                self.cached_users[user]['active_profile'] = \
                    profile_sheet.cell(request_p_loc, 2).value
                user_sheet.update_cell(
                    user_loc, 2, self.cached_users[user]['active_profile']
                    )

            # Gives an error if you select the already active profile
            elif profile_sheet.cell(request_p_loc, 2).value == \
                    self.cached_users[user]['active_profile']:

                self.error = ' The profile you have selected is already active'

        except KeyError:
            self.error = ' Could not find a claimed profile by that number.' + \
                ' Please type "!myprofiles" to find the correct number'

    def show_claimed_profiles(self, user):
        """Shows the claimed profiles to the user"""

        # Resets the error flag
        self.error = ''

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            pass

        else:
            self.refresh_auth()
            self.cache_user(user)

        # Checks if the list isnt empty
        if self.cached_users[user]['claimed_p_dict']:

            # Creates an empty list to append too
            formatted_claims = []

            for key, value in self.cached_users[user]['claimed_p_dict'].items():

                # formats the key + value
                formatted_claim = key + ': ' + value
                # before adding it to a list for easy printback
                formatted_claims.append(formatted_claim)

            return formatted_claims

        else:
            self.error = ' You have no claimed profiles'
            return False

    def unclaim_profile(self, profile_number, user):
        """Function that lets you unclaim profiles"""

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            self.refresh_auth()

        else:
            self.refresh_auth()
            self.cache_user(user)

        try:
            unwanted_profile = self.cached_users[user]['claimed_p_dict'][profile_number]

            # Updates the cells in batch to unclaim on the profile sheet
            update1 = profile_sheet.cell(int(profile_number), 15)
            update1.value = 'unclaimed'
            update2 = profile_sheet.cell(int(profile_number), 16)
            update2.value = ''
            update3 = profile_sheet.cell(int(profile_number), 17)
            update3.value = 'inactive'
            profile_sheet.update_cells([update1, update2, update3])

            # Checks if the profile being unclaimed was the active one
            if unwanted_profile == self.cached_users[user]['active_profile']:
                user_sheet.update_cell(
                    self.cached_users[user]['user_loc'], 2, ''
                    )
                self.cached_users[user]['active_profile'] = ''

            # Finds the location of the unwanted profile in the user sheet
            prof_user_loc = user_sheet.find(unwanted_profile)

            # Updates the cells to unclaim on the profile sheet
            user_sheet.update_cell(
                self.cached_users[user]['user_loc'], prof_user_loc.col, ''
                )

            self.print_back = unwanted_profile

            # Updates the cached user
            del self.cached_users[user]['claimed_p_dict'][profile_number]

        except KeyError:
            self.error = ' You have no claimed profile by that number'

    def find_value(self, user, request, request_type):
        """Function that finds associated values on the google sheets"""

        # resets the error flag
        self.error = ''

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            pass

        else:
            self.refresh_auth()
            self.cache_user(user)

        if request_type == 'check':

            # Checks that you input a valid skin
            if request.lower() in self.valid_types:
                # Gets the value out of the dict
                r_value = self.cached_users[user]['mods'][request.lower()]
                return r_value
            else:
                self.error = ' No check by that name try (str/dex/con/int/wis/cha)'

        elif request_type == 'save':

            # Checks that you input a valid skin
            if request.lower() in self.valid_types:
                # Gets the value out of the dict
                r_value = self.cached_users[user]['mods'][request.lower()]

                # Checks if you are proficient in the requested save
                if request.lower() in self.cached_users[user]['mods']['saves']:
                    # adds prof bonus to the mod
                    r_value = int(r_value) + int(self.cached_users[user]['mods']['prof_b'])
                    if r_value >= 0:
                        r_value = '+' + str(r_value)
                    return r_value
                else:
                    return r_value
            else:
                self.error = ' No save by that name try (str/dex/con/int/wis/cha)'

        elif request_type == 'skill':

            # An empty dict to store the skill type and name
            skill_type = {}

            # Checks if the input is valid and gets the right modifier for it
            for key in self.skills:
                # Checks if you use an abbreviation before adding the skill
                # and type of skill to the empty dict
                if request.lower() in self.skills[key].keys():
                    skill_type[key] = self.skills[key][request.lower()]
                    break
                # adds unabbreviated version to the dict
                elif request.lower().title() in self.skills[key].values():
                    skill_type[key] = request.lower().title()
                    break

            if not skill_type:
                self.error = \
                    ' no skill found by that name, type !skillhelp for abbreviations'

            else:
                # Gets the key which has the type of modifeir it needs to add.
                for key in skill_type.keys():
                    # Checks if you are proficient in the skill
                    if skill_type[key] in self.cached_users[user]['mods']['skills']:
                        # If you are proficient gets the right mod and adds
                        # prof bonus
                        r_value = int(self.cached_users[user]['mods'][key]) + \
                            int(self.cached_users[user]['mods']['prof_b'])
                        # Adds a + for the roll
                        if r_value >= 0:
                            r_value = '+' + str(r_value)
                            return r_value

                    # otherwise just grabs the mod and hands it off
                    else:
                        r_value = self.cached_users[user]['mods'][key]
                        return r_value

    def request_mod(self, user, request, request_type):
        """this part is called by user so needs some checks"""

        # resets the error flag
        self.error = ''

        # Checks if the user is already in the cache.
        if user in self.cached_users.keys():
            pass

        else:
            self.refresh_auth()
            self.cache_user(user)

        # Checks that the user has an active profile
        if self.cached_users[user]['active_profile'] == '':
            self.error = \
                ' You have no active profile please select one with !selectprofile'

        else:
            # Gets the requested value from the cache and returns it
            r_value = self.find_value(user, request, request_type)
            return r_value

    def refresh_auth(self):
        """Reauthorizes the token"""

        # Checks if 15 min has passed otherwise ignores the call for a refresh
        if datetime.now() > self.program_start_time + timedelta(minutes=15):
            Client.login()
            self.program_start_time = datetime.now()

        else:
            pass

    def shutdown(self, user):
        """shuts down the bot after saving"""

        # Checks if it Jord requesting the shutdown
        if int(user) == 267425491034701824:
            self.save_cache()
            self.print_back = ' Goodnight! :D'
            return True

        else:
            self.print_back = " You have no power here! >:D"
            return False

    def repair_cache(self, user):
        """shuts down the bot after saving"""

        # Checks if it is Jord requesting the repair
        if int(user) == 267425491034701824:
            self.cached_users = {}
            self.print_back = \
                " Well, I fixed it for you because you screwed up you dummy!"

        else:
            self.print_back = " Please contact Jord with any issues you have!"



# Sets the all the basic stuff
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('profile_auth_secret.json', scope)
Client = gspread.authorize(creds)

profile_sheet = Client.open('dnd_profiles').sheet1
user_sheet = Client.open('dnd_profiles').get_worksheet(1)


