import matplotlib.pyplot as plt

clients = [5, 10, 20, 30, 40]
tps = [900, 1600, 2500, 2800, 2900]
latency = [5.2, 6.0, 8.1, 12.5, 25.0]
cpu = [30, 45, 70, 85, 99]

plt.figure(figsize=(10, 6))

# TPS
plt.plot(clients, tps, marker='o', label='TPS')
# Latency (우측 y축)
plt.plot(clients, latency, marker='s', label='Latency (ms)')
# CPU (우측 y축)
plt.plot(clients, cpu, marker='^', label='CPU (%)')

plt.title("DB Benchmarks - TPS / Latency / CPU by Number of Clients")
plt.xlabel("Number of Clients (-c)")
plt.ylabel("Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("db_benchmark_chart.png")
plt.show()