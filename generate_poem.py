# Name: Kyle Odland
# Course: CS361
# A microservice that calls google gemini api to generate a poem, given a topic
# and a poetry style

import os
import zmq

import google.generativeai as genai

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# fetch the gemnini api key from the environmental variable
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# set parameters for gemini response
generation_config = {
  "max_output_tokens": 400,
  "response_mime_type": "text/plain",
}
# create AI model
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  generation_config=generation_config)

chat = model.start_chat(history=[])

# set up environment variable for ZMQ
context = zmq.Context()
# set up a reply socket for the server
socket = context.socket(zmq.REP)

port = 5225
port_str = str(port)
# bind the socket to a port number
socket.bind("tcp://*:" + port_str)
print("Server ready to receive at port " + port_str + "...")

while True:
    # receive request from client
    message = socket.recv_json()

    # get topic and style from json message from client
    topic = message['topic']
    style = message['style']

    if len(topic) > 0:
        # if the client sent Q, quit the server
        if topic.lower() == 'q':
            break
        # as long as topic isn't rg, set the request message for
        elif topic.lower() != 'rg':
            prompt = "write a poem about" + topic + "in the style of " + style

        # if the client wants a different poem, set request to have the same parameters
        else:
            prompt = "write a new version of the poem, with the same topic and style"

        # get a response from the Gemini API for the given prompt
        try:
            response = chat.send_message(prompt)
        except:
            response = "Could not generate poem, try again."

        # send message back to client
        socket.send_string(response.text)

# exit the server program
context.destroy()



