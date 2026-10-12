#!/usr/bin/env python
"""
Topology B: a 3-tier tree (1 core, 2 aggregation, 4 edge switches, 8 hosts)
with bandwidth and delay set per tier.

Usage:
  sudo python3 topology-b.py           # default Mininet controller
  sudo python3 topology-b.py remote    # use a remote controller (e.g. POX
                                       # running ethernet-learning)
"""

import sys

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.node import RemoteController

class TopologyB(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        
        # Link parameters per tier: L1 = core-aggregation,
        # L2 = aggregation-edge, L3 = edge-host.
        lvl1_bw = 150
        lvl2_bw = 65
        lvl3_bw = 20

        lvl1_delay = '45ms'
        lvl2_delay = '25ms'
        lvl3_delay = '10ms'


        # Add 8 hosts (h1-h8), 2 per edge switch
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')

        # Add 1 core switch (c1)
        c1 = self.addSwitch('c1')
        
        # Add 2 aggregation switches (a1, a2)
        a1 = self.addSwitch('a1')
        a2 = self.addSwitch('a2')
        
        # Add 4 edge switches (e1-e4), 2 per aggregation switch
        e1 = self.addSwitch('e1')
        e2 = self.addSwitch('e2')
        e3 = self.addSwitch('e3')
        e4 = self.addSwitch('e4')
        
        # L1 links: Connect core switch to aggregation switches (150Mbps, 45ms)
        self.addLink(c1, a1, bw=lvl1_bw, delay=lvl1_delay)
        self.addLink(c1, a2, bw=lvl1_bw, delay=lvl1_delay)

        # L2 links: Connect aggregation switches to edge switches (65Mbps, 25ms)
        self.addLink(a1, e1, bw=lvl2_bw, delay=lvl2_delay)
        self.addLink(a1, e2, bw=lvl2_bw, delay=lvl2_delay)
        self.addLink(a2, e3, bw=lvl2_bw, delay=lvl2_delay)
        self.addLink(a2, e4, bw=lvl2_bw, delay=lvl2_delay)

        # L3 links: Connect edge switches to hosts (20Mbps, 10ms)
        self.addLink(e1, h1, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e1, h2, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e2, h3, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e2, h4, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e3, h5, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e3, h6, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e4, h7, bw=lvl3_bw, delay=lvl3_delay)
        self.addLink(e4, h8, bw=lvl3_bw, delay=lvl3_delay)
 
        
if (__name__ == '__main__'):
    setLogLevel( 'info' )

    topo = TopologyB()
    if len(sys.argv) > 1 and sys.argv[1] == 'remote':
        net = Mininet(controller = RemoteController, topo = topo, link = TCLink, autoSetMacs = True, autoStaticArp = True)
    else:
        net = Mininet(topo = topo, link = TCLink, autoSetMacs = True, autoStaticArp = True)
    
    # Run network
    net.start()
    CLI( net )
    net.stop()