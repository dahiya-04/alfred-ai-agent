from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import random
from huggingface_hub import list_models

search = DuckDuckGoSearchRun()

@tool
def web_search_tool(query: str) -> str:
    """Search the web for information about unfamiliar guests."""
    return search.run(query)

@tool
def latest_news_tool(topic: str) -> str:
    """
    Get the latest news about a specific topic.
    """
    
    query = f"latest news about {topic}"
    
    results = search.run(query)
    
    return results


@tool
def get_weather_tool(location:str)-> str:
    """Fetches weather information for a given location."""

    weather_condition =[
         {"condition": "Rainy", "temp_c": 15},
        {"condition": "Clear", "temp_c": 25},
        {"condition": "Windy", "temp_c": 20}
    ]
    data = random.choice(weather_condition)
    return f"Wrather in {location} is  {data['condition']} with temp : {data['temp_c']}c"


@tool
def hub_stats_tool(author: str) -> str:
    """Fetches the most downloaded model from a specific author on the Hugging Face Hub."""
    try:
        # List models from the specified author, sorted by downloads
        models = list(list_models(author=author, sort="downloads", direction=-1, limit=1))

        if models:
            model = models[0]
            return f"The most downloaded model by {author} is {model.id} with {model.downloads:,} downloads."
        else:
            return f"No models found for author {author}."
    except Exception as e:
        return f"Error fetching models for {author}: {str(e)}"
    

