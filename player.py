from character import Character
import requests_cache
import asyncio
from aiohttp_client_cache import CachedSession, SQLiteBackend
import requests
import pprint
from colorama import Fore
from colorama import Style
from colorama import init
import datetime
import time
from tabulate import tabulate

def seconds_until_next_wednesday_6am():
    # Get the current date and time
    now = datetime.datetime.now()

    # Calculate the days until the next Wednesday (0 = Monday, 1 = Tuesday, ...)
    days_until_next_wednesday = (2 - now.weekday() + 7) % 7

    # Create a datetime object for the next Wednesday at 6:00 AM
    next_wednesday = now + datetime.timedelta(days=days_until_next_wednesday)
    next_wednesday = next_wednesday.replace(hour=6, minute=0, second=0, microsecond=0)

    # Calculate the time difference in seconds
    time_difference = next_wednesday - now

    return time_difference.total_seconds()

requests_cache.install_cache(cache_name='affix_cache', expire_after=seconds_until_next_wednesday_6am())

points_per_level = {2:40, 
 3:45, 
 4:50, 
 5:55, 
 6:60, 
 7:75, 
 8:80, 
 9:85, 
 10:90, 
 11:97, 
 12:104, 
 13:111, 
 14:128, 
 15:135, 
 16:142, 
 17:149, 
 18:156, 
 19:163, 
 20:170, 
 21:177, 
 22:184, 
 23:191, 
 24:198, 
 25:205, 
 26:212, 
 27:219, 
 28:226, 
 29:233, 
 30:240}

def get_approximate_lvl(score):
    approx = 0
    for key, value in points_per_level.items():
        if score >= value:
            approx = key
    return approx

class Player():

    def __init__(self, name):
        self.name = name
        self.characters = []
        self.results = []
        

    def get_name(self):
        return self.name

    def add_character(self,name, realm, region):
        self.characters.append(Character(name,realm,region))

    def remove_character(self, name, realm, region):
        self.characters.remove(Character(name, realm, region))




    def get_affix(self, region):
        affixes = requests.get(f"https://raider.io/api/v1/mythic-plus/affixes?region={region}&locale=en")
        if affixes.json()['affix_details'][0]['name'] == 'Tyrannical':
            return "Tyrannical"
        if affixes.json()['affix_details'][0]['name'] == 'Fortified':
            return "Fortified"

    def sort_by_score(self,value):
        return value['score']
    

    def who_to_play_for_key(self, shortname, level):
        print("")
        print(f"Who to play for {shortname.upper()}{level} ({self.get_affix('eu')})")
        not_ranked = self.characters.copy()
        ranked = []
        ## print(self.results[0])


        for result in self.results:
            if 'mythic_plus_best_runs' in result or 'mythic_plus_alternate_runs' in result:
                mythic_runs_key = 'mythic_plus_best_runs' if 'mythic_plus_best_runs' in result else 'mythic_plus_alternate_runs'

                for j in result.get(mythic_runs_key, []):
                    if j['short_name'] == shortname.upper() and self.get_affix("eu") == j['affixes'][0]['name']:
                        ranked.append(j)

                        for char in not_ranked:
                            if result['name'] == char.name and result['realm'] == char.realm and result['region'] == char.region:
                                not_ranked.remove(char)


        ## prepare table for printing

        ranked = sorted(ranked, key=self.sort_by_score, reverse=True)

        table_data = []
        headers = ["Name", "Class", "Score", "~ Key Level"]

        ## add ranked runs to table

        for run in ranked:
            for result in self.results:
                for run_type in ["mythic_plus_best_runs", "mythic_plus_alternate_runs"]:
                    if run_type in result and run in result[run_type]:
                        name = result['name']
                        class_name = result['class']
                        score = run['score']
                        approximate_key_level = get_approximate_lvl(run['score'])
                        color = Fore.LIGHTGREEN_EX if level <= approximate_key_level else Fore.YELLOW
                
                        table_data.append([f"{color}{name}{Style.RESET_ALL}", f"{color}{class_name}{Style.RESET_ALL}", f"{color}{score}{Style.RESET_ALL}", f"{color}{approximate_key_level}{Style.RESET_ALL}"])


        ## add unranked chars to table

        for char in not_ranked:
            characterclass = ""
            ## get class of character
            for result in self.results:
                if result['name'] == char.name and result['realm'] == char.realm and result['region'] == char.region:
                    characterclass = result['class']
            name = char.name
            class_name = characterclass
            score = 0
            approximate_key_level = 0
            color = Fore.RED
            
            table_data.append([f"{color}{name}{Style.RESET_ALL}", f"{color}{class_name}{Style.RESET_ALL}", f"{color}{score}{Style.RESET_ALL}", f"{color}{approximate_key_level}{Style.RESET_ALL}"])
            
        
        ## print table
        table = tabulate(table_data, headers, tablefmt="plain_grid")
        print(table)
        print("")
        
        
