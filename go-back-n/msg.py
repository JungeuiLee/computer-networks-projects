# Event-driven network simulator. The Go-Back-N protocol logic is in
# sender.py and receiver.py.

class msg:
    ''' Represents the Application Layer (layer 5) message that's passed down 
        to the Transport Layer protocol. '''
    def __init__(self, i):
        ''' 
        Initializes the data within the message to be a string that contains 
        20 copies of the same character. For example, 'aaaaaaaaaaaaaaaaaaaa'. 
        
        Parameters
        ----------
        - i : char
            - The character that will be used to create the data string in
              the message.
        '''
        temp = str(i)
        self.data = ""
        for i in range(20):
            self.data = self.data + temp