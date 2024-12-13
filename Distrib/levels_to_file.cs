using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.DrawingTools;

namespace NinjaTrader.NinjaScript.Strategies
{
    public class LevelsToFile : Strategy
    {
        private string filePath = @"C:\Users\Liikurserv\PycharmProjects\RT_Ninja\hardcoded_sr_levels_2.csv";

        private Dictionary<string, double> levelPrices = new Dictionary<string, double>();

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "LevelsToFile";
                Calculate = Calculate.OnEachTick;
            }
        }

        private void SaveLevelPrice(string tag, double price)
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
                Print($"Level {tag} -> {price:F2} saved to file.");
            }
            catch (Exception ex)
            {
                Print($"Error saving level to file: {ex.Message}");
            }
        }

        private void LoadLevelsFromFile()
        {
            if (File.Exists(filePath))
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
            }
        }

		private void RemoveLevelFromChart(string tag)
		{
			// Iterate through the DrawObjects to find and remove the line
			foreach (var drawObject in DrawObjects)
			{
				if (drawObject is DrawingTools.HorizontalLine horizontalLine && horizontalLine.Tag == tag)
				{
					RemoveDrawObject(tag);  // Pass the tag to remove the line
					Print($"Removed {tag} from chart.");
				}
			}
		}

        private void MonitorLevelChanges()
        {
            LoadLevelsFromFile();

            HashSet<string> currentTags = new HashSet<string>();

            foreach (var drawObject in DrawObjects)
            {
                if (drawObject is DrawingTools.HorizontalLine horizontalLine)
                {
                    string tag = horizontalLine.Tag;
                    double currentPrice = horizontalLine.StartAnchor.Price;

                    currentTags.Add(tag);

                    if (!levelPrices.ContainsKey(tag))
                    {
                        levelPrices[tag] = currentPrice;
                    }
                    else if (Math.Abs(levelPrices[tag] - currentPrice) > Double.Epsilon)
                    {
                        levelPrices[tag] = currentPrice;
                        Print($"Updated {tag} -> {currentPrice}");
                    }

                    SaveLevelPrice(tag, currentPrice);
                }
            }

            var deletedTags = levelPrices.Keys.Except(currentTags).ToList();
            foreach (var tag in deletedTags)
            {
                RemoveLevelFromChart(tag);
                levelPrices.Remove(tag);
                Print($"Deleted {tag} from chart and file.");
            }

            SaveLevelPrice(string.Empty, 0);
        }

        protected override void OnBarUpdate()
        {
            MonitorLevelChanges();
        }
    }
}
