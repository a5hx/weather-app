from tkinter import *
from tkinter import ttk 
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
        self.treap = Treap()
        for location in self.locations:
            self.treap.insertNode(location) 

    def search_locations(self, prefix):
        return self.treap.searchPrefix(prefix) 

class App:
    def __init__(self, root):
        self.window = root 
        self.window.title("Location Search")

        self.location_graph = LocationGraph()

        self.label = Label(self.window, text="Select a location:")
        self.label.pack()

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
        
        # Hide unnecessary widgets
        self.combo_box.pack_forget()
        self.button.pack_forget()
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
