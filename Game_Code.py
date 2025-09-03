import yaml
import heapq
import time
import random
import threading
import os
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
    def __init__(self, name, start_location, factory_map, game):
        super().__init__(daemon=True)  # dies with main program
        self.name = name
        self.location = start_location
        self.factory_map = factory_map
        self.game = game
        self.running = True

    def run(self):
        while self.running:
            time.sleep(random.randint(3, 6))  # wait before moving

            current = self.location
            neighbors = list(self.factory_map[current]['adjacent'].keys())
            if not neighbors:
                continue
            new_location = random.choice(neighbors)
            self.location = new_location

            # Check if player can see this enemy
            player_loc = self.game.player['location']
            player_los = self.factory_map[player_loc].get('los', [])
            if self.location == player_loc or self.location in player_los:
                print(f"\n⚠ You see {self.name} ({self.location})\n> ", end="", flush=True)


class main_game:
    def __init__(self):
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
    
    def spawn_enemies(self, num):
        for i in range(num):
            start = random.choice(list(factory_map.keys()))
            enemy = Enemy(f"ai_{i+1}", start, factory_map, self)
            self.enemies.append(enemy)
            enemy.start()
        print(f"Spawned {num} enemies.")
    
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

path = pathfinding()
main = main_game()
main.begin_game()

distance, path = path.shortest_path(factory_map, "Loading_Dock", "Catwalk")
print(f"Shortest distance: {distance}")
print(f"Path: {' -> '.join(path)}")   
