import matplotlib.pyplot as plt

query_names = [
    "PK Select", "Pattern Match", "Join: Top Rated", "Group By Genre/Year",
    "Director Join", "Subquery: Filmography", "CTE: Yearly Count", "Window: Top Rated/Year"
]
execution_times = [
    0.045,       # Simple Select
    2415.612,    # Pattern Matching
    304.313,     # Join: Top Rated Movies
    828.021,     # Multi-condition Group By
    4363.620,    # Director Join
    15510.881,   # Subquery: Actor Filmography
    564.843,     # CTE: Yearly Counts
    1067.106     # Window Function
]

colors = ['#FF9999', '#FFCC99', '#FFFF99', '#99FF99', '#99CCFF', '#CC99FF', '#FF99CC', '#B0B0B0']

plt.figure(figsize=(12, 6))
plt.barh(query_names[::-1], execution_times[::-1], color=colors[::-1])
plt.axvline(200, color='blue', linestyle='-', label='200ms Optimal') # 200ms
plt.axvline(1000, color='red', linestyle='-', label='1,000ms Warning') # 1000ms
plt.xlabel("Execution Time (ms)")
plt.title("IMDB Query Test: Execution Time by Query Type")
plt.grid(axis='x')
plt.tight_layout()
plt.savefig("results/01_query_result.png")