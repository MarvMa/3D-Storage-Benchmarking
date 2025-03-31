import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import ScalarFormatter

# Stil-Konfiguration
VALID_STYLES = plt.style.available
PLOT_STYLE = 'ggplot' if 'ggplot' in VALID_STYLES else 'default'
FONT_SIZE = 12
DPI = 300
FIGSIZE = (10, 6)
COLORS = {'file': '#1f77b4', 'db': '#ff7f0e', 'minio': '#2ca02c'}
LINE_STYLES = {'file': '-', 'db': '--', 'minio': ':'}

# Daten laden
with open('../benchmark_results/benchmark_02/benchmark_results_50_users_median.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)
os.makedirs('diagrams', exist_ok=True)


# Wissenschaftliche Diagrammgestaltung
def configure_plot(ax, title, ylabel):
    ax.set_title(title, fontsize=FONT_SIZE + 2, weight='bold')
    ax.set_xlabel('Time Elapsed (s)', fontsize=FONT_SIZE)
    ax.set_ylabel(ylabel, fontsize=FONT_SIZE)
    ax.grid(True, which='both', linestyle=':', alpha=0.7)
    ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE - 2)
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(ScalarFormatter())


# Individual Plots
for file_size in ['small', 'medium', 'large']:
    plt.style.use(PLOT_STYLE)
    fig, ax = plt.subplots(figsize=FIGSIZE)

    for storage in COLORS.keys():
        subset = df[(df['file_size'] == file_size) & (df['storage'] == storage)]
        if not subset.empty:
            latencies = subset['latency'].explode().astype(float).values
            time_axis = np.linspace(0, 600, len(latencies))  # 600s = 10min

            ax.plot(
                time_axis,
                latencies,
                color=COLORS[storage],
                linestyle=LINE_STYLES[storage],
                marker='o' if file_size == 'small' else '',
                markersize=4,
                linewidth=1.5,
                label=f'{storage.upper()}'
            )

    configure_plot(ax,
                   f'Latency Progression ({file_size.capitalize()} Files)',
                   'Latency (ms)')

    ax.legend(frameon=True, fontsize=FONT_SIZE - 2, loc='upper center',
              bbox_to_anchor=(0.5, -0.15), ncol=3)
    plt.tight_layout()
    plt.savefig(f'diagrams/latency_{file_size}.png', dpi=DPI, bbox_inches='tight')
    plt.close()

# Aggregierter Plot
plt.style.use(PLOT_STYLE)
fig, ax = plt.subplots(figsize=FIGSIZE)

metrics = []
for storage in COLORS.keys():
    median_latencies = [
        df[(df['storage'] == storage) & (df['file_size'] == fs)]['latency'].median()
        for fs in ['small', 'medium', 'large']
    ]
    metrics.append(median_latencies)

x = np.arange(3)
width = 0.25

for idx, (storage, latencies) in enumerate(zip(COLORS.keys(), metrics)):
    ax.bar(x + width * idx, latencies, width,
           color=COLORS[storage],
           edgecolor='black',
           label=f'{storage.upper()}')

ax.set_xticks(x + width)
ax.set_xticklabels(['Small', 'Medium', 'Large'])
ax.set_ylabel('Median Latency (ms)', fontsize=FONT_SIZE)
ax.set_title('Aggregated Latency Comparison', fontsize=FONT_SIZE + 2, weight='bold')
ax.legend(fontsize=FONT_SIZE - 2)
ax.set_yscale('log')
ax.yaxis.set_major_formatter(ScalarFormatter())

plt.tight_layout()
plt.savefig('diagrams/aggregated_latency.png', dpi=DPI)
plt.close()

print("Erfolgreich generierte Diagramme:")
print("- latency_small.png\n- latency_medium.png\n- latency_large.png")
print("- aggregated_latency.png")