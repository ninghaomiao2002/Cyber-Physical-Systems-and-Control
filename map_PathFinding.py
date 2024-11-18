import numpy as np
import random
import matplotlib.pyplot as plt
from collections import deque
import heapq

# Map and PathFinder classes (as per previous code)
class Map:
    def __init__(self, size):
        self.size = size
        self.grid = None
        self.x = 0
        self.y = 0

    def generate(self):
        self.grid = np.zeros((self.size, self.size), dtype=int)
        return self.grid

    def create_path(self):
        self.x, self.y = (0, 0)
        self.grid[self.x, self.y] = 1
        while (self.x, self.y) != (self.size - 1, self.size - 1):
            choice = random.choice(['right', 'down'])
            if choice == 'right' and self.x < self.size - 1:
                self.x += 1
            if choice == 'down' and self.y < self.size - 1:
                self.y += 1
            self.grid[self.x, self.y] = 1

    def create_divergence(self):
        path_points = [(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i, j] == 1]
        divergence = random.choice(path_points[5:15])
        self.x, self.y = divergence
        if self.x < self.size - 1 and self.grid[self.x + 1, self.y] == 1:
            self.y += 1
        else:
            self.x += 1
        self.grid[self.x, self.y] = 1
        while (self.x, self.y) != (self.size - 1, self.size - 1):
            choice = random.choice(['right', 'down'])
            if choice == 'right' and self.x < self.size - 1 and self.grid[self.x + 1, self.y] == 0:
                self.x += 1
            elif choice == 'down' and self.y < self.size - 1 and self.grid[self.x, self.y + 1] == 0:
                self.y += 1
            else:
                if self.x < self.size - 1 and self.grid[self.x + 1, self.y] == 0:
                    self.x += 1
                elif self.y < self.size - 1 and self.grid[self.x, self.y + 1] == 0:
                    self.y += 1
                else:
                    break
            self.grid[self.x, self.y] = 1



        plt.show()
    
    def show(self, paths=None):
        plt.imshow(self.grid, cmap='gray')

        # If paths are provided, overlay them with different colors
        if paths:
            for path in paths:
                path_x, path_y = zip(*path)
                plt.plot(path_y, path_x, linewidth=2, marker='o', markersize=5)

        plt.show()  


map = Map(16)
map.generate()
map.create_path()
map.create_divergence()
map.show()

class PathFinder:
    def __init__(self, grid):
        self.grid = grid
        self.size = len(grid)
        self.all_paths = []  # To store all valid paths

    def find_all_paths(self):
        start = (0, 0)
        end = (self.size - 1, self.size - 1)
        path = []
        self.dfs(start, end, path)
        return self.all_paths

    def dfs(self, current, end, path):
        x, y = current
        # Add the current position to the path
        path.append(current)

        # If we reach the end, store the path and backtrack
        if current == end:
            self.all_paths.append(list(path))  # Store a copy of the current path
        else:
            # Explore neighbors (left, up, down, right)
            directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]   # Down, right, up, left
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] == 1 and (nx, ny) not in path:
                    self.dfs((nx, ny), end, path)

        # Backtrack: remove the current position from the path
        path.pop()


pathfinder = PathFinder(map.grid)
all_paths = pathfinder.find_all_paths()

if all_paths:
    print(f"Found {len(all_paths)} paths:")
    for i, path in enumerate(all_paths):
        print(f"Path {i + 1}: {path}")
    # Show all paths on the map
    map.show(paths=all_paths)
else:
    print("No paths found.")
    map.show()

if all_paths:
    print(f"Found {len(all_paths)} paths:")
    for i, path in enumerate(all_paths):
        print(f"Path {i + 1}: {path}")
    
    # Calculate and display costs for each path
    print("\nPath Costs:")
    for i, path in enumerate(all_paths):
        cost = len(path) - 1  # Cost is the number of steps
        print(f"Path {i + 1}: Cost = {cost}")

#____________________ Algorithms ____________________        
        
# Add Dijkstra Path Finder class
class DijkstraPathFinder:
    def __init__(self, grid):
        self.grid = grid
        self.size = len(grid)
        self.start = (0, 0)
        self.end = (self.size - 1, self.size - 1)

    def find_shortest_path(self):
        # Priority queue: (cost, (x, y), path)
        pq = [(0, self.start, [])]
        visited = set()

        while pq:
            cost, current, path = heapq.heappop(pq)
            x, y = current

            if current in visited:
                continue
            visited.add(current)

            # Add current node to the path
            path = path + [current]

            # If we reach the end, return the cost and path
            if current == self.end:
                return cost, path

            # Explore neighbors (right, down, left, up)
            directions = [(0, -1), (-1, 0), (1, 0), (0, 1)] # order: left, up, down, right 
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] == 1 and (nx, ny) not in visited:
                    heapq.heappush(pq, (cost + 1, (nx, ny), path))

        # If no path is found
        return float('inf'), []

# Find the shortest path using Dijkstra's algorithm
dijkstra_pathfinder = DijkstraPathFinder(map.grid)
shortest_cost, shortest_path = dijkstra_pathfinder.find_shortest_path()

if shortest_path:
    print(f"Shortest path found using Dijkstra's algorithm with cost {shortest_cost}: {shortest_path}")
    map.show(paths=[shortest_path])
else:
    print("No path found.")
    map.show()

# Add Depth-First Search Path Finder class
class DFSPathFinder:
    def __init__(self, grid):
        self.grid = grid
        self.size = len(grid)
        self.start = (0, 0)
        self.end = (self.size - 1, self.size - 1)
        self.visited = set()

    def find_path(self):
        path = []
        if self.dfs(self.start, path):
            return path
        else:
            return None  # No path found

    def dfs(self, current, path):
        if current == self.end:  # If we've reached the destination
            path.append(current)
            return True

        x, y = current
        self.visited.add(current)  # Mark the current node as visited
        path.append(current)

        # Explore neighbors in (left, up, down, right) order
        directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]  
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] == 1 and neighbor not in self.visited:
                if self.dfs(neighbor, path):
                    return True

        # Backtrack if no valid path is found from this node
        path.pop()
        return False


# Find a path using Depth-First Search
dfs_pathfinder = DFSPathFinder(map.grid)
dfs_path = dfs_pathfinder.find_path()

if dfs_path:
    print(f"Path found using DFS: {dfs_path}")
    map.show(paths=[dfs_path])
else:
    print("No path found using DFS.")
    map.show()

