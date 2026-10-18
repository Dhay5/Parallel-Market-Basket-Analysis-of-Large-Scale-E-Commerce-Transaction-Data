# ARTI 503 Stage 1 — Shopping Pattern Explorer

Sequential market basket analysis using the UCI Online Retail II dataset.

## Setup and Run

Use Python 3.12. Open a terminal in the project folder and run:

```bash
python -m pip install -r requirements.txt
python -m unittest -v
python prepare_data.py
python benchmark.py --member YOUR_STUDENT_ID --out results/YOUR_STUDENT_ID
```

Replace YOUR_STUDENT_ID with your student ID. The output folder must be new.

The benchmark uses 25%, 50%, 75% and 100% of the prepared baskets, with one excluded warmup and five measured runs per size. It also measures the complete processing pipeline separately.

Execution may take many minutes. Leave the terminal open until it finishes.

## Benchmarking Procedure

All members must use the same code, dataset, dependencies and default settings. Keep the computer plugged in and close heavy background applications.

Retain all measured runs. Report the average execution time, CPU model, and physical/logical core counts. Pair-counting times and complete-pipeline times are different measurements and should be reported separately.

## Results

The specified output folder contains:

- hardware.json: computer specifications and benchmark settings.
- runs.csv: individual pair-counting execution times.
- summary.csv: mean, median, standard deviation and timing range.
- pipeline_runs.csv: execution times for each processing phase.
- top20.csv: the 20 most frequent product pairs.
- frequent_pairs.csv: product pairs meeting the 1% support threshold.

Keep these files as supporting evidence for the report.

## Dataset

D. Chen, Online Retail II, UCI Machine Learning Repository, 2012.

DOI: https://doi.org/10.24432/C5CG6D

Official dataset: https://archive.ics.uci.edu/dataset/502/online+retail+ii

License: CC BY 4.0.

prepare_data.py downloads the official dataset if needed and uses both worksheets. Cancelled transactions, invalid quantities/prices and non-merchandise codes are excluded. Each worksheet/invoice combination forms a basket, with repeated products counted once.

## Source Files

- mba.py: cleaning, basket construction and sequential pair counting.
- prepare_data.py: dataset download, validation and preparation.
- benchmark.py: hardware recording and repeated execution-time measurements.
- test_mba.py: correctness tests.
- analyze.py: exports frequent product pairs.
- make_figures.py: generates benchmark graphs.
- collect_member_results.py: combines member benchmark results.
- requirements.txt: required Python packages.

## Optional Commands

Perform a single sequential analysis:

```bash
python analyze.py --out analysis --min-support 0.01
```

Combine member results by listing all ten result folders:

```bash
python collect_member_results.py results/STUDENT_ID_1 results/STUDENT_ID_2 --out member_comparison.csv
```

The Word report provides the methodology, results and initial parallelisation plan. No parallel version is implemented in Stage 1.