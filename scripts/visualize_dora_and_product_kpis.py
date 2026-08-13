import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def generate_visual_charts():
    output_dir = '/home/ubuntu/AI-Code-Reviewer/reports/visuals'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Set professional dark theme
    plt.style.use('dark_background')
    
    # --- Chart 1: DORA Metrics Trends ---
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    quarters = ['Q1', 'Q2', 'Q3', 'Q4 (Proj)']
    deploy_freq = [5, 12, 18, 25]
    lead_time = [12.0, 8.0, 4.0, 2.0]
    
    ax1.plot(quarters, deploy_freq, marker='o', color='#3b82f6', linewidth=4, label='Deployment Frequency (per month)')
    ax1.set_ylabel('Frequency', color='#3b82f6', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#3b82f6')
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(quarters, lead_time, marker='s', color='#fb7185', linewidth=4, linestyle='--', label='Lead Time for Changes (hours)')
    ax1_twin.set_ylabel('Hours', color='#fb7185', fontsize=12, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor='#fb7185')
    
    plt.title('DORA Metrics: Velocity & Efficiency Trends', fontsize=18, fontweight='bold', pad=20)
    ax1.grid(True, linestyle=':', alpha=0.4)
    fig1.legend(loc='upper left', bbox_to_anchor=(0.15, 0.85), frameon=True, facecolor='#111827')
    
    path1 = os.path.join(output_dir, 'dora_metrics_trends.png')
    plt.savefig(path1, dpi=150, bbox_inches='tight')
    print(f"DORA chart saved to: {path1}")

    # --- Chart 2: Product Health & Accuracy ---
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    metrics = ['SAST Accuracy', 'AI Precision', 'Dependency Pass', 'Secret Scan FP']
    values = [94.0, 94.0, 98.0, 1.2]
    targets = [95.0, 90.0, 98.0, 1.0]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ax2.bar(x - width/2, values, width, label='Actual (Q3)', color='#10b981', alpha=0.8)
    ax2.bar(x + width/2, targets, width, label='Target / SLA', color='#6366f1', alpha=0.4)
    
    ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Product Health: Scan Accuracy vs Targets', fontsize=18, fontweight='bold', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics)
    ax2.legend()
    ax2.grid(axis='y', linestyle=':', alpha=0.4)
    
    path2 = os.path.join(output_dir, 'product_health_accuracy.png')
    plt.savefig(path2, dpi=150, bbox_inches='tight')
    print(f"Product health chart saved to: {path2}")

    return path1, path2

if __name__ == '__main__':
    generate_visual_charts()
