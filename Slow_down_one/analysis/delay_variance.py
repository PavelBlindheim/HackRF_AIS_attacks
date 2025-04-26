import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # Add this import to the script


def read_values(file_path):
    with open(file_path, 'r') as f:
        return [float(line.strip()) for line in f]

def plot_differences(base_path, selected_folder):
    attacker_path = os.path.join(base_path, "attacker", selected_folder)
    victim_path = os.path.join(base_path, "victim", selected_folder)
    
    if not os.path.isdir(attacker_path) or not os.path.isdir(victim_path):
        print("Invalid folder selection.")
        return
    
    all_differences = []
    
    for i in range(1, 6):  # Files 1.txt to 5.txt
        attacker_file = os.path.join(attacker_path, f"{i}.txt")
        victim_file = os.path.join(victim_path, f"{i}.txt")
        
        if not os.path.exists(attacker_file) or not os.path.exists(victim_file):
            print(f"Skipping {i}.txt due to missing files.")
            continue
        
        attacker_values = read_values(attacker_file)
        victim_values = read_values(victim_file)
        
        if len(attacker_values) != len(victim_values):
            print(f"Skipping {i}.txt due to mismatched line counts.")
            continue
        
        differences = [a - v for a, v in zip(attacker_values, victim_values)]
        all_differences.append(differences)
        
        plt.plot(differences, label=f"Test {i}")
    
    # Compute and plot the average difference
    if all_differences:
        avg_diff = [sum(x) / len(x) for x in zip(*all_differences)]
        plt.plot(avg_diff, label="Average", linewidth=2.5, color="black")
    
    # Add y=0 reference line
    plt.axhline(0, color='black', linewidth=1)
    
    plt.xlabel("Signal")
    plt.ylabel("Delay of attacking signal")
    plt.ylim(-0.1, 0.4)
    plt.xticks(np.arange(0, 20, step=1))
    plt.yticks(np.arange(-0.2, 0.51, step=0.1))
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.02))
    plt.gca().tick_params(which='minor', length=3)
    plt.title(f"Delay aimed at {selected_folder}")
    plt.legend()
    plt.show()

def main():
    base_path = "/home/pavel/Documents/master/ships/scripts/new_slow_down_one/results"  # Change this to your actual folder path
    selected_folder = input("Enter folder to analyze (e.g., 0ms, 50ms, etc.): ")
    plot_differences(base_path, selected_folder)

if __name__ == "__main__":
    main()
