from collections import deque

# Каждая клетка — пара (x, y): столбец и строка.
# При движении вправо растёт x, а при движении вниз растёт y.
DIRECTIONS = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}


class Level:
    """Класс хранит данные карты. __init__ заполняет их при создании."""

    def __init__(self, width, height, entrance, walls, traps,
                 deliveries, batteries, energy):
        self.width = width
        self.height = height
        self.entrance = entrance
        self.walls = walls
        self.traps = traps
        self.deliveries = deliveries
        self.batteries = batteries
        self.energy = energy

    def walkable(self, cell):
        x, y = cell
        inside = 0 <= x < self.width and 0 <= y < self.height
        return inside and cell not in self.walls

    def symbol(self, cell):
        """Один и тот же знак клетки для терминала и окна."""
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


def distances(start, open_cells):
    """Сколько шагов нужно от start до каждой доступной клетки."""
    steps = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS.values():
            neighbor = (x + dx, y + dy)
            if neighbor in open_cells and neighbor not in steps:
                steps[neighbor] = steps[(x, y)] + 1
                queue.append(neighbor)
    return steps


def visit_cells(cell, open_cells, visited):
    """Рекурсивно обходим карту, запоминая посещённые клетки."""
    if cell not in open_cells or cell in visited:
        return
    visited.add(cell)
    x, y = cell
    for dx, dy in DIRECTIONS.values():
        visit_cells((x + dx, y + dy), open_cells, visited)


def place_hazards(candidates, count, open_cells, entrance):
    """Убираем клетки из безопасной зоны, пока все проходы связаны."""
    placed = set()
    for cell in candidates:
        if len(placed) == count:
            break

        open_cells.remove(cell)
        reachable = set()
        visit_cells(entrance, open_cells, reachable)
        if len(reachable) == len(open_cells):
            placed.add(cell)
        else:
            # Эта клетка соединяет части этажа. Оставляем её свободной.
            open_cells.add(cell)
    return placed


def delivery_route_length(entrance, deliveries, open_cells):
    """Считаем длину маршрута до всех доставок и обратно к лифту."""
    remaining = sorted(deliveries)
    current = entrance
    length = 0
    while remaining:
        steps = distances(current, open_cells)
        # Словарь steps хранит число шагов до каждой цели.
        nearest = min(remaining, key=steps.get)
        length += steps[nearest]
        current = nearest
        remaining.remove(nearest)
    return length + distances(current, open_cells)[entrance]


def generate_level(number, rng):
    # Размеры растут, пока карта помещается в игровое окно.
    width = min(9 + number * 2, 29)
    height = min(5 + number * 2, 17)
    entrance = (1, 1)

    walls = set()
    interior = []
    for y in range(height):
        for x in range(width):
            cell = (x, y)
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                walls.add(cell)
            else:
                interior.append(cell)

    open_cells = set(interior)
    wall_candidates = interior.copy()
    wall_candidates.remove(entrance)
    rng.shuffle(wall_candidates)
    wall_percent = min(10 + 2 * number, 34)
    wall_count = len(interior) * wall_percent // 100
    inner_walls = place_hazards(wall_candidates, wall_count, open_cells, entrance)
    walls.update(inner_walls)

    available = sorted(open_cells)
    available.remove(entrance)
    rng.shuffle(available)
    delivery_count = min(number + 1, 9)
    deliveries = {}
    for cell in available[:delivery_count]:
        deliveries[cell] = rng.choice([10, 10, 25])

    # Лифт и доставки исключены из списка мест для ловушек и батареек.
    extras = available[delivery_count:]
    trap_count = min(number + 2, len(interior) // 6)
    traps = place_hazards(extras, trap_count, open_cells, entrance)

    batteries = set()
    for cell in extras:
        if cell not in traps:
            batteries.add(cell)
        if len(batteries) == 2:
            break

    # Даём энергию на безопасный маршрут и немного сверх него.
    route = delivery_route_length(entrance, deliveries, open_cells)
    spare_energy = max(2, 13 - number)
    return Level(width, height, entrance, walls, traps, deliveries,
                 batteries, route + spare_energy)
