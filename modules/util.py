import asyncio
import os

import requests
import random
import string


def generate_random_string(length):
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits  # You can add more characters if needed

    # Generate a random string of the specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))

    return random_string




async def stop_browser(profile_id):
    for _ in range(15):
        try:
            response = requests.get(f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop")
            return response.json()
        except Exception as e:
            print(f"Error stopping browser: {e}")
            await asyncio.sleep(1)


async def get_all_profiles(token):
    url = "https://anty-api.com/browser_profiles/"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    for _ in range(15):
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error getting profiles: {e}")
            await asyncio.sleep(1)


async def launch_browser(token, id):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    for _ in range(15):
        try:
            response = requests.get(f"http://localhost:3001/v1.0/browser_profiles/{id}/start?automation=1",
                                    headers=headers)
            data = response.json()
            endpoint = data["automation"]["wsEndpoint"]
            port = data["automation"]["port"]
            return endpoint, port
        except Exception as e:
            print(f"Error launching browser: {e}")
            await asyncio.sleep(1)


async def login_dolphin():
    url = "https://anty-api.com/auth/login"
    payload = {'username': os.environ["DOLPHIN_LOGIN"], 'password': os.environ["DOLPHIN_PASSWORD"]}
    for _ in range(15):
        try:
            response = requests.post(url, data=payload)
            return response.json()["token"]
        except Exception as e:
            print(f"Error logging in: {e}")
            await asyncio.sleep(1)
