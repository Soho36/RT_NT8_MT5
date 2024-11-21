#region Using declarations
using System;
using System.IO;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class MyCustomStrategy : Strategy
    {
        private bool executeLongTrade = false;
        private bool executeShortTrade = false;
        private double entryPrice = 0;
		private double stopPrice = 0;
        private double targetPrice1 = 0;
        private double targetPrice2 = 0;
		private Order longOrder1;
		private Order longOrder2;
		private Order shortOrder1;
		private Order shortOrder2;
		
		// Track whether stop losses have been moved to breakeven
		bool stopLossMovedToBreakevenLong1 = false;
		bool stopLossMovedToBreakevenShort1 = false;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Filetransmit2";
                Calculate = Calculate.OnEachTick;
                EntriesPerDirection = 1; // Allow entries
                EntryHandling = EntryHandling.UniqueEntries;
            }
        }

        protected override void OnBarUpdate()
		{
			if (CurrentBars[0] < BarsRequiredToTrade)
				return;

			string signalFilePath = "C:\\Users\\Liikurserv\\PycharmProjects\\RT_Ninja\\trade_signal.txt";

			if (File.Exists(signalFilePath))
			{
				try
				{
					string signal = File.ReadAllText(signalFilePath).Trim();
					string[] parts = signal.Split(',');

					if (parts.Length == 5)
					{
						string tradeDirection = parts[0].Trim();                    // Direction
						if (double.TryParse(parts[1].Trim(), out entryPrice) &&     // EntryPrice
							double.TryParse(parts[2].Trim(), out stopPrice) &&      // Stop-loss price
							double.TryParse(parts[3].Trim(), out targetPrice1) &&   // Take-profit1 price
							double.TryParse(parts[4].Trim(), out targetPrice2))     // Take-profit2 price        
						{
							if (tradeDirection.Equals("Buy", StringComparison.OrdinalIgnoreCase))
							{
								if (Position.MarketPosition == MarketPosition.Flat)
								{
									executeLongTrade = true;
									File.WriteAllText(signalFilePath, string.Empty);
								}
								else if (Position.MarketPosition == MarketPosition.Short)
								{
									CancelAllOrders();
									executeLongTrade = true;
									Print("Cancelled short orders to place long orders.");
									File.WriteAllText(signalFilePath, string.Empty);
								}
							}
							else if (tradeDirection.Equals("Sell", StringComparison.OrdinalIgnoreCase))
							{
								if (Position.MarketPosition == MarketPosition.Flat)
								{
									executeShortTrade = true;
									File.WriteAllText(signalFilePath, string.Empty);
								}
								else if (Position.MarketPosition == MarketPosition.Long)
								{
									CancelAllOrders();
									executeShortTrade = true;
									Print("Cancelled long orders to place short orders.");
									File.WriteAllText(signalFilePath, string.Empty);
								}
							}
						}
					}
				}
				catch (Exception ex)
				{
					Print($"Error reading signal file: {ex.Message}");
				}
			}

			// Handle long positions
			if (executeLongTrade)
			{
				try
				{
					if (longOrder1 == null || longOrder1.OrderState != OrderState.Working)
					{
						longOrder1 = EnterLongStopMarket(0, true, 2, entryPrice, "Long1");
						SetStopLoss("Long1", CalculationMode.Price, stopPrice, false);
						SetProfitTarget("Long1", CalculationMode.Price, targetPrice1);
						Print($"1-st LONG stop-market order placed at {entryPrice} with TP1: {targetPrice1}, SL: {stopPrice}");
					}
					if (longOrder2 == null || longOrder2.OrderState != OrderState.Working)
					{
						longOrder2 = EnterLongStopMarket(0, true, 1, entryPrice, "Long3");
						SetStopLoss("Long3", CalculationMode.Price, stopPrice, false);
						SetProfitTarget("Long3", CalculationMode.Price, targetPrice2);
						Print($"2-nd LONG stop-market order placed at {entryPrice} with TP2: {targetPrice2}, SL: {stopPrice}");
					}
				}
				catch (Exception ex)
				{
					Print($"Error placing long orders: {ex.Message}");
				}
				executeLongTrade = false; // Reset flag
			}

			// Handle short positions
			if (executeShortTrade)
			{
				try
				{
					if (shortOrder1 == null || shortOrder1.OrderState != OrderState.Working)
					{
						shortOrder1 = EnterShortStopMarket(0, true, 2, entryPrice, "Short1");
						SetStopLoss("Short1", CalculationMode.Price, stopPrice, false);
						SetProfitTarget("Short1", CalculationMode.Price, targetPrice1);
						Print($"1-st SHORT order placed at {entryPrice} with TP1: {targetPrice1}, SL: {stopPrice}");
					}
					if (shortOrder2 == null || shortOrder2.OrderState != OrderState.Working)
					{
						shortOrder2 = EnterShortStopMarket(0, true, 1, entryPrice, "Short2");
						SetStopLoss("Short2", CalculationMode.Price, stopPrice, false);
						SetProfitTarget("Short2", CalculationMode.Price, targetPrice2);
						Print($"2-nd SHORT stop-market order placed at {entryPrice} with TP2: {targetPrice2}, SL: {stopPrice}");
					}
				}
				catch (Exception ex)
				{
					Print($"Error placing short orders: {ex.Message}");
				}
				executeShortTrade = false;  // Reset flag
			}
		}
		private void CancelAllOrders()
		{
			try
			{
				foreach (Order order in Account.Orders)
				{
					// Cancel only orders associated with this strategy and in working/accepted state
					if ((order.OrderState == OrderState.Working || order.OrderState == OrderState.Accepted) && order.Name.StartsWith(Name))
					{
						CancelOrder(order);
						Print($"Cancelled order: {order.Name}");
					}
				}
			}
			catch (Exception ex)
			{
				Print($"Error canceling orders: {ex.Message}");
			}
		}
    }
}
