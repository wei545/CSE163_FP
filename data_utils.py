"""
This file cleans, loads, and merges
housing_units.csv, population.csv, and
hpi_master.csv.
"""
import pandas as pd


def load_housing_units(path: str) -> pd.DataFrame:
    # thousands=',' tells pandas to read "12,345" as 12345 automatically
    df = pd.read_csv(path, thousands=',')

    # Keep only county-level rows
    df = df[df['FILTER'] == 1]

    # Find all columns that hold housing unit counts (they start with HU_)
    hu_cols = []
    for col in df.columns:
        if col.startswith('HU_'):
            hu_cols.append(col)

    # Build a new table: one row per county per year
    rows = []
    for col in hu_cols:
        year = int(col[3:])  # "HU_2015" → 2015
        for i in df.index:
            county_name = df.loc[i, 'COUNTY'].strip()
            units = int(df.loc[i, col])
            rows.append({'COUNTY': county_name, 'Year': year, 'Housing_Units': units})

    return pd.DataFrame(rows)


def load_population(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, thousands=',')

    # Keep only county-level rows
    df = df[df['FILTER'] == 1]

    # Find all columns that hold population counts (they start with POP_)
    pop_cols = []
    for col in df.columns:
        if col.startswith('POP_'):
            pop_cols.append(col)

    rows = []
    for col in pop_cols:
        year = int(col[4:])  # "POP_2015" → 2015
        for i in df.index:
            county_name = df.loc[i, 'COUNTY'].strip()
            pop = int(df.loc[i, col])
            rows.append({'COUNTY': county_name, 'Year': year, 'Population': pop})

    return pd.DataFrame(rows)


def load_hpi(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Filter to WA state-level, and purchase-only HPI rows
    df = df[df['level'] == 'State']
    df = df[df['place_name'] == 'Washington']
    df = df[df['hpi_flavor'] == 'purchase-only']

    df = df[['place_name', 'yr', 'index_nsa']]
    df = df.rename(columns={'yr': 'Year', 'place_name': 'State'})
    return df


def merge_datasets(housing: pd.DataFrame,
                   population: pd.DataFrame) -> pd.DataFrame:
    merged = housing.merge(population, on=['COUNTY', 'Year'])
    return merged


def add_pop_growth(county_df: pd.DataFrame) -> pd.DataFrame:
    # Sort by year so we go in order
    sorted_indices = sorted(county_df.index, key=lambda i: county_df.loc[i, 'Year'])
    county_df = county_df.loc[sorted_indices].reset_index(drop=True)

    growth = []
    for i in range(len(county_df)):
        if i == 0:
            # No previous year to compare to
            growth.append(None)
        else:
            prev = county_df.loc[i - 1, 'Population']
            curr = county_df.loc[i, 'Population']
            pct_change = (curr - prev) / prev * 100
            growth.append(pct_change)

    county_df['Pop_Growth'] = growth
    return county_df


def compute_derived_columns(merged: pd.DataFrame) -> pd.DataFrame:
    # Housing units per person
    merged['Units_Per_Capita'] = merged['Housing_Units'] / merged['Population']

    sorted_indices = sorted(merged.index, key=lambda i: (merged.loc[i, 'COUNTY'], merged.loc[i, 'Year']))
    merged = merged.loc[sorted_indices].reset_index(drop=True)

    # Go through each county, compute its pop growth, collect all the rows
    all_rows = []
    for county in merged['COUNTY'].unique():
        county_rows = merged[merged['COUNTY'] == county].copy()
        county_rows = add_pop_growth(county_rows)
        for i in county_rows.index:
            all_rows.append(county_rows.loc[i].to_dict())

    # Build one big DataFrame from all the collected rows
    return pd.DataFrame(all_rows).reset_index(drop=True)


def main() -> None:
    housing = load_housing_units('data/housing_units.csv')
    population = load_population('data/population.csv')
    hpi = load_hpi('data/hpi_master.csv')

    print('=== HOUSING UNITS (cleaned) ===')
    print(housing.shape)
    print(housing.head(3))

    print()
    print('=== POPULATION (cleaned) ===')
    print(population.shape)
    print(population.head(3))

    print()
    print('=== HPI (cleaned) ===')
    print(hpi.shape)
    print(hpi.head(3))

    print()
    merged = merge_datasets(housing, population)
    merged = compute_derived_columns(merged)
    print('=== MERGED WITH DERIVED COLUMNS ===')
    print(merged.shape)
    print(merged.head(3))
    print(merged.isnull().sum())
    merged.to_csv('data/merged.csv', index=False)
    print('merged.csv saved!')


if __name__ == '__main__':
    main()
