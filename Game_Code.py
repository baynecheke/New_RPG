import yaml
import heapq
import time
import threading
with open("factory_map") as f:
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

class main:
    def __init__(self):
        self.player = {
            'player_stats':{
                'name': 'none',
                'health': 0,
                'strength': 0,
                'stealth': 0,
                'agility': 0,
                'special abilities': {},
            },
            'inventory': {},

            }

# distance, path = shortest_path(factory_map, "Loading Dock", "Catwalk")
# print(f"Shortest distance: {distance}")
# print(f"Path: {' -> '.join(path)}")   
