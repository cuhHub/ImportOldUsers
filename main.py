import requests
from concurrent.futures import ThreadPoolExecutor
from xmltodict import parse
import orjson
from dataclasses import dataclass
from functools import cache

@dataclass
class SteamUser():
    steam_id: str
    steam_username: str

@cache
def get_user_info(steam_id: str) -> SteamUser:
    response = requests.get(f"https://steamcommunity.com/profiles/{steam_id}/?xml=true")
    
    if not response.ok:
        raise Exception(f"Failed to get user info for {steam_id}: {response.text}")
    
    decoded = parse(response.text)
    
    if not decoded.get("profile"): # user doesnt exist
        return
    
    return SteamUser(decoded["profile"]["steamID64"], decoded["profile"]["steamID"])

def get_users(steam_ids: list[str]) -> list[SteamUser]:
    with ThreadPoolExecutor(max_workers = 64) as executor:
        return list(executor.map(get_user_info, steam_ids))
    
def get_steam_ids_from_config(path: str) -> list[str]:
    with open(path, "r") as f:
        steam_ids: list[dict[str, str]] = parse(f.read())["server_data"]["authorized"]["id"]
        return [steam_id["@value"] for steam_id in steam_ids]

if __name__ == "__main__":
    steam_ids = get_steam_ids_from_config("server_config.xml")
    users = get_users(steam_ids)
    
    print(f"Got {len(users)} users")
    
    with open("users.json", "wb") as f:
        f.write(orjson.dumps(users))