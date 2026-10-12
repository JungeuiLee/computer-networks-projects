# Event-driven network simulator. The Go-Back-N protocol logic is in
# sender.py and receiver.py.

class circular_buffer:
    ''' Represents the circular buffer that be used by the sender. '''
    def __init__(self, n):
        ''' 
        Initializes the relevant class variables of the circular buffer.
        
        Parameters
        ----------
        - n : int
            - The maximum number of packets that can be stored in the 
              circular buffer. 
        '''
        # The next slot in the circular buffer to remove a packet.
        self.read = 0
        # The next slot in the circular buffer to add a packet.
        self.write = 0
        # The maximum number of packets that can be stored in the circular 
        # buffer.
        self.max = n
        # The current number of packets stored in the circular buffer.
        self.count = 0
        # The data structure that actually stores the buffered packets.
        self.buffer = []
        # Initialize all entries in the buffer to NULL values.
        for i in range(n):
            self.buffer.append(None)

    def push(self, packet):
        ''' 
        Attempts to store a packet in the next available slot in the circular 
        buffer and updates the relevant class variables afterward. 
        
        Parameters
        ----------
        - packet : packet
            - The data packet that will be attempted to be stored in circular 
              buffer.
        '''
        if (self.count == self.max):
            return -1
        else:
            self.buffer[self.write] = packet

        self.write = (self.write + 1) % self.max
        self.count = self.count + 1
        return 0

    def pop(self):
        ''' Attempts to remove a pdata acket from the beginning of the 
            circular buffer and updates the relevant class variables. '''
        if (self.count == 0):
            return -1

        temp = self.buffer[self.read]
        self.read = (self.read + 1) % self.max
        self.count = self.count - 1
        return 0

    def read_all(self):
        ''' Returns a list containing all of the currently buffered 
            data packets. '''
        temp = []
        read = self.read
        for i in range(self.count):
            temp.append(self.buffer[read])
            read = (read + 1) % self.max
        return temp

    def print_buffer(self, calling_entity):
        ''' 
        Prints out the size of the circular buffer and the sequence numbers 
        of the currently buffered packets in a readable format. This will be 
        useful for debugging.
        
        Parameters
        ----------
        - calling_entity : char
            - Set to the character "S" or "R" to represent that the sender or 
              receiver, respectively, is the entity that wants to print out
              a circular buffer. With only unidirectional data transfer 
              required here, the sender should be the only one calling this function.
        '''
        print(f"  {calling_entity}:: Buffer size: {self.count}, Buffered Packets: [", end = "")
        
        index = 1
        for pkt in self.buffer:
            print(str(pkt.seqnum), end = "")
            if (index != self.count):
                print(", ", end = "")
            index += 1
        print("]")

    def is_full(self):
        ''' Determines if all slots in the circular buffer are currently 
            occupied. '''
        if (self.count == self.max):
            return True
        else:
            return False