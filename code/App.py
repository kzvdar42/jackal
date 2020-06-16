import sys
import time
import random

from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPoint, QBasicTimer

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
    def __init__(self, num_of_players, tile_size=64):
        # Init widget.
        super().__init__()
        self.num_of_players = num_of_players
        self.tile_size = tile_size
        self.game_logic = GameLogic(num_of_players, tile_size=tile_size)
        self.map_shape = self.game_logic.get_map_shape()
        self.key_press = ''

        # Init Qt timer.
        self.time = QBasicTimer()

        self.UI()
        self.start()

    def UI(self):
        self.setWindowTitle('Jackal')
        self.setStyleSheet("background-color: rgb(3,102,196)")
        self.update()

        # Resize the widget to fit the game map.
        self.setFixedSize(*self.map_shape)
        self.resize(*self.map_shape)
        self.show()

    def start(self):
        self.time.start(20, self)
        self.repaint()

    def update(self):
        # Force the redrawing of the map on state update.
        self.pixmap = None

    def paintEvent(self, e):
        painter = QPainter(self)
        # Redraw the game map if needed.
        if self.pixmap is None:
            self.pixmap = QPixmap(*self.map_shape)
            self.pixmap.fill(QColor('transparent'))
            pixmap_painter = QPainter(self.pixmap)
            self.game_logic.display_map(pixmap_painter)
        # Draw the game map.
        painter.drawPixmap(0, 0, self.pixmap)
        # Draw possible turns.
        self.game_logic.display_possible_turns(painter)
        # Draw the players.
        self.game_logic.display_players(painter)

    def keyPressEvent(self, e):
        pressed = e.key()
        if pressed == Qt.Key_Escape:
            self.close()
        else:
            self.key_press = pressed

    def mousePressEvent(self, event):
        # If field is changed, update the game map image.
        if self.game_logic.mouse_click((event.x(), event.y())):
            self.update()
        self.repaint()

    def timerEvent(self, e):
        # Move
        if self.key_press in self.__key_to_direction:
            # If field is changed, update the game map image.
            if self.game_logic.move_character(self.__key_to_direction[self.key_press]):
                self.update()
        elif self.key_press == Qt.Key_Return:
            self.game_logic.next_player()
        # Next character.
        elif self.key_press == Qt.Key_Alt:
            self.game_logic.next_character()
        # New game.
        elif self.key_press == Qt.Key_R:
            self.game_logic = GameLogic(self.num_of_players, tile_size=128)
            self.update()
        # If no click, do not refresh.
        else:
            return
        self.key_press = ''
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(4, tile_size=128)
    sys.exit(app.exec_())
