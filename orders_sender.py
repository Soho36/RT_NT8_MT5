import winsound
from data_handling_realtime import save_order_parameters_to_file


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
        last_signal,
        s_signal,
        n_index,
        buy_signal,
        sell_signal,
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker,
        stop_loss_offset,
        risk_reward
):
    # +------------------------------------------------------------------+
    # BUY ORDER
    # +------------------------------------------------------------------+
    print(f'Last signal: {last_signal}'.upper())
    print(f'Current signal: {s_signal}'.upper())

    if s_signal == last_signal:
        buy_signal, sell_signal = True, True  # Set Flags to enable new orders

    # If there is unique new signal and flag is True:
    if s_signal != last_signal and s_signal == f'100+{n_index}' and buy_signal:  # If there is signal and flag is True:
        winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
        print()
        print('▲ ▲ ▲ Buy order has been sent to MT5! ▲ ▲ ▲'.upper())

        # ORDER PARAMETERS
        stop_loss_price = round(last_candle_low - stop_loss_offset, 3)
        take_profit_price = round((((last_candle_close - stop_loss_price) * 1)  # R/R hardcoded
                                   + last_candle_close) + stop_loss_offset, 3)
        take_profit_price_2 = round((((last_candle_close - stop_loss_price) * 3)    # R/R hardcoded
                                     + last_candle_close) + stop_loss_offset, 3)

        # For MT5:
        # line_order_parameters = f'{ticker}, Buy, {stop_loss_price}, {take_profit_price}'
        # For NinjaTrader:
        line_order_parameters = f'Buy, {stop_loss_price}, {take_profit_price}, {take_profit_price_2}'

        save_order_parameters_to_file(line_order_parameters)    # Located in data_handling_realtime.py

        buy_signal = False  # Set flag to TRUE to prevent new order sending on each loop iteration

    # +------------------------------------------------------------------+
    # SELL ORDER
    # +------------------------------------------------------------------+

    if s_signal == last_signal:
        buy_signal, sell_signal = True, True  # Enable new orders

    # If there is unique new signal and flag is True:
    if s_signal != last_signal and s_signal == f'-100+{n_index}' and sell_signal:
        winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
        print()
        print('▼ ▼ ▼ Sell order has been sent to MT5! ▼ ▼ ▼'.upper())

        # ORDER PARAMETERS
        stop_loss_price = round(last_candle_high + stop_loss_offset)
        take_profit_price = round((last_candle_close - ((stop_loss_price - last_candle_close) * 1))  # R/R hardcoded
                                  + stop_loss_offset, 3)
        take_profit_price_2 = round((last_candle_close - ((stop_loss_price - last_candle_close) * 3))   # R/R hardcoded
                                    + stop_loss_offset, 3)

        # For MT5:
        # line_order_parameters = f'{ticker}, Sell, {stop_loss_price}, {take_profit_price}'
        # For NinjaTrader:
        line_order_parameters = f'Sell, {stop_loss_price}, {take_profit_price}, {take_profit_price_2}'

        save_order_parameters_to_file(line_order_parameters)    # Located in data_handling_realtime.py

        sell_signal = False  # Set flag to False to prevent new order sending on each loop iteration

    return buy_signal, sell_signal
