import matplotlib.pyplot as plt

clients = [1, 5, 10, 20, 50, 90]
tps = [1145, 3736, 5708, 6960, 6962, 6404]
latency = [0.873, 1.338, 1.752, 2.873, 7.181, 14.052]
cpu = [34, 137, 200, 200, 200, 200]
memory = [100, 118, 136, 193, 271, 378]

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
plt.savefig("results/08_insert_customer.png")