# Data Lakehouse Fundamentals

A data lakehouse combines the low-cost object storage of a data lake with the management features of a data warehouse. Files remain in open formats such as Parquet, but a table format layer adds structure and guarantees on top of those files.

The table format layer adds transactions to the lake. Writers commit changes atomically, so readers never observe a half-written table. The same layer provides schema enforcement, which rejects writes whose columns do not match the declared table schema, and schema evolution, which allows columns to be added in a controlled way.

Time travel is another lakehouse feature. Because every commit is recorded in a transaction log, a query can read the table as it existed at an earlier version or timestamp. Time travel is widely used to reproduce a report exactly as it was generated last week and to recover from an accidental delete.

The typical lakehouse layout has three zones. The bronze zone holds raw data exactly as it arrived from source systems. The silver zone holds cleaned and deduplicated records with consistent types. The gold zone holds aggregated, business-ready tables that analysts query directly.

Unlike a traditional warehouse, a lakehouse keeps data in open file formats, so multiple engines — a SQL engine, a Spark job, or a machine learning training run — can read the same tables without exporting copies between systems.
