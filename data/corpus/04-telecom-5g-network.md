# 5G Networks and Network Slicing

Fifth-generation mobile networks were designed for three broad classes of service: enhanced mobile broadband for high data rates, ultra-reliable low-latency communication for control systems, and massive machine-type communication for very large numbers of low-power devices.

Network slicing is the feature that lets one physical 5G network support all three classes at once. A network slice is a virtual network carved out of the shared physical infrastructure, with its own guaranteed bandwidth, latency budget, and capacity. An operator can run a slice tuned for video streaming traffic alongside a separate slice tuned for factory automation, and congestion in one slice does not consume the resources reserved for the other.

The 5G core is built as a set of software functions rather than fixed hardware appliances. The user plane function routes and forwards subscriber data traffic, while the access and mobility management function handles registration and handovers as devices move between radio cells.

At the radio layer, 5G uses wider channel bandwidths and massive MIMO antenna arrays, which form narrow beams toward individual devices. Beamforming improves signal quality and lets the same spectrum serve more users in dense areas such as stadiums.

Network slices are sold to enterprise customers as a managed product. A logistics company, for example, can buy a slice with a strict latency guarantee for its fleet trackers without building any radio infrastructure of its own.
