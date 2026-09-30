# Design notes

A bounded byte read avoids trusting a file's old size. Python's strict CSV
reader handles delimiters and quoted newlines. Header validation runs before
statistics so duplicate column names cannot silently overwrite one another.
A tuple set counts duplicate normalized rows; one Counter per column supports
missingness, distinct values, and frequency summaries.

The report is a plain dictionary, independent of the renderer. That gives the
JSON export and HTML table a single source of truth. Decimal is used rather
than float for the numeric summaries; non-finite and extremely large values
remain text. All dynamic HTML text is escaped, and the output has a restrictive
content-security policy with no script or network permissions.

Time is approximately proportional to total cell content. Memory depends on
unique rows and column values, not only file size. The explicit caps are a
small-tool boundary, not a promise of constant memory.

Three questions to explain: why "0" is not missing; how a quoted newline
differs from a record boundary; why numeric-looking account IDs should not be
silently converted. A small extension would add an explicit list of required
columns, with a test for a missing required column.
