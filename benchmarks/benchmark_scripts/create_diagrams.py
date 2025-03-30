import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

with open('benchmark_results.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)

for metric in ['latency', 'cpu_usage', 'memory_usage', 'io_read', 'io_write']:
    df[metric] = df[metric].apply(
        lambda x: np.mean(x) if isinstance(x, list) and len(x) > 0 else 0
    )
    df[metric] = pd.to_numeric(df[metric], errors='coerce').fillna(0)

# Farben für Storage-Typen
colors = {
    'file': '#1f77b4',
    'db': '#ff7f0e',
    'minio': '#2ca02c'
}

for file_size in ['small', 'medium', 'large']:
    for metric, ylabel in [
        ('latency', 'Latency (s)'),
        ('cpu_usage', 'CPU Usage (%)'),
        ('memory_usage', 'Memory Usage (MB)'),
        ('io_read', 'IO Read (MB/s)'),
        ('io_write', 'IO Write (MB/s)')
    ]:
        plt.figure(figsize=(10, 6))

        subset = df[df['file_size'] == file_size]
        storages = subset['storage'].unique()
        values = [subset[subset['storage'] == s][metric].mean() for s in storages]

        bars = plt.bar(
            storages,
            values,
            color=[colors[s] for s in storages],
            edgecolor='black'
        )

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.,
                height * 1.02,
                f'{height:.2f}',
                ha='center',
                va='bottom'
            )

        plt.title(f'{file_size.capitalize()} File - {metric.replace("_", " ").title()}')
        plt.xlabel('Storage Type')
        plt.ylabel(ylabel)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Log-Skala für bestimmte Metriken
        if metric in ['latency', 'io_write']:
            plt.yscale('log')

        plt.tight_layout()
        plt.savefig(f"{file_size}_{metric}_comparison.png")
        plt.close()
