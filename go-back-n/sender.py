"""Go-Back-N sender: sliding window of N=7 over a 3-bit (0-7) sequence space,
cumulative ACKs, and a single retransmission timer."""

from simulator import sim
from simulator import to_layer_three
from event_list import evl
from packet import *
from circular_buffer import circular_buffer

class S_sender:
    ''' Represents the sender in the Go-Back-N protocol. '''
    def __init__(self):
        ''' Initializes the relevant class variables for the sender. '''
        

        # Statistics Counters
        #---------------------------------------------------------------------
        # Number of Application Layer (layer 5) messages the sender receives.
        self.new_messages = 0
        # A layer 5 message is dropped when it's received while the sender's 
        # buffer is full.
        self.dropped_messages = 0
        # Number of new data packets sent by the sender.
        self.new_data = 0
        # A data packet is lost when it never arrives at the receiver.
        self.lost_data = 0
        # Data packets are retransmitted when a timer expires.
        self.retransmitted_data = 0
        # A received ACK is uncorrupted (verified using the checksum) and 
        # in-order.
        self.correct_ACKs = 0
        # A received ACK is corrupted (verified using the checksum).
        self.corrupted_ACKs = 0
        # A received ACK is out-of-window (i.e., has an acknowledgment number
        # not currently in the sender's window).
        self.out_of_window_ACKs = 0

        # Useful Variables
        #---------------------------------------------------------------------
        # The size of the sliding window and circular buffer.
        self.N = 7
        # The circular buffer that will store any outstanding and 
        # unacknowledged packets.
        self.c_b = circular_buffer(self.N)
        # Retransmission timeout passed to evl.start_timer().
        self.estimated_rtt = 30
        # Entity tag identifying the sender to the simulator.
        self.entity = 'S'

                # base of the sender's window
        self.window_base_number = 0
        # next sequence number to use
        self.next_sequence_number = 0
        return

    def S_output(self, message):
        '''
        The sender received a message from layer 5, so it should try to create
        a data packet containing the message and send it to the Network Layer
        (layer 3). 
        
        Parameters
        ----------
        - message : msg
            - The message the sender received from layer 5.
        '''
        # count all received messages from layer 5
        self.new_messages += 1

        if self.c_b.is_full():
            # drop message if window is full
            self.dropped_messages += 1
        else:
            # create new packet
            pck = packet(self.next_sequence_number, 0, message)

            # store in buffer for potential retransmission
            self.c_b.push(pck)

            # count new packets sent
            self.new_data += 1

            # send to network layer
            to_layer_three(self.entity ,pck)

            # start timer only if this is the only packet
            if self.c_b.count == 1:
                evl.start_timer(self.entity, self.estimated_rtt)
            self.next_sequence_number = (self.next_sequence_number + 1) % 8 # rotate seqnum 0~7
        return

    def S_input(self, received_packet):
        '''
        The sender received an ACK packet from layer 3. It should verify the
        received ACK and behave accordingly. 
        
        Parameters
        ----------
        - received_packet : packet
            - The received ACK packet that was sent by the receiver.
        '''
        # build list of seqnums currently in the window
        window_sequence_number = []
        for pkt in self.c_b.read_all():
            window_sequence_number.append(pkt.seqnum)

        if received_packet.checksum != received_packet.get_checksum():
            # discard corrupted ACK
            self.corrupted_ACKs += 1
        elif received_packet.acknum not in window_sequence_number:
            # discard out-of-window ACK
            self.out_of_window_ACKs += 1
        else:
            # valid ACK received
            self.correct_ACKs += 1

            # number of packets to pop
            count = window_sequence_number.index(received_packet.acknum) + 1
            for i in range(count):
                # remove ACKed packets from buffer (cumulative ACK)
                self.c_b.pop()
            
            if self.c_b.count == 0:
                # no more unACKed packets, stop timer
                evl.stop_timer()
            else:
                # restart timer for remaining packets
                evl.start_timer(self.entity, self.estimated_rtt)
        return

    def S_handle_timer(self):
        ''' Handles the expiration of the sender's timer. If this function
            is triggered, then it means that an ACK for any of the most 
            recently sent packets wasn't received by the sender in time, so 
            all currently outstanding and unacknowledged packets need to be 
            retransmitted. '''
        # get all buffered packets
        pcks = self.c_b.read_all()
        
        for pck in pcks:
            # retransmit all unACKed packets
            to_layer_three(self.entity ,pck)

            # count retransmission
            self.retransmitted_data += 1

        evl.start_timer(self.entity, self.estimated_rtt)
        return
    
    def S_lost_packet(self, lost_packet):
        '''
        This function is called by the simulator when a packet is lost. It
        updates the lost data packet counter.
        
        Parameters
        ----------
        - lost_packet : packet
            - A data packet that was lost in transit to the receiver.
        '''        
        # count lost packet
        self.lost_data += 1
        return

    def S_sim_end(self):
        ''' Called at the end of the simulation. Prints out all of the 
            statistics tracked by the sender. '''

        print("============SENDER STATISTICS===========")
        print("  Received Messages")
        print("    New                  -> ", self.new_messages)
        print("    Dropped              -> ", self.dropped_messages)
        print("  Sent Data")
        print("    New                  -> ", self.new_data)
        print("    Lost                 -> ", self.lost_data)
        print("    Retransmitted        -> ", self.retransmitted_data)
        print("  Received ACKs")
        print("    Correct              -> ", self.correct_ACKs)
        print("    Corrupted            -> ", self.corrupted_ACKs)
        print("    Out of Window        -> ", self.out_of_window_ACKs)
        print("")

a = S_sender()