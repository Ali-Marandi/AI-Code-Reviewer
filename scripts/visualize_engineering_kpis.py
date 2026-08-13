import matplotlib
matplotlib.use('Agg') # Use non-interactive backend to avoid Qt plugin issues
import matplotlib.pyplot as plt
import numpy as np
import os

def create_dashboard():
    # Set dark theme style
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('AI-Code-Reviewer Enterprise: Engineering KPI Dashboard', fontsize=24, fontweight='bold', color='#38bdf8', y=0.98)
    
    # 1. DORA Metrics: Deployment Frequency & Lead Time
    ax1 = plt.subplot(2, 2, 1)
    quarters = ['Q1', 'Q2', 'Q3', 'Q4 (Proj)']
    deployments = [5, 12, 18, 25]
    lead_time = [12, 8, 4, 2] # hours
    
    ax1.plot(quarters, deployments, marker='o', color='#38bdf8', linewidth=3, label='Deployments/Month')
    ax1.set_title('Delivery Velocity (DORA)', fontsize=16, color='white', pad=15)
    ax1.set_ylabel('Count', color='#a1a1aa')
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.legend(loc='upper left')
    
    ax1_twin = ax1.twinx()
    ax1_twin.bar(quarters, lead_time, alpha=0.2, color='#4ec9b0', label='Lead Time (Hrs)')
    ax1_twin.set_ylabel('Hours', color='#a1a1aa')
    ax1_twin.legend(loc='upper right')

    # 2. Product Health: Scan Findings & Accuracy
    ax2 = plt.subplot(2, 2, 2)
    categories = ['SAST', 'AI Review', 'Dependency', 'Secret Scan']
    findings = [120, 85, 45, 12]
    accuracy = [92, 94, 98, 100] # percentages
    
    colors = ['#38bdf8', '#4ec9b0', '#818cf8', '#fb7185']
    ax2.bar(categories, findings, color=colors, alpha=0.8)
    ax2.set_title('Scan Health & Finding Volume', fontsize=16, color='white', pad=15)
    ax2.set_ylabel('Findings Count', color='#a1a1aa')
    
    ax2_twin = ax2.twinx()
    ax2_twin.step(categories, accuracy, where='mid', color='white', linestyle=':', linewidth=2, label='Accuracy %')
    ax2_twin.set_ylim(80, 105)
    ax2_twin.set_ylabel('Accuracy %', color='#a1a1aa')
    ax2_twin.legend()

    # 3. Engineering Scaling: Headcount vs Plan
    ax3 = plt.subplot(2, 2, 3)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    actual_hc = [4, 5, 7, 8, 11, 12]
    target_hc = [4, 6, 8, 10, 12, 14]
    
    ax3.fill_between(months, target_hc, color='#38bdf8', alpha=0.1, label='Target')
    ax3.plot(months, actual_hc, color='#38bdf8', marker='s', linewidth=2, label='Actual')
    ax3.set_title('Engineering Scaling: Headcount', fontsize=16, color='white', pad=15)
    ax3.set_ylabel('Staff Count', color='#a1a1aa')
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.2)

    # 4. Critical Quality Gates Status
    ax4 = plt.subplot(2, 2, 4)
    gates = ['v1.1.0 Release', 'i18n Foundation', 'Security Audit', 'Design Partner']
    status = [100, 100, 85, 60] # Completion %
    
    y_pos = np.arange(len(gates))
    ax4.barh(y_pos, status, color='#4ec9b0', alpha=0.7)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(gates, color='white')
    ax4.set_xlim(0, 110)
    ax4.set_title('Phase 1 Execution Progress (%)', fontsize=16, color='white', pad=15)
    ax4.set_xlabel('Completion %', color='#a1a1aa')
    
    for i, v in enumerate(status):
        ax4.text(v + 2, i, f"{v}%", color='white', va='center', fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    output_dir = '/home/ubuntu/AI-Code-Reviewer/reports'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'engineering_kpi_dashboard.png')
    plt.savefig(output_path, dpi=150)
    print(f"Dashboard saved to: {output_path}")
    return output_path

if __name__ == '__main__':
    create_dashboard()
