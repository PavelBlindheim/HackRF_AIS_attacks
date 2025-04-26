import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_success_rates(base_path, selected_folder):
    folder_path = os.path.join(base_path, selected_folder)
    
    if not os.path.isdir(folder_path):
        print("Invalid folder selection.")
        return
    
    success_rates_25 = []
    success_rates_12_5 = []
    success_rates_custom = []
    
    for i in range(1, 6):  # Files captures_1.txt to captures_5.txt
        captures_file = os.path.join(folder_path, f"captures_{i}.txt")
        successrate_file = os.path.join(folder_path, f"successrate_{i}.txt")
        
        count_25 = 0
        count_12_5 = 0
        
        if os.path.exists(captures_file):
            with open(captures_file, 'r') as f:
                for line in f:
                    if line.startswith("25.0"):
                        count_25 += 1
                    elif line.startswith("12.5"):
                        count_12_5 += 1
        
        success_rate_25 = count_25 / 21
        success_rate_12_5 = count_12_5 / 20
        success_rates_25.append(success_rate_25)
        success_rates_12_5.append(success_rate_12_5)
        
        if os.path.exists(successrate_file):
            with open(successrate_file, 'r') as f:
                y_value = float(f.readline().strip())
                success_rate_custom = (20 - y_value) / 20
                success_rates_custom.append(success_rate_custom)
        
    avg_25 = sum(success_rates_25) / len(success_rates_25)
    avg_12_5 = sum(success_rates_12_5) / len(success_rates_12_5)
    avg_custom = sum(success_rates_custom) / len(success_rates_custom)
    
    return avg_25, avg_12_5, avg_custom

def plot_success_rates(base_path, selected_folder):
    avg_25, avg_12_5, avg_custom = calculate_success_rates(base_path, selected_folder)
    
    labels = ["RS reception rate", "FS reception rate", "Attack success rate"]
    values = [avg_25, avg_12_5, avg_custom]
    
    # Define colors transitioning from red (low success) to green (high success)
    colors = [(2 * (1 - value), 1, 0) for value in values]
    
    bars = plt.bar(labels, values, color=colors)
    plt.ylabel("Average Success Rate")
    plt.ylim(0, 1)
    plt.title(f"Average success rates at {selected_folder} delay")
    
    # Add percentage labels inside the bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{value*100:.1f}%", 
                 ha='center', va='center', fontsize=12, color='white', fontweight='bold')
    
    plt.show()

def main():
    base_path = "/home/pavel/Documents/master/ships/scripts/new_slow_down_one/results/observer"  # Change this to your actual folder path
    selected_folder = input("Enter folder to analyze (e.g., 0ms, 50ms, etc.): ")
    plot_success_rates(base_path, selected_folder)

if __name__ == "__main__":
    main()
