"""
Tests eda.py for correctness.
Daniil Kim
"""
import eda
import data_utils
# either import the functions and test them, or whole thign and use the fuctnions inside them
#See the data sets
'''
Write assert-based tests for:
    * clean_housing_units() returns correct shape
    * clean_population() aggregates correctly
    * merge_datasets() produces expected columns
    * derived columns (units per capita) compute correctly
- Run: python test_eda.py — should pass with no errors
'''
housing = load_housing_units('data/housing_units.csv')
population = load_population('data/population.csv')
hpi = load_hpi('data/hpi_master.csv')

def main() -> None:
    pass


if __name__ == '__main__':
    main()