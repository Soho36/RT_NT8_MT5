namespace NinjaTrader.NinjaScript.Strategies
{
    public class SaveOHLCVToFile : Strategy
    {
        private string filePath = "E:\\YandexDisk\\Documents\\55\\OHLCVData_1.csv";

        // OnStateChange is used to initialize the strategy
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                // Default properties
                Name = "SaveOHLCVToFile";
                Calculate = Calculate.OnBarClose; // Trigger logic on bar close
            }
            else if (State == State.Configure)
            {
                // Write the header to the file (if it doesn't already exist)
                if (!File.Exists(filePath))
                {
                    File.AppendAllText(filePath, "Ticker,Timeframe,Date,Time,Open,High,Low,Close,Volume" + Environment.NewLine);
                }
            }
        }

        // OnBarUpdate is called for each new bar
        protected override void OnBarUpdate()
        {
            if (IsHistorical)
            {
                // Skip historical data
                return;
            }

            // Extract OHLCV data from the previous bar
            double open = Open[1];
            double high = High[1];
            double low = Low[1];
            double close = Close[1];

            // Get current date and time
            DateTime now = Time[1]; // Time[1] gives the start time of the previous bar
            string currentDate = now.ToString("yyyy.MM.dd");
            string currentTime = now.ToString("HH:mm");

            // Write data to the file
            string dataLine = string.Join(",",
                Instrument.FullName,
                BarsPeriod.Value + BarsPeriod.BarsPeriodType.ToString(),
                currentDate,
                currentTime,
                open.ToString("F6"),
                high.ToString("F6"),
                low.ToString("F6"),
                close.ToString("F6"));

            Print("New line saved to file: " + dataLine);
            File.AppendAllText(filePath, dataLine + Environment.NewLine);
        }
    }
}
