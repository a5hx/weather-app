from tkinter import *
import random
import subprocess
import json
import os

class TreapNode:
    def __init__(self, location):
        self.location = location
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
        if root.location.lower().startswith(prefix.lower()):
            results.append(root.location)

        results += self.search(root.left, prefix)
        results += self.search(root.right, prefix)

        return results

    def searchPrefix(self, prefix):
        return self.search(self.root, prefix)

class LocationGraph:
    def __init__(self):
        self.locations = []
        self.treap = Treap()

    def addLocations(self, newLocations):
        combinedLocation = f"{newLocations[0]} -> {newLocations[1]}"
        self.treap.insertNode(combinedLocation)
        self.locations.append(combinedLocation)

    def searchLocations(self, prefix):
        return self.treap.searchPrefix(prefix)

class App:
    def __init__(self, root):
        self.window = root
        self.window.title("Location Search")
        self.window.geometry("600x600")
        self.window.configure(bg="#f0f0f0")

        self.location_graph = LocationGraph()

        self.label_arrival = Label(self.window, text="Enter arrival location:", bg="#f0f0f0")
        self.label_arrival.pack(pady=(20, 5))

        self.arrival_entry = Entry(self.window, width=50)
        self.arrival_entry.pack(pady=(0, 10))

        self.label_destination = Label(self.window, text="Enter destination location:", bg="#f0f0f0")
        self.label_destination.pack(pady=(10, 5))

        self.destination_entry = Entry(self.window, width=50)
        self.destination_entry.pack(pady=(0, 20))

        self.submit_button = Button(self.window, text="Submit Locations", command=self.submitLocations, bg="#4CAF50", fg="white")
        self.submit_button.pack(pady=(10, 20))

        self.label_search = Label(self.window, text="Search locations:", bg="#f0f0f0")
        self.label_search.pack(pady=(10, 5))

        self.search_entry = Entry(self.window, width=50)
        self.search_entry.pack(pady=(0, 5))

        self.search_button = Button(self.window, text="Search", command=self.performSearch, bg="#2196F3", fg="white")
        self.search_button.pack(pady=(5, 20))

        self.result_listbox = Listbox(self.window, width=50)
        self.result_listbox.pack()

        self.result_label = Label(self.window, text="", bg="#f0f0f0")
        self.result_label.pack(pady=(10, 10))

        self.weather_button = Button(self.window, text="Get Weather Info", command=self.openWeatherApp, bg="#2196F3", fg="white")
        self.weather_button.pack(pady=(20, 10))

        self.window.protocol("WM_DELETE_WINDOW", self.clearJson)

    def clearJson(self):
        if os.path.exists("locations.json"):
            open("locations.json", "w").close()
        self.window.destroy()

    def submitLocations(self):
        arrivalLocation = self.arrival_entry.get().strip()
        destinationLocation = self.destination_entry.get().strip()

        if arrivalLocation and destinationLocation:
            newLocations = [arrivalLocation, destinationLocation]
            self.location_graph.addLocations(newLocations)

            # Handling JSON file
            data = {"locations": []}
            if os.path.exists("locations.json"):
                with open("locations.json", "r") as json_file:
                    try:
                        content = json_file.read()
                        if content.strip():
                            data = json.loads(content)
                    except json.JSONDecodeError:
                        print("Error decoding JSON. Initializing with new data.")

            data["locations"].append({"arrival": arrivalLocation, "destination": destinationLocation})

            with open("locations.json", "w") as json_file:
                json.dump(data, json_file)

            self.arrival_entry.delete(0, END)
            self.destination_entry.delete(0, END)

            self.result_label.configure(text=f"Locations added: {newLocations}")

    def performSearch(self):
        prefix = self.search_entry.get()
        results = self.location_graph.searchLocations(prefix)

        self.result_listbox.delete(0, END)

        if results:
            for result in results:
                self.result_listbox.insert(END, result)
        else:
            self.result_label.configure(text="No locations found.")
        
        if results:
            self.result_listbox.pack()
        else:
            self.result_listbox.place_forget()

    def openWeatherApp(self):
        subprocess.Popen(["python", "weather_treap.py"])

root = Tk()
app = App(root)
root.mainloop()
