# Streaming Data Pipelines

A streaming pipeline processes records continuously as they arrive, instead of loading them in scheduled batches. Events are usually published to a distributed log, where they are retained in ordered partitions so consumers can replay them if a job fails.

Streaming jobs distinguish between event time, the moment an event actually occurred, and processing time, the moment the job observes it. Mobile devices and remote sensors often deliver events late or out of order, so results computed on event time need a policy for late data.

That policy is the watermark. A watermark is a timestamp threshold that declares the stream complete up to a point in time. When a streaming pipeline handles late-arriving events, it uses watermarks to decide how long to wait for stragglers before finalising a window. Events that arrive after the watermark plus the allowed lateness are typically sent to a side output for later inspection rather than silently dropped.

Stateful streaming jobs checkpoint their state periodically. A checkpoint is a consistent snapshot of operator state and log positions; if a worker crashes, the job restarts from the most recent checkpoint and replays only the events after it, which gives effectively-once results when sinks are idempotent.

Throughput is scaled by partitioning. A topic with twelve partitions can be consumed by up to twelve parallel workers, and the partition key determines which related events stay together in order, for example all events for one customer account.
