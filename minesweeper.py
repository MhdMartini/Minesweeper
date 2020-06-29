import random
from math import sqrt


def is_neighbor(tile_name1, tile_name2):
    x1, y1 = tile_name1.split(',')[-2:]
    x2, y2 = tile_name2.split(',')[-2:]
    x1, x2, y1, y2 = map(int, [x1, x2, y1, y2])
    # Distance formula:
    # sqrt( (x2-x1)^2 + (y2-y1)^2 )
    # Two tiles are neighbors if the distance between them is 1 or sqrt(2)
    distance = round(sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 2)
    if distance == 1 or distance == round(sqrt(2), 2):
        return True


def empty_parser(empty_tiles):
    # Initialize cluster with random tile
    # Delete that tile from main set (empty_tiles)
    # Loop through all empty tiles and cluster neighbors together
    # End result is a dictionary:
    # { "cluster# : {"tile,0,3", "tile,10,5", "tile,16,8", ...}, ...}
    empty_tile_clusters = {}
    idx = 0
    while True:
        # Choose random value from set of empty tiles
        value = random.sample(empty_tiles, 1)[0]
        cluster = {value}
        while True:
            temp = cluster.copy()

            for tile_name in empty_tiles:
                cluster_copy = cluster.copy()
                # As cluster grows, check if tile_name is a neighbor of any of the cluster elements
                for val in cluster_copy:
                    if is_neighbor(tile_name, val):
                        cluster |= {tile_name}
                        break
            if temp == cluster:  # If cluster did not grow after a full loop
                empty_tiles -= cluster
                empty_tile_clusters[f"cluster{idx}"] = cluster
                break

        # Return when all empty tiles are divided into clusters
        if not empty_tiles:
            return empty_tile_clusters

        idx += 1


class Tile:
    def __init__(self):
        self.mine = False

    def __repr__(self):
        return str(self.value)


class MineSweeper:
    # Minesweeper grid class
    def __init__(self, difficulty):
        self.empty_tile_clusters = set()
        # Initialize the game with grid of size length * length, and pass to 'fill()'
        switcher = {
            # {Level : (mine count, grid side length), ...}
            'beginner': (12, 12),
            'intermediate': (40, 16),
            'expert': (100, 25),
            "boss": (250, 40)
        }
        self.mine_count, self.side_length = switcher[difficulty.lower()]
        self.tile_count = self.side_length * self.side_length  # TODO
        self.tiles = {f"tile,{x},{y}": Tile() for x in range(self.side_length) for y in range(self.side_length)}
        self.tiles = self.fill()

    def fill(self):
        # Mines ratio and grid size are chosen according to specified difficulty
        # Create random mines coordinates
        # If idx is 12 and grid side length is 10, then y = 12//10 = 1, x = 12%10 = 2
        mines_positions = random.sample(range(self.tile_count), self.mine_count)

        self.mine_tiles = set()
        for idx in mines_positions:
            # Get coordinates from random number, and plant a mine at that coordinate
            y, x = divmod(idx, self.side_length)
            tile_name = f'tile,{x},{y}'
            self.tiles[tile_name].mine = True
            self.mine_tiles |= {tile_name}

        #
        empty_tiles = set()
        for tile_name, tile in self.tiles.items():
            neighbors_ = self.neighbors(tile_name)
            neighbors_mine_count = len(neighbors_ & self.mine_tiles)  # {1,2,3,4} & {1,4,5} = {1,4}
            tile.value = neighbors_mine_count
            if tile.mine:
                continue
            # neighbors_ = self.neighbors(tile_name)
            # neighbors_mine_count = len(neighbors_ & self.mine_tiles)  # {1,2,3,4} & {1,4,5} = {1,4}
            if neighbors_mine_count == 0:
                empty_tiles |= {tile_name}
            # tile.value = neighbors_mine_count

        self.empty_tile_clusters = empty_parser(empty_tiles)

        return self.tiles

    def __repr__(self):
        return f"Minesweeper {self.side_length} X {self.side_length} grid"

    def neighbors(self, tile_name):
        # Get the set of neighboring tiles of tile_name
        neighbors_ = set()
        x, y = tile_name.split(',')[-2:]
        x, y = int(x), int(y)
        directions = (-1, 0, 1)
        for i in directions:
            for j in directions:
                x_new, y_new = (x + i, y + j)
                if (0 <= x_new < self.side_length) and (0 <= y_new < self.side_length):
                    coord = f"{x_new},{y_new}"
                    neighbors_ |= {"tile," + coord}
                else:
                    continue
        return neighbors_


