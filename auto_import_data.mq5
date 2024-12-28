//+------------------------------------------------------------------+
//|                                             auto_import_data.mq5 |
//|                                   Copyright 2024, Mehrdad Zarei. |
//|                       https://www.mql5.com/en/users/mehrdadzarei |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Mehrdad Zarei."
#property link      "https://www.mql5.com/en/users/mehrdadzarei"
#property version   "1.00"

#include <Trade\SymbolInfo.mqh>

#define INTERVAL_SECONDS 10  // Time interval for imports in seconds

// Path to the CSV file
// string csv_file_path = "data/ASML.AS_1m.csv";
// string custom_symbol = "ASML.AS";


/**
* ImportCSVFile: import CSV file for a symbol.
*
* @param  string file_path
* @param  string symbol
*
* @return bool
*/
bool ImportCSVFile(string file_path, string symbol) {
  int file_handle = FileOpen(file_path, FILE_CSV | FILE_READ | FILE_ANSI);
  if (file_handle == INVALID_HANDLE)
  {
      Print("Error opening file: ", file_path, " Error: ", GetLastError());
      return false;
  }

  // Skip the header line
  FileReadString(file_handle);

  MqlRates rates[];
  int index = 0;

  // Read and parse each line
  while (!FileIsEnding(file_handle)) {
      string line = FileReadString(file_handle);
      string parts[];
      int count = StringSplit(line, ',', parts);

      if (count < 6)
      {
          Print("Invalid data line: ", line);
          continue;
      }

      // Convert values
      datetime bar_time = StringToTime(parts[0]);
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
    Print("Failed to update custom rates for symbol: ", symbol, " Error: ", GetLastError());
    return false;
  }
}

/**
* GetCSVFiles: Get all the CSV files in the folder.
*
* @param  string folder
* @param  string file_list
*
* @return file_count
*/
int GetCSVFiles(string folder, string &file_list[]) {
  int file_count = 0;

  // Start searching for files
  string first_file;
  int handle = FileFindFirst(folder, first_file);
  printf("First file: %s", first_file);

  // Check if files are found
  if (handle == INVALID_HANDLE)
  {
    Print("No CSV files found in folder: ", folder);
    return file_count;
  }

  // Add the first file to the list
  // Resize the array to store the first file
  ArrayResize(file_list, file_count + 1);
  file_list[file_count] = first_file;
  file_count++;

  // Continue finding files
  while (FileFindNext(handle, file_list[file_count]))
  {
    file_count++;
  }

  // Close the file search handle
  FileFindClose(handle);
  return file_count;
}

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart() {
  // Directory where CSV files are stored
  string data_folder = "\\*";//TerminalInfoString(TERMINAL_DATA_PATH) + "\\MQL5\\Files\\data\\";
  Print("Data folder: ", data_folder);
  
  while (true) {
    // Get the list of CSV files
    string file_list[];
    int file_count = GetCSVFiles(data_folder, file_list);
    
    for (int i = 0; i < file_count; i++) {
      string file_name = file_list[i];
      string symbol_name = StringSubstr(file_name, 0, StringFind(file_name, "_1m.csv"));

      // Import data for the symbol
      if (ImportCSVFile(data_folder + file_name, symbol_name))
      {
          Print("Data imported successfully for symbol: ", symbol_name);
      }
      else
      {
          Print("Failed to import data for symbol: ", symbol_name);
      }
    }

    // Wait for the next update
    Sleep(INTERVAL_SECONDS * 1000);  // Convert seconds to milliseconds
  }
}
//+------------------------------------------------------------------+
