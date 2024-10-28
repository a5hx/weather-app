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

class LocationGraph:
    def __init__(self):
        self.locations = []
        self.treap = Treap()

    def add_locations(self, new_locations):
        combined_location = f"{new_locations[0]} -> {new_locations[1]}"
        self.treap.insertNode(combined_location)
        self.locations.append(combined_location)

    def search_locations(self, prefix):
        return self.treap.searchPrefix(prefix)

class App:
    def __init__(self, root):
        self.window = root
        self.window.title("Location Search")

        self.location_graph = LocationGraph()

        # Labels and entries for arrival and destination locations
        self.label_arrival = Label(self.window, text="Enter arrival location:")
        self.label_arrival.pack()

        self.arrival_entry = Entry(self.window, width=50)
        self.arrival_entry.pack()

        self.label_destination = Label(self.window, text="Enter destination location:")
        self.label_destination.pack()

        self.destination_entry = Entry(self.window, width=50)
        self.destination_entry.pack()

        self.submit_button = Button(self.window, text="Submit Locations", command=self.submit_locations)
        self.submit_button.pack(pady=10)

        self.label_select = Label(self.window, text="Select a location:")
        self.label_select.pack()

        self.combo_box = ttk.Combobox(self.window, values=self.location_graph.locations)
        self.combo_box.pack()
        self.combo_box.bind("<<ComboboxSelected>>", self.handle_selection)  # Auto-trigger display on selection

        self.result_label = Label(self.window, text="")
        self.result_label.pack()

        # Button to open weather app
        self.weather_button = Button(self.window, text="Get Weather Info", command=self.open_weather_app)
        self.weather_button.pack(pady=10)

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

            self.combo_box['values'] = self.location_graph.locations
            self.arrival_entry.delete(0, END)
            self.destination_entry.delete(0, END)

    def handle_selection(self, event):
        location = self.combo_box.get()
        self.display_results(location)

    def display_results(self, location):
        self.result_label.configure(text=f"Opening weather forecast for {location}...")
        self.open_weather_app()

    def open_weather_app(self):
        subprocess.Popen(["python", "weather_treap.py"])  # Open the weather_treap.py

root = Tk()
app = App(root)
root.mainloop()
