import tkinter as tk
from tkinter import ttk
import os


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._get_words_from_node(node)

    def _get_words_from_node(self, node):
        words = []
        if node.is_end_of_word:
            words.append("")
        for char, child_node in node.children.items():
            suffixes = self._get_words_from_node(child_node)
            for suffix in suffixes:
                words.append(char + suffix)
        return words


class LocationGraph:
    def __init__(self):
        self.locations = [
            "Mumbai to Dubai", "Mumbai to Bali", "Mumbai to Zurich",
            "Delhi to Dubai", "Delhi to Bali", "Delhi to Zurich",
            "Bangalore to Dubai", "Bangalore to Bali",
            "Kolkata to Paris", "Kolkata to Rome", "Kolkata to Tokyo",
            "Auckland to Kuala Lumpur", "Chennai to Paris",
            "Chennai to Rome", "Chennai to Tokyo", "Hyderabad to Paris",
            "Hyderabad to Rome", "Hyderabad to Tokyo", "Jaipur to Paris",
            "Jaipur to Rome", "Jaipur to Tokyo", "Ahmedabad to Paris",
            "Ahmedabad to Rome", "Ahmedabad to Tokyo", "Pune to Paris",
            "Pune to Rome", "Pune to Tokyo"
        ]
        self.trie = Trie()
        for location in self.locations:
            self.trie.insert(location)

    def search_locations(self, prefix):
        return self.trie.search(prefix)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Location Search")
        
        # Initialize LocationGraph once
        self.location_graph = LocationGraph()

        self.label = tk.Label(root, text="Select a location:")
        self.label.pack()

        self.combo_box = ttk.Combobox(root, values=self.location_graph.locations)
        self.combo_box.pack()

        self.button = tk.Button(root, text="Search", command=self.handle_search)
        self.button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

        self.yes_button = tk.Button(root, text="Yes", command=self.execute_weather_code)
        self.no_button = tk.Button(root, text="No", command=self.display_thank_you)
        
        # Initially hide Yes and No buttons
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

    def handle_search(self):
        location = self.combo_box.get()
        self.display_results(location)

    def display_results(self, location):
        self.result_label.configure(text=f"Do you want to check the weather forecast in {location}?")
        self.yes_button.pack()
        self.no_button.pack()

    def execute_weather_code(self):
        # Using subprocess to avoid closing the current Tkinter window
        import subprocess
        subprocess.Popen(["python", "weather_treap.py"])
        # Optionally, you could also keep the current window open
        self.root.withdraw()  # Hide current window

    def display_thank_you(self):
        self.result_label.configure(text="Thank you for using the weather app!")
        
        # Hide unnecessary widgets
        self.combo_box.pack_forget()
        self.button.pack_forget()
        self.yes_button.pack_forget()
        self.no_button.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
