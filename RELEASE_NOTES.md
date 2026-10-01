# csv-quality-report 1.1.0

CSV Quality Report is a small offline Python tool for profiling CSV files and comparing two CSV snapshots. It uses the Python standard library only and does not upload input data.

## Highlights

- Generates self-contained offline HTML and JSON quality reports.
- Measures missing cells, duplicate normalized rows, distinct values and frequent values.
- Suggests numeric, text/mixed or empty column types.
- Reports numeric minimum, maximum and mean for finite numeric columns.
- Adds two-snapshot comparison for added/removed columns, suggested-type changes, missing-rate shifts, distinct-value shifts and row-count changes.
- Preserves input files and refuses to overwrite an existing output directory.
- Escapes report content and emits HTML without external scripts or network assets.

## Validation

The public `main` implementation at `e450105056a164eb57e429885126f55d5e791769` passed GitHub Actions run `36764877890`.

That run completed successfully across six jobs:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.13
- Ubuntu / Python 3.14
- macOS / Python 3.11
- macOS / Python 3.13
- macOS / Python 3.14

The release-candidate local suite contains 24 unit and CLI-level test methods covering sample metrics, UTF-8/BOM handling, Unicode, quoted fields/newlines, malformed rows, numeric boundaries, HTML escaping, input limits, output preservation, package-version identity, CSV-profile comparison behavior, and real comparison-CLI execution.

The release-candidate workflow adds Python 3.12 to the Ubuntu/macOS matrix. That new eight-job matrix is not treated as passing evidence until the release branch runs successfully on GitHub Actions.

## Scope

This is a bounded local data-quality reporting tool, not a spreadsheet engine, data-cleaning system, schema registry or big-data platform.

Type inference is descriptive rather than authoritative. Numeric-looking identifiers may be classified as numeric. Reports can contain source column names and frequent values, so exported reports may themselves be sensitive.
