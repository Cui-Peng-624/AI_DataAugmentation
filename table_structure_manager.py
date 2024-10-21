# table_structure_manager.py
import json
import os

class TableStructureManager:
    def __init__(self, json_file='table_structures.json'):
        self.json_file = json_file
        self.structures = self.load_structures()

    def load_structures(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_structures(self):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.structures, f, ensure_ascii=False, indent=2)

    def get_column_description(self, main_category, sub_category, column_name):
        return self.structures.get(main_category, {}).get(sub_category, {}).get(column_name, "No description available")

    def add_or_update_columns(self, main_category, sub_category, columns_dict):
        if main_category not in self.structures:
            self.structures[main_category] = {}
        if sub_category not in self.structures[main_category]:
            self.structures[main_category][sub_category] = {}
        
        self.structures[main_category][sub_category].update(columns_dict)
        self.save_structures()

    def get_all_columns(self, main_category, sub_category):
        return self.structures.get(main_category, {}).get(sub_category, {})