#!/usr/bin/env python3
"""
分析和比较geometric分布模型(lambda 0.1-0.9)和uniform分布模型的训练loss
从步骤20000-40960，使用300步滑动窗口的滑动平均
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

def extract_loss_from_log(log_file_path, start_step=20000, end_step=40960):
    """从日志文件中提取loss数据"""
    steps = []
    losses = []
    
    print(f"正在处理文件: {log_file_path}")
    
    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 匹配包含step和loss信息的行
            # 例如: [36mstep:   20,000 token: 10,485,760,000.0  [32mloss:  3.1234
            match = re.search(r'step:\s*([0-9,]+).*?loss:\s*([0-9.]+)', line)
            if match:
                step = int(match.group(1).replace(',', ''))
                loss = float(match.group(2))
                
                # 只保留指定范围内的步骤
                if start_step <= step <= end_step:
                    steps.append(step)
                    losses.append(loss)
    
    print(f"  提取到 {len(steps)} 个数据点，步骤范围: {min(steps) if steps else 'N/A'} - {max(steps) if steps else 'N/A'}")
    return steps, losses

def calculate_sliding_average(steps, losses, window_size=300):
    """计算滑动平均"""
    if len(losses) < window_size:
        print(f"警告: 数据点数量 ({len(losses)}) 小于窗口大小 ({window_size})")
        return steps, losses
    
    smoothed_losses = []
    smoothed_steps = []
    
    for i in range(len(losses) - window_size + 1):
        avg_loss = np.mean(losses[i:i + window_size])
        avg_step = np.mean(steps[i:i + window_size])
        smoothed_losses.append(avg_loss)
        smoothed_steps.append(avg_step)
    
    return smoothed_steps, smoothed_losses

def main():
    # 定义文件路径
    base_dir = Path("/Users/bytedance/Documents/UT_materails/geo_vs_uni")
    
    # 定义模型配置
    models = {
        'geometric_0.1': 'geo_0.1.log',
        'geometric_0.2': 'geo_0.2.log', 
        'geometric_0.3': 'geo_0.3.log',
        'geometric_0.4': 'geo_0.4.log',
        'geometric_0.5': 'geo_0.5.log',
        'geometric_0.6': 'geo_0.6.log',
        'geometric_0.7': 'geo_0.7.log',
        'geometric_0.8': 'geo_0.8.log',
        'geometric_0.9': 'geo_0.9.log',
        'uniform': 'uniform.log'
    }
    
    # 存储所有模型的数据
    all_data = {}
    
    # 处理每个模型
    for model_name, log_file in models.items():
        log_path = base_dir / log_file
        if log_path.exists():
            steps, losses = extract_loss_from_log(log_path, start_step=20000, end_step=40960)
            if steps and losses:
                # 计算滑动平均
                smoothed_steps, smoothed_losses = calculate_sliding_average(steps, losses, window_size=300)
                all_data[model_name] = {
                    'steps': smoothed_steps,
                    'losses': smoothed_losses
                }
            else:
                print(f"警告: 文件 {log_file} 中未找到有效数据")
        else:
            print(f"警告: 文件 {log_path} 不存在")
    
    if not all_data:
        print("错误: 未找到任何有效数据")
        return
    
    # 创建图表
    plt.figure(figsize=(14, 8))
    
    # 为geometric模型设置颜色渐变
    geometric_colors = plt.cm.viridis(np.linspace(0, 1, 9))  # 9个geometric模型
    
    # 绘制geometric模型
    for i, (model_name, data) in enumerate(all_data.items()):
        if model_name.startswith('geometric'):
            lambda_val = model_name.split('_')[1]
            plt.plot(data['steps'], data['losses'], 
                    color=geometric_colors[i], 
                    label=f'Geometric λ={lambda_val}', 
                    linewidth=1.5, alpha=0.8)
    
    # 绘制uniform模型（用红色突出显示）
    if 'uniform' in all_data:
        plt.plot(all_data['uniform']['steps'], all_data['uniform']['losses'], 
                color='red', label='Uniform', linewidth=2, alpha=0.9)
    
    # 设置图表属性
    plt.xlabel('Training Steps', fontsize=12)
    plt.ylabel('Loss (300-step sliding average)', fontsize=12)
    plt.title('Training Loss Comparison: Geometric vs Uniform Distribution\n(Steps 20,000-40,960 with 300-step sliding window)', fontsize=14)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存图表
    output_path = base_dir / 'loss_comparison_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存到: {output_path}")
    
    # 显示一些统计信息
    print("\n=== 统计信息 ===")
    for model_name, data in all_data.items():
        if data['losses']:
            final_loss = data['losses'][-1]
            min_loss = min(data['losses'])
            print(f"{model_name:15s}: 最终loss={final_loss:.4f}, 最小loss={min_loss:.4f}, 数据点={len(data['losses'])}")
    
    plt.show()

if __name__ == "__main__":
    main()

