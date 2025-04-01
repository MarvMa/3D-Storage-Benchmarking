import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

VALID_STYLES = plt.style.available
PLOT_STYLE = 'seaborn' if 'seaborn' in VALID_STYLES else 'ggplot'
plt.style.use(PLOT_STYLE)

FONT_SIZE = 12
DPI = 400
FIGSIZE = (12, 6)
COLORS = {'file': '#4C72B0', 'db': '#DD8452', 'minio': '#55A868'}
LINE_STYLES = {'file': '-', 'db': '-', 'minio': '-'}


def format_axis(value, pos):
    if value >= 1e6:
        return f'{value * 1e-6:.1f}M'
    if value >= 1e3:
        return f'{value * 1e-3:.0f}k'
    if value < 1:
        return f'{value:.2f}'
    return f'{value:.0f}'


METRIC_CONFIG = {
    'latency': {'unit': 'ms', 'formatter': format_axis},
    'cpu_usage': {'unit': '%', 'formatter': format_axis},
    'memory_usage': {'unit': 'GB', 'formatter': format_axis}
}


def load_data(filepath: str) -> pd.DataFrame:
    with open(filepath, 'r') as f:
        data = json.load(f)

    df = pd.json_normalize(
        data,
        meta=['storage', 'file_size'],
        errors='ignore'
    )

    df['file_size'] = pd.Categorical(df['file_size'], categories=['small', 'medium', 'large'], ordered=True)

    for metric in ['latency', 'cpu_usage', 'memory_usage']:
        df[metric] = df[metric].apply(lambda x: np.array(x).astype(float) if isinstance(x, list) else np.array([]))

    df['memory_usage'] = df['memory_usage'].apply(lambda x: x / 1e9)
    return df


def auto_scale(values: np.ndarray) -> str:
    if len(values) == 0:
        return 'linear'
    value_range = np.nanmax(values) - np.nanmin(values)
    return 'log' if value_range > 1000 else 'linear'


def create_ts_plots(df: pd.DataFrame) -> None:
    for metric, config in METRIC_CONFIG.items():
        for file_size in ['small', 'medium', 'large']:
            fig, ax = plt.subplots(figsize=FIGSIZE)
            subset = df[df['file_size'] == file_size]
            max_values = []
            for storage in COLORS.keys():
                data = subset[subset['storage'] == storage]
                if not data.empty and data[metric].iloc[0].size > 0:
                    values = data[metric].iloc[0]
                    time_axis = np.linspace(0, 600, len(values))
                    ax.plot(
                        time_axis,
                        values,
                        color=COLORS[storage],
                        linestyle=LINE_STYLES[storage],
                        linewidth=2,
                        label=storage.upper()
                    )
                    max_values.append(np.nanmax(values))
            if max_values:
                all_values = np.concatenate(subset[metric].values) if subset[metric].apply(
                    lambda x: x.size > 0).all() else np.array(max_values)
                scale_type = auto_scale(all_values)
                ax.set_yscale(scale_type)
                ax.xaxis.set_major_formatter(FuncFormatter(format_axis))
                ax.yaxis.set_major_formatter(FuncFormatter(config['formatter']))
                ax.set_title(f'{metric.capitalize()} ({file_size.capitalize()})', fontsize=FONT_SIZE + 2, pad=15)
                ax.set_xlabel('Time (seconds)', fontsize=FONT_SIZE)
                ax.set_ylabel(config['unit'], fontsize=FONT_SIZE)
                ax.grid(True, alpha=0.3)
                ax.legend(loc='upper center', ncol=len(COLORS),
                          bbox_to_anchor=(0.5, -0.15),
                          frameon=False)
            plt.savefig(os.path.join('diagrams', f'{metric}_{file_size}.png'),
                        dpi=DPI, bbox_inches='tight')
            plt.close()


def create_bar_plots(df: pd.DataFrame) -> None:
    for metric, config in METRIC_CONFIG.items():
        fig, ax = plt.subplots(figsize=FIGSIZE)

        agg_data = df.groupby(['storage', 'file_size'], observed=False)[metric] \
            .apply(lambda x: np.nanmedian(np.concatenate(x.values)) if x.size > 0 else np.nan) \
            .unstack()

        agg_data = agg_data[['small', 'medium', 'large']]

        x = np.arange(len(agg_data.columns))
        width = 0.28

        for idx, (storage, row) in enumerate(agg_data.iterrows()):
            ax.bar(x + width * idx, row.values, width,
                   color=COLORS.get(storage, '#000000'),
                   edgecolor='black',
                   linewidth=0.8,
                   label=storage.upper())

        all_values = agg_data.values.flatten()
        scale_type = auto_scale(all_values[~np.isnan(all_values)])
        ax.set_yscale(scale_type)

        ax.set_xticks(x + width)
        ax.set_xticklabels([s.capitalize() for s in agg_data.columns])
        ax.yaxis.set_major_formatter(FuncFormatter(config['formatter']))
        ax.set_title(f'Median {metric.capitalize()} Comparison', fontsize=FONT_SIZE + 2, pad=15)
        ax.set_ylabel(config['unit'], fontsize=FONT_SIZE)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(loc='upper right', frameon=False)

        plt.savefig(os.path.join('diagrams', f'aggregated_{metric}.png'),
                    dpi=DPI, bbox_inches='tight')
        plt.close()


def main():
    os.makedirs('diagrams', exist_ok=True)
    df = load_data('benchmark_results.json')
    create_ts_plots(df)
    create_bar_plots(df)


if __name__ == "__main__":
    main()
