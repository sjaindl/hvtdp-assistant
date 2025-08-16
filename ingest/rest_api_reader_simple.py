import requests
from llama_index.core import Document

endpoints = [
    "https://www.hvtdpstainz.at/api/getActiveMembership.php",
    "https://www.hvtdpstainz.at/api/getActivePlayers.php",
    "https://www.hvtdpstainz.at/api/getChefs.php",
    "https://www.hvtdpstainz.at/api/getDonations.php",
    "https://www.hvtdpstainz.at/api/getGames.php",
    "https://www.hvtdpstainz.at/api/getGoalOfTheSeason.php",
    "https://www.hvtdpstainz.at/api/getItems.php",
    "https://www.hvtdpstainz.at/api/getNews.php",
    "https://www.hvtdpstainz.at/api/getPappfans.php",
    "https://www.hvtdpstainz.at/api/getPhotos.php",
    "https://www.hvtdpstainz.at/api/getPlayerOfTheSeason.php",
    "https://www.hvtdpstainz.at/api/getScorers.php",
    "https://www.hvtdpstainz.at/api/getSquadPlayers.php",
    "https://www.hvtdpstainz.at/api/getStandings.php",
    "https://www.hvtdpstainz.at/api/getSupportMembership.php",
    "https://www.hvtdpstainz.at/api/getTicker.php",

    # "https://www.hvtdpstainz.at/api/getGoldenShot.php",
    # "https://www.hvtdpstainz.at/api/getSeasons.php",
    # "https://www.hvtdpstainz.at/api/getSurvey.php",
    # "https://www.hvtdpstainz.at/api/getVisitCount.php",
]

def load_rest_api_docs():
    docs = [load_api_data(url) for url in endpoints]
    return docs

#Best practice for JSON APIs in LlamaIndex
#Step 1: Fetch JSON from each endpoint.
#Step 2: Flatten or summarize it into a consistent, human-readable text format. ... TODO
#Step 3: Wrap it into a Document with optional metadata.

def load_api_data(api_url: str):
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()

    # Convert JSON to text (format however you want)
    text = ""
    #for item in data:
       # text += f"ID: {item['id']}\nName: {item['name']}\nDescription: {item['description']}\n\n"
    text = "\n".join(str(item) for item in data)
    #dump = json.dumps(data)

    # Wrap in LlamaIndex Document
    return Document(text=text, metadata={"source": api_url})

# Example usage
#documents = load_api_data("https://api.example.com/items")
#print(documents[0].text)
