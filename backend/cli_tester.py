import requests
import sys
import csv

from database.models import Engine, sessionmaker, Profile, isolate_stressed_element_in_field
from backend.utils.constants import BASE_URL

def login():
    while True:
        print("=== Electoral API Tester ===")
        username = input("Username: ")
        password = input("Password: ")

        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "username": username,
            "password": password
        })

        if resp.status_code == 200:
            data = resp.json()
            print("Logged in.")
            return data["access_token"], data["device_token"]
        else:
            print("Login failed. Try again.")

def main():
    access_token, device_token = login()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Device-Token": device_token
    }

    while True:
        print("""\n1) List profiles\n2) Export profiles\n3) Map profiles\n4) Quit""")
        choice = input("Choice: ")

        if choice == "1":
            score_min = input("score_min (press Enter to skip): ")
            origin = input("origin (press Enter to skip): ")

            params = {}
            if score_min:
                params["score_min"] = score_min
            if origin:
                params["origin"] = origin

            resp = requests.get(f"{BASE_URL}/profiles/", headers=headers, params=params)
            print(resp.json())

        elif choice == "2":
            score_min = input("score_min (press Enter to skip): ")
            origin = input("origin (press Enter to skip): ")

            params = {}
            if score_min:
                params["score_min"] = score_min
            if origin:
                params["origin"] = origin

            resp = requests.get(f"{BASE_URL}/profiles/export", headers=headers, params=params)

            with open("profiles_export.csv", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("Exported to profiles_export.csv")

        elif choice == "3":
            score_min = input("score_min (press Enter to skip): ")
            origin = input("origin (press Enter to skip): ")
            political_alignment = input("political alignment (press Enter to skip): ")
            start_lat = input("start_lat (MANDATORY): ")
            start_long = input("start_long (MANDATORY): ")

            payload = {
                "start_lat": float(start_lat),
                "start_lon": float(start_long),
                "ethnicity": origin or None,
                "political_alignment": political_alignment or None,
                "min_score_vote": int(score_min) if score_min else None
            }

            resp = requests.post(
                f"{BASE_URL}/profiles/optimize",
                headers=headers,
                json=payload
            )
            print(resp.json())

        elif choice == "4":
            sys.exit("Closing")

        else:
            print("Invalid choice.")

main()