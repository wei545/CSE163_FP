# Explaining Housing Supply and Population Growth across Washington Counties

**CSE 163 Final Project**
Authors: Henry Tran, Daniil Kim, Pherell Layanto

---

## Overview

This project analyzes county-level housing and population data across Washington State from
1990 to 2025. We investigate how housing supply and population have changed over time,
how strongly housing units correlate with population, how population is distributed across
counties, and whether housing units per capita relates to population growth rates.

---

## Required Installations

Make sure you have Python 3 and the following libraries installed. You can install all of them
with pip:

```
pip install pandas seaborn matplotlib statsmodels pytest
```

- **pandas** — data loading, cleaning, reshaping, and merging
- **seaborn** — all four visualizations
- **matplotlib** — plot formatting and saving
- **statsmodels** — OLS linear regression (Result Validity challenge goal)
- **pytest** — running the test suite

No other environment configuration is required. A standard Python 3 installation with pip is
sufficient.

---

## Datasets

You must download two CSV files and place them inside the `data/` folder before running
the project.

**1. WA OFM Housing Units**
URL: https://data.wa.gov/demographics/WAOFM-April-1-Housing-Units-by-State-County-and-Ci/hpz7-md2y/about_data

Click the **Export** button in the top-right corner of the page to download the CSV.
Save it as: `data/housing_units.csv`

**2. WA OFM Population**
URL: https://data.wa.gov/Demographics/WAOFM-April-1-Population-by-State-County-and-City-/2hia-rqet

Click the **Export** button in the top-right corner of the page to download the CSV.
Save it as: `data/population.csv`

> **Note:** A third dataset from the FHFA (House Price Index) was initially planned but was
> dropped because `hpi_master.csv` contained no county-level rows for Washington State.
> The project does not require it.

After downloading, your `data/` folder should look like this:

```
data/
  housing_units.csv
  population.csv
```

---

## File Descriptions

### `data_utils.py`
The data pipeline module. Contains all functions for loading, cleaning, reshaping, merging,
and computing derived columns:

- `load_housing_units(path)` — Reads `housing_units.csv`, filters to county-level rows
  (`FILTER == 1`), strips whitespace from county names, parses comma-formatted numbers,
  and reshapes from wide format (one column per year) to long format (one row per
  county-year).
- `load_population(path)` — Same process as above for `population.csv`.
- `load_hpi(path)` — Loads and filters `hpi_master.csv` to WA county-level, purchase-only
  rows. Returns an empty DataFrame on the real dataset (no matching rows); retained for
  completeness.
- `merge_datasets(housing, population, hpi)` — Inner-joins the housing and population
  DataFrames on `COUNTY` and `Year`, then inner-joins with HPI. On the real data, only
  housing and population are used.
- `compute_derived_columns(merged)` — Adds `Units_Per_Capita` (housing units divided by
  population) and `Pop_Growth` (year-over-year percentage change in population, computed
  independently per county). The first year for each county is `NaN`.
- `main()` — Runs the full pipeline end-to-end and saves the result to `data/merged.csv`.

### `eda.py`
The runnable analysis script. Loads `data/merged.csv`, prints summary statistics, and
produces all four visualizations:

- `load_data()` — Reads `data/merged.csv` into a DataFrame.
- `summary_statistics(df)` — Prints `describe()` output for the four quantitative columns,
  county value counts, and missing data counts.
- `plot_hpi_trend(df)` — Line plot of population over time for all 39 counties. Saved as
  `plot1_population_trend.png`.
- `plot_population_vs_hpi(df)` — Scatter plot of population vs. housing units. Saved as
  `plot2_pop_vs_units.png`.
- `plot_recent_hpi_by_county(df)` — Bar chart of each county's most recent (2025)
  population, sorted from highest to lowest. Saved as
  `plot3_recent_population_by_county.png`.
- `plot_units_vs_hpi_regression(df)` — Regression scatter plot of `Units_Per_Capita` vs.
  `Pop_Growth`. Saved as `plot4_units_vs_popgrowth_regression.png`.

### `test_utils.py`
Pytest test suite for `data_utils.py`. Uses small hand-crafted CSV fixtures (Alpha, Beta,
Gamma counties) to verify each function against known expected values. Covers filtering,
whitespace stripping, comma-number parsing, merge correctness, and per-county isolation of
`Pop_Growth`.

### `Test_utils.py`
An earlier version of the test file. `test_utils.py` is the canonical, up-to-date test file and
is the one that should be run.

### `test_eda.py`
Additional tests for `eda.py` functions.

### `data/merged.csv`
The merged output produced by running `data_utils.py`. Contains 1,404 rows (39 counties ×
36 years) and 6 columns: `COUNTY`, `Year`, `Housing_Units`, `Population`,
`Units_Per_Capita`, and `Pop_Growth`. This file is generated automatically; you do not need
to create it manually.

### Plot files (`.png`)
Pre-generated output images saved in the root directory:
- `plot1_population_trend.png`
- `plot2_pop_vs_units.png`
- `plot3_recent_population_by_county.png`
- `plot4_units_vs_popgrowth_regression.png`

These are overwritten each time `eda.py` is run.

---

## Step-by-Step Instructions to Reproduce Results

**Step 1 — Clone the repository**

```
git clone https://github.com/wei545/CSE163_FP.git
cd CSE163_FP
```

**Step 2 — Install dependencies**

```
pip install pandas seaborn matplotlib statsmodels pytest
```

**Step 3 — Download and place the datasets**

Download `housing_units.csv` and `population.csv` from the URLs listed in the Datasets
section above. Place both files inside the `data/` folder at the root of the repository.

**Step 4 — Generate `data/merged.csv`**

Run the data pipeline to load, clean, merge, and save the master dataset:

```
python data_utils.py
```

You should see shape and preview output printed to the terminal, followed by
`merged.csv saved!`. The file `data/merged.csv` will now exist.

**Step 5 — Run the analysis and generate all plots**

```
python eda.py
```

This will print summary statistics to the terminal and save all four plots as `.png` files in
the root directory. Each plot window will also open interactively; close it to continue to the
next one.

**Step 6 — Run the test suite**

```
pytest test_utils.py -v
```

All tests should pass. The `-v` flag gives per-test output. pytest creates and cleans up
temporary CSV fixtures automatically; no additional setup is needed.

---

## Notes

- All paths in `data_utils.py` and `eda.py` are relative (e.g., `data/housing_units.csv`,
  `data/merged.csv`). Run all commands from the root of the repository, not from inside
  the `data/` folder.
- The `p-value` annotated on Plot 4 (`p = 7.21e-23`) was produced by a separate OLS
  regression using `statsmodels`. This was run directly inside `eda.py` and printed to the
  terminal; the value was then added as a text annotation to the saved plot.
- The FHFA HPI dataset (`hpi_master.csv`) is not needed. `load_hpi()` and the three-way
  merge in `merge_datasets()` remain in the code but are not called by `eda.py`. The
  effective pipeline merges only housing and population.
