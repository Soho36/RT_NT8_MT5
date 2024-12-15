# Function to read levels from the first file (NT8 chart levels)
def read_chart_levels(file_path):
    levels = set()
    with open(file_path, 'r') as file:
        for line in file:
            # Extract price after the comma
            try:
                price = float(line.split(',')[-1].strip())
                levels.add(price)
            except ValueError:
                print(f"Invalid line in chart levels file: {line}")
    return levels


# Function to read prices from the second and third files (script and expired levels)
def read_price_levels(file_path):
    levels = set()
    with open(file_path, 'r') as file:
        for line in file:
            # Extract price after the comma
            try:
                price = float(line.split(',')[1].strip())
                levels.add(price)
            except (IndexError, ValueError):
                print(f"Invalid line in file: {line}")
    return levels


# Function to append new levels to the second file
def append_new_levels(file_path, new_levels):
    with open(file_path, 'a') as file:
        for level in new_levels:
            # Add a dummy timestamp for simplicity (could be replaced with actual logic)
            file.write(f"{level}\n")


# Main logic


# File paths
chart_levels_file = "chart_levels.txt"
python_levels_file = "python_levels.txt"
expired_levels_file = "expired_levels.txt"

# Step 1: Read levels from files
chart_levels = read_chart_levels(chart_levels_file)
read_price_levels(python_levels_file)
expired_levels = read_price_levels(expired_levels_file)

# Step 2: Find new levels (in chart_levels but not in expired_levels)
new_levels = chart_levels - expired_levels

# Step 3: Append new levels to the Python levels file
append_new_levels(python_levels_file, new_levels)

print("New levels added to the Python script file.")
