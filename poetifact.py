import time
import zmq

FACT_GENERATOR_FILE = "fact_generator.txt"
POEM_GENERATOR_PORT = 5225
FACTS_SERVICE_PORT = 5555  # Port for the facts management microservice

def request_random_fact():
    with open(FACT_GENERATOR_FILE, "w") as file:
        file.write("fetch_fact")

    while True:
        with open(FACT_GENERATOR_FILE, "r") as file:
            response = file.read().strip()
            if response and response != "fetch_fact":
                return response
        time.sleep(1)

def generate_poem(fact, style):
    # Set up environment variable for ZMQ
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{POEM_GENERATOR_PORT}")

    # Structure request for microservice
    request = {'topic': fact, 'style': style}
    socket.send_json(request)

    # Get response back from microservice
    message = socket.recv()
    context.destroy()
    return message.decode()

def select_poetry_style():
    styles = [
        "Villanelle", "Sonnet", "Sestina", "Acrostic", "Haiku",
        "Ballad", "Limerick", "Pantoum", "Blank Verse",
        "Diminishing Verse", "Free Verse", "Random"
    ]

    print("\nSelect a poetry style:")
    for i, style in enumerate(styles, start=1):
        print(f"{i}. {style}")

    choice = int(input("Enter the number of the desired style: ")) - 1
    if 0 <= choice < len(styles):
        return styles[choice]
    elif choice == len(styles):  # For "Random"
        import random
        return styles[random.randint(0, len(styles) - 2)]  # Random from 1 to 12
    else:
        print("Invalid choice. Defaulting to 'Free Verse'.")
        return "Free Verse"

def save_fact_to_service(fact):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{FACTS_SERVICE_PORT}")

    request = {'command': 'save', 'fact': fact}
    socket.send_json(request)
    response = socket.recv_json()
    context.destroy()
    return response

def view_saved_facts_from_service():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{FACTS_SERVICE_PORT}")

    request = {'command': 'view'}
    socket.send_json(request)
    response = socket.recv_json()
    context.destroy()
    return response.get('facts', [])

def delete_fact_from_service(index):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{FACTS_SERVICE_PORT}")

    request = {'command': 'delete', 'index': index}
    socket.send_json(request)
    response = socket.recv_json()
    context.destroy()
    return response

def main():
    while True:
        user_choice = input("\nType 'f' to generate a random fact, 's' to view saved facts, 'd' to delete a saved fact, or 'q' to quit: ").strip().lower()

        if user_choice == "f":
            fact = request_random_fact()
            print(f"\nRandom Fact: {fact}")

            # Ask to save the fact
            save_choice = input("Would you like to save this fact? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_response = save_fact_to_service(fact)
                print(save_response)

            # Generate poem from fact
            style = select_poetry_style()
            poem = generate_poem(fact, style)
            print("\nGenerated Poem:")
            print(poem)

            # Ask to regenerate the poem
            regenerate = input("\nDo you want to generate another poem with the same style? (y/n): ").strip().lower()
            if regenerate == 'y':
                poem = generate_poem(fact, style)
                print("\nRegenerated Poem:")
                print(poem)

        elif user_choice == "s":
            saved_facts = view_saved_facts_from_service()
            print("\nSaved Facts:")
            if not saved_facts:
                print("No saved facts.")
            else:
                for i, fact in enumerate(saved_facts):
                    print(f"{i + 1}: {fact}")

        elif user_choice == "d":
            saved_facts = view_saved_facts_from_service()
            if not saved_facts:
                print("No saved facts to delete.")
            else:
                print("\nEnter the number of the fact to delete:")
                try:
                    fact_index = int(input().strip()) - 1
                    if 0 <= fact_index < len(saved_facts):
                        delete_response = delete_fact_from_service(fact_index)
                        print(f"Deleted Fact: {delete_response}")
                    else:
                        print("Invalid index.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        elif user_choice == "q":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
