import tkinter as tk
import requests
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('flight_api')
endpoint_url = 'http://api.aviationstack.com/v1/flights'


def get_flight_details(iata_number):
    params = {
        'access_key': api_key,
        'flight_iata': iata_number
    }

    response = requests.get(endpoint_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            flight_data = data['data'][0]  

            flight_details = {
                'Flight Date': flight_data['flight_date'],
                'Flight Status': flight_data['flight_status'],
                'Departure Airport': flight_data['departure']['airport'],
                'Departure Time': flight_data['departure']['estimated'],
                'Terminal': flight_data['departure']['terminal'],
                'Landing Time': flight_data['arrival']['estimated'],
                'Arrival Airport': flight_data['arrival']['airport'],
                'Airline Name': flight_data['airline']['name'],
                'IATA Number': flight_data['flight']['iata']
            }

            result_label.config(text=format_flight_details(flight_details))
        else:
            result_label.config(text="No flight data found for the provided IATA number.")
    else:
        result_label.config(text=f"Request failed with status code {response.status_code}: {response.text}")


def format_flight_details(details):
    formatted_details = ""
    for key, value in details.items():
        formatted_details += f"{key}: {value}\n"
    return formatted_details


def manual_input():
    iata_label.config(state=tk.NORMAL)
    iata_entry.config(state=tk.NORMAL)
    index_label.config(state=tk.DISABLED)
    index_entry.config(state=tk.DISABLED)
    get_button.config(command=get_flight_manual)


def index_input():
    iata_label.config(state=tk.DISABLED)
    iata_entry.config(state=tk.DISABLED)
    index_label.config(state=tk.NORMAL)
    index_entry.config(state=tk.NORMAL)
    get_button.config(command=get_flight_index)


def get_flight_manual():
    iata_number = iata_entry.get()
    get_flight_details(iata_number)


def get_flight_index():
    selected_index = int(index_entry.get()) - 1
    if 0 <= selected_index < len(flights):
        selected_flight = flights[selected_index]
        iata_number = selected_flight['flight']['iata']
        get_flight_details(iata_number)
    else:
        result_label.config(text="Invalid index.")



window = tk.Tk()
window.title("Flight Details")
window.geometry("400x300")


choice_label = tk.Label(window, text="Choose an option:")
choice_label.pack()

manual_button = tk.Button(window, text="Enter IATA Manually", command=manual_input)
manual_button.pack()

index_button = tk.Button(window, text="Choose from Index", command=index_input)
index_button.pack()

iata_label = tk.Label(window, text="Enter IATA number:")
iata_label.pack()
iata_entry = tk.Entry(window)
iata_entry.pack()

index_label = tk.Label(window, text="Enter index:")
index_label.pack()
index_entry = tk.Entry(window)
index_entry.pack()

get_button = tk.Button(window, text="Get Flight Details", command=get_flight_manual)
get_button.pack()

result_label = tk.Label(window, text="")
result_label.pack()


response = requests.get(endpoint_url, params={'access_key': api_key})

if response.status_code == 200:
    data = response.json()
    flights = data['data']
    if flights:
        flight_selection_label = tk.Label(window, text="Available Flights:")
        flight_selection_label.pack()

        flight_selection = tk.Listbox(window)
        flight_selection.pack()

        flight_details_map = {}  

        for index, flight in enumerate(flights, start=1):
            iata_number = flight['flight']['iata']
            airline_name = flight['airline']['name']
            departure_airport = flight['departure']['airport']
            arrival_airport = flight['arrival']['airport']

            flight_selection.insert(tk.END, f"{index}. {iata_number} - {airline_name}: {departure_airport} to {arrival_airport}")

            # Store flight details in the hash map
            flight_details_map[iata_number] = {
                'Airline Name': airline_name,
                'Departure Airport': departure_airport,
                'Arrival Airport': arrival_airport
            }


def show_flight_details(event):
    selected_index = flight_selection.curselection()
    if selected_index:
        selected_index = int(selected_index[0])
        selected_flight = flights[selected_index]
        iata_number = selected_flight['flight']['iata']
        flight_details = flight_details_map.get(iata_number)
        if flight_details:
            result_label.config(text=format_flight_details(flight_details))
        else:
            result_label.config(text="Flight details not available.")
    else:
        result_label.config(text="No flight selected.")


flight_selection.bind('<<ListboxSelect>>', show_flight_details)

# Start the GUI event loop
window.mainloop()