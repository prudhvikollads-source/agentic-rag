# Cloud Data Warehouse Architecture

A cloud data warehouse separates storage and compute into independent layers. Data is stored once in low-cost object storage, while compute clusters can be scaled up, scaled down, or paused without copying the data. Because storage and compute scale independently, a team can add query capacity during a reporting peak without paying to duplicate the underlying dataset.

Tables are stored in a columnar format, which means the engine reads only the columns a query references instead of scanning entire rows. Columnar storage also compresses well because values in a single column share the same data type and similar value ranges.

Internally, data is organised into micro-partitions, which are small contiguous units of storage that carry metadata about the value ranges they contain. The query optimiser uses micro-partition metadata for partition pruning, skipping partitions that cannot match the filters in a query.

When the exact same query is executed again, the warehouse can serve the answer from a result cache. Cached query results are retained for 24 hours, provided the underlying data has not changed. If any table used by the query is updated, the cached result is invalidated immediately.

Workloads are isolated by assigning them to separate virtual warehouses. An extract-transform-load job running on one virtual warehouse does not compete for resources with a business-intelligence dashboard running on another, so a heavy load job cannot slow down interactive queries.

Access control is role-based. Analysts are granted read access to curated schemas, while raw ingestion schemas are writable only by the data engineering service accounts that run the loading pipelines.
