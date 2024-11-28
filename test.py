# Initialize variables
red_candle_found = False
red_candle_high = None
potential_ob_time = None

for subsequent_index in range(index + 1, len(output_df_with_levels)):

    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]

    # Convert to datetime for time calculations
    potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

    # Calculate time difference between the current potential candle
    # and the initial SR level interaction
    time_diff = (potential_ob_time - pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60

    # Check if we've exceeded the maximum waiting time
    trace = 'BR-O_longs_1'
    if check_time_limit(
            max_time_waiting_for_entry,
            subsequent_index,
            potential_ob_time,
            level_interaction_signal_time,
            time_diff,
            trace
    ):
        break  # Exit the loop if time limit is exceeded

    print(
        f"Looking for RED candle at index {subsequent_index}, "
        f"Time: {potential_ob_time}"
    )

    # Check if it's a red candle (close < open)
    if potential_ob_candle['Close'] < potential_ob_candle['Open']:
        print(
            f"○ Last RED candle found at index {subsequent_index}, "
            f"Time: {potential_ob_time}"
        )
        # Check if the red candle is above the SR level
        if potential_ob_candle['Close'] > current_sr_level:
            # Candle must be above the level
            red_candle_high = potential_ob_candle['High']
            red_candle_found = True

            # Check the current position state
            current_position_state = get_position_state()
            if current_position_state == '' or current_position_state == 'closed':
                print(
                    f"⦿ It's above the level at index {subsequent_index}, "
                    f"Time: {potential_ob_time}"
                )
                print('PLACE STOPMARKET.2B')

                # Use the current red candle data to create the signal
                signal = f'100+{subsequent_index}'
                trigger_price = potential_ob_candle['High']  # Ensure it's the current red candle high

                # Generate and send the signal
                s_signal, n_index, t_price = signal_triggered_output(
                    subsequent_index,
                    potential_ob_time,
                    trigger_price,
                    trade_type,
                    side,
                    signal
                )

                # Reset variables after signal creation to avoid stale data
                red_candle_high = None
                potential_ob_time = None

                # Break after generating the signal
                break
            else:
                # Position is open, continue tracking candles but do not generate signals
                print('THERE IS AN OPEN POSITION. SKIPPING SIGNAL CREATION...'.upper())

                # Clear stale data to avoid reusing old values when position closes
                red_candle_high = None
                potential_ob_time = None
