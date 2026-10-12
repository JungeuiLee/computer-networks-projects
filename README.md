# Computer Networks Projects

Three networking projects in Python, each working at a different layer of the stack:

| Project | Layer | What it does |
|---|---|---|
| [`trivia-server/`](trivia-server) | Application | Multithreaded TCP trivia game server and client with a JSON message protocol, deployed on a cloud VM |
| [`go-back-n/`](go-back-n) | Transport | Go-Back-N reliable data transfer over a simulated channel with packet loss and corruption |
| [`sdn-mininet/`](sdn-mininet) | Link / SDN | Mininet topologies with per-link bandwidth and delay, plus a POX OpenFlow controller that acts as a self-learning Ethernet switch |

---

## 1. Trivia Server (TCP sockets)

A trivia game where multiple clients play at the same time against one server.

- **Concurrency:** the server accepts connections on one socket and hands each client to its own thread.
- **Protocol:** client and server exchange newline-delimited JSON messages: `start_game`, `question`, `answer`, `result`, `game_over`, `quit`. Each game asks five random questions and scores the answers.
- **Deployment:** ran on a Google Cloud VM, reachable from remote clients through a firewall rule on TCP port 12345.

```bash
cd trivia-server
python3 server.py local                 # or: python3 server.py cloud  (binds 0.0.0.0)
python3 client.py local                 # or: python3 client.py cloud <server-host>
```

## 2. Go-Back-N Reliable Transfer

The sender and receiver of a Go-Back-N protocol, running on top of an event-driven network simulator that can drop or corrupt packets.

- **Window and sequence numbers:** window size N = 7 over a 3-bit sequence space (0–7, mod 8), with sent-but-unacknowledged packets kept in a circular buffer.
- **Cumulative ACKs:** an in-order, uncorrupted ACK slides the window forward past every packet it covers. Corrupted or out-of-window ACKs are ignored.
- **Single timer:** one retransmission timer for the oldest unacknowledged packet. When it expires, every packet in the window is resent.
- **Receiver:** delivers only in-order, checksum-valid packets. When a packet is corrupted or out of order, it re-sends the ACK for the last in-order sequence number.
- **Statistics:** the sender counts new and dropped messages, lost and retransmitted packets, and correct, corrupted, and out-of-window ACKs, so behavior can be compared across loss and corruption rates.

```bash
cd go-back-n
python3 main.py        # tune nsimmax / lossprob / corruptprob / Lambda in simulator.py
```

**Implemented:** `sender.py`, `receiver.py`.

## 3. SDN with Mininet and POX

### Topologies and measurements

The topologies are built with Mininet `TCLink`s that have fixed bandwidth and delay. Latency is measured with `ping` and throughput with `iperf`.

**Topology A**: per-link measurements

| Link | Latency (ms) | Throughput (Mbps) |
|---|---|---|
| L1 | 10.98 | 28.5 |
| L2 | 42.08 | 18.5 |
| L3 | 31.73 | 37.3 |
| L4 | 21.57 | 9.49 |

**Topology B**: a 3-tier tree with 1 core switch, 2 aggregation switches, 4 edge switches, and 8 hosts.

| Tier | Configured | Derived latency (ms) |
|---|---|---|
| L1 (core–aggregation) | 150 Mbps / 45 ms | 46.49 |
| L2 (aggregation–edge) | 65 Mbps / 25 ms | 26.74 |
| L3 (edge–host) | 20 Mbps / 10 ms | 10.69 |

End-to-end throughput between hosts stays below the 20 Mbps edge links (18.9 / 18.1 / 13.7 Mbps measured), because every host-to-host path goes through an L3 link. Each link latency was derived by subtracting the measured round-trip times of shorter paths from longer ones.

### Self-learning switch controller (`ethernet-learning.py`)

A POX controller that turns every OpenFlow switch into a learning switch.

1. On each `PacketIn`, the controller records which port reaches the source MAC address, separately for each switch.
2. **Destination known:** the controller installs two `ofp_flow_mod` rules, forward (`src→dst`) and reverse (`dst→src`), so later packets are switched without contacting the controller. Packets whose output port equals their input port are dropped.
3. **Destination unknown:** the controller floods the packet with `OFPP_FLOOD` and installs no rule.

Result on Topology C: `pingall` had 0% packet loss. 19 packets reached the controller and 4 were flooded. Only the first ping of each pair shows extra latency, from the controller round trip; after that the installed flow rules take over.

```bash
# terminal 1 (POX): copy ethernet-learning.py into pox/ext/, then
./pox.py ethernet-learning

# terminal 2
sudo python3 sdn-mininet/topology-c.py           # or topology-a.py / topology-b.py remote
mininet> pingall
```

**Implemented:** `ethernet-learning.py`, `topology-b.py`.
