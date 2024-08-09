import requests
import time

API_KEY = "7yqDHNkxUXc2NC/exFwISg==iHX8hiE5gGKTsl70"
BASE_URL = "https://api.api-ninjas.com/v1/facts"

FACT_GENERATOR_FILE = "fact_generator.txt"

def fetch_random_fact():
    headers = {"X-Api-Key": API_KEY}
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code == 200:
        try:
            fact_data = response.json()
            if fact_data:
                return fact_data[0].get("fact", "No fact available.")
            else:
                return "No fact returned from API."
        except ValueError:
            return "Error: Received non-JSON response."
    else:
        return f"Error: {response.status_code}. Response: {response.text}"

def run_fact_service():
    print("Fact generator service starting...\n")
    while True:
        time.sleep(1)

        with open(FACT_GENERATOR_FILE, "r") as file:
            request = file.read().strip()

        if request == "fetch_fact":
            print("Fetching fact...\n")
            fact = fetch_random_fact()
            time.sleep(1)
            with open(FACT_GENERATOR_FILE, "w") as file:
                file.write(fact)  # Write the fact as the response
            print(f"Sending fact to UI: {fact}\n")
            print("Fact generator service running...\n")

if __name__ == "__main__":
    run_fact_service()