import tkinter as tk
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
apiKey = os.getenv('flight_api')
endpointUrl = 'http://api.aviationstack.com/v1/flights'

def getFlightDetails(arrivalLocation, destinationLocation, resultFrame):
    # Clear any previous results
    for widget in resultFrame.winfo_children():
        widget.destroy()

    params = {
        'access_key': apiKey,
        'dep_iata': arrivalLocation,
        'arr_iata': destinationLocation,
        'limit': 1  # Limit to 1 flight result for simplicity
    }

    try:
        response = requests.get(endpointUrl, params=params)
        response.raise_for_status()  # Raise error for bad responses (4xx/5xx)

        data = response.json()
        if data.get('data'):
            flightData = data['data'][0]  # Get the first flight result

            # Extract relevant flight details
            flightDetails = {
                'Flight Date': flightData.get('flight_date', 'N/A'),
                'Flight Status': flightData.get('flight_status', 'N/A'),
                'Departure Airport': flightData['departure'].get('airport', 'N/A'),
                'Departure Time': flightData['departure'].get('estimated', 'N/A'),
                'Terminal': flightData['departure'].get('terminal', 'N/A'),
                'Landing Time': flightData['arrival'].get('estimated', 'N/A'),
                'Arrival Airport': flightData['arrival'].get('airport', 'N/A'),
                'Airline Name': flightData['airline'].get('name', 'N/A'),
                'IATA Number': flightData['flight'].get('iata', 'N/A')
            }

            # Display flight details in the result frame
            displayFlightDetails(flightDetails, resultFrame)
        else:
            tk.Label(resultFrame, text="No flight data found for the provided IATA codes.").pack(pady=10)

    except requests.exceptions.RequestException as e:
        tk.Label(resultFrame, text=f"Error fetching flight data: {e}").pack(pady=10)

def displayFlightDetails(flightDetails, frame):
    """Displays the flight details in the result frame."""
    for key, value in flightDetails.items():
        detail = f"{key}: {value}"
        tk.Label(frame, text=detail).pack(anchor='w', padx=10, pady=2)

def loadLocations():
    try:
        with open("locations.json", "r") as jsonFile:
            locations = json.load(jsonFile)
            return locations['arrival'], locations['destination']
    except FileNotFoundError:
        return None, None
    except json.JSONDecodeError:
        return None, None
