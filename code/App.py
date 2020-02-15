import sys
import time
import random

from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPoint, QBasicTimer

import GameMap
from Characters import Player

UP = Qt.Key_Up
DOWN = Qt.Key_Down
RIGHT = Qt.Key_Right
LEFT = Qt.Key_Left
ENTER = Qt.Key_Return


class App(QWidget):
    """The main class of the game."""
    # TODO: Custom assignment of color and position.

    def __init__(self, num_of_players):
        # Init widget.
        super().__init__()
        self.num_of_players = num_of_players
        self.tile_size = 64
        self.key_press = ''

        # Init the game map.
        self.game_map = GameMap.create_map()
        # Init players.
        self.cur_player = 0
        self.players = []
        colors = Player._get_possible_colors()  # TODO: Shuffle colors?
        for i in range(num_of_players):
            self.players.append(Player(colors[i], side=i))

        # Init Qt things.
        self.time = QBasicTimer()

        self.UI()
        self.start()

    def UI(self):
        self.setWindowTitle('Jackal')
        self.update()

        # Resize the widget to fit the game map.
        # self.setFixedSize(pixmap.width(), pixmap.height())
        self.resize(self.pixmap.width(), self.pixmap.height())
        self.show()

    def update(self):
        # Draw the game map.
        game_map_img = ImageQt(GameMap.map_to_img(self.game_map))
        self.pixmap = QPixmap.fromImage(game_map_img).copy()
        self.show()

    def start(self):
        self.time.start(20, self)
        self.repaint()

    def paintEvent(self, e):
        painter = QPainter(self)
        # Draw the game map.
        painter.drawPixmap(0, 0, self.pixmap)
        # Draw the players.
        GameMap.display_players(painter, self.players)

    def keyPressEvent(self, e):
        pressed = e.key()
        if pressed == Qt.Key_Escape:
            self.close()
        elif pressed in (UP, DOWN, RIGHT, LEFT, ENTER):
            self.key_press = pressed

    def timerEvent(self, e):
        character = self.players[self.cur_player].characters[0]
        x, y = character.coords
        if self.key_press == RIGHT:
            character.move((x + 1, y))
        elif self.key_press == LEFT:
            character.move((x - 1, y))
        elif self.key_press == UP:
            character.move((x, y - 1))
        elif self.key_press == DOWN:
            character.move((x, y + 1))
        elif self.key_press == ENTER:
            self.cur_player = (self.cur_player + 1) % self.num_of_players
        self.key_press = ''
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(2)
    sys.exit(app.exec_())
