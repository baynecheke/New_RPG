import yaml
import heapq
import time
import threading
global factory_map
with open("factory") as f:
    data = yaml.safe_load(f)
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
            'location': 'Loading Dock',
            }
    def begin_game(self):
        print("Game starting up...")
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
            print(f"You can move to: {' '.join(factory_map[current_location]['adjacent'])}")
            return False

        travel_info = factory_map[current_location]['adjacent'][destination]
        travel_time = travel_info['cost'] / 5  # scale cost to seconds, adjust as desired

        print(f"Moving from {current_location} to {destination} via {travel_info['method']}...")
        for i in range(int(travel_time)):
            print(".", end="", flush=True)
            time.sleep(1)

        self.player['location'] = destination
        print(f"\nYou have arrived at {destination}.")
        print(factory_map[destination]['desc'])
        return True

path = pathfinding()
main = main_game()
main.begin_game()
main.move_player('Catwalk')

distance, path = path.shortest_path(factory_map, "Loading Dock", "Catwalk")
print(f"Shortest distance: {distance}")
print(f"Path: {' -> '.join(path)}")   
