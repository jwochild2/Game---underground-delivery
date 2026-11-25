from level import DIRECTIONS, generate_level


class Game:
    """Хранит номер этажа, очки и положение курьера."""

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
        self.message = "Доставьте все посылки и вернитесь к лифту."

    def move(self, command):
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
            restored = min(8, self.level.energy - self.energy)
            self.energy += restored
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
