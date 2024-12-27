//+------------------------------------------------------------------+
//|                                             auto_import_data.mq5 |
//|                                   Copyright 2024, Mehrdad Zarei. |
//|                       https://www.mql5.com/en/users/mehrdadzarei |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Mehrdad Zarei."
#property link      "https://www.mql5.com/en/users/mehrdadzarei"
#property version   "1.00"

#include <Trade\SymbolInfo.mqh>

// Path to the CSV file
string csv_file_path = "data/NVDA_1m_mt5.csv";
string custom_symbol = "NVDA";


//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
  {
//---
   // Open the CSV file
    int file_handle = FileOpen(csv_file_path, FILE_CSV | FILE_READ | FILE_ANSI);
    if (file_handle == INVALID_HANDLE)
    {
        Print("Error opening CSV file: ", GetLastError());
        return;
    }

    // Create an array to hold custom rates data
    MqlRates rates[];
    int index = 0;

    // Read and parse the CSV file
    while (!FileIsEnding(file_handle))
    {
        string time, open, high, low, close, volume;

        // Read one line
        time = FileReadString(file_handle);
        open = FileReadString(file_handle);
        high = FileReadString(file_handle);
        low = FileReadString(file_handle);
        close = FileReadString(file_handle);
        volume = FileReadString(file_handle);

        // Convert the strings to appropriate data types
        datetime bar_time = StringToTime(time);
        double bar_open = StringToDouble(open);
        double bar_high = StringToDouble(high);
        double bar_low = StringToDouble(low);
        double bar_close = StringToDouble(close);
        long bar_volume = StringToInteger(volume);

        // Resize the array to accommodate the new bar
        ArrayResize(rates, index + 1);

        // Populate the bar data
        rates[index].time = bar_time;
        rates[index].open = bar_open;
        rates[index].high = bar_high;
        rates[index].low = bar_low;
        rates[index].close = bar_close;
        rates[index].tick_volume = bar_volume;

        index++;
    }

    // Close the file
    FileClose(file_handle);

    // Update the custom symbol with the rates data
    if (!CustomRatesUpdate(custom_symbol, rates))
    {
        Print("Failed to update custom symbol: ", GetLastError());
    }
    else
    {
        Print("CSV data imported successfully for ", custom_symbol);
    }
  }
//+------------------------------------------------------------------+
