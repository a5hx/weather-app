from tkinter import *
from tkinter import ttk
import random
import subprocess
import json  # Import json to save locations

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
        
        # Check for duplicates before adding
        if combined_location not in self.locations:
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

        self.button = Button(self.window, text="Search", command=self.handle_search)
        self.button.pack(pady=10)

        self.result_label = Label(self.window, text="")
        self.result_label.pack()

        self.yes_button = Button(self.window, text="Yes", command=self.execute_weather_code)
        self.no_button = Button(self.window, text="No", command=self.display_thank_you)

        self.yes_button.pack_forget()
        self.no_button.pack_forget()

        # Override the window close protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def submit_locations(self):
        arrival_location = self.arrival_entry.get().strip()
        destination_location = self.destination_entry.get().strip()

        if arrival_location and destination_location:
            new_locations = [arrival_location, destination_location]
            combined_location = f"{arrival_location} -> {destination_location}"

            # Load existing locations from the JSON file
            try:
                with open("locations.json", "r") as json_file:
                    if json_file.readable():
                        json_file.seek(0)  # Reset file pointer to the start
                        content = json_file.read().strip()
                        if content:  # Check if file is not empty
                            data = json.loads(content)
                        else:
                            data = {"locations": []}
                    else:
                        data = {"locations": []}
            except FileNotFoundError:
                data = {"locations": []}
            except json.JSONDecodeError:
                # Handle the case where JSON is invalid
                print("Invalid JSON file. Resetting to empty.")
                data = {"locations": []}

            # Check for duplicates in JSON
            if {"arrival": arrival_location, "destination": destination_location} not in data["locations"]:
                # Add to JSON if it's a new entry
                data["locations"].append({"arrival": arrival_location, "destination": destination_location})
                # Save to the JSON file
                with open("locations.json", "w") as json_file:
                    json.dump(data, json_file)

            # Add locations to the treap
            if combined_location not in self.location_graph.locations:
                self.location_graph.add_locations(new_locations)

            self.combo_box['values'] = self.location_graph.locations
            self.arrival_entry.delete(0, END)
            self.destination_entry.delete(0, END)

    def handle_search(self):
        location = self.combo_box.get()
        if location:
            self.display_results(location)
        else:
            self.result_label.configure(text="Please select a location.")

    def display_results(self, location):
        self.result_label.configure(text=f"Do you want to check the weather forecast in {location}?")
        self.yes_button.pack()
        self.no_button.pack()

    def execute_weather_code(self):
        try:
            subprocess.Popen(["python", "live_flight_hashmaps.py"])  # Change to your flight details file
        except Exception as e:
            print(f"Error executing weather code: {e}")

    def display_thank_you(self):
        self.result_label.configure(text="Thank you for using the weather app!")
        
        self.combo_box.pack_forget()
        self.button.pack_forget()
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

    def on_closing(self):
        # Clear the contents of the JSON file
        with open("locations.json", "w") as json_file:
            json.dump({"locations": []}, json_file)  # Resetting the locations list
        self.window.destroy()  # Close the window

root = Tk()
app = App(root)
root.mainloop()
