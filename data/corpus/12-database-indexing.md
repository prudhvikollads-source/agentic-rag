# Database Indexing and Query Performance

A database index is a separate data structure, usually a B-tree, that lets the engine find rows by an indexed column without scanning the whole table. The index stores the column values in sorted order together with pointers to the matching rows, so a lookup walks the tree in logarithmic time instead of reading every row.

Indexes are not free. Every insert, update, and delete must also maintain each index on the table, and each index consumes storage. A table with many indexes reads quickly in many different ways but writes more slowly, so indexes are added for queries that actually run, not for every column just in case.

A composite index covers two or more columns in a defined order. A composite index helps queries that filter on its leading column, and queries that filter on the leading column together with the next column. It does not help a query that filters only on the second column, because the entries are sorted first by the leading column. Column order in a composite index should therefore follow the filters of the most important queries.

A covering index includes every column a query needs, so the engine answers the query from the index alone and never visits the table rows. Covering indexes are especially effective for frequent, narrow queries on large tables.

Partial indexes index only the rows matching a condition, for example only orders that are still open. They are smaller and cheaper to maintain than a full index when queries almost always carry the same filter condition.
