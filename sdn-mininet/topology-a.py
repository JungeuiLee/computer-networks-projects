#!/usr/bin/env python
"""
Topology A: reference topology used for latency/throughput measurements.

Usage:
  sudo python3 topology-a.py           # default Mininet controller
  sudo python3 topology-a.py remote    # use a remote controller
"""

import sys

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.node import RemoteController

class TopologyA(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

	# Define all of the hosts.
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')
        h9 = self.addHost('h9')

	# Define each switch.
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')

	# Add links between each host and the switches.
        self.addLink(h1, s2)
        self.addLink(h2, s3)
        self.addLink(h3, s4)
        self.addLink(h4, s4)
        self.addLink(h5, s1)
        self.addLink(h6, s1)
        self.addLink(h7, s5)
        self.addLink(h8, s5)
        self.addLink(h9, s5)

	# Add links between the switches, with bandwidth (Mbps) and delay (ms)
        # constraints.
        self.addLink(s1, s2, bw = 30, delay = '10ms')
        self.addLink(s2, s3, bw = 20, delay = '40ms')
        self.addLink(s3, s4, bw = 40, delay = '30ms')
        self.addLink(s4, s5, bw = 10, delay = '20ms')
        

if (__name__ == '__main__'):
    setLogLevel( 'info' )
        
    # Create data network.
    topo = TopologyA()
    if len(sys.argv) > 1 and sys.argv[1] == 'remote':
        net = Mininet(controller = RemoteController, topo = topo, link = TCLink, autoSetMacs = True, autoStaticArp = True)
    else:
        net = Mininet(topo = topo, link = TCLink, autoSetMacs = True, autoStaticArp = True)

    # Run the network.
    net.start()
    CLI( net )
    net.stop()