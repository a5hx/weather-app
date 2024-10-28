from tkinter import *
from tkinter import ttk
import random
import subprocess
import json  # Import json to save locations
import os  # Import os to handle file operations

class TreapNode:
    def __init__(self, location):
        self.location = location  # Store combined location
        self.priority = random.randint(1, 100)
        self.left = None
        self.right = None

class Treap:
    def __init__(self):
        self.root = None

    def rotateRight(self, root):
        leftChild = root.left
        root.left = leftChild.right
        leftChild.right = root
        return leftChild

    def rotateLeft(self, root):
        rightChild = root.right
        root.right = rightChild.left
        rightChild.left = root
        return rightChild

    def insert(self, root, location):
        if root is None:
            return TreapNode(location)

        if location < root.location:
            root.left = self.insert(root.left, location)
            if root.left.priority > root.priority:
                root = self.rotateRight(root)
        else:
            root.right = self.insert(root.right, location)
            if root.right.priority > root.priority:
                root = self.rotateLeft(root)

        return root

    def insertNode(self, location):
        self.root = self.insert(self.root, location)

    def search(self, root, prefix):
        if root is None:
            return []

        results = []
        if root.location.startswith(prefix):
            results.append(root.location)

        if prefix < root.location:
            results += self.search(root.left, prefix)
        else:
            results += self.search(root.right, prefix)

        return results

    def searchPrefix(self, prefix):
        return self.search(self.root, prefix)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True

    def search(self, prefix):
        current = self.root
        for char in prefix:
            if char not in current.children:
                return []
            current = current.children[char]
        return self._find_words(current, prefix)

    def _find_words(self, node, prefix):
        words = []
        if node.is_end_of_word:
            words.append(prefix)

        for char, child in node.children.items():
            words += self._find_words(child, prefix + char)

        return words

class LocationGraph:
    def __init__(self):
        self.locations = []
        self.treap = Treap()
        self.trie = Trie()

    def add_locations(self, new_locations):
        combined_location = f"{new_locations[0]} -> {new_locations[1]}"
        self.treap.insertNode(combined_location)
        self.trie.insert(combined_location)
        self.locations.append(combined_location)

    def search_locations(self, prefix):
        return self.treap.searchPrefix(prefix)

    def autocomplete(self, prefix):
        return self.trie.search(prefix)

class App:
    def __init__(self, root):
        self.window = root
        self.window.title("Location Search")
        self.window.geometry("400x400")  # Set window size
        self.window.configure(bg="#f0f0f0")  # Set background color

        self.location_graph = LocationGraph()

        # Labels and entries for arrival and destination locations
        self.label_arrival = Label(self.window, text="Enter arrival location:", bg="#f0f0f0")
        self.label_arrival.pack(pady=(20, 5))

        self.arrival_entry = Entry(self.window, width=50)
        self.arrival_entry.pack(pady=(0, 10))

        self.label_destination = Label(self.window, text="Enter destination location:", bg="#f0f0f0")
        self.label_destination.pack(pady=(10, 5))

        self.destination_entry = Entry(self.window, width=50)
        self.destination_entry.pack(pady=(0, 20))

        self.submit_button = Button(self.window, text="Submit Locations", command=self.submit_locations, bg="#4CAF50", fg="white")
        self.submit_button.pack(pady=(10, 20))

        # Search field for location autocomplete
        self.label_search = Label(self.window, text="Search locations:", bg="#f0f0f0")
        self.label_search.pack(pady=(10, 5))

        self.search_entry = Entry(self.window, width=50)
        self.search_entry.pack(pady=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search)  # Trigger autocomplete on key release

        self.autocomplete_listbox = Listbox(self.window, width=50)
        self.autocomplete_listbox.pack()

        self.result_label = Label(self.window, text="", bg="#f0f0f0")
        self.result_label.pack(pady=(10, 10))

        # Button to open weather app
        self.weather_button = Button(self.window, text="Get Weather Info", command=self.open_weather_app, bg="#2196F3", fg="white")
        self.weather_button.pack(pady=(20, 10))

        # Bind the close window protocol to the clear_json method
        self.window.protocol("WM_DELETE_WINDOW", self.clear_json)

    def clear_json(self):
        # Clear the contents of locations.json
        if os.path.exists("locations.json"):
            open("locations.json", "w").close()  # Clear the file
        self.window.destroy()  # Close the window

    def submit_locations(self):
        arrival_location = self.arrival_entry.get().strip()
        destination_location = self.destination_entry.get().strip()

        if arrival_location and destination_location:
            new_locations = [arrival_location, destination_location]
            self.location_graph.add_locations(new_locations)

            # Load existing locations from the JSON file
            try:
                with open("locations.json", "r") as json_file:
                    content = json_file.read()
                    if not content.strip():  # Check if the file is empty
                        print("JSON file is empty. Initializing with new data.")
                        data = {"locations": []}
                    else:
                        data = json.loads(content)  # Try loading the JSON data

                    if "locations" not in data:
                        data["locations"] = []
                    data["locations"].append({"arrival": arrival_location, "destination": destination_location})

            except FileNotFoundError:
                print("File not found. Creating a new JSON file.")
                data = {"locations": [{"arrival": arrival_location, "destination": destination_location}]}
            except json.JSONDecodeError:
                print("Error decoding JSON. Initializing with new data.")
                data = {"locations": [{"arrival": arrival_location, "destination": destination_location}]}
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return

            # Save locations to a JSON file
            with open("locations.json", "w") as json_file:
                json.dump(data, json_file)

            self.arrival_entry.delete(0, END)
            self.destination_entry.delete(0, END)

            self.result_label.configure(text=f"Locations added: {new_locations}")

    def on_search(self, event):
        prefix = self.search_entry.get()
        suggestions = self.location_graph.autocomplete(prefix)

        # Clear previous suggestions
        self.autocomplete_listbox.delete(0, END)

        # Add new suggestions
        for suggestion in suggestions:
            self.autocomplete_listbox.insert(END, suggestion)

        if suggestions:
            self.autocomplete_listbox.place(x=20, y=self.search_entry.winfo_y() + 25)
        else:
            self.autocomplete_listbox.place_forget()

    def open_weather_app(self):
        subprocess.Popen(["python", "weather_treap.py"])  # Open the weather_treap.py

root = Tk()
app = App(root)
root.mainloop()
