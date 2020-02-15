import sys
import time
import random

from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPoint, QBasicTimer

import GameMap
from GameLogic import GameLogic
from Characters import Player


class App(QWidget):
    """The main class of the game."""

    __key_to_direction = {
        Qt.Key_Up: 'up',
        Qt.Key_Down: 'down',
        Qt.Key_Right: 'right',
        Qt.Key_Left: 'left',
    }

    # TODO: Custom assignment of color and position.
    def __init__(self, num_of_players):
        # Init widget.
        super().__init__()
        self.game_logic = GameLogic(num_of_players)
        self.key_press = ''

        # Init Qt timer.
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
        game_map_img = ImageQt(self.game_logic.get_map_image())
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
        self.game_logic.display_players(painter)

    def keyPressEvent(self, e):
        pressed = e.key()
        if pressed == Qt.Key_Escape:
            self.close()
        else:
            self.key_press = pressed

    def timerEvent(self, e):
        if self.key_press in self.__key_to_direction:
            self.game_logic.move_character(
                self.__key_to_direction[self.key_press])
        elif self.key_press == Qt.Key_Return:
            self.game_logic.next_player()
        self.key_press = ''
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(2)
    sys.exit(app.exec_())
