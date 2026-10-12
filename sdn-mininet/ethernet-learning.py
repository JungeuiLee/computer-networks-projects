#!/usr/bin/env python
"""
POX OpenFlow controller that turns every connected switch into a
self-learning Ethernet switch.

For each PacketIn the controller learns (switch, source MAC) -> input port.
If the destination MAC is already known on that switch, it installs a pair of
flow rules (forward and reverse) so later traffic is switched in hardware;
otherwise it floods the packet without installing any rule.

Usage (from the POX directory):  ./pox.py ethernet-learning
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
import re

log = core.getLogger()

flood_counter = 0
packets_received = 0

# switch ID -> {MAC address -> port number}: which port on each switch
# reaches each host.
mac_table = {}


def _handle_PacketIn(event):
  '''
  Handle an OFPacketIn message that a switch has sent to the controller 
  because the switch doesn't have a matching rule for the packet it received.
  '''
  global flood_counter
  global packets_received
  global mac_table
  packets_received += 1
  log.info('Number of packets received so far: {}'.format(packets_received))
  
  # Extract the port the packet came in on for the switch that's contacting 
  # the controller.
  packet_input_port = event.port

  # Ports a flood would go out of (all ports except the input port and the
  # switch's local port).
  other_ports = len(event.connection.ports) - 2

  # Use POX to parse the packet.
  packet = event.parsed

  # Extract the packet's source and destination MAC addresses.
  src_mac = str(packet.src)
  dst_mac = str(packet.dst)

  # Packets with a destination MAC address that starts with "33:33:" are
  # invalid, so they're immediately dropped by the controller.
  pattern = r"33:33:"
  match = re.search(pattern, dst_mac) 
  if match:
    return

  # Extract the sending switch's ID.
  switch_ID = str(event.connection.dpid) + str(event.connection.ID)
  
  log.info('Packet has arrived: SRCMAC:{} DSTMAC:{} from switch:{} in-port:{}'.format(src_mac, dst_mac, switch_ID, packet_input_port))

  # Learn which port on this switch reaches the source MAC.
  if switch_ID not in mac_table:
    mac_table[switch_ID] = {}
  if src_mac not in mac_table[switch_ID]:
    mac_table[switch_ID][src_mac] = packet_input_port

  # Known destination: install forward and reverse flow rules and send the
  # original packet out the learned port.
  if dst_mac in mac_table.get(switch_ID, {}):
    output_port = mac_table[switch_ID][dst_mac]
    
    # Drop the packet if input and output ports are the same (loop prevention)
    if output_port == packet_input_port:
      return
    
    # Rule 1: Forward packets from src to dst out the correct output port
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match(dl_src=packet.src, dl_dst=packet.dst)
    msg.actions.append(of.ofp_action_output(port=output_port))
    msg.data = event.ofp
    event.connection.send(msg)
    
    # Rule 2: Install reverse rule to forward reply packets from dst back to src
    msg2 = of.ofp_flow_mod()
    msg2.match = of.ofp_match(dl_src=packet.dst, dl_dst=packet.src)
    msg2.actions.append(of.ofp_action_output(port=packet_input_port))
    event.connection.send(msg2)

  # Unknown destination: flood out every port except the input port.
  # No flow rules are installed in this case.
  else:
    # Update the flood counter by the number of ports flooded
    flood_counter += other_ports
    log.info('Flooded messages so far: {}'.format(flood_counter))
    
    # Send a packet-out message instructing the switch to flood
    msg = of.ofp_packet_out()
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    msg.data = event.ofp
    msg.in_port = event.port
    event.connection.send(msg)



def launch ():
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Self-learning switch controller running.")