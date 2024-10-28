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

    def addLocations(self, newLocations):
        for location in newLocations:
            self.treap.insertNode(location) 
            self.locations.append(location)

    def searchLocations(self, prefix):
        return self.treap.searchPrefix(prefix)

class App:
    def __init__(self, root):
        self.window = root 
        self.window.title("Location Search")

        self.locationGraph = LocationGraph()

        self.label = Label(self.window, text="Enter locations (comma-separated):")
        self.label.pack()

        self.locationEntry = Entry(self.window, width=50)
        self.locationEntry.pack()

        self.submitButton = Button(self.window, text="Submit Locations", command=self.submitLocations)
        self.submitButton.pack(pady=10)

        self.labelSelect = Label(self.window, text="Select a location:")
        self.labelSelect.pack()

        self.comboBox = ttk.Combobox(self.window, values=self.locationGraph.locations)
        self.comboBox.pack()

        self.button = Button(self.window, text="Search", command=self.handleSearch)
        self.button.pack(pady=10)

        self.resultLabel = Label(self.window, text="")
        self.resultLabel.pack()

        self.yesButton = Button(self.window, text="Yes", command=self.executeWeatherCode)
        self.noButton = Button(self.window, text="No", command=self.displayThankYou)

        self.yesButton.pack_forget()
        self.noButton.pack_forget()

    def submitLocations(self):
        locationsInput = self.locationEntry.get().split(',')
        newLocations = [loc.strip() for loc in locationsInput if loc.strip()]

        self.locationGraph.addLocations(newLocations)

        self.comboBox['values'] = self.locationGraph.locations
        self.locationEntry.delete(0, END)

    def handleSearch(self):
        location = self.comboBox.get()
        self.displayResults(location)

    def displayResults(self, location):
        self.resultLabel.configure(text=f"Do you want to check the weather forecast in {location}?")
        self.yesButton.pack()
        self.noButton.pack()

    def executeWeatherCode(self):
        subprocess.Popen(["python", "weather_treap.py"])
        self.window.quit()

    def displayThankYou(self):
        self.resultLabel.configure(text="Thank you for using the weather app!")
        
        self.comboBox.pack_forget()
        self.button.pack_forget()
        self.yesButton.pack_forget()
        self.noButton.pack_forget()

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()