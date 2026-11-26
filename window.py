from pathlib import Path
from random import Random
import tkinter as tk

from game import Game
from main import game_key

BACKGROUND = "#111722"
PANEL = "#1b2636"
TEXT = "#f3f6fb"
MUTED = "#a7b7cb"
ACCENT = "#6ee7bb"
CELL_COLORS = {"#": "#34455b", "!": "#77384a", "+": "#225746",
               "E": "#244e66", "D": "#6e511d", "X": "#79492a"}
CELL_LABELS = {"!": "!", "+": "+", "E": "⇧", "D": "10", "X": "25"}


class CourierWindow:
    def __init__(self, root):
        self.root = root
        self.game = Game(Random())
        root.title("Подземная доставка")
        root.configure(bg=BACKGROUND, padx=20, pady=16)
        root.resizable(False, False)

        self.title = tk.Label(root, bg=BACKGROUND, fg=TEXT, font=("Arial", 22, "bold"))
        self.title.pack(anchor="w", pady=(0, 12))

        body = tk.Frame(root, bg=BACKGROUND)
        body.pack()
        self.board = tk.Canvas(body, width=610, height=358, bg=PANEL, highlightthickness=0)
        self.board.pack(side="left")

        source = tk.PhotoImage(file=str(Path(__file__).with_name("courier.png")))
        # Берём лицо из фотографии и делаем маленькую копию для карты.
        self.portrait = tk.PhotoImage()
        self.portrait.tk.call(self.portrait, "copy", source, "-from", 168, 25, 348, 205,
                              "-subsample", 2, 2)
        self.token = self.portrait.subsample(5, 5)
        sidebar = tk.Frame(body, bg=PANEL, padx=16, pady=14)
        sidebar.pack(side="left", fill="y", padx=(12, 0))
        tk.Label(sidebar, image=self.portrait, bg=PANEL).pack(anchor="w")
        tk.Label(sidebar, text="Курьер", bg=PANEL, fg=ACCENT, font=("Arial", 15, "bold")).pack(
            anchor="w", pady=(6, 14)
        )
        self.stats = tk.Label(sidebar, width=20, justify="left", anchor="w",
                              bg=PANEL, fg=TEXT, font=("Arial", 13))
        self.stats.pack(anchor="w")
        tk.Label(sidebar, text="⇧  Лифт\n!   Ловушка\n+  Батарейка\n10 / 25  Очки за доставку",
                 justify="left", bg=PANEL, fg=MUTED, font=("Arial", 11)).pack(anchor="w", pady=(18, 0))

        self.message = tk.Label(root, bg=BACKGROUND, fg=TEXT, font=("Arial", 13), anchor="w")
        self.message.pack(fill="x", pady=(10, 4))
        self.controls = tk.Label(root, bg=BACKGROUND, fg=MUTED, font=("Arial", 11), anchor="w")
        self.controls.pack(fill="x")
        root.bind("<KeyPress>", self.on_key)
        self.draw()

    def on_key(self, event):
        key = game_key(event.char)
        if key == "q" or event.keysym == "Escape":
            self.root.destroy()
            return
        if self.game.status == "lost" and key == "r":
            self.game = Game(Random())
        elif key in ("w", "a", "s", "d"):
            self.game.move(key)
        else:
            return
        self.draw()

    def draw(self):
        game = self.game
        level = game.level
        self.title.configure(text=f"Подземная доставка   /   Этаж {game.floor:02}")
        self.stats.configure(text=f"Энергия  {game.energy}/{level.energy}\n"
                             f"Очки  {game.score}\nДоставок осталось  {len(level.deliveries)}")
        self.message.configure(text=game.message or " ")
        self.controls.configure(text="R — новая игра     Q — выход" if game.status == "lost"
                                else "WASD — движение     Q — выход")

        board = self.board
        board.delete("all")
        size = min(34, 610 // level.width, 358 // level.height)
        left = (610 - size * level.width) // 2
        top = (358 - size * level.height) // 2
        # Рисуем клетку за клеткой. Курьеру рисуем фото вместо знака.
        for y in range(level.height):
            for x in range(level.width):
                cell = level.symbol((x, y))
                px, py = left + x * size, top + y * size
                board.create_rectangle(px, py, px + size, py + size, outline=PANEL,
                                       fill=CELL_COLORS.get(cell, BACKGROUND))
                cx, cy = px + size // 2, py + size // 2
                if (x, y) == game.position:
                    board.create_rectangle(px + 1, py + 1, px + size - 1, py + size - 1, outline=ACCENT)
                    board.create_image(cx, cy, image=self.token)
                elif cell in CELL_LABELS:
                    board.create_text(cx, cy, text=CELL_LABELS[cell], fill=TEXT, font=("Arial", 11, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    CourierWindow(root)
    root.mainloop()
