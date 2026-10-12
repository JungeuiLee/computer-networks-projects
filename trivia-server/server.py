"""
Multithreaded TCP trivia server.

Each client connection is handled in its own thread. Client and server
exchange newline-delimited JSON messages (start_game, question, answer,
result, game_over, quit).

Usage:
    python3 server.py local   # bind to localhost for local testing
    python3 server.py cloud   # bind to 0.0.0.0 so remote clients can connect
"""

import sys, os
from socket import *
import time
import json
import random
import signal
import threading

# Local testing: clients and server on the same machine.
LOCAL_HOST = "localhost"
LOCAL_PORT = 12345

# Cloud deployment: listen on all interfaces for remote clients.
REMOTE_HOST = "0.0.0.0"
REMOTE_PORT = 12345

class Server:
    def __init__(self, server_host, server_port):
        """Create the listening socket and load the question bank."""
        self.server_host = server_host
        self.server_port = server_port

        # Create the TCP listening socket used to accept client connections.
        self.server_socket = socket(AF_INET, SOCK_STREAM)

        # Load the trivia question bank once when the server starts.
        with open("trivia_questions.json", "r") as f:
            self.questions = json.load(f)

    def run(self):
        """Accept clients forever, spawning one thread per connection."""
        # Bind the listening socket to the selected host/port and begin listening.
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(5)
        print(f"Server running on {self.server_host}:{self.server_port}")

        # Accept connections forever; each client is handled in its own thread.
        while True:
            print("Waiting for client connection...")
            connection_socket, client_address = self.server_socket.accept()
            print(f"Connected to {client_address}")

            # Start a separate thread so multiple clients can play at the same time.
            client_thread = threading.Thread(
                target=self.trivia_game,
                args=(connection_socket, client_address),
                daemon=True
            )
            client_thread.start()

    def trivia_game(self, connection_socket, client_address):
        """Run trivia rounds with one client until it quits or disconnects.

        Each round sends five random questions, scores each answer, and ends
        with a game_over summary. The same connection is reused for
        additional rounds.
        """
        # Wrap the socket in a file-like reader so each JSON message can be read line by line.
        conn_file = connection_socket.makefile("r")
        try:
            # Keep serving this client until it disconnects or sends a quit request.
            while True:
                line = conn_file.readline()
                if not line:
                    print(f"[{client_address}] disconnected")
                    break

                msg = json.loads(line.strip())
                mtype = msg.get("type")

                # Start one new trivia round and track the client's total score for that round.
                if mtype == "start_game":
                    # Choose five distinct questions for this game instance.
                    total_score = 0
                    selected_qids = random.sample(list(self.questions.keys()), 5)

                    # Send each question, receive one answer, then return the scoring result.
                    for qid in selected_qids:
                        # Send the question text and its multiple-choice options to the client.
                        qtext, choices, correct = self.questions[qid]

                        qmsg = {
                            "type": "question",
                            "qid": qid,
                            "question": qtext,
                            "choices": choices
                        }
                        connection_socket.sendall((json.dumps(qmsg) + "\n").encode())

                        # Read the client's answer for the current question.
                        ans_line = conn_file.readline()
                        if not ans_line:
                            break
                        ans_msg = json.loads(ans_line.strip())

                        # Compare the selected choice number with the correct choice number.
                        user_answer = str(ans_msg.get("answer", ""))
                        is_correct = (user_answer == str(correct))
                        score = 1 if is_correct else 0
                        total_score += score

                        # Return the per-question result so the client can display feedback.
                        rmsg = {
                            "type": "result",
                            "correct": is_correct,
                            "correct_answer": str(correct),
                            "score": score
                        }
                        connection_socket.sendall((json.dumps(rmsg) + "\n").encode())

                    # After all five questions, send the round summary to the client.
                    gmsg = {
                        "type": "game_over",
                        "total_score": total_score,
                        "total_questions": 5
                    }
                    connection_socket.sendall((json.dumps(gmsg) + "\n").encode())

                # Acknowledge the quit request so both sides can close cleanly.
                elif mtype == "quit":
                    resp = {"type": "ack", "message": "bye"}
                    connection_socket.sendall((json.dumps(resp) + "\n").encode())
                    break

                # Reject unexpected message types to keep the protocol predictable.
                else:
                    resp = {"type": "error", "message": "unknown_type"}
                    connection_socket.sendall((json.dumps(resp) + "\n").encode())
        # Log unexpected per-client errors, then close this client's resources.
        except Exception as e:
            print(f"[{client_address}] Error: {e}")
        # Always close the socket and file wrapper for this client thread.
        finally:
            conn_file.close()
            connection_socket.close()

    def signal_handler(self, sig, frame):
        """Close the listening socket on Ctrl+C so the port is freed."""
        print('\nReceived signal: ', sig)
        print('Performing cleanup...')
        try:
            if self.server_socket is not None:
                self.server_socket.close()
        except Exception as e:
            print(f"Cleanup error: {e}")
        print('Exiting gracefully.')
        sys.exit(0)

USAGE = "\nusage: python3 server.py [local | cloud]\n"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)

    option = sys.argv[1]
    if option in ("local", "1"):
        server = Server(LOCAL_HOST, LOCAL_PORT)
    elif option in ("cloud", "2"):
        server = Server(REMOTE_HOST, REMOTE_PORT)
    else:
        print(USAGE)
        sys.exit(1)

    # Release the port cleanly on Ctrl+C.
    signal.signal(signal.SIGINT, server.signal_handler)
    server.run()