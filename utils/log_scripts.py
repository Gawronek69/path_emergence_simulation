import pandas as pd
import re

def time_info():
    data = []
    log_file = "simulation_performance.log"


    pattern = re.compile(r"INFO - (\w+) took ([\d\.]+)s")

    try:
        with open(log_file, "r") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    func_name = match.group(1)
                    duration = float(match.group(2))
                    data.append({"function": func_name, "duration": duration})
    except FileNotFoundError:
        print(f"Error: Could not find file '{log_file}'")
        return

    if not data:
        print("No matches found! Check your regex or if the log file is empty.")
        return

    df = pd.DataFrame(data)

    print("--- STATISTICS ---")
    print(df.groupby("function")["duration"].describe())