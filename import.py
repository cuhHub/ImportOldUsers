import orjson
import os
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

def import_user(steam_user: str, steam_id: str):
    PORT = os.environ.get("PORT")
    API_TOKEN = os.environ.get("API_TOKEN")
    
    response = requests.post(
        f"http://localhost:{PORT}/players/",
        json = {"steam_username": steam_user, "steam_id": steam_id},
        headers = {"x-authorization" : f"Bearer {API_TOKEN}"}
    )

    if not response.ok and response.json()["detail"].find("already exists") == -1: # we need to add error codes
        raise Exception(f"Failed to import user {steam_user}: {response.text}")

if __name__ == "__main__":
    if not os.path.exists("users.json"):
        raise FileNotFoundError("users.json not found, run `main.py` first")

    with open("users.json", "rb") as file:
        users = orjson.loads(file.read())
        
        with ThreadPoolExecutor(max_workers = 64) as executor:
            executor.map(lambda user: import_user(*user.values()), users)