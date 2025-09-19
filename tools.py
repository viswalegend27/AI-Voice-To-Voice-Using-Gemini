import logging # used to log the information
from livekit.agents import function_tool, RunContext
import requests

@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """Get the current weather for a given city."""
    # Construct the weather API URL (wttr.in provides simple weather info)
    url = f"https://wttr.in/{city}?format=3"
    
    try:
        # Send GET request with a timeout to avoid hanging
        response = requests.get(url, timeout=5)
        
        # Raises error automatically if status code is 4xx/5xx
        # obtained as an unformated string
        response.raise_for_status()
        # Clean response text for logging/returning
        # Retriving only text
        weather = response.text.strip()
        logging.info(f"Weather for {city}: {weather}") # logging the information in terminal
        return weather
    
    except requests.RequestException as e:
        # Handles all request-related errors (network, timeout, bad status)
        logging.error(f"Weather request failed for {city}: {e}") # logs the error in terminal
        return f"Could not retrieve weather for {city}."
    
# Function to get my date and time
@function_tool()
async def get_datetime(context: "RunContext", query: str = "full") -> str:
    """
    Get a human-like response for current date and time.
    query options:
    - "time" -> Returns time in 12-hour format with AM/PM and part of day.
    - "date" -> Returns natural date format (e.g., September 18, 2025).
    - "day"  -> Returns weekday name.
    - "full" -> Returns full sentence with day, date, time.
    """
    from datetime import datetime
    import logging

    try:
        now = datetime.now()

        hour_24 = now.hour
        minute = now.minute

        # converstion to 12-hour format
        hour_12 = hour_24 % 12 or 12
        am_pm = "AM" if hour_24 < 12 else "PM"

        # saying the time of the day in casual format
        if 5 <= hour_24 < 12:
            part_of_day = "morning"
        elif 12 <= hour_24 < 17:
            part_of_day = "afternoon"
        elif 17 <= hour_24 < 21:
            part_of_day = "evening"
        else:
            part_of_day = "night"

        # formated strings
        time_str = f"{hour_12}:{minute:02d} {am_pm} ({part_of_day})"
        date_str = now.strftime("%B %d, %Y")
        day_str = now.strftime("%A")
        full_str = f"It’s {day_str}, {date_str} at {time_str}"

        # Decide response
        if query == "time":
            response = f"The time is {time_str}"
        elif query == "date":
            response = f"Today is {date_str}"
        elif query == "day":
            response = f"Today is {day_str}"
        else:
            response = full_str

        logging.info(f"Datetime response for query='{query}': {response}")
        return response

    except Exception as e:
        logging.error(f"Failed to get datetime: {e}")
        return "Sorry, I couldn’t figure out the current date and time."