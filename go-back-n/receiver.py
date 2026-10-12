"""Go-Back-N receiver: delivers in-order packets, discards corrupted or
out-of-order packets, and re-ACKs the last in-order sequence number."""

from simulator import to_layer_five
from packet import send_ack

class R_receiver:
    ''' Represents the receiver in the Go-Back-N protocol. '''
    def __init__(self):
        ''' Initializes the relevant class variables for the receiver. '''
        

        # Statistics Counters
        #---------------------------------------------------------------------
        # Number of new ACKs the receiver sends to the Network Layer (layer 3).
        self.new_ACKs = 0
         # An ACK packet is lost when it never arrives at the sender.
        self.lost_ACKs = 0
        # An ACK is retransmitted if the receiver receives a data packet that 
        # is corrupted or has the wrong sequence number (i.e., the number of
        # NACKs sent by the receiver).
        self.retransmitted_ACKs = 0
        # A received data packet is uncorrupted (verified using the checksum)
        # and in-order.
        self.correct_data = 0
        # A received data packet is corrupted (verified using the checksum).
        self.corrupted_data = 0
        # A received data packet is out-of-order (i.e., has the wrong sequence
        # number).
        self.out_of_order_data = 0

        # Useful Variables
        #---------------------------------------------------------------------
        # The size of the sliding window.
        self.N = 7
        # Entity tag identifying the receiver to the simulator.
        self.entity = 'R'

        # next expected seqnum from sender
        self.expected_sequence_number = 0
        return

    def R_input(self, received_packet):
        ''' 
        The receiver received a data packet from layer 3. It should verify the
        received data packet and behave accordingly. 
        
        Parameters
        ----------
        - received_packet : packet
            - The received data packet that was sent by the sender.
        ''' 
        if received_packet.checksum != received_packet.get_checksum():
            # discard corrupted packet
            self.corrupted_data += 1
            # send NACK
            send_ack(self.entity, (self.expected_sequence_number - 1) % 8)
            self.retransmitted_ACKs += 1
        elif received_packet.seqnum != self.expected_sequence_number:
            # discard out-of-order packet
            self.out_of_order_data += 1

            # send NACK
            send_ack(self.entity, (self.expected_sequence_number - 1) % 8)
            self.retransmitted_ACKs += 1
        else:
            # deliver to layer 5
            to_layer_five(self.entity, received_packet.payload.data)
            send_ack(self.entity, received_packet.seqnum) # send ACK
            # rotate seqnum
            self.expected_sequence_number = (self.expected_sequence_number + 1) % 8
            self.correct_data += 1
            self.new_ACKs += 1
        return
    
    def R_lost_packet(self, lost_packet):
        '''
        This function is called by the simulator when a packet is lost. It
        updates the lost ACK counter.
        
        Parameters
        ----------
        - lost_packet : packet
            - An ACK packet that was lost in transit to the Sender.
        '''
        # count lost ACK packet
        self.lost_ACKs += 1
        return

    def R_sim_end(self):
        ''' Called at the end of the simulation. Prints out all of the 
            statistics tracked by the receiver. '''

        print("===========RECEIVER STATISTICS==========")
        print("  Sent ACKs")
        print("    New                  -> ", self.new_ACKs)
        print("    Lost                 -> ", self.lost_ACKs)
        print("    Retransmitted        -> ", self.retransmitted_ACKs)
        print("  Received Data")
        print("    Correct              -> ", self.correct_data)
        print("    Corrupted            -> ", self.corrupted_data)
        print("    Out of Order         -> ", self.out_of_order_data)
        print("")

b = R_receiver()