from level import DIRECTIONS, generate_level


class Game:
    def __init__(self, rng):
        self.rng = rng
        self.floor = 1
        self.score = 0
        self.start_floor()

    def start_floor(self):
        self.level = generate_level(self.floor, self.rng)
        self.position = self.level.entrance
        self.energy = self.level.energy
        self.status = "playing"
        self.message = "Это первый этаж игры."

    def move(self, command):
        if command not in DIRECTIONS:
            return
        x, y = self.position
        dx, dy = DIRECTIONS[command]
        destination = (x + dx, y + dy)
        if self.level.walkable(destination):
            self.position = destination
            self.message = ""
        else:
            self.message = "Путь перекрыт."
