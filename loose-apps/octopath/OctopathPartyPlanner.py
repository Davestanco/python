import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QLineEdit, QListWidgetItem,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt


# -----------------------------
# Data Models
# -----------------------------
class Skill:
    def __init__(self, name, hits):
        self.name = name
        self.hits = hits

    def to_dict(self):
        return {"name": self.name, "hits": self.hits}

    @staticmethod
    def from_dict(data):
        return Skill(data["name"], data["hits"])


class Character:
    def __init__(self, name):
        self.name = name
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def remove_skill(self, index):
        if 0 <= index < len(self.skills):
            del self.skills[index]

    def to_dict(self):
        return {
            "name": self.name,
            "skills": [s.to_dict() for s in self.skills]
        }

    @staticmethod
    def from_dict(data):
        c = Character(data["name"])
        for s in data["skills"]:
            c.add_skill(Skill.from_dict(s))
        return c


# -----------------------------
# Main App
# -----------------------------
class PartyPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Octopath Traveler Party Planner")

        self.characters = {}
        self.party = []

        self.init_ui()

    # ---------------- UI ----------------
    def init_ui(self):
        layout = QHBoxLayout()

        # LEFT: available + add character
        left = QVBoxLayout()

        self.char_list = QListWidget()
        self.char_list.itemClicked.connect(self.select_character)

        self.new_char_input = QLineEdit()
        self.new_char_input.setPlaceholderText("New character name")

        add_char_btn = QPushButton("Add Character")
        add_char_btn.clicked.connect(self.add_character)

        remove_char_btn = QPushButton("Remove Character")
        remove_char_btn.clicked.connect(self.remove_character)

        left.addWidget(QLabel("Characters"))
        left.addWidget(self.char_list)
        left.addWidget(self.new_char_input)
        left.addWidget(add_char_btn)
        left.addWidget(remove_char_btn)

        # CENTER: party
        center = QVBoxLayout()

        self.party_list = QListWidget()

        add_to_party_btn = QPushButton("Add to Party →")
        add_to_party_btn.clicked.connect(self.add_selected_to_party)

        remove_from_party_btn = QPushButton("Remove from Party")
        remove_from_party_btn.clicked.connect(self.remove_from_party)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load)

        center.addWidget(QLabel("Party"))
        center.addWidget(self.party_list)
        center.addWidget(add_to_party_btn)
        center.addWidget(remove_from_party_btn)
        center.addWidget(save_btn)
        center.addWidget(load_btn)

        # RIGHT: skills
        right = QVBoxLayout()

        self.selected_label = QLabel("No character selected")
        self.skill_list = QListWidget()
        self.skill_list.itemClicked.connect(self.prepare_edit_skill)

        self.skill_name = QLineEdit()
        self.skill_name.setPlaceholderText("Skill name")

        self.hit_input = QSpinBox()
        self.hit_input.setRange(1, 10)

        add_skill_btn = QPushButton("Add / Update Skill")
        add_skill_btn.clicked.connect(self.add_or_update_skill)

        delete_skill_btn = QPushButton("Delete Skill")
        delete_skill_btn.clicked.connect(self.delete_skill)

        self.overview = QLabel("Skill Overview")

        right.addWidget(self.selected_label)
        right.addWidget(self.skill_list)
        right.addWidget(self.skill_name)
        right.addWidget(self.hit_input)
        right.addWidget(add_skill_btn)
        right.addWidget(delete_skill_btn)
        right.addWidget(self.overview)

        layout.addLayout(left)
        layout.addLayout(center)
        layout.addLayout(right)

        self.setLayout(layout)

        # demo data
        self.add_character("Warrior")
        self.add_character("Mage")

    # ---------------- Characters ----------------
    def add_character(self, name=None):
        if not name:
            name = self.new_char_input.text().strip()

        if not name:
            return

        if name in self.characters:
            return

        self.characters[name] = Character(name)
        self.char_list.addItem(name)
        self.new_char_input.clear()

    def remove_character(self):
        item = self.char_list.currentItem()
        if not item:
            return

        name = item.text()
        del self.characters[name]

        self.char_list.takeItem(self.char_list.row(item))

        if name in self.party:
            self.party.remove(name)
            self.refresh_party()

        self.update_overview()

    # ---------------- Party ----------------
    def add_selected_to_party(self):
        item = self.char_list.currentItem()
        if not item:
            return

        name = item.text()
        if name not in self.party:
            self.party.append(name)

        self.refresh_party()
        self.update_overview()

    def remove_from_party(self):
        item = self.party_list.currentItem()
        if not item:
            return

        name = item.text()
        self.party.remove(name)
        self.refresh_party()
        self.update_overview()

    def refresh_party(self):
        self.party_list.clear()
        self.party_list.addItems(self.party)

    # ---------------- Skills ----------------
    def select_character(self, item):
        name = item.text()
        self.current_character = name

        self.selected_label.setText(name)
        self.refresh_skills()

    def refresh_skills(self):
        self.skill_list.clear()
        char = self.characters.get(self.current_character)
        if not char:
            return

        for i, s in enumerate(char.skills):
            self.skill_list.addItem(f"{i}: {s.name} ({s.hits} hits)")

    def prepare_edit_skill(self, item):
        idx = int(item.text().split(":")[0])
        char = self.characters[self.current_character]
        skill = char.skills[idx]

        self.skill_name.setText(skill.name)
        self.hit_input.setValue(skill.hits)

    def add_or_update_skill(self):
        if not hasattr(self, "current_character"):
            return

        name = self.skill_name.text().strip()
        hits = self.hit_input.value()

        if not name:
            return

        char = self.characters[self.current_character]
        char.add_skill(Skill(name, hits))
        # update if exists
        # for s in char.skills:
        #     if s.name == name:
        #         s.hits = hits
        #         break
        # else:
        #     char.add_skill(Skill(name, hits))

        self.refresh_skills()
        self.update_overview()

    def delete_skill(self):
        if not hasattr(self, "current_character"):
            return

        item = self.skill_list.currentItem()
        if not item:
            return

        idx = int(item.text().split(":")[0])
        self.characters[self.current_character].remove_skill(idx)

        self.refresh_skills()
        self.update_overview()

    # ---------------- Overview ----------------
    def update_overview(self):
        skill_data = {}
    
        # Build grouped structure
        for name in self.party:
            char = self.characters[name]
    
            for skill in char.skills:
                if skill.name not in skill_data:
                    skill_data[skill.name] = {
                        "entries": [],   # (character, hits)
                        "total_hits": 0
                    }
    
                skill_data[skill.name]["entries"].append((name, skill.hits))
                skill_data[skill.name]["total_hits"] += skill.hits
    
        # Build display
        text = "Skill Overview (grouped + hit breakdown):\n\n"
    
        for skill_name, data in sorted(skill_data.items()):
            entries = data["entries"]
            total_hits = data["total_hits"]
            users = len(entries)
    
            text += f"{skill_name}:\n"
    
            # per-character breakdown
            for char_name, hits in entries:
                text += f"  {char_name}: {hits} hit(s)\n"
    
            text += f"  Users: {users}\n"
            text += f"  Total Hits: {total_hits}\n\n"
    
        self.overview.setText(text)

    # ---------------- Save / Load ----------------
    def save(self):
        data = {
            "characters": {n: c.to_dict() for n, c in self.characters.items()},
            "party": self.party
        }

        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON (*.json)")
        if not path:
            return

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load File", "", "JSON (*.json)")
        if not path:
            return

        with open(path, "r") as f:
            data = json.load(f)

        self.characters = {
            n: Character.from_dict(c) for n, c in data["characters"].items()
        }
        self.party = data["party"]

        self.char_list.clear()
        self.char_list.addItems(self.characters.keys())

        self.refresh_party()
        self.update_overview()


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PartyPlanner()
    window.resize(1000, 500)
    window.show()
    sys.exit(app.exec())