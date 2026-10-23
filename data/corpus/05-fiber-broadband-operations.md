# Fibre Broadband Network Operations

Fibre-to-the-home networks are usually built as a passive optical network. A single feeder fibre from the exchange is split by a passive optical splitter, commonly in a 1:32 or 1:64 ratio, so one exchange port serves dozens of homes without any powered equipment in the street cabinet.

The optical line terminal at the exchange transmits downstream traffic to every home on the splitter, and each home's optical network terminal selects only the traffic addressed to it. Upstream traffic is shared using time-division multiplexing, where each terminal transmits in assigned time slots.

Field engineers locate faults with an optical time-domain reflectometer, usually shortened to OTDR. An OTDR sends pulses of light into the fibre and measures the reflections that return. From the timing and strength of those reflections, the OTDR measures the distance to a fault, such as a break or a bad splice, often to within a few metres, so a repair crew can be sent to the right location the first time.

A common cause of degraded service is a dirty or poorly seated connector, which introduces insertion loss. Cleaning connectors and checking the optical power budget — the difference between transmitted power and the receiver sensitivity — is the first step in most fault investigations.

Operators monitor the optical power received at each home terminal continuously. A gradual decline in received power usually indicates a bending loss or a deteriorating splice, while a sudden drop to zero indicates a fibre cut.
