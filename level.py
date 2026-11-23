# Клетка хранит координаты (столбец, строка).
DIRECTIONS = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}


class Level:
    def __init__(self):
        self.width = 11
        self.height = 7
        self.entrance = (1, 1)
        self.walls = set()
        self.traps = set()
        self.batteries = set()
        self.deliveries = {}
        self.energy = 60

        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    self.walls.add((x, y))

    def walkable(self, cell):
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height and cell not in self.walls

    def symbol(self, cell):
        if cell == self.entrance:
            return "E"
        if cell in self.walls:
            return "#"
        if cell in self.traps:
            return "!"
        if cell in self.batteries:
            return "+"
        if cell in self.deliveries:
            if self.deliveries[cell] == 25:
                return "X"
            return "D"
        return "."


def generate_level(number, rng):
    level = Level()
    level.walls.update({(5, 2), (5, 3), (5, 4)})
    return level
