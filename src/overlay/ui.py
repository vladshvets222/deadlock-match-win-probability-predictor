from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar
)

from PySide6.QtCore import Qt

import styles


class PredictionWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
        QWidget {{
            background-color: {styles.BACKGROUND};
            border-radius: {styles.RADIUS}px;
        }}

        QLabel {{
            color: white;
        }}

        QProgressBar {{
            border: none;
            background: #333333;
            border-radius: 8px;
            text-align:center;
            height:18px;
        }}

        QProgressBar::chunk {{
            background-color: #3cc96b;
            border-radius:8px;
        }}
        """)



        self.title = QLabel("DEADLOCK OVERLAY")
        self.title.setAlignment(Qt.AlignCenter)


        self.arch_label = QLabel("Archmother")
        self.hidden_label = QLabel("Hidden King")


        names = QHBoxLayout()
        names.addWidget(self.hidden_label)
        names.addStretch()
        names.addWidget(self.arch_label)


        self.bar = QProgressBar()
        self.bar.setRange(0,100)


        self.arch_prob = QLabel("50.0 %")
        self.hidden_prob = QLabel("50.0 %")

        probs = QHBoxLayout()

        probs.addWidget(self.arch_prob)
        probs.addStretch()
        probs.addWidget(self.hidden_prob)


        self.info = QLabel("")
        self.info.setAlignment(Qt.AlignCenter)


        self.title.setStyleSheet("""
        font-size:22px;
        font-weight:bold;
        color:white;
        """)


        self.arch_label.setStyleSheet("""
        font-size:16px;
        font-weight:bold;
        color:white;
        """)

        self.hidden_label.setStyleSheet("""
        font-size:16px;
        font-weight:bold;
        color:white;
        """)

        self.arch_prob.setStyleSheet("""
        font-size:28px;
        font-weight:bold;
        color:#45d86c;
        """)

        self.hidden_prob.setStyleSheet("""
        font-size:28px;
        font-weight:bold;
        color:#ff6666;
        """)

        self.info.setStyleSheet("""
        font-size:14px;
        color:#BBBBBB;
        """)        

        layout = QVBoxLayout()

        layout.addWidget(self.title)

        layout.setContentsMargins(20,20,20,20)

        layout.setSpacing(12)

        layout.addLayout(names)

        layout.addWidget(self.bar)

        layout.addLayout(probs)

        layout.addSpacing(10)

        layout.addWidget(self.info)

        self.setLayout(layout)

        self.current_probability = 50.0

    def update_prediction(self, data):

        target = data["probability"] * 100

        self.current_probability += (
            target - self.current_probability
        )

        arch = self.current_probability

        hidden = 100 - arch

        self.bar.setValue(int(arch))

        self.arch_prob.setText(f"{arch:.1f}%")
        self.hidden_prob.setText(f"{hidden:.1f}%")


        self.info.setText(
            f"Time: {data['minute']} min  Model: {data['model']}"
        )