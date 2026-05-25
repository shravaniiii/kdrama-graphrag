import requests
import os

TMDB_KEY = os.getenv("TMDB_API_KEY", "8284d54bd44687cf6afa5c309266d7b2")
BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"

DRAMA_NAME_MAP = {
    "goblin": "Guardian: The Lonely and Great God",
    "guardian": "Guardian: The Lonely and Great God",
    "crash landing on you": "Crash Landing on You",
    "cloy": "Crash Landing on You",
    "squid game": "Squid Game",
    "extraordinary attorney woo": "Extraordinary Attorney Woo",
    "attorney woo": "Extraordinary Attorney Woo",
    "the glory": "The Glory",
    "itaewon class": "Itaewon Class",
    "descendants of the sun": "Descendants of the Sun",
    "hotel del luna": "Hotel Del Luna",
    "vincenzo": "Vincenzo",
    "reply 1988": "Reply 1988",
    "hospital playlist": "Hospital Playlist",
    "my love from the star": "My Love from the Star",
    "boys over flowers": "Boys Over Flowers",
    "business proposal": "A Business Proposal",
    "flower of evil": "Flower of Evil",
    "hometown cha cha cha": "Hometown Cha-Cha-Cha",
    "twenty five twenty one": "Twenty-Five Twenty-One",
    "queen of tears": "Queen of Tears",
    "lovely runner": "Lovely Runner",
    "alchemy of souls": "Alchemy of Souls",
    "all of us are dead": "All of Us Are Dead",
    "sweet home": "Sweet Home",
    "signal": "Signal",
    "my mister": "My Mister",
    "move to heaven": "Move to Heaven",
    "reply 1997": "Reply 1997",
    "reply 1994": "Reply 1994",
    "reply 1988": "Reply 1988",
}

def search_drama(name: str):
    search_name = DRAMA_NAME_MAP.get(name.lower(), name)
    url = f"{BASE_URL}/search/tv"
    params = {
        "api_key": TMDB_KEY,
        "query": search_name,
        "language": "en-US"
    }
    r = requests.get(url, params=params, timeout=10)
    results = r.json().get("results", [])
    kr_results = [x for x in results if "KR" in x.get("origin_country", [])]
    if kr_results:
        return kr_results[0]
    return results[0] if results else None

def get_poster_url(drama_name: str):
    drama = search_drama(drama_name)
    if drama and drama.get("poster_path"):
        return IMG_BASE + drama["poster_path"], drama.get("name", drama_name)
    return None, drama_name

def search_person(name: str):
    url = f"{BASE_URL}/search/person"
    params = {
        "api_key": TMDB_KEY,
        "query": name,
        "language": "en-US"
    }
    r = requests.get(url, params=params, timeout=10)
    results = r.json().get("results", [])
    return results[0] if results else None

def get_actor_photo_url(actor_name: str):
    person = search_person(actor_name)
    if person and person.get("profile_path"):
        return IMG_BASE + person["profile_path"], person.get("name", actor_name)
    return None, actor_name

KNOWN_DRAMAS = list(DRAMA_NAME_MAP.keys()) + [
    "weightlifting fairy kim bok joo", "healer", "pinocchio",
    "while you were sleeping", "strong woman do bong soon",
    "what's wrong with secretary kim", "fight for my way",
    "the heirs", "true beauty", "moon lovers",
    "scarlet heart ryeo", "kill me heal me", "secret garden",
    "coffee prince", "city hunter", "the king eternal monarch",
    "start up", "nevertheless", "extracurricular", "my name",
    "prison playbook", "vagabond", "kingdom"
]

KNOWN_ACTORS = [
    "gong yoo", "lee dong wook", "hyun bin", "son ye jin",
    "park seo joon", "kim ji won", "lee min ho", "park shin hye",
    "song joong ki", "song hye kyo", "lee jong suk", "park min young",
    "ji chang wook", "kim soo hyun", "lee joon gi",
    "jun ji hyun", "yoo in na", "park bo young", "nam joo hyuk",
    "lee sung kyung", "shin min ah", "kim seon ho", "park eun bin",
    "lee jae wook", "jung so min", "moon chae won"
]

def extract_dramas_from_text(text: str):
    text_lower = text.lower()
    found = []
    for drama in KNOWN_DRAMAS:
        if len(drama) < 4:
            continue
        if drama in text_lower and drama not in [d for _, d in found]:
            position = text_lower.find(drama)
            found.append((position, drama))
    
    found.sort(key=lambda x: x[0])
    return [drama for _, drama in found[:3]]
    
    # sort by position in text so first mentioned = first image
    found.sort(key=lambda x: x[0])
    return [drama for _, drama in found[:3]]

def extract_actors_from_text(text: str):
    text_lower = text.lower()
    found = []
    for actor in KNOWN_ACTORS:
        if len(actor) < 4:
            continue
        if actor in text_lower and actor not in found:
            found.append(actor)
    return found[:3]