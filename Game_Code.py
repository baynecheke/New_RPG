import yaml
import heapq
import time
import random
import threading
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

with open(r"C:\Users\djche\OneDrive\new_RPG\New_RPG\factory", "r") as r:
    data = yaml.safe_load(r)
    factory_map = data["factory_map"]




class pathfinding():
    def __init__(self):
        nothing = 10
    def shortest_path(self, factory_map, start, goal):
        """
        Returns the shortest path and total distance between two locations.
        Works with the new 'adjacent' format:
        adjacent:
            RoomName:
            method: walk/ladder/stairs
            cost: int
        """
        queue = [(0, start, [start])]
        visited = set()

        while queue:
            dist, current, path = heapq.heappop(queue)

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return dist, path

            for neighbor, info in factory_map[current].get("adjacent", {}).items():
                cost = info["cost"]
                if neighbor not in visited:
                    heapq.heappush(queue, (dist + cost, neighbor, path + [neighbor]))

        return float("inf"), []  # no path found
class Enemy(threading.Thread):
    def __init__(self, name, factory_map, player, pathfinder, delay=2):
        super().__init__(daemon=True)
        self.name = name
        self.factory_map = factory_map  # must be the dict of rooms
        self.player = player
        self.pathfinder = pathfinder
        self.delay = delay

        # Pick random starting location
        self.current_location = random.choice(list(self.factory_map.keys()))

    def run(self):
        while True:
            time.sleep(self.delay)  # move at same speed as player
            
            # Find shortest path toward player
            _, path = self.pathfinder.shortest_path(
                self.factory_map,
                self.current_location,
                self.player['location']
            )

            if len(path) > 1:
                next_room = path[1]
                travel_info = self.factory_map[self.current_location]['adjacent'][next_room]
                travel_time = travel_info['cost'] / 2.5
                print(f"{self.name} is moving from {self.current_location} to {next_room} via {travel_info['method']}...")
                time.sleep(travel_time)
                self.current_location = next_room
            else:
                # Already at the player location, no movement needed
                next_room = self.current_location

            # Check if enemy is near or found the player
            if self.current_location == self.player['location']:
                print(f"\n⚠ {self.name} has found you in {self.current_location}!")
            elif self.player['location'] in self.factory_map[self.current_location].get("adjacent", {}):
                print(f"\n👀 You see {self.name} nearby in {self.current_location}.")

class main_game:
    def __init__(self):
        self.factory_map = factory_map
        self.player = {
            'player_stats':{
                'name': 'none',
                'health': 0,
                'strength': 0,
                'stealth': 0,
                'agility': 0,
                'special abilities': {},
                'injuries': {},
            },
            'inventory': {},
            'location': 'Loading_Dock',
            'status': 'none'
            }
        self.enemies = []
    def spawn_enemies(self, enemy_count):
        pathfinder = pathfinding()  # create the pathfinder once
        for i in range(enemy_count):
            enemy = Enemy(
                f"ai_{i+1}",      # name
                self.factory_map, # ✅ this must be the dict
                self.player,      # player dict
                pathfinder        # pathfinder object
        )
        enemy.start()
    def begin_game(self):
        print("Game starting up...")

        enemy_count = int(input("How many enemies do you want? "))
        self.spawn_enemies(enemy_count)

        self.player['player_stats']['health'] = 100
        print(f"Health = {self.player['player_stats']['health']}.")

        self.player['player_stats']['strength'] = 5
        print(f"Strength = {self.player['player_stats']['strength']}.")

        self.player['player_stats']['stealth'] = 5
        print(f"Stealth = {self.player['player_stats']['stealth']}.")

        self.player['player_stats']['agility'] = 5
        print(f"Agility = {self.player['player_stats']['agility']}.")
        
        self.add_item('rifle')
        print(f"{self.player['inventory']}")
        
        while True:
            if random.randint(1,3) ==3:
                self.print_color("You feel something watching you.", "danger")
            current_location = self.player['location']
            print(f"You are at: {current_location}")
            print(f"You can move to: {', '.join(factory_map[current_location]['adjacent'])}")
            choice = input("Where do you want to go:")
            
            self.move_player(choice)
        
    def print_rgb(self, text, r, g, b):
        # Construct the ANSI escape code using an f-string
        rgb_code = f"\033[38;2;{r};{g};{b}m"
        # The reset code returns the terminal to its default color
        reset_code = "\033[0m"
        print(f"{rgb_code}{text}{reset_code}")
    
    def print_color(self, text, type):
        if type == 'danger':
            r = 138
            g = 0
            b = 0
            self.print_rgb(text, r, g, b)
        else:
            print(text)

    def add_item(self, item, quantity=1):
        """Add an item (or increase its quantity)."""
        if item in self.player['inventory']:
            self.player['inventory'][item] += quantity
        else:
            self.player['inventory'][item] = quantity

    def remove_item(self, item, quantity=1):
        """Remove an item (or decrease its quantity)."""
        if item in self.player['inventory']:
            self.player['inventory'][item] -= quantity
            if self.player['inventory'][item] <= 0:
                del self.player['inventory'][item]
        else:
            print(f"{item} not in inventory!")

    def player_action(self):
        print()

    def move_player(self, destination):
        """Move player to an adjacent location with simulated travel time."""
        current_location = self.player['location']

        if destination not in factory_map[current_location]['adjacent']:
            print(f"You can't move directly from {current_location} to {destination}.")
            print(f"You can move to: {', '.join(factory_map[current_location]['adjacent'])}")
            return False

        travel_info = factory_map[current_location]['adjacent'][destination]
        travel_time = travel_info['cost'] / 2.5  

        print(f"Moving from {current_location} to {destination} via {travel_info['method']}...")
        self.player['status'] = 'walking'
        for i in range(int(travel_time)):
            print(".", end="", flush=True)
            time.sleep(1)
        self.player['status'] = 'idle'
        print(self.player['status'])

        self.player['location'] = destination
        print(f"\nYou have arrived at {destination}.")
        print(factory_map[destination]['desc'])
        return True

log = []
main = main_game()
# AI thread example
def start_enemy_threads(main_game_instance):
    for enemy in main_game_instance.enemies:
        enemy.start()

# Use PromptSession for player input
session = PromptSession()
with patch_stdout():
    while True:
        # Show last few log messages
        if log:
            print("\n".join(log[-10:]))

        # Prompt player
        cmd = session.prompt("> ")

        # Move player or handle commands
        main.move_player(cmd)


path = pathfinding()
main.begin_game()

distance, path = path.shortest_path(factory_map, "Loading_Dock", "Catwalk")
print(f"Shortest distance: {distance}")
print(f"Path: {' -> '.join(path)}")   
