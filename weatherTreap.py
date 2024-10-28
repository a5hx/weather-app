from tkinter import *
from tkinter import ttk 
import requests
import random
import os
from dotenv import load_dotenv
from travelTreap import Treap

load_dotenv()
api_key = os.getenv('weather_api')

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.locations = []
        self.create_widgets()

    def create_widgets(self):
        self.num_locations_label = Label(self.root, text="Enter the number of locations you want to add:")
        self.num_locations_label.pack()

        self.num_locations_entry = Entry(self.root)
        self.num_locations_entry.pack()

        self.location_label = Label(self.root, text="Enter a location:")
        self.location_label.pack()

        self.location_entry = Entry(self.root)
        self.location_entry.pack()

        self.add_location_button = Button(self.root, text="Add Location", command=self.add_location)
        self.add_location_button.pack()

        self.get_weather_button = Button(self.root, text="Get Weather", command=self.get_weather)
        self.get_weather_button.pack()

        self.weather_frame = Frame(self.root)
        self.weather_frame.pack(fill=BOTH, expand=True)

        self.weather_canvas = Canvas(self.weather_frame)
        self.weather_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.weather_scrollbar = ttk.Scrollbar(self.weather_frame, orient=VERTICAL, command=self.weather_canvas.yview)
        self.weather_scrollbar.pack(side=RIGHT, fill=Y)

        self.weather_canvas.configure(yscrollcommand=self.weather_scrollbar.set)
        self.weather_canvas.bind('<Configure>', lambda e: self.weather_canvas.configure(scrollregion=self.weather_canvas.bbox("all")))

        self.weather_frame_inner = Frame(self.weather_canvas)
        self.weather_canvas.create_window((0, 0), window=self.weather_frame_inner, anchor="nw")

        self.weather_canvas.bind_all("<MouseWheel>", lambda e: self.weather_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.treap_label = Label(self.root, text="")
        self.treap_label.pack()

        self.exit_button = Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack()

        self.book_flight_label = Label(self.root, text="Do you want to see the flight details?")
        self.book_flight_label.pack()

        self.yes_button = Button(self.root, text="Yes", command=self.book_flight)
        self.yes_button.pack()

        self.no_button = Button(self.root, text="No", command=self.display_thank_you)
        self.no_button.pack()

    def add_location(self):
        location = self.location_entry.get()
        if location:
            self.locations.append(location)
            self.location_entry.delete(0, END)

    def get_weather(self):
        api_endpoint = 'http://api.openweathermap.org/data/2.5/weather'
        treap = Treap()

        for location in self.locations:
            priority = random.randint(1, 100)
            url = f"{api_endpoint}?appid={api_key}&q={location}"

            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()
                temperature = weather_data['main']['temp'] - 273.15
                humidity = weather_data['main']['humidity']
                description = weather_data['weather'][0]['description']

                weather_info = f"Weather in {location}:\n" \
                               f"Temperature: {temperature:.2f}°C\n" \
                               f"Humidity: {humidity}%\n" \
                               f"Description: {description}"

                treap.insert(location, priority)

                weather_label = Label(self.weather_frame_inner, text=weather_info)
                weather_label.pack()
            else:
                error_label = Label(self.weather_frame_inner, text=f"Could not fetch weather for {location}. Please check the name and try again.")
                error_label.pack()

        self.treap_label.config(text="Treap:\n" + treap.display())

    def book_flight(self):
        selected_location = self.locations[-1] if self.locations else ""  # Get the last added location
        import subprocess
        subprocess.Popen(["python", "live_flight_hashmaps.py", selected_location])
        self.root.withdraw()

    def display_thank_you(self):
        thank_you_label = Label(self.root, text="Thank you for using our Weather App!")
        thank_you_label.pack()

if __name__ == "__main__":
    root = Tk()
    root.geometry("600x600")
    app = WeatherApp(root)
    root.mainloop()
