import matplotlib.pyplot as plt

clients = [5, 10, 20, 50, 90]
tps = [944, 33111, 34011, 34046, 32670]
latency = [5.2, 0.302, 0.588, 1.469, 2.755]
cpu = [200, 200, 200, 200, 200]

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
plt.savefig("01_simple_select_result.png")
plt.show()