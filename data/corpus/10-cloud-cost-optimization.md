# Cloud Cost Optimisation

Cloud bills are dominated by a small number of services, so cost optimisation starts by tagging every resource with an owner and a project. Without tags, a bill can be reported only as a single total, and no team can be held accountable for its share.

Reserved capacity is the largest single saving lever for steady workloads. Under reserved capacity pricing, a team commits to using a given amount of compute for a one-year or three-year term, and in exchange receives a substantial discount compared with on-demand pricing for the same capacity. The trade-off is flexibility: the commitment is paid for whether or not the capacity is actually used, so reservations should cover only the stable baseline of a workload, never its peaks.

Rightsizing is the second lever. Monitoring data typically shows many virtual machines running at a small fraction of their provisioned CPU, and moving each workload to the smallest instance size that still meets its performance target cuts its hourly cost directly.

Storage costs are controlled with lifecycle policies. Objects that have not been accessed for a defined period are moved automatically to cheaper archive storage tiers, and temporary objects such as build outputs are deleted by rule after a short retention window.

Idle resources are the purest waste. Development environments that run overnight and at weekends can be stopped on a schedule, which removes roughly two thirds of their running hours without affecting anyone's working day.
