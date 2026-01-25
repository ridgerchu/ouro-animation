import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

# Load the results data
with open('results.json', 'r') as f:
    results = json.load(f)

# === 全局字体增大（放在 import 之后，任何绘图之前）===
plt.rcParams.update({
    "font.size": 12,       # 基础字体
    "axes.titlesize": 14,  # 图标题
    "axes.labelsize": 12,  # 坐标轴标题
    "xtick.labelsize": 11, # x 轴刻度
    "ytick.labelsize": 11, # y 轴刻度
    "legend.fontsize": 11  # 图例文字
})

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(results)

# ===== 仅保留“同款模型里同时存在 loop 与 unloop”的样本 =====
# 判定是否 loop：按 max_loops > 1（如你们标准不同，可自行改这一行）
def _is_loop(ci):
    return (ci.get('max_loops', 0) or 0) > 1

# 标记是否 loop
df['__is_loop'] = df['checkpoint_info'].apply(_is_loop)

# 定义“同款模型”的 key（同 hidden_dim & n_layers）
# 如需更严格（同款+同数据量），把下行替换成包含 dataset_size_k 的三元组：
# df['__pair_key'] = df['checkpoint_info'].apply(lambda ci: (ci['hidden_dim'], ci['n_layers'], ci['dataset_size_k']))
df['__pair_key'] = df['checkpoint_info'].apply(lambda ci: (ci['hidden_dim'], ci['n_layers']))

# 只保留在同一 __pair_key 下同时存在 loop 与 unloop 的行
mask_has_both = df.groupby('__pair_key')['__is_loop'].transform(lambda s: s.nunique() == 2)
df = df[mask_has_both].reset_index(drop=True)

# （可选的稳妥提示）若过滤后为空，给出信息以免后续报错
if len(df) == 0:
    raise ValueError("过滤后没有成对（loop/unloop）的同款模型数据，请检查 results.json 或配对键定义。")

# Scatter plot: x = P_params (log scale), y = capacity_ratio * P_params (log scale)
x_list = []
y_list = []
number_of_samples_list = []
for i in range(len(df)):
    xi = df["P_params"][i]
    yi = df["capacity_ratio"][i]["R"] * df["P_params"][i]
    x_list.append(xi)
    y_list.append(yi)

    number_of_samples_list.append(df['checkpoint_info'][i]['dataset_size_k'])

fig, ax = plt.subplots(figsize=(8, 6))  # 4:3 比例

# Assign a color to each unique number of samples
unique_samples = sorted(set(number_of_samples_list))
# Use a set of distinct, high-contrast colors for better visibility
from matplotlib import cm

# Use the 'tab10' colormap for up to 10 distinct colors, or 'tab20' for more
if len(unique_samples) <= 10:
    base_cmap = plt.cm.get_cmap('tab10')
else:
    base_cmap = plt.cm.get_cmap('tab20')

color_map = {val: base_cmap(i % base_cmap.N) for i, val in enumerate(unique_samples)}
colors = [color_map[n] for n in number_of_samples_list]

max_loops_list = [df['checkpoint_info'][i].get('max_loops', 0) for i in range(len(df))]
JITTER_L1  = 0.98   # 稍微向下
JITTER_L4  = 1.02   # 稍微向上
JITTER_OTH = 1.00   # 其他保持不变

y_list_plot = []
for y, ml in zip(y_list, max_loops_list):
    if ml == 1:
        y_list_plot.append(y * JITTER_L1)
    elif ml == 4:
        y_list_plot.append(y * JITTER_L4)
    else:
        y_list_plot.append(y * JITTER_OTH)

SIZE_LOOP1 = 90
SIZE_LOOP4 = 210
SIZE_OTHER = 90
sizes = []
for ml in max_loops_list:
    if ml == 1:
        sizes.append(SIZE_LOOP1)
    elif ml == 4:
        sizes.append(SIZE_LOOP4)
    else:
        sizes.append(SIZE_OTHER)

ax.scatter(
    x_list,
    y_list_plot,
    s=sizes,
    c=colors,
    alpha=0.7,
    linewidths=0.5,
    edgecolors='k'
)

# Create a legend for number of samples
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label=f'# {val}k',
           markerfacecolor=color_map[val], markeredgecolor='k', markersize=8)
    for val in unique_samples
]
# Add the y/x lines to the legend as well
# Add lines for y/x = 2, 1，但不加入图例
x_vals = np.logspace(np.log10(min(x_list)), np.log10(max(x_list)), 100)
for ratio, style, color in zip([2, 1], ['--', '-'], ['red', 'black']):
    ax.plot(x_vals, ratio * x_vals, style, color=color, label=None)

def _legend_marker_size(area):
    return np.sqrt(area) * 0.45

loop_handles = [
    Line2D(
        [0], [0], marker='o', color='w', label='loop-1',
        markerfacecolor='lightgray', markeredgecolor='k',
        markersize=_legend_marker_size(SIZE_LOOP1)
    ),
    Line2D(
        [0], [0], marker='o', color='w', label='loop-4',
        markerfacecolor='lightgray', markeredgecolor='k',
        markersize=_legend_marker_size(SIZE_LOOP4)
    )
]
legend_elements.extend(loop_handles)

line_handles = [
    Line2D([0], [0], linestyle=style, color=color, label=f'{ratio} bit / param')
    for ratio, style, color in zip([2, 1], ['--', '-'], ['red', 'black'])
]
legend_elements.extend(line_handles)

ax.legend(handles=legend_elements, loc='upper left', frameon=True, title="Legend")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Number of Parameters (P_params, log scale)")
ax.set_ylabel("Bits of Knowledge (log scale)")
ax.set_title("Scaling: Bits of Knowledge vs. Params")
ax.grid(True, which="both", ls="--", alpha=0.5)

fig.tight_layout()
fig.savefig('knowledge_scaling.png', dpi=300)
fig.savefig('knowledge_scaling.pdf', dpi=300)
