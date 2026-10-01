# Validation record

## Public implementation baseline

Repository: `dexter02-crypt/csv-quality-report`

Baseline `main` commit:

`e450105056a164eb57e429885126f55d5e791769`

GitHub Actions run `36764877890` completed successfully on that exact commit.

The six successful jobs were:

- macOS / Python 3.11
- macOS / Python 3.13
- macOS / Python 3.14
- Ubuntu / Python 3.11
- Ubuntu / Python 3.13
- Ubuntu / Python 3.14

Each job checked out the repository, configured Python, processed the dependency file and ran:

`python -m unittest discover -s tests -v`

## Test coverage

The release-candidate local suite contains **24 test methods**.

Coverage includes:

- expected metrics from the synthetic example
- numeric summaries and zero handling
- missing-value semantics
- whitespace-normalized duplicate detection
- header-only and blank-record behavior
- UTF-8 BOM and Unicode input
- quoted commas and embedded newlines
- alternate delimiters
- invalid/duplicate headers
- malformed and ragged records
- row, column and byte limits
- invalid delimiters
- non-finite and expression-like numeric text
- HTML escaping and restrictive CSP output
- JSON/HTML output round-trip
- refusal to overwrite existing output directories
- input preservation and real profile CLI execution
- invalid encoding rejection
- snapshot comparison for column additions/removals, type changes, missing-rate shifts and row-count changes
- package version identity for v1.1.0
- real comparison-CLI execution, HTML/JSON output creation and source-file preservation

Release-preparation commit `c6d2bdbcdaec085e42714f31dc462535bae9b1dc` expanded the matrix to Python 3.11, 3.12, 3.13 and 3.14 on both Ubuntu and macOS.

Push run `36861674114` and pull-request run `36861729732` each completed all eight jobs successfully. This establishes hosted CI evidence for the expanded matrix on that exact implementation candidate.

Later documentation-only evidence updates still require their own fresh CI before integration.

## Demonstration

The supplied synthetic `examples/orders.csv` produces:

- 12 data rows
- 6 columns
- 4 missing cells
- 1 duplicate row after the first occurrence

`docs/example-report/` contains generated report artifacts and `docs/demo.png` shows the generated HTML example.

## Boundaries

The application uses Python standard-library modules only.

It accepts UTF-8 CSV input and does not parse Excel workbooks or guess delimiters. Default limits are 20 MiB, 100,000 nonblank records and 200 columns. Data is retained in memory within those limits.

HTML output escapes dynamic values and contains no application JavaScript or external assets. The tool reports observations and does not silently repair the source dataset.

GitHub Actions evidence demonstrates the listed hosted runner/Python combinations only. It is not proof of universal input correctness, performance on arbitrary data, production readiness or business meaning of detected changes.
