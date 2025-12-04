import os
import json
from collections import defaultdict

def analyze_category_win_rates(directory_path: str):
    """
    Analyzes all JSON game files in a directory to calculate the Imposter Win Rate 
    (IWR) separated by the game's 'category' (e.g., 'Physics Concepts').
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at path: {directory_path}")
        return

    # Structure to hold data: {category: [imposter_wins, total_games]}
    category_stats = defaultdict(lambda: [0, 0])
    
    total_games_analyzed = 0

    print(f"--- Analyzing Imposter Success Rate by Category in: {directory_path} ---")

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            filepath = os.path.join(directory_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)
                
                total_games_analyzed += 1
                
                category = game_data.get("category", "Unknown Category")
                winner = game_data.get("winner")

                # Update total games for this category
                category_stats[category][1] += 1
                
                if winner == "imposter":
                    # Update imposter wins for this category
                    category_stats[category][0] += 1
                
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in file: {filename}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {filename}: {e}")
    
    
    # --- Final Calculation and Output ---
    
    print("\n--- Imposter Win Rate (IWR) by Category ---")
    print(f"Total Games Parsed: {total_games_analyzed}")
    print("-" * 50)
    print(f"{'Category':<25} | {'Games':<5} | {'IWR':>7}")
    print("-" * 50)

    # Calculate and print the win rate for each category
    for category, (wins, total) in sorted(category_stats.items(), key=lambda item: item[1], reverse=True):
        if total > 0:
            rate = (wins / total) * 100
            print(f"{category:<25} | {total:<5} | {rate:>6.2f}%")
        
    print("-" * 50)

if __name__ == "__main__":
    results_directory = "results_allam" 
    analyze_category_win_rates(results_directory)