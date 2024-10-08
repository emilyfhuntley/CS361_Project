import requests

API_KEY = "7yqDHNkxUXc2NC/exFwISg==iHX8hiE5gGKTsl70"
BASE_URL = "https://api.api-ninjas.com/v1/facts"

def print_menu():
    print("\nOPTIONS:")
    print("f: Generate random fact (or press Enter)")
    print("s: View saved facts")
    print("d: Delete a saved fact")
    print("r: Revisit a previously generated fact")
    print("h: Show help and about page")
    print("q: Quit")

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
        return f"Error: Received status code {response.status_code}. Response: {response.text}"

def save_fact(fact, saved_facts):
    saved_facts.append(fact)

def view_saved_facts(saved_facts):
    if not saved_facts:
        return "No saved facts."
    return "\n".join(f"{i + 1}: {fact}" for i, fact in enumerate(saved_facts))

def view_generated_facts(generated_facts):
    if not generated_facts:
        return "No generated facts."
    return "\n".join(f"{i + 1}: {fact}" for i, fact in enumerate(generated_facts))

def delete_fact(index, saved_facts):
    if 0 <= index < len(saved_facts):
        return saved_facts.pop(index)
    return "Invalid index."

def show_about_page():
    return (
        "\n"
        "Fact Frenzy is a random fact generator CLI app that uses Facts API from API Ninja.\n"
        "The Facts API provides tons of random interesting facts about science, literature,\n"
        "philosophy, and other cool topics!! Expand your trivia knowledge today!\n\n"
        
        "OPTIONS:\n"
        "   Type 'f' or hit enter to get a random fact from the Facts API.\n"
        "   Type 's'  to view a list of all saved facts from this session. Saved facts\n"
        "       will be lost when the session is quit (q).\n"
        "   Type 'd'  to delete a saved fact. You will be asked to pick the fact from \n"
        "       the list, and the program will ask you to confirm it.\n"
        "   Type 'r'  to revisit a previously generated fact. All generated facts will \n"
        "       be listed and you can select one to save again.\n"
        "   Type 'h' to show help and about page. That's how you got here!\n"
        "   Type 'q' to quit. The session will end and all saved facts will be lost!!!\n"
        "\n"
        "Developed by Emily Huntley, for Oregon State's CS361 in Summer 2024.\n"
        "Contact: huntleye@oregonstate.edu\n"
        "Facts API: https://api-ninjas.com/api/facts"
    )

def print_bubble_title():
    bubble_title = r"""
                 ___           _         ___                          
                | __|__ _  __ | |_      | __|_ _  ___  _ _   ___ _  _ 
                | _|/ _` |/ _||  _|     | _|| '_|/ -_)| ' \ |_ /| || |
                |_| \__,_|\__| \__|     |_| |_|  \___||_||_|/__| \_, |
                                                                 |__/
    """
    print(bubble_title)
    print("            Learn new random trivia with the option to save your favorites!")
    print("               NOTE: Saved facts are only stored until the session ends.")

def main():
    saved_facts = []
    generated_facts = []
    
    print_bubble_title()

    while True:
        print_menu()
        user_choice = input("\nEnter your choice: ").strip().lower()

        if user_choice == "f" or user_choice == "":
            fact = fetch_random_fact()
            print(f"\nRandom Fact: {fact}")
            generated_facts.append(fact)
            save_choice = input("\nEnter 'y' if you would like to save this fact: ").strip().lower()
            if save_choice == "y":
                save_fact(fact, saved_facts)
                print("Fact saved.")
            else:
                print("Fact not saved.")

        elif user_choice == "s":
            print("\nSaved Facts:")
            print(view_saved_facts(saved_facts))

        elif user_choice == "d":
            if not saved_facts:
                print("No saved facts to delete.")
            else:
                print("Saved Facts:")
                print(view_saved_facts(saved_facts))
                print("\nEnter the number of the fact to delete:")
                try:
                    fact_index = int(input().strip()) - 1
                    if 0 <= fact_index < len(saved_facts):
                        delete_confirmation = input(f"Are you sure you want to delete this fact: '{saved_facts[fact_index]}'? (y/n): ").strip().lower()
                        if delete_confirmation == "y":
                            result = delete_fact(fact_index, saved_facts)
                            print(f"Deleted Fact: {result}")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("Invalid index.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        elif user_choice == "h":
            print_bubble_title()
            print(show_about_page())

        elif user_choice == "q":
            print("\nWARNING: All saved facts will be lost if you quit.")
            quit_confirmation = input(f"\nAre you sure you want to quit? (y/n): ").strip().lower()
            if quit_confirmation == "y":
                print("\nQuitting program. Goodbye!")
                break
            else:
                print("\nQuitting canceled. Returning to main menu...")

        elif user_choice == "r":
            print("\nGenerated Facts:")
            print(view_generated_facts(generated_facts))
            if not generated_facts:
                print("No generated facts to redo.")
            else:
                print("\nEnter the number of the fact to redo:")
                try:
                    fact_index = int(input().strip()) - 1
                    if 0 <= fact_index < len(generated_facts):
                        fact = generated_facts[fact_index]
                        print(f"\nRedo Fact: {fact}")
                        save_choice = input("\nEnter 'y' if you would like to save this fact: ").strip().lower()
                        if save_choice == "y":
                            save_fact(fact, saved_facts)
                            print("Fact saved.")
                        else:
                            print("Fact not saved.")
                    else:
                        print("Invalid index.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        else:
            print("Invalid choice. Please enter 'r', 's', 'd', 'h', or 'q'.")

        

if __name__ == "__main__":
    main()
