# This script contains all calculations for the evaluation part of my thesis

import csv
from itertools import combinations

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ks_2samp
from statsmodels.stats.multitest import multipletests

main_path = r"Path to GreyBoxGrammar_Runs"

csv_files = [f"{main_path}\\output_1",
             f"{main_path}\\output_2",
             f"{main_path}\\output_3",
             f"{main_path}\\output_4",
             f"{main_path}\\output_5"]

# csv_files = [f"D:/Projects/benchmarkResults/output_cmplog1",
#              f"D:/Projects/benchmarkResults/output_cmplog2",
#              f"D:/Projects/benchmarkResults/output_cmplog3",
#              f"D:/Projects/benchmarkResults/output_cmplog4",
#              f"D:/Projects/benchmarkResults/output_cmplog5"]

seed_strategies = [("single", "single"),
                   ("cov", "random"),
                   ("max_cov", "max cov"),
                   ("1-wise", "t = 1"),
                   ("2-wise", "t = 2")]

# seed_strategies = [("cov", "random"),
#                    ("cov_cmplog", "random CmpLog")]

result_seed_strategies = {}
result_execs_per_sec = {}

for seed_strategy in seed_strategies:
    result_seed_strategies[seed_strategy[0]] = []
    result_execs_per_sec[seed_strategy[0]] = []

# Read each csv file
for csv_file in csv_files:
    for seed_strategy in seed_strategies:
        csv_file_paths = [(f"{csv_file}/{seed_strategy[0]}/default/plot_data", "normal")]
        count = 0
        for csv_file_path_tuple in csv_file_paths:
            csv_file_path = csv_file_path_tuple[0]
            with open(csv_file_path, 'r') as file:
                reader = csv.reader(file)
                # Skip the header row
                next(reader)
                edges_found = []
                total_execs = []
                execs_per_sec = []
                for row in reader:
                    edges_found.append(int(row[-1]))
                    total_execs.append(int(row[-2]))  # Append total_execs
                    execs_per_sec.append(float(row[-3]))
                combined_analyzed = pd.DataFrame({'execs': total_execs, 'edges': edges_found}).set_index('execs')
                result_seed_strategies[seed_strategy[0]].append(combined_analyzed)
                result_execs_per_sec[seed_strategy[0]].extend(execs_per_sec)

fig, axs = plt.subplots(len(seed_strategies), figsize=(5, 9))

# Define a color palette
palette = sns.color_palette("husl", len(seed_strategies))

combined_mean = None
combined_strategies = {}
for i, seed_strategy in enumerate(seed_strategies):
    results = result_seed_strategies[seed_strategy[0]]

    test = result_execs_per_sec[seed_strategy[0]]

    median_execs = np.median(test)
    print(f"Key \"{seed_strategy[1]}\" has a median of {median_execs} execs/s")

    combined = None

    for index, result in enumerate(results):
        if combined is None:
            combined = result
            continue

        combined = combined.join(result, rsuffix=f'_{index}', how='outer')

    combined = combined.ffill().dropna().iloc[::5, :]
    combined_strategies[seed_strategy[0]] = combined
    mean = combined.mean(axis=1)
    combined_analyzed = pd.DataFrame(
        {'mean': mean, 'min': combined.min(axis=1), 'max': combined.max(axis=1)}
    )

    mean_dataframe = pd.DataFrame({seed_strategy[1]: mean})
    if combined_mean is None:
        combined_mean = mean_dataframe
    else:
        combined_mean = combined_mean.join(mean_dataframe, how='outer')

    color = palette[i]
    light_color = sns.light_palette(color, as_cmap=True)(0.5)

    sns.lineplot(data=combined_analyzed, x='execs', y='mean', color=color, ax=axs[i], legend='brief', label="mean")
    sns.lineplot(data=combined_analyzed, x='execs', y='min', color=light_color, ax=axs[i])
    sns.lineplot(data=combined_analyzed, x='execs', y='max', color=light_color, ax=axs[i])
    line = axs[i].lines
    axs[i].fill_between(line[0].get_xdata(), line[1].get_ydata(), line[2].get_ydata(), color=light_color)
    axs[i].set_title(seed_strategy[1])
    axs[i].set_xlabel("total executions")
    axs[i].set_ylabel("edges found")
    axs[i].set_xlim([0, 1250000000])
    axs[i].set_ylim([6000, 8000])
    # Edge case hack
    if i == 0:
        axs[i].legend(loc="upper left")

plt.tight_layout()
plt.show()

combined_mean = combined_mean.ffill().dropna().iloc[::5, :]

data = [(value, strategy) for strategy, values in combined_strategies.items()
        for value in values.loc[:1250000000].values.flatten()]

combined_analyzed = pd.DataFrame(data, columns=['Edges', 'Strategy'])

combined_analyzed = combined_analyzed.replace({'cov': 'random', 'cov_cmplog': 'random CmpLog', "max_cov": "max cov", "1-wise": "t = 1", "2-wise": "t = 2"})


sns.set_theme(rc={'figure.figsize':(5.0, 2.0)})
sns.displot(combined_analyzed, kind='ecdf', x='Edges', hue='Strategy', palette=palette)
plt.show()

for pair in combinations(seed_strategies, 2):
    sampleAKey = pair[0][0]
    sampleBKey = pair[1][0]

    sampleA = combined_strategies[sampleAKey].loc[:1250000000].values.flatten().tolist()
    sampleB = combined_strategies[sampleBKey].loc[:1250000000].values.flatten().tolist()

    # Tests the null hypothesis is that sampleA(x) <= sampleBKey(x) for all x. Small p-values indicate that it's the alt greater
    statistic_great = ks_2samp(sampleA, sampleB, alternative='greater')

    statistic_less = ks_2samp(sampleA, sampleB, alternative='less')

    # Apply Benjamini-Hochberg procedure
    pvalues = [statistic_great.pvalue, statistic_less.pvalue]
    reject, pvals_corrected, _, _ = multipletests(pvalues, method='fdr_bh')

    print(f"{sampleAKey} > {sampleBKey}: {pvals_corrected[0]:.2f}")
    print(f"{sampleAKey} < {sampleBKey}: {pvals_corrected[1]:.2f}")

    # Interpret results
    if not reject[0] and reject[1]:
        print(f"{sampleAKey} is stochastically dominant over {sampleBKey}")
    elif not reject[1] and reject[0]:
        print(f"{sampleBKey} is stochastically dominant over {sampleAKey}")
    else:
        print(f"No conclusive evidence of stochastic dominance in either direction, {sampleAKey} vs. {sampleBKey}")


plt.figure(figsize=(5, 4))
sns.lineplot(data=combined_mean, palette=palette)
ax = plt.gca()
ax.set_xlim([0, 1250000000])
ax.set_ylim([6400, 7600])
ax.set_xlabel("total executions")
ax.set_ylabel("edges found")
plt.tight_layout()
plt.show()
