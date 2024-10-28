import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import os
import json
from dotenv import load_dotenv
from live_flight_hashmaps import get_flight_details
from iata import get_iata_code, airports


load_dotenv()
apis_key = os.getenv('weather_api')

class TreapNode:
    def __init__(self, key, priority):
        self.key = key
        self.priority = priority
        self.left = None
        self.right = None

class Treap:
    def __init__(self):
        self.root = None

    def rotate_left(self, node):
        y = node.right
        node.right = y.left
        y.left = node
        return y

    def rotate_right(self, node):
        x = node.left
        node.left = x.right
        x.right = node
        return x

    def insert(self, key, priority):
        self.root = self._insert(self.root, key, priority)

    def _insert(self, node, key, priority):
        if node is None:
            return TreapNode(key, priority)

        if key < node.key:
            node.left = self._insert(node.left, key, priority)
            if node.left.priority > node.priority:
                node = self.rotate_right(node)
        else:
            node.right = self._insert(node.right, key, priority)
            if node.right.priority > node.priority:
                node = self.rotate_left(node)

        return node

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right)

    def display(self):
        return self._display(self.root)

    def _display(self, node, level=0):
        if node is not None:
            output = ""
            output += self._display(node.right, level + 1)
            output += "    " * level + f"({node.key}, {node.priority})\n"
            output += self._display(node.left, level + 1)
            return output
        return ""

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")

        # Load locations from JSON file
        self.locations = self.load_locations()

        # Create widgets
        self.create_widgets()

    def load_locations(self):
        try:
            # Load existing locations from the JSON file
            if os.path.exists("locations.json"):
                with open("locations.json", "r") as json_file:
                    content = json_file.read()
                    if content.strip():  # Check if the file is not empty
                        data = json.loads(content)
                        return [f"{loc['arrival']} -> {loc['destination']}" for loc in data.get("locations", [])]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load locations: {e}")
        return []  # Return an empty list if file doesn't exist or is empty

    def create_widgets(self):
        self.location_label = tk.Label(self.root, text="Select location to get weather:")
        self.location_label.pack(pady=10)

        self.combo_box = ttk.Combobox(self.root, values=self.locations, state='readonly')
        self.combo_box.pack(pady=10)

        self.get_weather_button = tk.Button(self.root, text="Get Weather", command=self.get_weather)
        self.get_weather_button.pack(pady=10)

        self.get_flights_button = tk.Button(self.root, text="Get Flights", command=self.get_flights)
        self.get_flights_button.pack(pady=10)

        self.weather_frame = tk.Frame(self.root)
        self.weather_frame.pack(fill=tk.BOTH, expand=True)

        self.weather_canvas = tk.Canvas(self.weather_frame)
        self.weather_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.weather_scrollbar = ttk.Scrollbar(self.weather_frame, orient=tk.VERTICAL, command=self.weather_canvas.yview)
        self.weather_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.weather_canvas.configure(yscrollcommand=self.weather_scrollbar.set)
        self.weather_canvas.bind('<Configure>', lambda e: self.weather_canvas.configure(scrollregion=self.weather_canvas.bbox("all")))

        self.weather_frame_inner = tk.Frame(self.weather_canvas)
        self.weather_canvas.create_window((0, 0), window=self.weather_frame_inner, anchor="nw")

    def show_loading_message(self):
        self.loading_label = tk.Label(self.weather_frame_inner, text="Loading...", justify="center", anchor="center")
        self.loading_label.pack(pady=10)

    def remove_loading_message(self):
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()

    def fetch_and_display_weather(self, location_name):
        self.show_loading_message()  # Show loading message
        api_key = apis_key
        api_endpoint = 'http://api.openweathermap.org/data/2.5/weather'
        url = f"{api_endpoint}?appid={api_key}&q={location_name}&units=metric"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            weather_data = response.json()

            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']

            weather_info = f"Weather in {location_name}:\n" \
                           f"Temperature: {temperature:.2f}°C\n" \
                           f"Humidity: {humidity}%\n" \
                           f"Description: {description}"

            weather_label = tk.Label(self.weather_frame_inner, text=weather_info, justify="center", anchor="center")
            weather_label.pack(pady=10)

            # Center the weather info
            self.weather_frame_inner.update_idletasks()  # Update the layout
            self.weather_canvas.config(scrollregion=self.weather_canvas.bbox("all"))

        except Exception as e:
            self.display_error_message(f"Could not fetch weather for {location_name}: {e}")
        finally:
            self.remove_loading_message()  # Remove loading message

    def display_error_message(self, message):
        error_label = tk.Label(self.weather_frame_inner, text=message, justify="center", anchor="center")
        error_label.pack(pady=10)

    def get_weather(self):
        selected_location = self.combo_box.get()
        if selected_location:
            # Split the selected location into departure and arrival
            locations = selected_location.split(" -> ")
            departure_location = locations[0]
            arrival_location = locations[1] if len(locations) > 1 else None

            # Clear previous weather information
            for widget in self.weather_frame_inner.winfo_children():
                widget.destroy()

            # Get weather for departure location
            self.fetch_and_display_weather(departure_location)

            # Get weather for arrival location if it exists
            if arrival_location:
                self.fetch_and_display_weather(arrival_location)

    def get_flights(self):
        selected_location = self.combo_box.get()
        if selected_location:
            # Split the selected location into arrival and destination
            locations = selected_location.split(" -> ")
            arrival_city = locations[1].strip() if len(locations) > 1 else None
            departure_city = locations[0].strip()
            
            # Get IATA codes for both cities
            departure_iata = get_iata_code(departure_city, airports)
            arrival_iata = get_iata_code(arrival_city, airports) if arrival_city else None

            # Check if IATA codes were found
            if departure_iata == "No matching airports found.":
                messagebox.showwarning("Warning", f"Departure city '{departure_city}' not found.")
                return
            if arrival_iata == "No matching airports found.":
                messagebox.showwarning("Warning", f"Arrival city '{arrival_city}' not found.")
                return

            # Call the flight details function with the IATA codes
            self.weather_frame_inner = tk.Frame(self.weather_frame)  # Ensure the result frame is initialized
            self.weather_frame_inner.pack(pady=10)  # Add padding for better spacing
            get_flight_details(departure_iata, arrival_iata, self.weather_frame_inner)
        else:
            messagebox.showwarning("Warning", "Please select a valid arrival and destination.")

# Ensure the script runs only if it is the main program
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")
    app = WeatherApp(root)
    root.mainloop()
