from tkinter import *
from tkinter import ttk 
import random
import subprocess

class TreapNode:
    def __init__(self, key):
        self.key = key
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

    def insert(self, root, key):
        if root is None:
            return TreapNode(key)

        if key < root.key:
            root.left = self.insert(root.left, key)
            if root.left.priority > root.priority:
                root = self.rotateRight(root) 
        else:
            root.right = self.insert(root.right, key)
            if root.right.priority > root.priority:
                root = self.rotateLeft(root)  

        return root

    def insertNode(self, key):
        self.root = self.insert(self.root, key)

    def search(self, root, prefix):
        if root is None:
            return []

        results = []
        if root.key.startswith(prefix):
            results.append(root.key)

        if prefix < root.key:
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
        for location in new_locations:
            self.treap.insertNode(location) 
            self.locations.append(location)

    def search_locations(self, prefix):
        return self.treap.searchPrefix(prefix)

class App:
    def __init__(self, root):
        self.window = root 
        self.window.title("Location Search")

        self.location_graph = LocationGraph()

        self.label = Label(self.window, text="Enter locations (comma-separated):")
        self.label.pack()

        self.location_entry = Entry(self.window, width=50)
        self.location_entry.pack()

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

    def submit_locations(self):
        locations_input = self.location_entry.get().split(',')
        new_locations = [loc.strip() for loc in locations_input if loc.strip()]

        self.location_graph.add_locations(new_locations)

        self.combo_box['values'] = self.location_graph.locations
        self.location_entry.delete(0, END)

    def handle_search(self):
        location = self.combo_box.get()
        self.display_results(location)

    def display_results(self, location):
        self.result_label.configure(text=f"Do you want to check the weather forecast in {location}?")
        self.yes_button.pack()
        self.no_button.pack()

    def execute_weather_code(self):
        subprocess.Popen(["python", "weather_treap.py"])

    def display_thank_you(self):
        self.result_label.configure(text="Thank you for using the weather app!")
        
        self.combo_box.pack_forget()
        self.button.pack_forget()
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
