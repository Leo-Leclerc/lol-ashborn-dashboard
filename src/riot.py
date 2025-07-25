import os
import requests
from typing import Dict, List, Optional

API_KEY = os.getenv("RIOT_API_KEY")
REGION = "euw1"
MATCH_REGION = "europe"

_HEADERS = {"X-Riot-Token": API_KEY}

def _get(url: str) -> Dict:
    r = requests.get(url, headers=_HEADERS)
    r.raise_for_status()
    return r.json()

def get_summoner_info(name: str) -> Dict:
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}"
    return _get(url)

def get_rank_info(summoner_id: str) -> Optional[Dict]:
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    entries = _get(url)
    for e in entries:
        if e["queueType"] == "RANKED_SOLO_5x5":
            return e
    return None

def get_match_ids(puuid: str, count: int = 10) -> List[str]:
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    return _get(url)

def get_match_details(match_id: str) -> Dict:
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    return _get(url)
