# Tenable Interview 2

This repository contains the solution for Tenable's Interview 2 exercise. The task is expected to involve concurrent Python programming, including multithreading and/or multiprocessing.

## Goals

The implementation should be:

- Correct and deterministic where possible
- Safe when work is executed concurrently
- Clear about shared state, synchronization, and process boundaries
- Efficient without sacrificing readability
- Covered by focused tests

## Development

Use Python 3. The project is intentionally kept minimal until the interview requirements are provided.

Create and activate a virtual environment if needed:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install project and development dependencies once they are defined:

```bash
python -m pip install -r requirements.txt
```

## Running the solution

The command for running the solution will be documented here once the exercise requirements and entry point are added.

## Running tests

Run the test suite with:

```bash
python -m pytest
```

If `pytest` is not yet installed, install it in the active virtual environment before running the tests.

## Concurrency notes

When implementing the exercise, document the choice between threads and processes and the reason for it. Pay particular attention to:

- Whether the workload is I/O-bound or CPU-bound
- The effect of Python's Global Interpreter Lock (GIL)
- Safe access to shared mutable state
- Task submission, completion, cancellation, and shutdown
- Exception propagation from workers
- Avoiding deadlocks, races, starvation, and unnecessary contention
- Reproducible tests for concurrent behavior

## Repository layout

The layout will evolve with the solution. New modules and tests should be organized clearly, for example:

```text
.
├── README.md
├── src/       # application or solution code
└── tests/     # automated tests
```
