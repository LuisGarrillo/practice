import pygame, json
PHYSICS_TILES = {"grass", "stone"}
NEIGHBOR_OFFSETS = [
    (-1, 0), (-1, -1), (0, -1), (0, 0), (0, 1), (1, 1), (1, 0), (-1, 1), (1, -1)
]
AUTOTILES_TYPES = {"grass", "stone"}
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}
class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def save(self, path):
        with open(path, "w") as file:
            json.dump({"tilemap": self.tilemap, "tile_size": self.size, "offgrid": self.offgrid_tiles}, file)

    def load(self, path):
        with open(path, "r") as file:
            map_data = json.load(file)

        self.tilemap = map_data["tilemap"]
        self.size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]

    def autotile(self):
        for location in self.tilemap:
            tile = self.tilemap[location]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                check_location = str(tile["position"][0] + shift[0]) + ";" + str(tile["position"][1] + shift[1])
                if (
                    check_location in self.tilemap and  
                    self.tilemap[check_location]["type"] == tile["type"]
                    ):

                    neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile["type"] in AUTOTILES_TYPES and neighbors in AUTOTILE_MAP):
                tile["variant"] = AUTOTILE_MAP[neighbors]

    def extract(self,id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        for location in self.tilemap:
            tile = self.tilemap[location]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["position"] = matches[-1]["position"].copy()
                matches[-1]["position"][0] *= self.size
                matches[-1]["position"][1] *= self.size
                if not keep:
                    del self.tilemap["location"]

        return matches

    def tiles_around(self, position):
        tiles = []
        tile_location = (int(position[0] // self.size), int(position[1] // self.size))

        for offset in NEIGHBOR_OFFSETS:
            check_location = str(tile_location[0] + offset[0]) + ";" + str(tile_location[1] + offset[1])
            if check_location in self.tilemap:
                tiles.append(self.tilemap[check_location])
        return tiles
    
    def physics_rects_around(self, position):
        rects = []
        for tile in self.tiles_around(position):
            if tile["type"] in PHYSICS_TILES:
                rects.append(pygame.Rect(
                    tile["position"][0] * self.size, 
                    tile["position"][1] * self.size,
                    self.size,
                    self.size
                ))
        return rects

    def render(self, surface, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surface.blit(
                self.game.assets[tile["type"]][tile["variant"]], 
                (tile["position"][0] - offset[0], tile["position"][1] - offset[1]) 
            )

        for x in range(offset[0] // self.size, (offset[0] + surface.get_width()) // self.size + 1):
            for y in range(offset[1] // self.size, (offset[1] + surface.get_height()) // self.size + 1):
                location = str(x) + ";" + str(y)

                if location in self.tilemap:
                    tile = self.tilemap[location]
                    surface.blit(
                    self.game.assets[tile["type"]][tile["variant"]],
                    (tile["position"][0] * self.size - offset[0], tile["position"][1] * self.size - offset[1])
                    )

        #for location in self.tilemap:
        #    tile = self.tilemap[location]
        #    surface.blit(
        #        self.game.assets[tile["type"]][tile["variant"]],
        #       (tile["position"][0] * self.size - offset[0], tile["position"][1] * self.size - offset[1])
        #   )