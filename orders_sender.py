import winsound
from data_handling_realtime import save_order_parameters_to_file, get_current_pending_order_direction
import time


def last_candle_ohlc(output_df_with_levels):
    try:
        last_candle_high = output_df_with_levels['High'].iloc[-1]
        last_candle_low = output_df_with_levels['Low'].iloc[-1]
        last_candle_close = output_df_with_levels['Close'].iloc[-1]
        ticker = output_df_with_levels['Ticker'].iloc[-1]
        return last_candle_high, last_candle_low, last_candle_close, ticker
    except IndexError:
        print("Must be at least two rows in the source file")
        return


def send_buy_sell_orders(
        stop_market_price,
        last_signal,
        current_signal,
        n_index,
        buy_signal,
        sell_signal,
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker,
        stop_loss_offset,
        risk_reward,
        # reverse_trades
):
    # +------------------------------------------------------------------+
    # BUY ORDER
    # +------------------------------------------------------------------+
    print(f'Last signal: {last_signal}'.upper())
    print(f'Current signal: {current_signal}'.upper())

    # Flag reset logic for enabling new orders after each order processed
    if current_signal != last_signal:
        # If there is unique new signal and flag is True:
        if current_signal == f'100+{n_index}' and buy_signal:  # If there is signal and flag is True:

            winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
            print()
            print('▲ ▲ ▲ Buy order has been sent to NT8! ▲ ▲ ▲'.upper())

            # ORDER PARAMETERS
            stop_loss_price = round(last_candle_low - stop_loss_offset, 3)
            take_profit_price = round((((last_candle_high - stop_loss_price) * 1)  # R/R hardcoded
                                       + last_candle_high) + stop_loss_offset, 3)
            take_profit_price_2 = round((((last_candle_high - stop_loss_price) * 2)  # R/R hardcoded
                                         + last_candle_high) + stop_loss_offset, 3)

            line_order_parameters_nt8 = \
                f'Buy, {stop_market_price}, {stop_loss_price}, {take_profit_price}, {take_profit_price_2}'
            line_order_cancel = 'cancel'

            if get_current_pending_order_direction():   # If there is an active order:
                print('Cancelling previous order...')
                save_order_parameters_to_file(line_order_cancel)    # cancel it and...
                time.sleep(1)
                print('Submitting new order: ', line_order_parameters_nt8)
                save_order_parameters_to_file(line_order_parameters_nt8)    # save new order to file
            else:
                print('Submitting new order: ', line_order_parameters_nt8)
                save_order_parameters_to_file(line_order_parameters_nt8)

            # Reset buy_signal flag after processing order to allow the next unique signal
            buy_signal = False  # Prevent repeated order for the same signal
        # Reset flags here if a new unique signal occurs in consecutive candles
        if current_signal != last_signal:
            buy_signal, sell_signal = True, True  # Reset flags to allow the next unique signal

    # +------------------------------------------------------------------+
    # SELL ORDER
    # +------------------------------------------------------------------+

    # Flag reset logic for enabling new orders after each order processed
    if current_signal != last_signal:
        if current_signal == f'-100+{n_index}' and sell_signal:
            # Play sound to indicate order sent
            winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
            print()
            print('▼ ▼ ▼ Sell order has been sent to NT8! ▼ ▼ ▼'.upper())

            # Order parameters
            stop_loss_price = round(last_candle_high + stop_loss_offset, 3)
            take_profit_price = round((last_candle_low - ((stop_loss_price - last_candle_low) * 1))     # R/R hardcoded
                                      + stop_loss_offset, 3)
            take_profit_price_2 = round((last_candle_low - ((stop_loss_price - last_candle_low) * 2))   # R/R hardcoded
                                        + stop_loss_offset, 3)

            line_order_parameters_nt8 = \
                f'Sell, {stop_market_price}, {stop_loss_price}, {take_profit_price}, {take_profit_price_2}'
            line_order_cancel = 'cancel'

            if get_current_pending_order_direction():   # If there is an active order:
                print('Cancelling previous order...')
                save_order_parameters_to_file(line_order_cancel)    # cancel it and...
                time.sleep(1)
                print('Submitting new order: ', line_order_parameters_nt8)
                save_order_parameters_to_file(line_order_parameters_nt8)  # save new order to file
            else:
                print('Submitting new order: ', line_order_parameters_nt8)
                save_order_parameters_to_file(line_order_parameters_nt8)

            # Reset sell_signal flag after processing order to allow the next unique signal
            sell_signal = False  # Prevent repeated order for the same signal

        # Reset flags here if a new unique signal occurs in consecutive candles
        if current_signal != last_signal:
            buy_signal, sell_signal = True, True  # Reset flags to allow the next unique signal

    return buy_signal, sell_signal
