import json
import os


class MemoryAgent:

    def __init__(self):
        self.file = "data/sai_memory.json"

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.file):
            self._save({
                "profile": {},
                "goals": [],
                "facts": []
            })

    def _load(self):
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_memory(self):
        return self._load()

    def add_goal(self, goal):
        data = self._load()

        if goal not in data["goals"]:
            data["goals"].append(goal)

        self._save(data)

    def add_fact(self, fact):
        data = self._load()

        if fact not in data["facts"]:
            data["facts"].append(fact)

        self._save(data)

    def set_profile(self, key, value):
        data = self._load()

        data["profile"][key] = value

        self._save(data)