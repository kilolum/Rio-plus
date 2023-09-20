import requests, json, requests_cache, threading
from player import Player
from character import Character
import time
import asyncio
import re
import datetime
import time

players = []
default_player = 0

def print_json(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

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
    
    # Convert the time difference to seconds
    seconds_until_next_wednesday = time_difference.total_seconds()
    
    return seconds_until_next_wednesday

requests_cache.install_cache(cache_name='rio_cache', expire_after=60*60*24)

"""
p1 = Player("Noslack")
p1.add_character("Slackless", "Blackmoore", "eu")
p1.add_character("Noslack", "Blackmoore", "eu")
p1.add_character("Raidover", "Blackmoore", "eu")
p1.add_character("Shifts", "Blackmoore", "eu")
p1.add_character("Neverslacks", "Blackmoore", "eu")
p1.add_character("Neverslack", "Blackmoore", "eu")
p1.add_character("Neverlags", "Blackmoore", "eu")
p1.add_character("Stopslack", "Blackmoore", "eu")
p1.add_character("Slacksabit", "Blackmoore", "eu")
p1.add_character("Slacksalot", "Blackmoore", "eu")
p1.add_character("Neverkicks", "Blackmoore", "eu")
p1.add_character("Díesalot", "Blackmoore", "eu")
p1.add_character("Dontslack", "Blackmoore", "eu")

p2 = Player("Millis")
p2.add_character("Qtmilli", "Silvermoon", "eu")
p2.add_character("Qtmillisen", "Silvermoon", "eu")
p2.add_character("Demonmilly", "Silvermoon", "eu")
p2.add_character("Qtmilly", "Silvermoon", "eu")
p2.add_character("Sillyqt", "Silvermoon", "eu")
p2.add_character("Qtmílly", "Silvermoon", "eu")

p3 = Player("Bloodfang")
p3.add_character("Hiraèth", "Silvermoon", "eu")
p3.add_character("Stbenji", "Silvermoon", "eu")
p3.add_character("Hiràeth", "Silvermoon", "eu")
p3.add_character("Sénnon", "Silvermoon", "eu")
p3.add_character("Voidyspirit", "Silvermoon", "eu")
p3.add_character("Hîmawarì", "Silvermoon", "eu")

players.append(p1)
players.append(p2)
players.append(p3)
"""

def update_all_players():
    start = time.time()

    for p in players:
        c = asyncio.run(p.get_player_update())

    end = time.time()
    print(end - start)

"""for p in players:
    p.who_to_play_for_key("hoi", 20)
    p.who_to_play_for_key("bh", 20)
    p.who_to_play_for_key("nelt", 20)
    p.who_to_play_for_key("nl", 20)
    p.who_to_play_for_key("uld", 20)
    p.who_to_play_for_key("fh", 20)
## p1.who_to_play_for_key("hoi", 20)
## p1.who_to_play_for_key("bh", 20)
"""

def save_to_file():
    # Create a list of dictionaries for players and their characters
    player_data = [{"name": player.name, "characters": [{"name": char.name, "realm": char.realm, "region": char.region} for char in player.characters]} for player in players]

    data_to_save = {"players": player_data}

    # Serializing json
    output_json = json.dumps(data_to_save, indent=4)
 
    # Writing to sample.json
    with open("playerdata.json", "w") as outfile:
        outfile.write(output_json)

def load_from_file():
    try:
        with open("playerdata.json", "r") as infile:
            data = json.load(infile)
        
        players = []

        for player_data in data.get("players", []):
            player = Player(player_data["name"])
            characters = player_data.get("characters", [])
            
            for char_data in characters:
                player.add_character(char_data["name"], char_data["realm"], char_data["region"])
            
            players.append(player)

        return players

    except FileNotFoundError:
        print("File 'playerdata.json' not found.")
        print("Start by adding a player and then add characters to the player")
        return []

def add_player(players):
    name = input("Enter the name of the player: ").strip().capitalize()
    player = Player(name)
    players.append(player)
    print(f"Player '{name}' added.")

def remove_player(players):
    playernames = "Valid choices for players to remove: "
    for player in players:
        playernames += (f"{player.name}, ")
    playernames = playernames[:-2]
    print(playernames)
    name = input("Enter the name of the player to remove: ").strip().capitalize()
    for player in players:
        if player.name == name:
            players.remove(player)
            print(f"Player '{name}' removed.")
            return
    print(f"Player '{name}' not found.")

def add_character(players):
    playernames = "Valid choices for players to add characters to: "
    for player in players:
        playernames += (f"{player.name}, ")
    playernames = playernames[:-2]
    print(playernames)
    player_name = input("Enter the name of the player to add a character to: ").strip().capitalize()
    for player in players:
        if player.name == player_name:
            char_name = input("Enter the name of the character: ").strip().capitalize()
            char_realm = input("Enter the realm of the character: ").strip()
            char_region = input("Enter the region of the character: ").strip().lower()
            character = Character(char_name, char_realm, char_region)
            player.characters.append(character)
            print(f"Character '{char_name}' added to player '{player_name}'.")
            return
    print(f"Player '{player_name}' not found.")

def remove_character(players):
    playernames = "Valid choices for players to remove characters from: "
    for player in players:
        playernames += (f"{player.name}, ")
    playernames = playernames[:-2]
    print(playernames)
    player_name = input("Enter the name of the player to remove a character from: ").strip().capitalize()
    for player in players:
        if player.name == player_name:

            charnames = f"Valid choices for characters to be removed from player {player_name}: "
            for character in player.characters:
                charnames += (f"{character.name}, ")
            charnames = charnames[:-2]
            print(charnames)

            char_name = input("Enter the name of the character to remove: ").strip().capitalize()
            for character in player.characters:
                if character.name == char_name:
                    player.characters.remove(character)
                    print(f"Character '{char_name}' removed from player '{player_name}'.")
                    return
            print(f"Character '{char_name}' not found for player '{player_name}'.")
            return
    print(f"Player '{player_name}' not found.")


menu_options_main = {
    1: 'Who should i play for this key?',
    2: 'Add/remove player/character',
    3: 'Change default player',
    4: 'Get vault status',
    5: 'Exit'
}

menu_options_add_remove_player_character = {
    1: "Add Player",
    2: "Remove Player",
    3: "Add Character to Player",
    4: "Remove Character from Player",
    5: "Back to main menu"
}

def print_menu(menu_options_name):
    for key in menu_options_name.keys():
        print (key, '-', menu_options_name[key] )

def option1(): # WHO TO PLAY
    print('Enter dungeon and keystone level (e.g. BH7, NELT10, ULD21):')
    input_data = input().strip().upper()

    # Use regular expressions to extract dungeon and level
    match = re.match(r"([A-Z]{2,4})(\d{1,2})", input_data)

    if match:
        dungeon = match.group(1)
        level = int(match.group(2))
        players[default_player].who_to_play_for_key(dungeon, level)
    else:
        print("Invalid input format. Please enter dungeon abbreviation and keystone level (e.g. BH7, NELT10, ULD21).")
        

def option2(): # Add/remove player/character
    print_menu(menu_options_add_remove_player_character)
    choice = input("Enter your choice: ")

    if choice == "1":
        add_player(players)
        save_to_file()
    elif choice == "2":
        remove_player(players)
        save_to_file()
    elif choice == "3":
        add_character(players)
        save_to_file()
    elif choice == "4":
        remove_character(players)
        save_to_file()
    elif choice == "5":
        save_to_file()
    elif choice == "7":
        return
    else:
        print("Invalid choice. Please try again.")


def option3(): # CHANGE DEFAULT PLAYER
    playernames = "Valid choices for new default players are: "
    for player in players:
        playernames += (f"{player.name}, ")
    playernames = playernames[:-2]
    print(playernames)
    print('Enter playername to set as new default player:')
    new_default_player = input().strip().capitalize()

    for player in players:
        if player.name.capitalize() == new_default_player:
            defaultplayer = players.index(player)
            return defaultplayer

    else:
        print("Invalid input format. Please enter a valid player name")

## TODO implement get vault status

def option4():
    pass        

if __name__ == '__main__':
    while 1:
        option = '' # reset option
        print('')
        print_menu(menu_options_main)
        players = load_from_file()
        if len(players) >= 1: update_all_players()
        try:
            option = int(input('Enter your choice: '))
        except:
            pass
        print('')

        if option == 1:
            option1()
            continue
        if option == 2:
            option2()
            continue
        if option == 3:
            default_player = option3()
            continue
        if option == 4:
            option4()
            continue
        if option == 5:
            exit()
        else: 
            print(f'Invalid option. Please enter a digit between 1 and {len(menu_options_main)}')









