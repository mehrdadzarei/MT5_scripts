//+------------------------------------------------------------------+
//|                                             auto_import_data.mq5 |
//|                                   Copyright 2024, Mehrdad Zarei. |
//|                       https://www.mql5.com/en/users/mehrdadzarei |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Mehrdad Zarei."
#property link      "https://www.mql5.com/en/users/mehrdadzarei"
#property version   "1.00"

#include <Trade\SymbolInfo.mqh>

#define INTERVAL_SECONDS 30  // Time interval for imports in seconds

//--- Global variables
string settings = "symbols.csv"; // File name for the symbol settings
bool update_all = false; // Update all data


/**
* ImportCSVFile: import CSV file for a symbol.
*
* @param  string file_path
* @param  string symbol
*
* @return bool
*/
bool ImportCSVFile(string file_path, string symbol, ENUM_TIMEFRAMES timeframe) {
  
  // get the last bar from the chart
  MqlRates last_bar[];
  int last_bar_count = CopyRates(symbol, timeframe, 0, 1, last_bar);
  datetime last_bar_time = (last_bar_count > 0 && !update_all) ? last_bar[0].time : 0;
  // Print("Last bar time: ", TimeToString(last_bar[0].time));
  
  int file_handle = FileOpen(file_path, FILE_CSV | FILE_READ | FILE_ANSI);
  if (file_handle == INVALID_HANDLE) {
    Print("Error opening file: ", file_path, " Error: ", GetLastError());
    return false;
  }

  // Skip the header line
  FileReadString(file_handle);

  MqlRates rates[], to_add[];
  int index = 0;

  // Read and parse each line
  while (!FileIsEnding(file_handle)) {
    string line = FileReadString(file_handle);
    string parts[];
    int count = StringSplit(line, ',', parts);

    if (count < 6) {
      Print("Invalid data line: ", line);
      continue;
    }

    // Convert values
    datetime bar_time = StringToTime(parts[0]);

    // Skip bars that are already imported
    if (bar_time < last_bar_time) {
      continue;
    }
    
    double bar_open = StringToDouble(parts[1]);
    double bar_high = StringToDouble(parts[2]);
    double bar_low = StringToDouble(parts[3]);
    double bar_close = StringToDouble(parts[4]);
    long bar_volume = StringToInteger(parts[5]);

    // Resize the rates array
    ArrayResize(rates, index + 1);
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

  // Update the symbol's custom rates
  if (CustomRatesUpdate(symbol, rates)) {
    return true;
  } else {
    // Print("Failed to update custom rates for symbol: ", symbol, " Error: ", GetLastError());
    return false;
  }
}

/**
* get_list_of_symbols: Get all the symbols from the file.
*
* @param  string file_list
* @param  string symbol_list
*
* @return file_count
*/
int Get_list_of_symbols(string &file_list[], string &symbol_list[]) {
  int file_count = 0;

  // Open the file
  int file_handle = FileOpen(settings, FILE_CSV | FILE_READ | FILE_ANSI);
  //FileOpen(file_path, FILE_CSV | FILE_READ | FILE_ANSI);
  if (file_handle == INVALID_HANDLE)
  {
    Print("Error opening file: ", settings, " Error: ", GetLastError());
    return false;
  }

  // skip the header
  FileReadString(file_handle);

  // Read each line and add the symbol to the list
  while (!FileIsEnding(file_handle)) {
    string line = FileReadString(file_handle);
    string parts[];
    StringSplit(line, ',', parts);

    // Resize the array to store the symbol
    ArrayResize(file_list, file_count + 1);
    ArrayResize(symbol_list, file_count + 1);
    symbol_list[file_count] = parts[0];
    file_list[file_count] = parts[1];
    file_count++;
  }

  // print the list of symbols
  // for (int i = 0; i < file_count; i++) {
  //   Print("Symbol: ", file_list[i]);
  // }

  // Close the file
  FileClose(file_handle);

  return file_count;
}

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart() {
  // Get the list of all the symbols
  string file_list[], symbol_list[];
  int file_count = Get_list_of_symbols(file_list, symbol_list);
  
  while (true) {
    // Loop through each symbol and import the data
    for (int i = 0; i < file_count; i++) {
      string file_name = file_list[i];
      string symbol_name = symbol_list[i];

      // Import data for different timeframes
      string timeframes[] = {"1m", "5m", "1h", "1d"};
      ENUM_TIMEFRAMES periods[] = {PERIOD_M1, PERIOD_M5, PERIOD_H1, PERIOD_D1};

      for (int tf = 0; tf < ArraySize(timeframes); tf++) {
        string timeframe = timeframes[tf];
        ENUM_TIMEFRAMES period = periods[tf];

        // Import data for the symbol and timeframe
        if (ImportCSVFile(file_name + "_" + timeframe + ".csv", symbol_name, period)) {
          Print("Data imported successfully for symbol: ", symbol_name, " timeframe: ", timeframe);
        } else {
          Print("Failed to import data for symbol: ", symbol_name, " timeframe: ", timeframe);
        }
      }
      
      // // get the last 5 bars from the chart for each timeframe and print them
      // for (int tf = 0; tf < ArraySize(timeframes); tf++) {
      //   string timeframe = timeframes[tf];
      //   ENUM_TIMEFRAMES period = periods[tf];

      //   MqlRates last_bars[];
      //   int last_bars_count = CopyRates(symbol_name, period, 0, 5, last_bars);
      //   for (int j = 0; j < last_bars_count; j++) {
      //       Print(symbol_name, " ", timeframe, " Time: ", TimeToString(last_bars[j].time), " Open: ", DoubleToString(last_bars[j].open, 2), " High: ", DoubleToString(last_bars[j].high, 2), " Low: ", DoubleToString(last_bars[j].low, 2), " Close: ", DoubleToString(last_bars[j].close, 2));
      //   }
      // }
    }

    // // get current timeframe and symbol from the chart and import the data for that
    // string symbol_name = Symbol();
    // ENUM_TIMEFRAMES period = Period();
    // string timeframe;
    // switch (period) {
    //   case PERIOD_M1: timeframe = "1m"; break;
    //   case PERIOD_M5: timeframe = "5m"; break;
    //   case PERIOD_H1: timeframe = "1h"; break;
    //   case PERIOD_D1: timeframe = "1d"; break;
    //   default: timeframe = "1m"; break;
    // }
    // string file_name = symbol_name;

    // // delete the existing data for the symbol and timeframe
    // CustomRatesDelete(symbol_name, 0, LONG_MAX);
    // if (ImportCSVFile(file_name + "_" + timeframe + ".csv", symbol_name, period)) {
    //       Print("Data imported successfully for symbol: ", symbol_name, " timeframe: ", timeframe);
    //     } else {
    //       Print("Failed to import data for symbol: ", symbol_name, " timeframe: ", timeframe);
    //     }
    // Wait for the next update
    for (int j = 0; j < INTERVAL_SECONDS; j++) {
      Sleep(1000);  // Sleep for 1 second
    }
  }
}
//+------------------------------------------------------------------+
