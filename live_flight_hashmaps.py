import tkinter as tk
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv('flight_api')
endpoint_url = 'http://api.aviationstack.com/v1/flights'

def get_flight_details(arrival_location, destination_location, result_frame):
    # Clear any previous results
    for widget in result_frame.winfo_children():
        widget.destroy()

    params = {
        'access_key': api_key,
        'dep_iata': arrival_location,
        'arr_iata': destination_location,
        'limit': 1  # Limit to 1 flight result for simplicity
    }

    try:
        response = requests.get(endpoint_url, params=params)
        response.raise_for_status()  # Raise error for bad responses (4xx/5xx)

        data = response.json()
        if data.get('data'):
            flight_data = data['data'][0]  # Get the first flight result

            # Extract relevant flight details
            flight_details = {
                'Flight Date': flight_data.get('flight_date', 'N/A'),
                'Flight Status': flight_data.get('flight_status', 'N/A'),
                'Departure Airport': flight_data['departure'].get('airport', 'N/A'),
                'Departure Time': flight_data['departure'].get('estimated', 'N/A'),
                'Terminal': flight_data['departure'].get('terminal', 'N/A'),
                'Landing Time': flight_data['arrival'].get('estimated', 'N/A'),
                'Arrival Airport': flight_data['arrival'].get('airport', 'N/A'),
                'Airline Name': flight_data['airline'].get('name', 'N/A'),
                'IATA Number': flight_data['flight'].get('iata', 'N/A')
            }

            # Display flight details in the result frame
            display_flight_details(flight_details, result_frame)
        else:
            tk.Label(result_frame, text="No flight data found for the provided IATA codes.").pack(pady=10)

    except requests.exceptions.RequestException as e:
        tk.Label(result_frame, text=f"Error fetching flight data: {e}").pack(pady=10)

def display_flight_details(flight_details, frame):
    """Displays the flight details in the result frame."""
    for key, value in flight_details.items():
        detail = f"{key}: {value}"
        tk.Label(frame, text=detail).pack(anchor='w', padx=10, pady=2)

def load_locations():
    try:
        with open("locations.json", "r") as json_file:
            locations = json.load(json_file)
            return locations['arrival'], locations['destination']
    except FileNotFoundError:
        return None, None
    except json.JSONDecodeError:
        return None, None
