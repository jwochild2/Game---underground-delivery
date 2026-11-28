"""Запуск игры в терминале, чтение клавиш и отображение карты."""

import os
from random import Random
import sys

from game import Game, GameError

RUSSIAN_KEYS = {"ц": "w", "ф": "a", "ы": "s", "в": "d",
                "й": "q", "к": "r", "и": "b", "о": "j"}


def game_key(text):
    """Поддерживаем обе раскладки клавиатуры."""
    key = text.lower()
    return RUSSIAN_KEYS.get(key, key)


def read_key():
    """Получаем одно нажатие. Способ зависит от системы."""
    if not sys.stdin.isatty():
        return sys.stdin.read(1)
    if os.name == "nt":
        import msvcrt

        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            msvcrt.getwch()
            return ""
        return key

    import termios
    import tty

    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def draw(game):
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")
    level = game.level
    print(f"ПОДЗЕМНАЯ ДОСТАВКА  /  ЭТАЖ {game.floor:02}")
    print(f"Энергия {game.energy}/{level.energy}   Очки {game.score}   Доставок осталось {len(level.deliveries)}\n")
    for y in range(level.height):
        row = []
        for x in range(level.width):
            cell = (x, y)
            if cell == game.position:
                row.append("@")
            else:
                row.append(level.symbol(cell))
        print(" ".join(row))
    print("\n@ курьер   # стена   ! ловушка   + батарейка")
    print("E лифт    D доставка +10    X срочная доставка +25\n")
    if game.message:
        print(game.message)
    print("R — новая игра   Q — выход" if game.status == "lost" else "WASD — движение   B — ускорение (5 очков)   Q — выход", flush=True)


def main():
    print("Подземная доставка\nEnter — начать   Q — выход", flush=True)
    while True:
        key = read_key()
        if not key or game_key(key) == "q":
            return
        if key in ("\n", "\r"):
            break

    game = Game(Random())
    while True:
        draw(game)
        key = game_key(read_key())
        if not key:
            if not sys.stdin.isatty():
                return
            continue
        if key == "q":
            return
        if game.status == "lost" and key == "r":
            game = Game(Random())
        elif key == "b":
            try:
                game.buy_speed()
            except GameError as error:
                game.message = str(error)
        else:
            game.move(key)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
