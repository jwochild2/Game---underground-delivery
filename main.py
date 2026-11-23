from random import Random
from game import Game


def draw(game):
    print(f"Этаж {game.floor}. Энергия {game.energy}. Очки {game.score}.")
    print(f"Доставок осталось: {len(game.level.deliveries)}")
    for y in range(game.level.height):
        row = []
        for x in range(game.level.width):
            cell = (x, y)
            if cell == game.position:
                row.append("@")
            else:
                row.append(game.level.symbol(cell))
        print(" ".join(row))
    print("@ курьер, # стена, E лифт, ! ловушка, + батарейка, D и X доставки")
    print(game.message)


def main():
    game = Game(Random())
    while True:
        draw(game)
        command = input("WASD + Enter — ход, R — новая игра, Q — выход: ").lower()
        if command == "q":
            break
        if command == "r":
            game = Game(Random())
        else:
            game.move(command)


if __name__ == "__main__":
    main()
