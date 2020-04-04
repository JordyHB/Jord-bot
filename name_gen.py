import os
import requests
from bs4 import BeautifulSoup


class NameGen():
    """A class that handles fetching names and sending them to the user"""

    def __init__(self):
        """initializes all attributes"""
        self.names = []
        self.error = False

    def handle_input(self, race, subtype, extra):
        """Main function that sorts the user input"""

        # Resets the error flag
        self.error = False

        # Combines the input into 1 string
        name_input = race + ' ' + subtype + ' ' + extra

        # Opens the txt file containing all possible options
        with open(os.path.join("textfiles", "available_name_groups.txt")) as f:
            # Creates an empty list to store the possible options
            options = []
            # Reads the file line for line and adds the options to a list
            for line in f.readlines():
                options.append(line.rstrip())

        # Checks if the user input is valid
        if name_input.rstrip().lower() not in options:
            self.error = "Invalid input, please !Nhelp for all possible inputs"
            return

        # Hands it down to get processed by get_names
        else:
            # Checks if extra is empty or not to prevent capitalizing the A
            self.get_names(name_input.rstrip().title())

    def get_names(self, tribe, n=10):
        # replace any spaces with '+' (needed for conversion to url)
        print(tribe)
        tribe_as_header = tribe.replace(' ', '+')
        # make the url
        url = "https://donjon.bin.sh/name/rpc.cgi?type=" + \
            tribe_as_header + "&n=" + str(n)
        print(url)
        # get the page
        page = requests.get(url)
        # get the html
        html = BeautifulSoup(page.content, 'html.parser')
        page_as_string = html.prettify()
        # break the string on linebreaks
        self.names = page_as_string.splitlines()
        print(self.names)
