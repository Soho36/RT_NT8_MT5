for i in range(5):
    if i == 2:
        print(f"Skipping {i} using 'continue'")
        break  # Skip the rest of the loop for this iteration and go to the next one
    elif i == 3:
        print(f"Breaking the loop at {i}")
        break  # Exit the loop completely
    print(f"Processing {i}")  # Only runs if neither 'continue' nor 'break' was triggered
