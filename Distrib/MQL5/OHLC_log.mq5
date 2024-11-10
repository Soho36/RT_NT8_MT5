#property version "1.1"
#property script_show_inputs

input string account_last_3_digits="";

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
// Will use the static Old_Time variable to serve the bar time.
// At each OnTick execution we will check the current bar time with the saved one.
// If the bar time isn't equal to the saved time, it indicates that we have a new tick.
   static datetime Old_Time;
   datetime New_Time[1];
   bool IsNewBar=false;

// copying the last bar time to the element New_Time[0]
   int copied=CopyTime(_Symbol,_Period,0,1,New_Time);
   if(copied>0) // ok, the data has been copied successfully
     {
      if(Old_Time!=New_Time[0]) // if old time isn't equal to new bar time
        {
         IsNewBar=true;   // if it isn't a first call, the new bar has appeared
 
         // Print OHLC of the new bar
         double open = iOpen(_Symbol, _Period, 1); // Open price of the previous bar
         double high = iHigh(_Symbol, _Period, 1); // High price of the previous bar
         double low = iLow(_Symbol, _Period, 1); // Low price of the previous bar
         double close = iClose(_Symbol, _Period, 1); // Close price of the previous bar
         long volume = iVolume(_Symbol, _Period, 1); // Volume of the previous bar
         Print(open,";", high,";", low,";", close,";", volume);
         
         // Save OHLCV data to file
         SaveOHLCVToFile(open, high, low, close, volume);
         
         Old_Time=New_Time[0];            // saving bar time
        }
     }
   else
     {
      Alert("Error in copying historical times data, error =",GetLastError());
      ResetLastError();
      return;
     }

//--- EA should only check for new trade if we have a new bar
   if(IsNewBar==false)
     {
      return;
     }
  }
  
// Function to save OHLCV data to a file
void SaveOHLCVToFile(double open, double high, double low, double close, double volume)
{
    // Get the current ticker symbol and timeframe
    string ticker = _Symbol;
    ENUM_TIMEFRAMES timeframe = _Period;
    
    // Get the current date and time separately
    string current_date = TimeToString(TimeCurrent(), TIME_DATE);    // Get date in YYYY.MM.DD format
    string current_time = TimeToString(TimeCurrent(), TIME_MINUTES); // Get time in HH:MM format
    
    // Open the file in append mode
    int file_handle = FileOpen("OHLCVData_" + account_last_3_digits + ".csv", FILE_WRITE | FILE_CSV | FILE_END, ";");
    if (file_handle != INVALID_HANDLE)
    {
        FileSeek(file_handle, 0, SEEK_END);
        // Write OHLCV data to the file with Date and Time in separate columns
        FileWrite(file_handle, ticker, EnumToString(timeframe), current_date, current_time, 
                  DoubleToString(open, _Digits), DoubleToString(high, _Digits), 
                  DoubleToString(low, _Digits), DoubleToString(close, _Digits), DoubleToString(volume, _Digits));

        // Close the file
        FileClose(file_handle);
    }
    else
    {
        Print("Failed to open the file for writing!");
    }
}
