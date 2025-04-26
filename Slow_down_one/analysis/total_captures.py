import os
import pandas as pd
from collections import defaultdict

def count_lines(base_path):
    results = defaultdict(lambda: defaultdict(lambda: {'25.0': 0, '12.5': 0}))
    
    # Iterate through each folder (0ms, 100ms, etc.)
    for folder in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder)
        
        if os.path.isdir(folder_path):
            # Iterate through each file in the folder
            for file in sorted(os.listdir(folder_path)):
                if file.startswith("captures_") and file.endswith(".txt"):
                    file_path = os.path.join(folder_path, file)
                    
                    with open(file_path, 'r') as f:
                        for line in f:
                            if line.startswith("25.0"):
                                results[folder][file]['25.0'] += 1
                            elif line.startswith("12.5"):
                                results[folder][file]['12.5'] += 1
    
    return results

def main():
    base_path = "/home/pavel/Documents/master/ships/scripts/new_slow_down_one/results/observer"
    data = count_lines(base_path)
    
    # Convert results to a Pandas DataFrame for table format
    rows = []
    for folder, files in data.items():
        for file, counts in files.items():
            rows.append([folder, file, counts['25.0'], counts['12.5']])
    
    df = pd.DataFrame(rows, columns=['Delay', 'File', 'Real signal', 'Spoofed signal'])
    print(df)
    
    # Save to CSV if needed
    df.to_csv("output.csv", index=False)

if __name__ == "__main__":
    main()
