from functools import wraps
from level import DIRECTIONS, generate_level


class GameError(Exception):
    """Общая ошибка игровой команды."""


class NotEnoughPoints(GameError):
    """На ускорение не хватает очков."""


def count_moves(function):
    """Декоратор считает только шаги, которые действительно изменили позицию."""
    @wraps(function)
    def wrapper(self, command):
        old_position = self.position
        old_floor = self.floor
        result = function(self, command)
        if self.position != old_position or self.floor != old_floor:
            self.moves += 1
        return result
    return wrapper


def create_energy_bonus(amount):
    """Замыкание запоминает, сколько энергии даёт батарейка."""
    def restore(game):
        restored = min(amount, game.level.energy - game.energy)
        game.energy += restored
        return restored
    return restore


class Game:
    """Хранит номер этажа, очки и положение курьера."""

    def __init__(self, rng):
        self.rng = rng
        self.floor = 1
        self.score = 0
        self.moves = 0
        self.restore_energy = create_energy_bonus(8)
        self.start_floor()

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        # Свойство не позволяет энергии выйти за допустимые границы.
        self._energy = max(0, min(value, self.level.energy))

    def buy_speed(self):
        if self.status != "playing":
            return
        if self.score < 5:
            raise NotEnoughPoints("Для ускорения нужно 5 очков.")
        self.score -= 5
        self.fast_moves = 3
        self.message = "Ускорение на 3 команды WASD. Стоимость — 5 очков."

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
