import subprocess
import sys
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def get_commits(email, year):
    cmd = f"git log --all --author='{email}' --since='{year}-01-01' --until='{year}-12-31' --pretty=format:'%ad' --date=short"
    output = subprocess.check_output(cmd, shell=True).decode()
    dates = output.splitlines()
    return [datetime.strptime(date, '%Y-%m-%d') for date in dates]

def generate_heatmap(dates, year):
    commit_counts = Counter(dates)
    dates_range = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31')
    df = pd.DataFrame(index=dates_range, data={'Commits': [commit_counts.get(date, 0) for date in dates_range]})
    df['DayOfWeek'] = df.index.dayofweek
    df['Week'] = df.index.isocalendar().week
    df_pivot = df.pivot("DayOfWeek", "Week", "Commits")
    plt.figure(figsize=(15, 3))
    ax = sns.heatmap(df_pivot, cmap="YlGnBu")
    ax.set_title(f"GitHub Style Commit Graph for {year}")
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

    try:
        year = int(year)  # Converting year to integer
        dates = get_commits(email, year)
        generate_heatmap(dates, year)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
