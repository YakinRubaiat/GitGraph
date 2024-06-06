import subprocess
import os
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def get_commits(email, year=None, repo_path="."):
    original_dir = os.getcwd()
    os.chdir(repo_path)

    if year:
        cmd = f"git log --all --author={email} --since='{year}-01-01' --until='{year}-12-31' --pretty=format:'%ad' --date=short"
    else:
        cmd = f"git log --all --author={email} --pretty=format:'%ad' --date=short"

    try:
        output = subprocess.check_output(cmd, shell=True).decode()
    finally:
        os.chdir(original_dir)

    dates = output.splitlines()
    dates = [datetime.strptime(date.strip("'"), '%Y-%m-%d') for date in dates]

    if not year:
        years = [date.year for date in dates]
        min_year, max_year = min(years), max(years)
        return dates, min_year, max_year

    return dates

def prepare_data(dates):
    commit_counts = Counter(dates)
    min_date = min(dates).replace(month=1, day=1)
    max_date = max(dates).replace(month=12, day=31)
    dates_range = pd.date_range(start=min_date, end=max_date)

    df = pd.DataFrame(index=dates_range, data={'Commits': [commit_counts.get(date, 0) for date in dates_range]})
    df['DayOfWeek'] = df.index.dayofweek
    df['Week'] = df.index.isocalendar().week

    days = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    df['DayOfWeek'] = df['DayOfWeek'].apply(lambda x: days[x])

    return df

def generate_heatmap(dates, year, person_name=None):
    df = prepare_data(dates)
    df_year = df[df.index.year == year]
    if df_year.empty:
        raise ValueError(f"No commits found for the year {year}.")
    df_aggregated = df_year.groupby(['DayOfWeek', 'Week']).sum().reset_index()
    df_pivot = df_aggregated.pivot(index='DayOfWeek', columns='Week', values='Commits')
    df_pivot = df_pivot.reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    df_pivot = df_pivot.fillna(0)

    plt.figure(figsize=(12, 6))
    sns.heatmap(df_pivot, cmap="Greens", square=True, linewidths=.5, cbar_kws={"shrink": 0.5})
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)

    if person_name:
        title = f"{person_name}'s Commit Graph for {year}"
    else:
        title = f"Commit Graph for {year}"
        
    plt.title(title)
    plt.xlabel('Week')
    plt.ylabel('')
    plt.show()

def generate_combined_heatmap(dates, min_year, max_year, person_name=None):
    df = prepare_data(dates)
    num_years = max_year - min_year + 1
    fig, axes = plt.subplots(num_years, 1, figsize=(8, num_years * 2), constrained_layout=True)
    if num_years == 1:
        axes = [axes]

    for ax, year in zip(axes, range(min_year, max_year + 1)):
        year_start, year_end = datetime(year, 1, 1), datetime(year, 12, 31)
        dates_range = pd.date_range(start=year_start, end=year_end)
        df_year = df.reindex(dates_range, fill_value=0)
        df_pivot = df_year.pivot_table(index=df_year.index.dayofweek, columns='Week', values='Commits', fill_value=0)
        sns.heatmap(df_pivot, cmap="Greens", square=True, linewidths=.5, cbar=False, ax=ax)
        ax.set_title(f"{year}")
        ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
        ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)

        ax.set_xticks(range(0, 54, 2))
        ax.set_xticklabels(range(1, 54, 2))
        ax.set_xlabel('Week')

    if person_name:
        title = f"{person_name}'s Commit Graph from {min_year} to {max_year}"
    else:
        title = f"Commit Graph from {min_year} to {max_year}"

    fig.suptitle(title, fontsize=16)

    display_tkinter(fig)

def display_tkinter(fig):
    root = tk.Tk()
    root.title("Scrollable GitHub Commit Graph")
    root.protocol("WM_DELETE_WINDOW", root.quit)
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    FigureCanvasTkAgg(fig, frame).get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar = NavigationToolbar2Tk(FigureCanvasTkAgg(fig, frame), frame)
    toolbar.update()
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    root.mainloop()

def print_ascii_art():
    print("\033[91m   ____ _ _  \033[0m\n\033[92m  / ___(_) |_ \033[0m\n\033[93m | |  _| | __|\033[0m\n\033[94m | |_| | | |_ \033[0m\n\033[95m  \____|_|\__|\033[0m")

def main():
    print_ascii_art()
    email = input("Enter the email: ")
    year = input("Enter the year (or leave blank to use all years): ")
    repo_path = input("Enter the path of the repository: ")
    person_name = input("Enter the person's name (optional): ")
    try:
        if year:
            dates = get_commits(email, int(year), repo_path)
            generate_heatmap(dates, int(year), person_name)
        else:
            dates, min_year, max_year = get_commits(email, repo_path=repo_path)
            generate_combined_heatmap(dates, min_year, max_year, person_name)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
