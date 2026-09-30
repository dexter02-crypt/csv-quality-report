# Validation record

## Executed here

- Environment: Linux, CPython 3.13.5.
- Command: `python -B -m unittest discover -s tests -v`.
- Result: **18 tests passed**, zero failed, zero skipped.
- Full captured test output: [test-output.txt](test-output.txt).

The application and its tests use Python standard-library modules only.

The included `setup.sh` was also executed in a fresh, isolated project copy: it created a new virtual environment and passed all tests without third-party dependencies.

## Actual demonstration

The supplied synthetic CSV produces 12 rows, six columns, four missing cells and one duplicate row after the first occurrence. `docs/example-report/report.html` and `report.json` are actual application outputs. `docs/demo.png` was rendered from that generated HTML using headless Chromium in-memory; it is not a Mac/browser-installation test. The HTML contains six rendered column-summary rows and no scripts.

## Boundaries

macOS installation, your local GUI/file-opening behavior, successful live webcam
capture, real GitHub publication and GitHub Actions execution have **not** been
verified by this record. The workflow requests multiple Python/OS combinations;
that configuration is not evidence that those jobs ran. No measured detection
accuracy, production-readiness or universal input-correctness claim is made.
These are author-run tests, not independent certification.

## Your local verification

Run setup and the sample on your own machine. Once the repository is published,
record your actual OS/Python versions, the command, its real result, and one
small change you understand. Do not rewrite unexecuted checks as passing checks.
