import pandas as pd


"""
Main function analyzing price interaction with levels and long/short signals generation logics
"""


def level_rejection_signals(
        output_df_with_levels,
        sr_levels,
        level_interactions_threshold,
        max_time_waiting_for_entry
):

    n_index = None
    s_signal = None

    # Create a dictionary to track signal count per level
    level_signal_count = {i: 0 for i in range(1, len(sr_levels) + 1)}

    output_df_with_levels.reset_index(inplace=True)

    """
    Function to check if the time difference has exceeded the time limit and print the necessary information.
    Returns True if the time limit is exceeded, otherwise False.
    """
    def check_time_limit(
            m_time_waiting_for_entry,
            subs_index,
            candle_time,
            lev_inter_signal_time,
            t_diff,
            trce
    ):

        if t_diff > m_time_waiting_for_entry:
            print(
                "xxxxxxxxxxxxxxxxx\n"
                f"x {trce}: Exceeded {m_time_waiting_for_entry}-minute window "
                f"at index {subs_index}, \n"
                f"x Level interaction time: {lev_inter_signal_time}, \n"
                f"x Candle time: {candle_time}, \n"
                f"x Time diff: {t_diff} minutes\n"
                "xxxxxxxxxxxxxxxxx"
            )
            return True
        return False

    """
    Print triggered signals
    """
    def signal_triggered_output(
            nn_index,
            sig_time,
            p_level,
            t_type,
            t_side,
            ss_signal
    ):

        print(
            "++++++++++++++++++++++++++\n"
            f"+ {t_type.upper()} {t_side.capitalize()} triggered at index {nn_index}, "
            f"Time: {sig_time}, "
            f"Candle closing price: {p_level}\n"
            f"+ s_signal: {ss_signal}\n"
            "++++++++++++++++++++++++++"
        )
        print('-----------------------------------------------------------------------------------------------------')
        return ss_signal, nn_index     # RETURNS SIGNAL FOR send_buy_sell_orders()

    sr_level_columns = output_df_with_levels.columns[8:]  # Assuming SR level columns start from the 8th column onwards
    for index, row in output_df_with_levels.iterrows():
        previous_close = output_df_with_levels.iloc[index - 1]['Close'] if index > 0 else None
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']
        current_candle_date = row['Date']
        current_candle_time = row['Time']

        subsequent_index = None  # Initialize subsequent_index

        # Loop through each level column
        for level_column in sr_level_columns:
            current_sr_level = row[level_column]
            if current_sr_level is not None:
                # Check if signal count for this level has reached the threshold
                if level_signal_count[level_column] < level_interactions_threshold:

                    # **************************************************************************************************
                    # SHORTS LOGICS BEGIN HERE
                    # **************************************************************************************************
                    # REJECTION SHORTS LOGIC:

                    if previous_close is not None and previous_close < current_sr_level:
                        if current_candle_high > current_sr_level:
                            if current_candle_close < current_sr_level:
                                # Over-Under condition met for short
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time
                                print('-------------------------------------------------------------------------------')
                                print(f"▲▼ Short: 'Over-under' condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first green candle (where close > open)
                                green_candle_found = False
                                green_candle_low = None
                                potential_ob_time = None
                                trade_type = 'rejection'
                                side = 'short'

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                    # Convert to datetime for time calculations
                                    potential_ob_time = pd.to_datetime(
                                        str(potential_ob_candle['Date']) + ' ' + str(potential_ob_candle['Time'])
                                    )
                                    # Calculate time difference between the current potential candle
                                    # and the initial SR level interaction
                                    time_diff = (potential_ob_time - pd.to_datetime(
                                        level_interaction_signal_time)).total_seconds() / 60

                                    # Check if we've exceeded the maximum waiting time
                                    trace = 'Rejection_shorts_1'
                                    if check_time_limit(
                                            max_time_waiting_for_entry,
                                            subsequent_index,
                                            potential_ob_time,
                                            level_interaction_signal_time,
                                            time_diff,
                                            trace
                                    ):
                                        break   # Exit the loop if time limit is exceeded

                                    print(
                                        f"Looking for GREEN candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )
                                    # Check if it's a green candle (close > open)
                                    if potential_ob_candle['Close'] > potential_ob_candle['Open']:
                                        print(
                                            f"○ Last GREEN candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        # Check if the green candle is below the SR level
                                        if potential_ob_candle['Close'] < current_sr_level:
                                            green_candle_low = potential_ob_candle['Low']
                                            green_candle_found = True
                                            print(
                                                f"Green candle is below the SR level at index {subsequent_index}, "
                                                f"Now waiting for next candle to close below "
                                                f"Time: {potential_ob_time}"
                                            )
                                            break
                                        else:
                                            print(
                                                f"Green candle found, but it's not below the level. "
                                                f"Checking next candle..."
                                            )

                                # Step 2: After finding the green candle, wait for the price to hit its low
                                if green_candle_found:
                                    # Store the time of the green candle
                                    potential_ob_time = pd.to_datetime(potential_ob_time)
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                        signal_time = next_candle_after_ob['Time']
                                        # Calculate the time difference in minutes
                                        # between the green candle and the current candle
                                        time_diff = (potential_ob_time -
                                                     pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60

                                        print(
                                            f"Waiting for next candle to close below GREEN candle low at {next_index},"
                                            f"Time: {signal_time}"
                                        )

                                        # Check if we've exceeded the maximum waiting time
                                        trace = 'Rejection_shorts_2'
                                        if check_time_limit(
                                                max_time_waiting_for_entry,
                                                next_index,
                                                potential_ob_time,
                                                level_interaction_signal_time,
                                                time_diff,
                                                trace
                                        ):
                                            break  # Exit the loop if time limit is exceeded

                                        # THIS IS THE ACTUAL SIGNAL FOR TRADE OPEN
                                        if next_candle_after_ob['Close'] < green_candle_low:
                                            # Store the time of the next candle after OB
                                            next_candle_after_ob_time = pd.to_datetime(
                                                str(next_candle_after_ob['Date']) + ' '
                                                + str(next_candle_after_ob['Time'])
                                            )

                                            if next_candle_after_ob['Close'] < current_sr_level:
                                                # signal = -100  # Short signal
                                                signal = f'-100+{next_index}'
                                                price_level = next_candle_after_ob['Close']

                                                s_signal, n_index = signal_triggered_output(
                                                    next_index,
                                                    signal_time,
                                                    price_level,
                                                    trade_type,
                                                    side,
                                                    signal
                                                )

                                                break
                                            else:
                                                print(
                                                    f"It closed below, but we are not under the level."
                                                    f" Checking next candle..."
                                                )
                                                # Calculate time difference between the current potential candle
                                                # and the initial SR level interaction
                                                time_diff = (next_candle_after_ob_time - pd.to_datetime(
                                                    level_interaction_signal_time)).total_seconds() / 60

                                                # Check if we've exceeded the maximum waiting time
                                                trace = 'Rejection_shorts_3'
                                                if check_time_limit(
                                                        max_time_waiting_for_entry,
                                                        subsequent_index,
                                                        next_candle_after_ob_time,
                                                        level_interaction_signal_time,
                                                        time_diff,
                                                        trace
                                                ):
                                                    break  # Exit the loop if time limit is exceeded

                                        elif next_candle_after_ob['Close'] > next_candle_after_ob['Open']:
                                            next_candle_after_ob_time = pd.to_datetime(
                                                str(next_candle_after_ob['Date']) + ' '
                                                + str(next_candle_after_ob['Time'])
                                            )
                                            signal_time = next_candle_after_ob['Time']
                                            green_candle_low = next_candle_after_ob['Low']
                                            print(
                                                f"NEW GREEN candle formed at index {next_index}, "
                                                f"Time: {signal_time}, "
                                            )
                                            subsequent_index = next_index
                                            time_diff = (next_candle_after_ob_time -
                                                         pd.to_datetime(
                                                             level_interaction_signal_time)).total_seconds() / 60

                                            # Check if we've exceeded the maximum waiting time
                                            trace = 'Rejection_shorts_4'
                                            if check_time_limit(
                                                    max_time_waiting_for_entry,
                                                    next_index,
                                                    next_candle_after_ob_time,
                                                    level_interaction_signal_time,
                                                    time_diff,
                                                    trace
                                            ):
                                                break  # Exit the loop if time limit is exceeded
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated


#                   BR-D LOGIC BEGIN HERE ******************************************************************************
                    # Previous close was above level
                    if previous_close is not None and previous_close > current_sr_level:
                        if current_candle_close < current_sr_level:
                            # Over condition met for short
                            level_signal_count[level_column] += 1
                            level_interaction_signal_time = current_candle_time
                            print('-------------------------------------------------------------------------------')
                            print(f"▼ Short: 'Under' condition met at index {index}, "
                                  f"Time: {current_candle_time}, "
                                  f"SR level: {current_sr_level}")

                            # Step 1: Find the first green candle (where close > open)
                            green_candle_found = False
                            green_candle_low = None
                            potential_ob_time = None
                            trade_type = 'BR-D'
                            side = 'short'

                            for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                # Convert to datetime for time calculations

                                potential_ob_time = pd.to_datetime(
                                    str(potential_ob_candle['Date']) + ' ' + str(potential_ob_candle['Time'])
                                )

                                # Calculate time difference between the current potential candle
                                # and the initial SR level interaction
                                time_diff = (potential_ob_time - pd.to_datetime(
                                    level_interaction_signal_time)).total_seconds() / 60

                                # Check if we've exceeded the maximum waiting time
                                trace = 'BR-D_shorts_1'
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
                                    f"Looking for GREEN candle at index {subsequent_index}, "
                                    f"Time: {potential_ob_time}"
                                )

                                # Check if it's a green candle (close > open)
                                if potential_ob_candle['Close'] > potential_ob_candle['Open']:
                                    print(
                                        f"○ Last GREEN candle found at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )

                                    # Check if the green candle is below the SR level
                                    if potential_ob_candle['Close'] < current_sr_level:
                                        green_candle_low = potential_ob_candle['Low']
                                        green_candle_found = True
                                        print(
                                            f"⦿ It's below the level at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        break  # Exit the loop, as we have found the valid green candle below the level

                                    else:
                                        print(
                                            f"Green candle found, but it's not below the level. "
                                            f"Checking next candle...")

                            # Step 2: After finding the green candle, wait for the price to hit its low
                            if green_candle_found:
                                # Store the time of the green candle
                                potential_ob_time = pd.to_datetime(potential_ob_time)
                                for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                    next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                    signal_time = next_candle_after_ob['Time']
                                    # Calculate the time difference in minutes
                                    # between the green candle and the current candle
                                    time_diff = (potential_ob_time -
                                                 pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60

                                    print(
                                        f"Waiting for next candle to close below GREEN candle low at {next_index}, "
                                        f"Time: {signal_time}"
                                    )

                                    # Check if we've exceeded the maximum waiting time
                                    trace = 'BR-D_shorts_2'
                                    if check_time_limit(
                                            max_time_waiting_for_entry,
                                            next_index,
                                            signal_time,
                                            level_interaction_signal_time,
                                            time_diff,
                                            trace
                                    ):
                                        break  # Exit the loop if time limit is exceeded

                                    # THIS IS THE ACTUAL SIGNAL FOR LONG TRADE OPEN
                                    # Price hits the low of the green candle
                                    if next_candle_after_ob['Close'] < green_candle_low:
                                        # Store the time of the next candle after OB
                                        next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                        if next_candle_after_ob['Close'] < current_sr_level:
                                            # signal = -100  # Short signal
                                            signal = f'-100+{next_index}'
                                            price_level = next_candle_after_ob['Close']

                                            s_signal, n_index = signal_triggered_output(
                                                next_index,
                                                signal_time,
                                                price_level,
                                                trade_type,
                                                side,
                                                signal
                                            )
                                            break
                                        else:
                                            print(
                                                f"It closed below, but we are not below the level. "
                                                f"Checking next candle..."
                                            )
                                            # Calculate time difference between the current potential candle
                                            # and the initial SR level interaction
                                            time_diff = (next_candle_after_ob_time - pd.to_datetime(
                                                level_interaction_signal_time)).total_seconds() / 60

                                            # Check if we've exceeded the maximum waiting time
                                            trace = 'BR-D_shorts_3'
                                            if check_time_limit(
                                                    max_time_waiting_for_entry,
                                                    subsequent_index,
                                                    next_candle_after_ob_time,
                                                    level_interaction_signal_time,
                                                    time_diff,
                                                    trace
                                            ):
                                                break  # Exit the loop if time limit is exceeded

                                    elif next_candle_after_ob['Close'] > next_candle_after_ob['Open']:
                                        next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                        signal_time = next_candle_after_ob['Time']
                                        green_candle_low = next_candle_after_ob['Low']
                                        print(
                                            f"NEW GREEN candle formed at index {next_index}, "
                                            f"Time: {signal_time}, "
                                        )
                                        subsequent_index = next_index
                                        time_diff = (next_candle_after_ob_time -
                                                     pd.to_datetime(
                                                         level_interaction_signal_time)).total_seconds() / 60

                                        # Check if we've exceeded the maximum waiting time
                                        trace = 'BR-D_shorts_4'
                                        if check_time_limit(
                                                max_time_waiting_for_entry,
                                                next_index,
                                                next_candle_after_ob_time,
                                                level_interaction_signal_time,
                                                time_diff,
                                                trace
                                        ):
                                            break  # Exit the loop if time limit is exceeded
                                break  # Exit the level loop once a signal is generated

                    #  ********************************************************************************************
                    #  LONGS LOGICS BEGIN HERE
                    #  ********************************************************************************************
                    # REJECTION LONGS LOGIC:
                    if previous_close is not None and previous_close > current_sr_level:
                        if current_candle_low < current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Over-Under condition met for long
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time
                                print('-------------------------------------------------------------------------------')
                                print(f"▼▲ Long: 'Under-over' condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None
                                potential_ob_time = None
                                trade_type = 'rejection'
                                side = 'long'

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                    # Convert to datetime for time calculations
                                    potential_ob_time = pd.to_datetime(
                                        str(potential_ob_candle['Date']) + ' ' + str(potential_ob_candle['Time'])
                                    )
                                    # Calculate time difference between the current potential candle
                                    # and the initial SR level interaction
                                    time_diff = (potential_ob_time - pd.to_datetime(
                                        level_interaction_signal_time)).total_seconds() / 60

                                    # Check if we've exceeded the maximum waiting time
                                    trace = 'Rejection_longs_1'
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
                                        # Check if the red candle is below the SR level
                                        if potential_ob_candle['Close'] > current_sr_level:
                                            red_candle_high = potential_ob_candle['High']
                                            red_candle_found = True
                                            print(
                                                f"Red candle is above the SR level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            break
                                        else:
                                            print(f"Red candle found, but it's not above the level. "
                                                  f"Checking next candle...")

                                # Step 2: After finding the red candle, wait for the price to hit its high
                                if red_candle_found:
                                    # Store the time of the green candle
                                    potential_ob_time = pd.to_datetime(potential_ob_time)
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                        signal_time = next_candle_after_ob['Time']
                                        # Calculate the time difference in minutes
                                        # between the green candle and the current candle
                                        time_diff = (potential_ob_time -
                                                     pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60
                                        print(
                                            f"Waiting for next candle to close above RED candle high at {next_index},"
                                            f"Time: {signal_time}"
                                        )

                                        # Check if we've exceeded the maximum waiting time
                                        trace = 'Rejection_longs_2'
                                        if check_time_limit(
                                                max_time_waiting_for_entry,
                                                next_index,
                                                potential_ob_time,
                                                level_interaction_signal_time,
                                                time_diff,
                                                trace
                                        ):
                                            break  # Exit the loop if time limit is exceeded

                                        # Price hits the high of the red candle
                                        if next_candle_after_ob['Close'] > red_candle_high:
                                            # Store the time of the next candle after OB
                                            next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                            if next_candle_after_ob['Close'] > current_sr_level:
                                                # signal = 100  # Long signal
                                                signal = f'100+{next_index}'
                                                price_level = next_candle_after_ob['Close']

                                                s_signal, n_index = signal_triggered_output(
                                                    next_index,
                                                    signal_time,
                                                    price_level,
                                                    trade_type,
                                                    side,
                                                    signal
                                                )
                                                break
                                            else:
                                                print(
                                                    f"It closed above, but we are not above the level. "
                                                    f"Checking next candle..."
                                                )
                                                # Calculate time difference between the current potential candle
                                                # and the initial SR level interaction
                                                time_diff = (next_candle_after_ob_time - pd.to_datetime(
                                                    level_interaction_signal_time)).total_seconds() / 60

                                                # Check if we've exceeded the maximum waiting time
                                                trace = 'Rejection_longs_3'
                                                if check_time_limit(
                                                        max_time_waiting_for_entry,
                                                        subsequent_index,
                                                        next_candle_after_ob_time,
                                                        level_interaction_signal_time,
                                                        time_diff,
                                                        trace
                                                ):
                                                    break  # Exit the loop if time limit is exceeded

                                        elif next_candle_after_ob['Close'] < next_candle_after_ob['Open']:
                                            next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                            signal_time = next_candle_after_ob['Time']
                                            red_candle_high = next_candle_after_ob['High']
                                            print(
                                                f"NEW RED candle formed at index {next_index}, "
                                                f"Time: {signal_time}, "
                                            )
                                            subsequent_index = next_index
                                            time_diff = (next_candle_after_ob_time -
                                                         pd.to_datetime(
                                                             level_interaction_signal_time)).total_seconds() / 60

                                            # Check if we've exceeded the maximum waiting time
                                            trace = 'Rejection_longs_4'
                                            if check_time_limit(
                                                    max_time_waiting_for_entry,
                                                    next_index,
                                                    next_candle_after_ob_time,
                                                    level_interaction_signal_time,
                                                    time_diff,
                                                    trace
                                            ):
                                                break  # Exit the loop if time limit is exceeded

                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated

#                   BR-O LOGIC BEGIN HERE *****************************************************************************
                    # Previous close was below level
                    if previous_close is not None and previous_close < current_sr_level:
                        if current_candle_close > current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Under condition met for long
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time
                                print('-------------------------------------------------------------------------------')
                                print(f"▲ Long: 'Over' condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None
                                potential_ob_time = None
                                trade_type = 'BR-O'
                                side = 'Long'

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]

                                    # Convert to datetime for time calculations
                                    potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                                    # Calculate time difference between the current potential candle
                                    # and the initial SR level interaction
                                    time_diff = (potential_ob_time - pd.to_datetime(
                                        level_interaction_signal_time)).total_seconds() / 60

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
                                            print(
                                                f"⦿ It's above the level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            break
                                        else:
                                            print(f"But we are not above the level. Checking next candle...")

                                # Step 2: After finding the red candle, wait for the price to hit its high
                                if red_candle_found:
                                    # Store the time of the red candle
                                    potential_ob_time = pd.to_datetime(potential_ob_time)
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                        signal_time = next_candle_after_ob['Time']
                                        # Calculate the time difference in minutes
                                        # between the red candle and the current candle
                                        time_diff = (potential_ob_time -
                                                     pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60

                                        print(
                                            f"Waiting for next candle to close above RED candle high at {next_index},"
                                            f"Time: {signal_time}"
                                        )

                                        # Check if we've exceeded the maximum waiting time
                                        trace = 'BR-O_longs_2'
                                        if check_time_limit(
                                                max_time_waiting_for_entry,
                                                next_index,
                                                potential_ob_time,
                                                level_interaction_signal_time,
                                                time_diff,
                                                trace
                                        ):
                                            break  # Exit the loop if time limit is exceeded

                                        if next_candle_after_ob['Close'] > red_candle_high:
                                            # Price hits the high of the red candle
                                            # Store the time of the next candle after OB
                                            next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                            if next_candle_after_ob['Close'] > current_sr_level:
                                                # signal = 100  # Long signal
                                                signal = f'100+{next_index}'
                                                price_level = next_candle_after_ob['Close']

                                                s_signal, n_index = signal_triggered_output(
                                                    next_index,
                                                    signal_time,
                                                    price_level,
                                                    trade_type,
                                                    side,
                                                    signal
                                                )
                                                break
                                            else:
                                                print(
                                                    f"It closed above, but we are not above the level. "
                                                    f"Checking next candle..."
                                                )
                                                # Calculate time difference between the current potential candle
                                                # and the initial SR level interaction
                                                time_diff = (next_candle_after_ob_time - pd.to_datetime(
                                                    level_interaction_signal_time)).total_seconds() / 60

                                                # Check if we've exceeded the maximum waiting time
                                                trace = 'BR-O_longs_3'
                                                if check_time_limit(
                                                        max_time_waiting_for_entry,
                                                        subsequent_index,
                                                        next_candle_after_ob_time,
                                                        level_interaction_signal_time,
                                                        time_diff,
                                                        trace
                                                ):
                                                    break  # Exit the loop if time limit is exceeded

                                        elif next_candle_after_ob['Close'] < next_candle_after_ob['Open']:
                                            next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                            signal_time = next_candle_after_ob['Time']
                                            red_candle_high = next_candle_after_ob['High']
                                            print(
                                                f"NEW RED candle formed at index {next_index}, "
                                                f"Time: {signal_time}, "
                                            )
                                            subsequent_index = next_index
                                            time_diff = (next_candle_after_ob_time -
                                                         pd.to_datetime(
                                                             level_interaction_signal_time)).total_seconds() / 60

                                            # Check if we've exceeded the maximum waiting time
                                            trace = 'BR-O_longs_4'
                                            if check_time_limit(
                                                    max_time_waiting_for_entry,
                                                    next_index,
                                                    next_candle_after_ob_time,
                                                    level_interaction_signal_time,
                                                    time_diff,
                                                    trace
                                            ):
                                                break  # Exit the loop if time limit is exceeded
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated

    return (
            level_signal_count,
            s_signal,
            n_index
    )
