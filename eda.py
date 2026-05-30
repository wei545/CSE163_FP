"""
Provides exploratory
data analysis visualizations
concerning files in the data
folder.
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf


def load_data() -> pd.DataFrame:
    """Load the merged data from CSV."""
    return pd.read_csv('data/merged.csv')


def summary_statistics(df: pd.DataFrame) -> None:
    """Print summary statistics for quantitative variables, categorical, and missing data."""
    print("=== SUMMARY STATISTICS ===")
    print("\nQuantitative variables describe:")
    quantitative_cols = ['Housing_Units', 'Population', 'Units_Per_Capita', 'Pop_Growth']
    print(df[quantitative_cols].describe())
    
    print("\nCounty value counts:")
    print(df['COUNTY'].value_counts())
    
    print("\nMissing data:")
    print(df.isnull().sum())


def plot_population_trend(df: pd.DataFrame) -> None:
    """Plot Population trend over time by county."""
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=df, x='Year', y='Population', hue='COUNTY', style='COUNTY')
    plt.title('Population Trend Over Time by County')
    plt.xlabel('Year')
    plt.ylabel('Population')
    plt.legend(title='County', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('plot1_population_trend.png')
    plt.show()


def plot_population_vs_units(df: pd.DataFrame) -> None:
    """Scatter plot of Population vs Housing Units."""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Population', y='Housing_Units', hue='COUNTY')
    plt.title('Relationship Between Population and Housing Units')
    plt.xlabel('Population')
    plt.ylabel('Housing Units')
    plt.legend(title='County', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('plot2_pop_vs_units.png')
    plt.show()


def plot_recent_population_by_county(df: pd.DataFrame) -> None:
    """Bar chart of most recent population by county, sorted high to low."""
    recent_df = df.sort_values('Year').groupby('COUNTY').tail(1).sort_values('Population', ascending=False)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=recent_df, x='COUNTY', y='Population')
    plt.title('Most Recent Population by County (Sorted High to Low)')
    plt.xlabel('County')
    plt.ylabel('Most Recent Population')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plot3_recent_population_by_county.png')
    plt.show()


def plot_units_vs_growth_regression(df: pd.DataFrame) -> None:
    """Scatter plot with regression line of Units per Capita vs Population Growth."""
    df_clean = df.dropna(subset=['Pop_Growth'])
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_clean, x='Units_Per_Capita', y='Pop_Growth', scatter_kws={'alpha':0.5})
    plt.title('Units per Capita vs Population Growth with Regression Line')
    plt.xlabel('Units per Capita')
    plt.ylabel('Population Growth (%)')
    plt.tight_layout()
    plt.savefig('plot4_units_vs_popgrowth_regression.png')
    plt.show()

def run_result_validity(df) -> None:
    '''
    Runs a OLS linear regression to validate the realtionship
    between housing units per capita and population growth
    '''
    print("Running Result Validity Challenge...")

    # Drop rows where Pop_Growth is NaN
    clean_df = df.dropna(subset=['Units_Per_Capita', 'Pop_Growth'])
    
    # Fit the OLS model: Pop_Growth (Y) vs Units_Per_Capita (X)
    model = smf.ols(formula='Pop_Growth ~ Units_Per_Capita', data=clean_df).fit()
    
    # Print the full summary table to the terminal
    print("\n=== OLS Regression Results ===")
    print(model.summary())
    
    # Extract and print just the p-value
    p_value = model.pvalues['Units_Per_Capita']
    print(f"\nExact P-Value for Units_Per_Capita: {p_value}")       

def main() -> None:
    df = load_data()
    sns.set_style("whitegrid")
    summary_statistics(df)
    plot_population_trend(df)
    plot_population_vs_units(df)
    plot_recent_population_by_county(df)
    plot_units_vs_growth_regression(df)

    run_result_validity(df)


if __name__ == '__main__':
    main()
