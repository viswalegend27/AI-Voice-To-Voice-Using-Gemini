import logging # used to log the information
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun

@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """Get the current weather for a given city."""
    # Construct the weather API URL (wttr.in provides simple weather info)
    url = f"https://wttr.in/{city}?format=3"
    
    try:
        # Send GET request with a timeout to avoid hanging
        response = requests.get(url, timeout=5)
        # Raises error automatically if status code is 4xx/5xx
        response.raise_for_status()
        # Clean response text for logging/returning
        weather = response.text.strip()
        logging.info(f"Weather for {city}: {weather}") # logging the information
        return weather

    except requests.RequestException as e:
        # Handles all request-related errors (network, timeout, bad status)
        logging.error(f"Weather request failed for {city}: {e}")
        return f"Could not retrieve weather for {city}."
      
@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        # Initialize DuckDuckGo search tool and run the query
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(tool_input=query)

        # Log the search results for traceability
        logging.info(f"Search result for '{query}': {results}")
        return results

    except Exception as e:
        # Handle any errors (e.g., tool issues, bad input)
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."

