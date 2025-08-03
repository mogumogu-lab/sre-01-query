import matplotlib.pyplot as plt
import numpy as np

query_names = [
    "PK Select", "Pattern Match", "Join: Top Rated", "Group By Genre/Year",
    "Director Join", "Subquery: Filmography", "CTE: Yearly Count", "Window: Top Rated/Year"
]
execution_times_no_index = [
    0.045,       # Simple Select
    2415.612,    # Pattern Matching
    304.313,     # Join: Top Rated Movies
    828.021,     # Multi-condition Group By
    4363.620,    # Director Join
    15510.881,   # Subquery: Actor Filmography
    564.843,     # CTE: Yearly Counts
    1067.106     # Window Function
]

execution_times_with_index = [
    0.045,      # PK Select (With Index == No Index, PK)
    3.3,        # Pattern Match (With Index)
    112.311,    # Join: Top Rated Movies (With Index)
    654.906,    # Multi-condition Group By (With Index)
    2885.571,   # Director Join (With Index)
    265.851,    # Subquery: Actor Filmography (With Index)
    44.415,     # CTE: Yearly Counts (With Index)
    1144.054    # Window Function (With Index)
]

y = np.arange(len(query_names))
height = 0.35

plt.figure(figsize=(14, 6))

# No Index
bar_no_index = plt.barh(y - height/2, execution_times_no_index, height, label='No Index', color='#FF9999')
# With Index
bar_with_index = plt.barh(y + height/2, execution_times_with_index, height, label='With Index', color='#99CCFF')

plt.yticks(y, query_names)
plt.gca().invert_yaxis()

plt.axvline(200, color='blue', linestyle='--', label='200ms Optimal') # 200ms
plt.axvline(1000, color='red', linestyle='--', label='1,000ms Warning') # 1000ms
plt.xlabel("Execution Time (ms)")
plt.title("IMDB Query Test: Execution Time by Query Type")
plt.grid(axis='x')
plt.tight_layout()

for rect in bar_no_index:
    width = rect.get_width()
    plt.text(width + 20, rect.get_y() + rect.get_height()/2, f"{width:.3f}", va='center', ha='left', fontsize=10, color='#C0392B')

for rect in bar_with_index:
    width = rect.get_width()
    plt.text(width + 20, rect.get_y() + rect.get_height()/2, f"{width:.3f}", va='center', ha='left', fontsize=10, color='#2471A3')

plt.legend()

plt.savefig("results/01_query_result.png")