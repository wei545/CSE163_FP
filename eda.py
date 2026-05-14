"""
Provides exploratory
data analysis visualizations
concerning files in the data
folder.
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm


def load_data() -> pd.DataFrame:
    """Load the merged data from CSV."""
    return pd.read_csv('data/merged.csv')


def summary_statistics(df: pd.DataFrame) -> None:
    """Print summary statistics for quantitative variables, categorical, and missing data."""
    print("=== SUMMARY STATISTICS ===")
    print("\nQuantitative variables describe:")
    quantitative_cols = ['Housing_Units', 'Population', 'Units_Per_Capita', 'Pop_Growth', 'index_nsa']
    print(df[quantitative_cols].describe())
    
    print("\nCounty value counts:")
    print(df['COUNTY'].value_counts())
    
    print("\nMissing data:")
    print(df.isnull().sum())


def plot_hpi_trend(df: pd.DataFrame) -> None:
    """Plot HPI trend over time by county."""
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=df, x='Year', y='index_nsa', hue='COUNTY', style='COUNTY')
    plt.title('HPI Trend Over Time by County')
    plt.xlabel('Year')
    plt.ylabel('HPI Index (NSA)')
    plt.legend(title='County', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('plot1_hpi_trend.png')
    plt.show()


def plot_population_vs_hpi(df: pd.DataFrame) -> None:
    """Scatter plot of Population vs HPI."""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Population', y='index_nsa')
    plt.title('Relationship Between Population and HPI')
    plt.xlabel('Population')
    plt.ylabel('HPI Index (NSA)')
    plt.tight_layout()
    plt.savefig('plot2_pop_vs_hpi.png')
    plt.show()


def plot_recent_hpi_by_county(df: pd.DataFrame) -> None:
    """Bar chart of most recent HPI by county, sorted high to low."""
    recent_df = df.sort_values('Year').groupby('COUNTY').tail(1).sort_values('index_nsa', ascending=False)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=recent_df, x='COUNTY', y='index_nsa')
    plt.title('Most Recent HPI by County (Sorted High to Low)')
    plt.xlabel('County')
    plt.ylabel('Most Recent HPI Index (NSA)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plot3_recent_hpi_by_county.png')
    plt.show()


def plot_units_vs_hpi_regression(df: pd.DataFrame) -> None:
    """Scatter plot with regression line of Units per Capita vs HPI."""
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='Units_Per_Capita', y='index_nsa', scatter_kws={'alpha':0.5})
    plt.title('Units per Capita vs HPI with Regression Line')
    plt.xlabel('Units per Capita')
    plt.ylabel('HPI Index (NSA)')
    plt.tight_layout()
    plt.savefig('plot4_units_vs_hpi_regression.png')
    plt.show()


def main() -> None:
    df = load_data()
    sns.set_style("whitegrid")
    summary_statistics(df)
    plot_hpi_trend(df)
    plot_population_vs_hpi(df)
    plot_recent_hpi_by_county(df)
    plot_units_vs_hpi_regression(df)


if __name__ == '__main__':
    main()