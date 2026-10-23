# API Design and Pagination

A well-designed HTTP API models resources as nouns, uses standard methods for operations on them, and returns consistent error bodies that include a machine-readable error code, a human-readable message, and the identifier of the request that failed.

List endpoints must paginate, because an unbounded list response grows slower and heavier as the table grows. The two common schemes are offset pagination and cursor pagination. Offset pagination asks for a page number and a page size, and the server skips the corresponding number of rows.

Cursor pagination works differently. The server returns an opaque cursor with each page, and the client sends that cursor back to fetch the next page. Because the cursor encodes the position of the last row returned, cursor pagination stays stable when rows are inserted or deleted while a client is paging: no item is skipped and none is returned twice. Offset pagination cannot offer that stability, because inserting a row before the current offset shifts every subsequent page by one.

Versioning protects existing clients from breaking changes. The common approach places the major version in the URL path, and only breaking changes — removing a field, changing a type — require a new major version. Adding an optional field is not breaking and does not need one.

Rate limiting is communicated, not just enforced. Responses include headers stating the limit, the remaining allowance, and the time at which the allowance resets, so well-behaved clients can slow down before they are rejected with a 429 response.
