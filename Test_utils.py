"""
Tests utils.py for correctness.
Daniil Kim
"""

import pytest
import pandas as pd
from data_utils import (
    load_housing_units,
    load_population,
    merge_datasets,
    compute_derived_columns,
)

'''
pytest writes these CSVs to a temporary folder automatically
and cleans them up after each test
'''


@pytest.fixture
def housing_csv(tmp_path):
    '''
    create a small csv to test housing
    '''
    path = tmp_path / "housing.csv"
    path.write_text("""\
SEQUENCE,FILTER,COUNTY,JURISDICTION,HU_2020,HU_2021,HU_2022
1,1,Alpha,Alpha County,"1,000","1,100","1,200"
2,2,Alpha,Unincorporated Alpha,"400","450","500"
3,1,Beta,Beta County,"2,000","2,050","2,100"
4,1, Gamma ,Gamma County,"500","510","520"
""")
    return path


@pytest.fixture
def population_csv(tmp_path):
    '''
    create another csv to test population
    '''
    path = tmp_path / "population.csv"
    path.write_text("""\
SEQUENCE,FILTER,COUNTY,JURISDICTION,POP_2020,POP_2021,POP_2022
1,1,Alpha,Alpha County,"10,000","10,500","11,000"
2,2,Alpha,Unincorporated Alpha,"4,000","4,200","4,400"
3,1,Beta,Beta County,"20,000","20,200","20,400"
4,1, Gamma ,Gamma County,"5,000","5,050","5,100"
""")
    return path


@pytest.fixture
def loaded(housing_csv, population_csv):
    return (
        load_housing_units(housing_csv),
        load_population(population_csv),
    )

'''
testing housing function with assert stemeents
'''

def test_load_housing_units_shape(housing_csv):
    df = load_housing_units(housing_csv)
    assert df.shape == (9, 3)  # 3 counties x 3 years


def test_load_housing_units_columns(housing_csv):
    df = load_housing_units(housing_csv)
    assert set(df.columns) == {"COUNTY", "Year", "Housing_Units"}


def test_load_housing_units_excludes_non_county_filter(housing_csv):
    # FILTER != 1 rows (unincorporated jurisdictions) must be dropped
    df = load_housing_units(housing_csv)
    assert "Unincorporated Alpha" not in df["COUNTY"].values


def test_load_housing_units_strips_county_name(housing_csv):
    # " Gamma " in the CSV should become "Gamma"
    df = load_housing_units(housing_csv)
    assert "Gamma" in df["COUNTY"].values
    assert " Gamma " not in df["COUNTY"].values


def test_load_housing_units_parses_thousands_comma(housing_csv):
    # "1,000" in the CSV should be read as the integer 1000
    df = load_housing_units(housing_csv)
    alpha_2020 = df[
        (df["COUNTY"] == "Alpha") & (df["Year"] == 2020)
    ]["Housing_Units"].iloc[0]
    assert alpha_2020 == 1000


def test_load_housing_units_year_is_int(housing_csv):
    df = load_housing_units(housing_csv)
    assert df["Year"].dtype in (int, "int64", "int32")


def test_load_housing_units_all_years_present(housing_csv):
    df = load_housing_units(housing_csv)
    assert set(df["Year"].unique()) == {2020, 2021, 2022}


'''
testing populatino function with assert stemeents
'''


def test_load_population_shape(population_csv):
    df = load_population(population_csv)
    assert df.shape == (9, 3)


def test_load_population_columns(population_csv):
    df = load_population(population_csv)
    assert set(df.columns) == {"COUNTY", "Year", "Population"}


def test_load_population_excludes_non_county_filter(population_csv):
    df = load_population(population_csv)
    assert "Unincorporated Alpha" not in df["COUNTY"].values


def test_load_population_parses_thousands_comma(population_csv):
    df = load_population(population_csv)
    alpha_2020 = df[
        (df["COUNTY"] == "Alpha") & (df["Year"] == 2020)
    ]["Population"].iloc[0]
    assert alpha_2020 == 10_000


def test_load_population_strips_county_name(population_csv):
    df = load_population(population_csv)
    assert "Gamma" in df["COUNTY"].values
    assert " Gamma " not in df["COUNTY"].values


'''
testing merge function with assert stemeents
'''


def test_merge_shape(loaded):
    merged = merge_datasets(*loaded)
    assert merged.shape == (9, 4)  # 3 counties x 3 years, 4 columns


def test_merge_columns(loaded):
    merged = merge_datasets(*loaded)
    assert set(merged.columns) == {
        "COUNTY", "Year", "Housing_Units", "Population"
    }


def test_merge_no_nulls(loaded):
    # Inner join on clean matching data should produce zero NaNs
    merged = merge_datasets(*loaded)
    assert merged.isnull().sum().sum() == 0


def test_merge_drops_unmatched_counties(loaded):
    # A county in housing/population but absent from HPI should be dropped
    housing, population = loaded
    housing = pd.concat([
        housing,
        pd.DataFrame([{"COUNTY": "NoHPI", "Year": 2020, "Housing_Units": 999}])
    ])
    population = pd.concat([
        population,
        pd.DataFrame([{"COUNTY": "NoHPI", "Year": 2020, "Population": 9999}])
    ])
    merged = merge_datasets(housing, population)
    assert "NoHPI" not in merged["COUNTY"].values


def test_merge_correct_values(loaded):
    # Spot-check one row has consistent values across all three sources
    merged = merge_datasets(*loaded)
    row = merged[
        (merged["COUNTY"] == "Alpha") & (merged["Year"] == 2022)
    ].iloc[0]
    assert row["Housing_Units"] == 1200
    assert row["Population"] == 11_000


'''
testing derived function with assert stemeents
'''


@pytest.fixture
def merged_df():
    return pd.DataFrame({
        "COUNTY": ["Alpha", "Alpha", "Alpha", "Beta", "Beta", "Beta"],
        "Year": [2020, 2021, 2022, 2020, 2021, 2022],
        "Housing_Units": [1000, 1100, 1200, 2000, 2050, 2100],
        "Population": [10000, 10500, 11000, 20000, 20200, 20400],
    })


def test_compute_derived_adds_units_per_capita(merged_df):
    assert "Units_Per_Capita" in compute_derived_columns(merged_df).columns


def test_compute_derived_adds_pop_growth(merged_df):
    assert "Pop_Growth" in compute_derived_columns(merged_df).columns


def test_compute_derived_units_per_capita_value(merged_df):
    result = compute_derived_columns(merged_df)
    row = result[
        (result["COUNTY"] == "Alpha") & (result["Year"] == 2020)
    ].iloc[0]
    assert abs(row["Units_Per_Capita"] - 1000 / 10000) < 1e-9


def test_compute_derived_first_year_per_county_is_null(merged_df):
    # Each county's first year has no prior year, so Pop_Growth must be NaN
    result = compute_derived_columns(merged_df)
    for county in ["Alpha", "Beta"]:
        first_row = result[
            result["COUNTY"] == county
        ].sort_values("Year").iloc[0]
        assert pd.isna(first_row["Pop_Growth"]), (
            f"{county} first year should be NaN"
        )


def test_compute_derived_pop_growth_correct_value(merged_df):
    result = compute_derived_columns(merged_df)
    alpha_2021 = result[
        (result["COUNTY"] == "Alpha") & (result["Year"] == 2021)
    ].iloc[0]
    assert abs(alpha_2021["Pop_Growth"] - 5.0) < 1e-9  # (10500-10000)/10000*100 = 5%


def test_compute_derived_row_count_unchanged(merged_df):
    assert len(compute_derived_columns(merged_df)) == len(merged_df)


def test_compute_derived_all_counties_present(merged_df):
    result = compute_derived_columns(merged_df)
    assert set(result["COUNTY"].unique()) == {"Alpha", "Beta"}


def test_compute_derived_growth_not_cross_contaminated(merged_df):
    # Alpha 2020 NaN must not be influenced by Beta rows; Beta 2021 must be correct
    result = compute_derived_columns(merged_df)
    alpha_2020 = result[
        (result["COUNTY"] == "Alpha") & (result["Year"] == 2020)
    ].iloc[0]
    beta_2021 = result[
        (result["COUNTY"] == "Beta") & (result["Year"] == 2021)
    ].iloc[0]
    assert pd.isna(alpha_2020["Pop_Growth"])
    assert abs(beta_2021["Pop_Growth"] - 1.0) < 1e-9


