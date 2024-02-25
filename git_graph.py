import subprocess
import os
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def get_commits(email, year, repo_path):
    # Change to the specified repository directory
    original_dir = os.getcwd()  # Save the original directory to return later
    os.chdir(repo_path)

    cmd = f"git log --all --author={email} --since='{year}-01-01' --until='{year}-12-31' --pretty=format:'%ad' --date=short"
    try:
        output = subprocess.check_output(cmd, shell=True).decode()
    finally:
        os.chdir(original_dir)  # Return to the original directory

    dates = output.splitlines()
    # Strip single quotes from each date string before parsing
    return [datetime.strptime(date.strip("'"), '%Y-%m-%d') for date in dates]


def generate_heatmap(dates, year):
    commit_counts = Counter(dates)
    dates_range = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31')
    df = pd.DataFrame(index=dates_range, data={'Commits': [commit_counts.get(date, 0) for date in dates_range]})
    df['DayOfWeek'] = df.index.dayofweek
    df['Week'] = df.index.isocalendar().week

    # Mapping integers to three-letter day names
    days = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}

    # Replace day of week integers with three-letter strings
    df['DayOfWeek'] = df['DayOfWeek'].apply(lambda x: days[x])

    # Aggregate data to avoid duplicates in the pivot table
    df_aggregated = df.groupby(['DayOfWeek', 'Week']).sum().reset_index()

    # Pivot the aggregated data
    df_pivot = df_aggregated.pivot(index='DayOfWeek', columns='Week', values='Commits')

    # Reorder the days of the week starting from Monday
    df_pivot = df_pivot.reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

    # Fill NaN values with 0 since days without commits won't appear in the data
    df_pivot = df_pivot.fillna(0)

    plt.figure(figsize=(15, 5))
    sns.heatmap(df_pivot, cmap="Greens", square=True, cbar_kws={"shrink": 0.5}, linewidths=.5)
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)
    plt.title(f"GitHub Style Commit Graph for {year}")
    plt.xlabel('')
    plt.ylabel('')
    plt.show()





def print_ascii_art():
    # ASCII Art with ANSI escape codes for colors
    print("\033[91m" + "   ____ _ _  " + "\033[0m")
    print("\033[92m" + "  / ___(_) |_ " + "\033[0m")
    print("\033[93m" + " | |  _| | __|" + "\033[0m")
    print("\033[94m" + " | |_| | | |_ " + "\033[0m")
    print("\033[95m" + "  \____|_|\__|" + "\033[0m")

def main():
    # Print ASCII Art
    print_ascii_art()

    # ASCII Art Title
    print("GITHUB GRAPH\n")

    # Interactive Inputs
    email = input("Enter the email: ")
    year = input("Enter the year: ")
    repo_path = input("Enter the path of the repository: ")  # New input for repository path

    try:
        year = int(year)  # Converting year to integer
        dates = get_commits(email, year, repo_path)  # Pass the repo_path to get_commits
        generate_heatmap(dates, year)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
