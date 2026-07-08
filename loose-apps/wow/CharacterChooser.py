import json
import random
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

DATA_FILE = Path("./loose-apps/wow/characters.json")


class CharacterPicker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WoW Character Picker")
        self.resize(700, 500)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Level", "Class"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        self.result_label = QLabel("Press 'Choose Character'")
        self.result_label.setStyleSheet("font-size:18px; font-weight:bold;")

        choose_btn = QPushButton("🎲 Choose Character")
        choose_btn.clicked.connect(self.choose_character)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_character)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_character)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_characters)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.addWidget(choose_btn)
        layout.addWidget(self.result_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_characters()

    def load_characters(self):
        if not DATA_FILE.exists():
            return

        with open(DATA_FILE, "r") as f:
            characters = json.load(f)

        self.table.setRowCount(0)

        for character in characters:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(
                row, 0, QTableWidgetItem(character["name"])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(str(character["level"]))
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(character["class"])
            )

    def save_characters(self):
        characters = []

        for row in range(self.table.rowCount()):
            name = self.get_text(row, 0)
            level = self.get_text(row, 1)
            wow_class = self.get_text(row, 2)

            if not name:
                continue

            try:
                level = int(level)
            except ValueError:
                level = 1

            characters.append(
                {
                    "name": name,
                    "level": level,
                    "class": wow_class,
                }
            )

        with open(DATA_FILE, "w") as f:
            json.dump(characters, f, indent=4)

        QMessageBox.information(self, "Saved", "Characters saved.")

    def choose_character(self):
        characters = []

        for row in range(self.table.rowCount()):
            name = self.get_text(row, 0)
            level = self.get_text(row, 1)
            wow_class = self.get_text(row, 2)

            if name:
                characters.append((name, level, wow_class))

        if not characters:
            QMessageBox.warning(
                self,
                "No Characters",
                "Add at least one character.",
            )
            return

        chosen = random.choice(characters)

        self.result_label.setText(
            f"🎉 {chosen[0]}\n"
            f"Level {chosen[1]} {chosen[2]}"
        )

    def add_character(self):
        self.table.insertRow(self.table.rowCount())

    def remove_character(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def get_text(self, row, col):
        item = self.table.item(row, col)
        return item.text() if item else ""


app = QApplication(sys.argv)

with open("./loose-apps/wow/theme.qss") as f:
    app.setStyleSheet(f.read())



window = CharacterPicker()
window.show()

sys.exit(app.exec())