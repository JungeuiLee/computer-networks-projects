# Event-driven network simulator. The Go-Back-N protocol logic is in
# sender.py and receiver.py.

class event:
    ''' Represents an event that occurs in the simulation. '''
    def __init__(self, evtime, evtype, eventity, pkt = None):
        ''' 
        Initializes the relevant class variables of an event.
        
        Parameters
        ----------
        - evtime : float
            - Event time.
        - evtype : str 
            - Event type code (e.g., "FROM_LAYER5", "FROM_LAYER3", or 
              "TIMER_INTERRUPT").
        - eventity : char
            - Set to the character "S" or "R" to represent that the sender or 
              receiver, respectively, is the entity this event is for.
        - pkt : packet
            - A pointer to a packet (if any) that's associated with this event.
        '''
        self.evtime = evtime
        self.evtype = evtype
        self.eventity = eventity
        self.pkt = pkt
        self.prev = None
        self.next = None