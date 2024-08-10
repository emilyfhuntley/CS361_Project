import os
import zmq

FACTS_FILE = "saved_facts.txt"

def initialize_facts_file():
    """Ensure the facts file exists."""
    if not os.path.exists(FACTS_FILE):
        with open(FACTS_FILE, "w") as f:
            pass  # Create an empty file
    else:
        with open(FACTS_FILE, "w") as f:
            f.truncate(0)

def save_fact(fact):
    """Save a fact to the facts file."""
    with open(FACTS_FILE, "a") as f:
        f.write(fact + "\n")

def view_saved_facts():
    """View all saved facts."""
    with open(FACTS_FILE, "r") as f:
        facts = f.readlines()
    return [fact.strip() for fact in facts]

def delete_fact(index):
    """Delete a saved fact by index."""
    facts = view_saved_facts()
    if 0 <= index < len(facts):
        deleted_fact = facts.pop(index)
        with open(FACTS_FILE, "w") as f:
            for fact in facts:
                f.write(fact + "\n")
        return deleted_fact
    return None

def clear_facts():
    """Clears all saved facts."""
    with open(FACTS_FILE, "w") as f:
        f.truncate(0)

def handle_request(request):
    """Handle requests from the client."""
    command = request.get('command')
    
    if command == "save":
        fact = request.get('fact')
        save_fact(fact)
        return "Fact saved."

    elif command == "view":
        facts = view_saved_facts()
        return {"facts": facts}

    elif command == "delete":
        index = request.get('index')
        deleted_fact = delete_fact(index)
        return deleted_fact if deleted_fact else "Invalid index."

    elif command == "clear":
        clear_facts()
        return "Facts cleared."

    return "Unknown command."

def main():
    # Set up ZMQ server
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")  # Bind to port 5555
    print("Fact saver service ready to receive at port 5555...")

    # Initialize facts file
    initialize_facts_file()

    while True:
        # Wait for the next request from the client
        request = socket.recv_json()
        print("Fact saver received request:", request)

        # Quit if request is to quit
        if request.get('command') == 'quit':
            break

        # Handle the request and send the response back to the client
        response = handle_request(request)
        socket.send_json(response)
        print("-------------------------------------------\n")
        print("Fact saver service ready to receive at port 5555...")

    # exit the server program
    context.destroy()
    
if __name__ == "__main__":
    main()
