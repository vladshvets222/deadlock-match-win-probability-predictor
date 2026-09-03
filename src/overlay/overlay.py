import sys
import os

import styles

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication

from prediction import PredictionManager
from ui import PredictionWidget



if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable) # Running as compiled exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Running as py file


PREDICTION_FILE = os.path.join(BASE_DIR, "predictor", "shared", "prediction.json")

app = QApplication(sys.argv)
manager = PredictionManager(PREDICTION_FILE)
widget = PredictionWidget()

widget.resize(styles.WINDOW_WIDTH, styles.WINDOW_HEIGHT)

#Make overlya transparent

widget.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
widget.setAttribute(Qt.WA_TranslucentBackground)
widget.setAttribute(Qt.WA_TransparentForMouseEvents)

#Position

screen = QGuiApplication.primaryScreen()
geometry = screen.geometry()
margin = 7
x = geometry.right() - widget.width() - margin
y = geometry.top() + margin
widget.show()
widget.move(x, y)

#update

def refresh():
    data = manager.get_prediction()
    if data is None:
        return
    widget.update_prediction(data)


timer = QTimer()
timer.timeout.connect(refresh)
timer.start(300)


sys.exit(app.exec())