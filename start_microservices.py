import subprocess
import time
import os
import signal

def start_microservice(script_name):
    try:
        # Start the microservice as a separate process
        process = subprocess.Popen(["python", script_name])
        print(f"Started {script_name} microservice.")
        return process
    except Exception as e:
        print(f"Failed to start {script_name}: {e}")
        return None

def stop_microservices(processes):
    for process in processes:
        if process:
            print(f"Stopping microservice with PID {process.pid}...")
            os.kill(process.pid, signal.SIGTERM)

if __name__ == "__main__":
    # List of microservice scripts to start
    microservices = [
        "fact_generator.py",
        "fact_saver.py",
        "generate_poem.py"
    ]

    processes = []

    # Start each microservice
    for service in microservices:
        process = start_microservice(service)
        processes.append(process)
        time.sleep(1)  # Add a slight delay to ensure they start properly

    print("All microservices are running.")

    try:
        # Wait for user input to stop the microservices
        while True:
            command = input("Type 'q' to stop all microservices and exit: ").strip().lower()
            if command == "q":
                stop_microservices(processes)
                print("All microservices stopped. Exiting.")
                break
    except KeyboardInterrupt:
        stop_microservices(processes)
        print("\nAll microservices stopped. Exiting.")
