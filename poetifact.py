import time
import zmq
import platform
import os

# Paths for communication
POEM_FILE = "poem.txt"  # The file that will contain the poem
IMAGE_OUTPUT_FILE = "image_path.txt"  # The file to write the image path
FACT_GENERATOR_FILE = "fact_generator.txt" # Will contain a fact or request
POEM_GENERATOR_PORT = 5225
FACTS_SERVICE_PORT = 5555  # Port for the facts management microservice

def print_menu():
    print()
    print(line_break(40))
    print("OPTIONS:")
    print("f: Generate random fact (or press Enter)")
    print("s: View saved facts")
    print("d: Delete a saved fact")
    print("p: Create a poem from a saved fact.")
    print("h: Show help and about page")
    print("q: Quit")
    print(line_break(40))

def line_break(length):
    """Prints a line break of a given length."""
    line = ""
    for i in range(length):
        line = line + "-"
    return(line)

def show_about_page():
    return (
        "\n"
        "PoetiFact can generate and save random fun facts, and transform them into poetry!\n"
        "Poems can be written on a piece of parchment and saved as an image.\n"
        
        "OPTIONS:\n"
        "   Type 'f' or hit enter to get a random fact from the Facts API.\n"
        "   Type 's'  to view a list of all saved facts from this session. Saved facts\n"
        "       will be lost when the session is quit (q).\n"
        "   Type 'd'  to delete a saved fact. You will be asked to pick the fact from \n"
        "       the list, and the program will ask you to confirm it.\n"
        "   Type 'p' to create a poem from a saved fact. Pick from 5 poetry styles.\n"
        "       Poems can then be turned into an image on a parchment background.\n"
        "   Type 'h' to show help and about page. That's how you got here!\n"
        "   Type 'q' to quit. The session will end and all saved facts will be lost!!!\n"
        "\n"
        "Developed by Emily Huntley, for Oregon State's CS361 in Summer 2024.\n"
        "Contact: huntleye@oregonstate.edu\n"
        "Facts API: https://api-ninjas.com/api/facts\n"
        "Poems are generated using Google Gemini API: https://ai.google.dev/\n"
        "Image background retrieved from the public domain: https://digitaltmuseum.org\n"
        "Poem font: Antro Vecta by Youssef Habchi https://youssef-habchi.com/"
    )

def print_bubble_title():
    bubble_title = r"""                     ____            _   _ _____          _   
                    |  _ \ ___   ___| |_(_)  ___|_ _  ___| |_ 
                    | |_) / _ \ / _ \ __| | |_ / _` |/ __| __|
                    |  __/ (_) |  __/ |_| |  _| (_| | (__| |_ 
                    |_|   \___/ \___|\__|_|_|  \__,_|\___|\__|
    """
    print(bubble_title)
    print("         Get random facts, save your favorites, and create poetry from them!")
    print("               NOTE: Saved facts are only stored until the session ends.")

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
        "Sonnet", "Haiku", "Limerick",
        "Blank Verse (Maximum 16 lines)", "Free Verse (Maximum 16 lines)", "Random"
    ]

    print("\nSelect a poetry style:")
    for i, style in enumerate(styles, start=1):
        print(f"{i}. {style}")

    choice = int(input("Enter the number of the desired style: ")) - 1
    if 0 <= choice < len(styles) - 1:
        return styles[choice]
    elif choice == len(styles) - 1:  # For "Random"
        import random
        return styles[random.randint(0, len(styles) - 2)]  # Random from 1 to 12
    else:
        print("Invalid choice. Defaulting to 'Free Verse'.")
        return "Free Verse (Maximum 16 lines)"

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

def print_saved_facts(saved_facts):
    """Prints the saved facts retrieved from the service"""

    print("\nSaved Facts:")
    if not saved_facts:
        print("No saved facts.")
    else:
        for i, fact in enumerate(saved_facts):
            print(f"{i + 1}: {fact}")

def delete_fact_from_service(index):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{FACTS_SERVICE_PORT}")

    request = {'command': 'delete', 'index': index}
    socket.send_json(request)
    response = socket.recv_json()
    context.destroy()
    return response

def clear_facts_from_service():
    """Clears all saved facts, used when quitting the program."""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{FACTS_SERVICE_PORT}")

    request = {'command': 'clear'}
    socket.send_json(request)
    response = socket.recv_json()
    context.destroy()
    return response

def create_image(poem):

    # Clear image output file 
    with open(IMAGE_OUTPUT_FILE, "w") as file:
        file.truncate(0)
        
    # Send poem to microservice comm pipeline
    with open(POEM_FILE, "w") as file:
        file.write(poem)
    
    # Open image when it is generated
    while True:
        with open(IMAGE_OUTPUT_FILE, "r") as file:
            image_path = file.read().strip()
            if len(image_path) > 0 and os.path.exists(image_path):
                # OPEN IMAGE
                if platform.system() == "Windows":
                    os.startfile(image_path)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f"open {image_path}")
                else:  # Assume Linux or other
                    os.system(f"xdg-open {image_path}")
                break  # Exit loop after opening the image
        time.sleep(1)  # Check every second for the image path

def user_choice_d():
    """Walks the user through steps to delete a fact from saved facts."""

    # Show saved facts to choose from
    saved_facts = view_saved_facts_from_service()
    print_saved_facts(saved_facts)
    if not saved_facts:
        print("No saved facts to delete.")
    else:
        print("\nEnter the number of the fact to delete:")
        try:
            fact_index = int(input().strip()) - 1
            if 0 <= fact_index < len(saved_facts):
                delete_confirmation = input(f"Are you sure you want to delete this fact: '{saved_facts[fact_index]}'? (y/n): ").strip().lower()
                if delete_confirmation == 'y':
                    delete_response = delete_fact_from_service(fact_index)
                    print(f"Deleted Fact: {delete_response}")
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def user_choice_f():
    """Walks the user through steps to generate a random fact."""

    fact = request_random_fact()
    print(f"\nRandom Fact: {fact}")

    # Ask to save the fact
    save_choice = input("\nWould you like to save this fact? (y/n): ").strip().lower()
    if save_choice == 'y':
        save_response = save_fact_to_service(fact)
        print(save_response)
    else:
        print("Fact not saved.")

def user_choice_p():
    """Walks the user though steps to create a poem from saved fact."""
    saved_facts = view_saved_facts_from_service()
    print_saved_facts(saved_facts)
    if not saved_facts:
        print("No saved facts to select from.")
    else:
        print("\nEnter the number of the fact to write a poem about:")
        try:
            fact_index = int(input().strip()) - 1
            if 0 <= fact_index < len(saved_facts):
                style = select_poetry_style()
                poem = generate_poem(saved_facts[fact_index], style)
                print("\nGenerated Poem:\n")
                print(poem)

                # Ask to make image
                image = input("\nDo you want to make an image of this poem? (y/n): ").strip().lower()
                if image == 'y':
                    create_image(poem)
                    print("\nYour image has been generated. Please save it in a new location if you would like to keep it.")
                    print("****WARNING: The image file will be overwritten if you generate another image****")

            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        
def main():
    clear_facts_from_service()
    print_bubble_title()    
    while True:
        print_menu()
        user_choice = input("\nEnter your choice: ").strip().lower()

        # Request for random fact
        if user_choice == "f" or user_choice == "":
            user_choice_f()

        # Request to see saved facts
        elif user_choice == "s":
            saved_facts = view_saved_facts_from_service()
            print_saved_facts(saved_facts)

        # Request to delete saved fact
        elif user_choice == "d":
            user_choice_d()
            
        # Request to create poem from saved fact
        elif user_choice == "p":
            user_choice_p()

        # Help and about
        elif user_choice == "h":
            print(line_break(80))
            print_bubble_title()
            print(show_about_page())
            print(line_break(80))

        elif user_choice == "q":
            print("\nWARNING: All saved facts will be lost if you quit.")
            quit_confirmation = input(f"\nAre you sure you want to quit? (y/n): ").strip().lower()
            if quit_confirmation == "y":
                print("\n", clear_facts_from_service())
                print("\nQuitting program. Goodbye!")
                break
            else:
                print("\nQuitting canceled. Returning to main menu...")
                
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
