import matplotlib.pyplot as plt

clients = [1, 5, 10, 20, 50, 90]
tps = [1742, 3376, 3335, 3300, 3136, 3040]
latency = [0.574, 1.481, 2.998, 6.001, 15.515, 29.596]
cpu = [101, 200, 200, 200, 200, 200]
memory = [50, 59, 70, 91, 156, 243]

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# TPS
axs[0, 0].plot(clients, tps, marker='o', label='TPS')
axs[0, 0].set_title('TPS')
axs[0, 0].set_xlabel('Number of Clients')
axs[0, 0].set_ylabel('TPS')
axs[0, 0].grid(True)

# Latency
axs[0, 1].plot(clients, latency, marker='s', color='tab:orange', label='Latency (ms)')
axs[0, 1].set_title('Latency')
axs[0, 1].set_xlabel('Number of Clients')
axs[0, 1].set_ylabel('Latency (ms)')
axs[0, 1].grid(True)

# CPU
axs[1, 0].plot(clients, cpu, marker='^', color='tab:red', label='CPU (%)')
axs[1, 0].set_title('CPU Usage')
axs[1, 0].set_xlabel('Number of Clients')
axs[1, 0].set_ylabel('CPU (%)')
axs[1, 0].grid(True)

# Memory
axs[1, 1].plot(clients, memory, marker='D', color='tab:green', label='Memory (MB)')
axs[1, 1].set_title('Memory Usage')
axs[1, 1].set_xlabel('Number of Clients')
axs[1, 1].set_ylabel('Memory (MB)')
axs[1, 1].grid(True)

plt.tight_layout()
plt.savefig("results/05_film_rental_history.png")