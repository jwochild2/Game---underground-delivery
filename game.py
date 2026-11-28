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
        self.fast_moves = 0
        self.message = "Доставьте все посылки и вернитесь к лифту."

    def move(self, command):
        if self.status != "playing" or command not in DIRECTIONS:
            return
        steps = 1
        if self.fast_moves > 0:
            steps = 2
        old_floor = self.floor
        for _ in range(steps):
            self.step(command)
            if self.status != "playing" or self.floor != old_floor:
                break
        if self.fast_moves > 0:
            self.fast_moves -= 1

    @count_moves
    def step(self, command):
        if self.status != "playing" or command not in DIRECTIONS:
            return

        # Сначала проверяем клетку. Стена не тратит энергию.
        dx, dy = DIRECTIONS[command]
        x, y = self.position
        destination = (x + dx, y + dy)
        if not self.level.walkable(destination):
            self.message = "Путь перекрыт."
            return

        self.position = destination
        self.message = ""
        cost = 1
        if destination in self.level.traps:
            cost = 5
            self.message = "Ловушка! Потрачено 5 энергии."
        self.energy = max(0, self.energy - cost)
        if self.energy == 0:
            self.status = "lost"
            self.message = "Энергия закончилась."
            return

        # После шага отмечаем использованную батарейку или доставку.
        if destination in self.level.batteries:
            self.level.batteries.remove(destination)
            restored = self.restore_energy(self)
            self.message = f"Батарейка восстановила {restored} энергии."

        if destination in self.level.deliveries:
            reward = self.level.deliveries[destination]
            del self.level.deliveries[destination]
            self.score += reward
            self.message = f"Посылка доставлена. +{reward} очков."
            if not self.level.deliveries:
                self.message += " Возвращайтесь к лифту."

        if destination == self.level.entrance and not self.level.deliveries:
            completed_floor = self.floor
            self.floor += 1
            self.start_floor()
            self.message = f"Этаж {completed_floor} пройден. Новая карта готова."
