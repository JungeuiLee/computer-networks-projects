# Event-driven network simulator. The Go-Back-N protocol logic is in
# sender.py and receiver.py.
# Tune nsimmax, lossprob, corruptprob, and Lambda below to change the scenario.

from msg import *
from event_list import *
from event import *

import random
import copy

class simulator:
    ''' Simulates a network's behavior. '''
    def __init__(self):
        ''' 
        Initializes the relevant class variables of the simulator.
        '''
        self.nsim = 0   # The number of messages passed down from layer 5 to 
                        # layer 4 so far.
        self.time = 0.0 # Used for calculating the total time the simulation
                        # took to complete.

        # Simulation parameters: number of messages, loss/corruption
        # probability, and message arrival rate.
        self.nsimmax = 20  # The number of Application Layer (layer 5) 
                           # messages to generate, then stop the simulation.
        self.lossprob = 0.0  # The probability that a packet is dropped.
        self.corruptprob = 0.0  # The probability that one bit in a packet is 
                                # flipped / corrupted.
        self.Lambda = 500  # The arrival rate of messages from layer 5.
       
        self.envlist = evl
        self.generate_next_arrival()  # Initialize the event list.

    def generate_next_arrival(self):
        ''' Initializes the simulator's event list. '''
        if (self.nsim >= (self.nsimmax - 1)):
            return
        time = self.time + self.Lambda
        self.envlist.insert(event(time, "FROM_LAYER5", "S"))
        return

    def run(self):
        ''' Run the network simulation by actualizing all of the events in 
            the event list. '''
        while (1):
            env = self.envlist.remove_head()
            if (env == None):
                print("\n  Simulation complete...\n")
                self.endTime = self.time
                from sender import a
                from receiver import b
                
                print("  Final Simulation Time  -> ", self.endTime)
                print()
                a.S_sim_end()
                b.R_sim_end()
                return
            else:
                self.time = env.evtime

            if (env.evtype == "FROM_LAYER5"):
                self.generate_next_arrival()
                ch = chr(97 + self.nsim % 26)
                m = msg(ch)
                self.nsim = self.nsim + 1
                if (env.eventity == "S"):
                    from sender import a
                    a.S_output(m)
                else:
                    from receiver import b
                    b.R_output(m)

            elif (env.evtype == "FROM_LAYER3"):
                pkt2give = env.pkt
                if (env.eventity == "S"):
                    from sender import a
                    a.S_input(pkt2give)
                else:
                    from receiver import b
                    b.R_input(pkt2give)

            elif (env.evtype == "TIMER_INTERRUPT"):
                if (env.eventity == "S"):
                    from sender import a
                    a.S_handle_timer()
                else:
                    b.R_handle_timer()

            else:
                print("!!!!!!!????")

def to_layer_three(calling_entity, packet):
    ''' 
    Sends a packet to the calling entity's Network Layer (layer 3).

    Parameters
    ----------
    - calling_entity : char
        - Set to the character "S" or "R" to represent that the sender or 
          receiver, respectively, is the entity that is sending the packet to 
          layer 3.
    - packet : packet
        - The data or ACK packet that is being sent to layer 3.
    '''
    # Apply loss probability to the packet.
    if (random.uniform(0, 1) < sim.lossprob):
        if (calling_entity == "S"):
            from sender import a
            a.S_lost_packet(packet)
        else:
            from receiver import b
            b.R_lost_packet(packet)
        return

    pkt = copy.deepcopy(packet)

    # Apply corruption probability to the packet.
    if (random.uniform(0, 1) < sim.corruptprob):
        if (pkt.payload != 0):
            pkt.payload.data = pkt.payload.data[0:-1] + "1"
        else:
            pkt.seqnum = -1

    q = sim.envlist.head
    lasttime = sim.time
    while (q != None):
        if ((q.eventity != calling_entity) and (q.evtype == "FROM_LAYER3")):
            lasttime = q.evtime

        q = q.next

    eventime = lasttime + 1 + 9 * random.uniform(0, 1)
    if (calling_entity == "S"):
        sim.envlist.insert(event(eventime, "FROM_LAYER3", "R", pkt))
    else:
        sim.envlist.insert(event(eventime, "FROM_LAYER3", "S", pkt))

def to_layer_five(calling_entity, message):
    '''
    Passes the received message to layer 5.

    Parameters
    ----------
    - calling_entity : char
        - Set to the character "S" or "R" to represent that the sender or 
          receiver, respectively, is the entity that received this message.
          With only unidirectional data transfer required here, the
          receiver should be the only one calling this function.
    - message : str
        - The data inside the Application Layer message that the calling 
          entity received.
    '''
    print(f"  {calling_entity}:: Data received： {message}")

sim = simulator()