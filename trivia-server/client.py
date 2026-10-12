"""
Interactive TCP client for the trivia server.

Usage:
    python3 client.py local                 # connect to a server on localhost
    python3 client.py cloud <server-host>   # connect to a remote server
"""

import sys
from socket import *
import json

LOCAL_HOST = "localhost"
LOCAL_PORT = 12345
REMOTE_PORT = 12345

class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.client_file = None

    def run(self):
        """Connect once, then play rounds until the user chooses to quit."""
        print("=====================================================================")
        print("                    University of Minnesota Trivia                   ")
        print("=====================================================================\n")
            
        print("\n------------------------- GAME INSTRUCTIONS -------------------------")
        print("  • Five random trivia questions about the University of Minnesota")
        print("    will be proposed to you along with possible answers.\n")
        
        print("  • Select your answer by entering the associated number (e.g., '1').\n")
        
        print("  • After all five questions have been answered, you will receive")
        print("    your total score.")

        # Open one TCP connection and reuse it across multiple game rounds.
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.server_host, self.server_port))
        self.client_file = self.client_socket.makefile("r")
        print(f"Connected to {self.server_host}:{self.server_port}")

        # Keep the same TCP connection open and let the user play multiple rounds.
        while(1):
            
            # Ask whether the user wants to start another round on the current connection.
            print("\nWould you like to start a new game? [y/n]: ")

            # Get the user's response.
            while (1):
                print("Input: ", end = "")
                st = input()

                if ((st != "y") and (st != "Y") and (st != "n") and (st != "N")):
                    continue
                else:
                    break
            
            # If the input is "n" or "N", then quit the program.
            if ((st == "n") or (st == "N")):
                
                # Tell the server this client is done before closing the socket.
                req = {"type": "quit"}
                self.client_socket.sendall((json.dumps(req) + "\n").encode())

                line = self.client_file.readline()
                # Wait for the server's acknowledgement before closing.
                self.client_file.readline()

                if self.client_file is not None:
                    self.client_file.close()
                if self.client_socket is not None:
                    self.client_socket.close()
                print("\nClient is exiting...")   
                sys.exit(0)

            else:
                # Ask the server to begin a new five-question game.
                req = {"type": "start_game"}
                self.client_socket.sendall((json.dumps(req) + "\n").encode())

                # Process the five question/result exchanges in the order sent by the server.
                for _ in range(5):
                    line = self.client_file.readline()
                    if not line:
                        print("Server disconnected.")
                        break

                    qmsg = json.loads(line.strip())
                    if qmsg.get("type") != "question":
                        print(f"Unexpected from server: {qmsg}")
                        break

                    qnum = qmsg.get("qnum", _ + 1)
                    print(f"\nQuestion {qnum}: {qmsg['question']}")
                    print("-" * 69)
                    for i, c in enumerate(qmsg["choices"], start=1):
                        print(f"  {i}) {c}")

                    # Re-prompt until the user selects one of the displayed choices.
                    while True:
                        ans = input("\nAnswer: ").strip()
                        if ans.isdigit() and 1 <= int(ans) <= len(qmsg["choices"]):
                            break

                    amsg = {"type": "answer", "qid": qmsg["qid"], "answer": ans}
                    self.client_socket.sendall((json.dumps(amsg) + "\n").encode())

                    line = self.client_file.readline()
                    if not line:
                        print("Server disconnected.")
                        break

                    rmsg = json.loads(line.strip())
                    if rmsg.get("type") != "result":
                        print(f"Unexpected from server: {rmsg}")
                        break
                    
                    if rmsg.get("correct"):
                        points = rmsg.get("score", 1)
                        if points == 1:
                            print("Correct answer! You scored 1 point.")
                        else:
                            print(f"Correct answer! You scored {points} points.")
                    else:
                        correct_value = rmsg.get("correct_answer")
                        correct_text = correct_value

                        # If the server sent the correct answer as a choice number,
                        # convert it into the actual answer text for display.
                        try:
                            idx = int(correct_value)
                            if 1 <= idx <= len(qmsg["choices"]):
                                correct_text = qmsg["choices"][idx - 1]
                        except (TypeError, ValueError):
                            pass
                        print(f"Wrong answer. The correct answer was '{correct_text}'.")
                
                # Receive the round summary only after all per-question exchanges are complete.
                line = self.client_file.readline()
                if line:
                    gmsg = json.loads(line.strip())
                    if gmsg.get("type") == "game_over":
                        print("\n----------------------------- GAME OVER -----------------------------")
                        total_score = gmsg.get("total_score")
                        if total_score == 1:
                            print("Total score: 1 point")
                        else:
                            print(f"Total score: {total_score} points")
                        print("\nThanks for playing!")


USAGE = "\nusage: python3 client.py local | python3 client.py cloud <server-host>\n"

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "local":
        client = Client(LOCAL_HOST, LOCAL_PORT)
    elif len(sys.argv) == 3 and sys.argv[1] == "cloud":
        client = Client(sys.argv[2], REMOTE_PORT)
    else:
        print(USAGE)
        sys.exit(1)

    client.run()