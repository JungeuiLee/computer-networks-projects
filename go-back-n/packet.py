# Event-driven network simulator. The Go-Back-N protocol logic is in
# sender.py and receiver.py.

from simulator import to_layer_three

class packet:
    ''' Represents the (data and ACK packets that are sent across the 
        simulated network. '''
    def __init__(self, seqnum = 0, acknum = 0, payload = 0):
        ''' 
        Initializes the relevent class variables for the packet class. 
        
        Parameters
        ----------
        - seqnum : int
            - The packet's sequence number. This field should only be set by 
              the sender when it creates a new data packet. The default value
              is 0.
        - acknum : int
            - The packet's acknowledgment (ACK) number. This field should 
              only be set by the receiver when it creates a new ACK or NACK
              packet. The default value is 0.
        - payload : msg
            - The Application Layer message that was passed down to the 
              Transport Layer protocol.
        '''
        # The packet's sequence number.
        self.seqnum = seqnum
        # The packet's acknowledgment number.
        self.acknum = acknum
        # The packet's payload which contains an Application Layer message.
        self.payload = payload
        # The packet's checksum. This is automatically calculated when a 
        # is first created packet.
        self.checksum = self.get_checksum() 

    def get_checksum(self):
        ''' Computes the checksum of a packet's current contents and it can be 
            used to verify the checksum stored within a received packet. '''
        checksum = 0
        if (self.payload != 0):
            for i in range(20):
                checksum = checksum + ord(self.payload.data[i])
        
        checksum = checksum + self.seqnum + self.acknum
        return checksum

def send_ack(calling_entity, acknowledgment_number):
    ''' 
    Sends an ACK on behalf of the calling entity. This function can also be
    used to send a NACK implicitly by sending an ACK with the last expected 
    sequence number. If the currently expected sequence number is 0, then 
    last expected sequence number would be N because of the rotating sequence
    numbers.
    
    Parameters
    ----------
    - calling_entity : char
        - Set to the character "S" or "R" to represent that the sender or 
          receiver, respectively, is the entity that wants to send an ACK.
          With only unidirectional data transfer required here, the
          receiver should be the only one calling this function.
    - acknowledgment_number : int
        - The number of the acknowledgment being sent to the sender.
    '''
    pkt = packet(acknum = acknowledgment_number)
    to_layer_three(calling_entity, pkt)