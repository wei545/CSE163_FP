"""
This file cleans, loads, and merges
housing_units.csv, population.csv, and
hpi_master.csv.
"""
import pandas as pd


def load_housing_units(path: str) -> pd.DataFrame:
    """Load and clean WA housing units dataset."""
    df = pd.read_csv(path)
    county_only = df[df['FILTER'] == 1]
    hu_cols = [c for c in county_only.columns if c[:3] == 'HU_']
    all_rows = []
    for col in hu_cols:
        year = int(col[3:])
        for idx in county_only.index:
            all_rows.append({
                'COUNTY': county_only.loc[idx, 'COUNTY'].strip(),
                'Year': year,
                'Housing_Units': int(str(
                    county_only.loc[idx, col]).replace(',', ''))
            })
    return pd.DataFrame(all_rows)


def load_population(path: str) -> pd.DataFrame:
    """Load and clean WA population dataset."""
    df = pd.read_csv(path)
    county_only = df[df['FILTER'] == 1]
    pop_cols = [c for c in county_only.columns if c[:4] == 'POP_']
    all_rows = []
    for col in pop_cols:
        year = int(col[4:])
        for idx in county_only.index:
            all_rows.append({
                'COUNTY': county_only.loc[idx, 'COUNTY'].strip(),
                'Year': year,
                'Population': int(str(
                    county_only.loc[idx, col]).replace(',', ''))
            })
    return pd.DataFrame(all_rows)


def load_hpi(path: str) -> pd.DataFrame:
    """Load Washington State-level HPI (purchase-only) from hpi_master.csv.

    Note: hpi_master.csv does not contain county-level WA rows.
    County HPI is distributed separately as hpi_at_county.xlsx.
    State-level is used as a proxy for EDA purposes.
    """
    df = pd.read_csv(path)
    is_state = df['level'] == 'State'
    is_wa = df['place_name'] == 'Washington'
    is_purchase = df['hpi_flavor'] == 'purchase-only'
    df = df[is_state & is_wa & is_purchase].copy()
    df = df[['place_name', 'yr', 'index_nsa']]
    df = df.rename(columns={'yr': 'Year', 'place_name': 'State'})
    return df


def merge_datasets(housing: pd.DataFrame,
                   population: pd.DataFrame) -> pd.DataFrame:
    """Merge housing and population datasets on COUNTY and Year."""
    merged = housing.merge(population, on=['COUNTY', 'Year'])
    return merged


def add_pop_growth(county_data: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year population growth % for one county."""
    county_data = county_data.sort_values('Year').copy()
    growth = [None]
    for i in range(1, len(county_data)):
        prev = county_data['Population'].iloc[i - 1]
        curr = county_data['Population'].iloc[i]
        growth.append((curr - prev) / prev * 100)
    county_data['Pop_Growth'] = growth
    return county_data


def compute_derived_columns(merged: pd.DataFrame) -> pd.DataFrame:
    """Add Units_Per_Capita and Pop_Growth columns to merged dataset."""
    merged['Units_Per_Capita'] = (merged['Housing_Units'] /
                                  merged['Population'])
    merged = merged.sort_values(['COUNTY', 'Year'])
    return (merged.groupby('COUNTY')
            .apply(add_pop_growth)
            .reset_index(drop=True))


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
