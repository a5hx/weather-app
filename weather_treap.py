import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import io
import random
import os
from dotenv import load_dotenv


load_dotenv()
apis_key = os.getenv('weather_api')



class Treapnode:  # Fixed class name to Treapnode
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
            return Treapnode(key, priority)  # Use correct class name here

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
        self.locations = []
        self.is_dark_mode = tk.BooleanVar()
        self.create_widgets()

    def create_widgets(self):
        self.num_locations_label = tk.Label(self.root, text="Enter the number of locations you want to add:")
        self.num_locations_label.pack()

        self.num_locations_entry = tk.Entry(self.root)
        self.num_locations_entry.pack()

        self.location_label = tk.Label(self.root, text="Enter a location:")
        self.location_label.pack()

        self.location_entry = tk.Entry(self.root)
        self.location_entry.pack()

        self.add_location_button = tk.Button(self.root, text="Add Location", command=self.add_location)
        self.add_location_button.pack()

        self.get_weather_button = tk.Button(self.root, text="Get Weather", command=self.get_weather)
        self.get_weather_button.pack()

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

        self.weather_canvas.bind_all("<MouseWheel>", lambda e: self.weather_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.treap_label = tk.Label(self.root, text="")
        self.treap_label.pack()

        self.mode_checkbutton = ttk.Checkbutton(self.root, text="Dark Mode", variable=self.is_dark_mode, command=self.toggle_mode)
        self.mode_checkbutton.pack()

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack()

        self.book_flight_label = tk.Label(self.root, text="Do you want to see the flight details?")
        self.book_flight_label.pack()

        self.yes_button = tk.Button(self.root, text="Yes", command=self.book_flight)
        self.yes_button.pack()

        self.no_button = tk.Button(self.root, text="No", command=self.display_thank_you)
        self.no_button.pack()

    def add_location(self):
        location = self.location_entry.get()
        if location:  # Check if the location entry is not empty
            self.locations.append(location)
            self.location_entry.delete(0, tk.END)
            print(f"Added location: {location}")  # Debugging info
        else:
            print("Location entry is empty.")  # Debugging info

    def get_weather(self):
        api_key = apis_key  # Replace with your API key securely
        api_endpoint = 'http://api.openweathermap.org/data/2.5/weather'
        treap = Treap()

        for location in self.locations:
            priority = random.randint(1, 100)

            url = f"{api_endpoint}?appid={api_key}&q={location}"

            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()
                temperature = weather_data['main']['temp']
                temperature_celsius = temperature - 273.15
                humidity = weather_data['main']['humidity']
                description = weather_data['weather'][0]['description']

                weather_info = f"Weather in {location}:\n" \
                               f"Temperature: {temperature_celsius:.2f}°C\n" \
                               f"Humidity: {humidity}%\n" \
                               f"Description: {description}"

                # Add weather advisories
                if temperature_celsius > 35 and "sun" in description.lower():
                    weather_info += "\nIt's sunny and the temperature is high. Make sure to put on sunscreen and wear loose, comfortable cotton clothes before leaving your home."
                if "cloud" in description.lower() or "rain" in description.lower():
                    weather_info += "\nIt's cloudy or rainy. Remember to bring an umbrella with you."
                if temperature_celsius < 20:
                    weather_info += "\nThe temperature is less than 20°C. Come prepared in proper winter clothes of your choice."
                if temperature_celsius > 45:
                    weather_info += "\nThe temperature is very high. It's advised to stay in indoor environments and drink plenty of water to avoid heatstroke."
                if "snow" in description.lower():
                    weather_info += "\nIt's snowy. Make sure to wear snow boots and appropriate clothes to protect yourself."

                treap.insert(location, priority)

                weather_label = tk.Label(self.weather_frame_inner, text=weather_info)
                weather_label.pack()

                # Load image
                image_url = f"http://source.unsplash.com/500x300/?{location.replace(' ', '+')}"
                image_data = requests.get(image_url)
                if image_data.status_code == 200:
                    image = Image.open(io.BytesIO(image_data.content))
                    image = image.resize((500, 300), Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(image)
                    image_label = tk.Label(self.weather_frame_inner, image=photo)
                    image_label.image = photo
                    image_label.pack()
                else:
                    image_not_found_label = tk.Label(self.weather_frame_inner, text="Image not found")
                    image_not_found_label.pack()
            else:
                error_label = tk.Label(self.weather_frame_inner, text=f"Could not fetch weather for {location}. Please check the name and try again.")
                error_label.pack()

        treap_output = "Treap:\n" + treap.display()
        self.treap_label.config(text=treap_output)

    def toggle_mode(self):
        is_dark_mode = self.is_dark_mode.get()
        if is_dark_mode:
            self.root.configure(bg="#1e1e1e")
            self.weather_frame_inner.configure(bg="#1e1e1e")
            self.treap_label.configure(bg="#1e1e1e", fg="white")
            self.mode_checkbutton.configure(style="DarkMode.TCheckbutton")
        else:
            self.root.configure(bg="white")
            self.weather_frame_inner.configure(bg="white")
            self.treap_label.configure(bg="white", fg="black")
            self.mode_checkbutton.configure(style="LightMode.TCheckbutton")

    def book_flight(self):
        import subprocess
        subprocess.Popen(["python", "live_flight_hashmaps.py"])
        self.root.withdraw()

    def display_thank_you(self):
        thank_you_label = tk.Label(self.root, text="Thank you for using our Weather App!")
        thank_you_label.pack()

root = tk.Tk()
root.geometry("600x600")

style = ttk.Style()
style.configure("DarkMode.TCheckbutton", background="#1e1e1e", foreground="white")
style.configure("LightMode.TCheckbutton", background="white", foreground="black")

app = WeatherApp(root)
root.mainloop()
