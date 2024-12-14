import os

nt8_file = "nt8_levels.csv"
python_file = "python_valid_levels.csv"
expired_file = "expired_levels.csv"


# Load levels from files
def load_levels(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, 'r') as f:
        return {line.strip() for line in f}


nt8_levels = load_levels(nt8_file)
python_levels = load_levels(python_file)
expired_levels = load_levels(expired_file)
print('nt8_levels', nt8_levels)
print('python_levels', python_levels)
print('expired_levels', expired_levels)

# Process NT8 levels
new_levels = nt8_levels - python_levels - expired_levels
print('new_levels', new_levels)

if new_levels:
    with open(python_file, 'a') as f:
        for level in new_levels:
            f.write(level + '\n')
    print(f"Added new levels: {new_levels}")

# Remove expired levels
current_valid_levels = python_levels & nt8_levels
expired_now = python_levels - current_valid_levels
print('current_valid_levels', current_valid_levels)
print('expired_now', expired_now)

if expired_now:
    with open(expired_file, 'a') as f:
        for level in expired_now:
            f.write(level + '\n')
    print(f"Expired levels: {expired_now}")

# Update Python valid levels file
with open(python_file, 'w') as f:
    for level in current_valid_levels:
        f.write(level + '\n')
