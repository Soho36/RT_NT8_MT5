using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using NinjaTrader.NinjaScript;

namespace NinjaTrader.NinjaScript.Strategies
{
    public class LevelsToFile : Strategy
    {
        private string filePath = @"C:\Users\Liikurserv\PycharmProjects\RT_Ninja\nt8_levels.csv";
        private Dictionary<string, double> levelPrices = new Dictionary<string, double>();

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "LevelsToFile";
                Calculate = Calculate.OnBarClose; // Run once per bar
            }
            else if (State == State.Configure)
            {
                LoadLevelsFromFile(); // Initialize levels
            }
        }

        private void SaveAllLevelsToFile()
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(filePath, false))
                {
                    foreach (var entry in levelPrices)
                    {
                        writer.WriteLine($"{entry.Key},{entry.Value:F2}");
                    }
                }
                // Print("All levels saved to file.");
            }
            catch (Exception ex)
            {
                Print($"Error saving levels to file: {ex.Message}");
            }
        }

        private void LoadLevelsFromFile()
        {
            if (File.Exists(filePath))
            {
                try
                {
                    string[] lines = File.ReadAllLines(filePath);
                    levelPrices.Clear();
                    foreach (var line in lines)
                    {
                        string[] parts = line.Split(',');
                        if (parts.Length == 2 && double.TryParse(parts[1], out double price))
                        {
                            levelPrices[parts[0]] = price;
                        }
                    }
                    Print("Levels loaded from file.");
                }
                catch (Exception ex)
                {
                    Print($"Error loading levels from file: {ex.Message}");
                }
            }
        }

        private void MonitorLevelChanges()
        {
            HashSet<string> currentTags = new HashSet<string>();

            foreach (var drawObject in DrawObjects)
            {
                if (drawObject is DrawingTools.HorizontalLine horizontalLine)
                {
                    string tag = horizontalLine.Tag;
                    double currentPrice = horizontalLine.StartAnchor.Price;

                    currentTags.Add(tag);

                    if (!levelPrices.ContainsKey(tag) || Math.Abs(levelPrices[tag] - currentPrice) > Double.Epsilon)
                    {
                        levelPrices[tag] = currentPrice; // Add or update level
                        Print($"Level {tag} updated to {currentPrice:F2}");
                    }
                }
            }

            // Detect and remove deleted levels
            var deletedTags = levelPrices.Keys.Except(currentTags).ToList();
            foreach (var tag in deletedTags)
            {
                levelPrices.Remove(tag); // Remove from dictionary
                RemoveDrawObject(tag); // Directly remove from chart
                Print($"Level {tag} removed.");
            }

            SaveAllLevelsToFile(); // Save all changes once
        }

        protected override void OnBarUpdate()
        {
            MonitorLevelChanges(); // Monitor levels once per bar
        }
    }
}
