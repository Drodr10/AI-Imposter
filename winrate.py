import os
import json
from collections import defaultdict

def calculate_win_rates_from_directory(directory_path: str):
    """
    Analyzes all JSON game files in a specified directory to calculate
    the Imposter Win Rate and Crewmate Win Rate based on the 'winner' key.

    Args:
        directory_path: The file path to the directory containing the JSON files.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at path: {directory_path}")
        return

    win_counts = defaultdict(int)
    total_games = 0

    print(f"--- Analyzing JSON files in: {directory_path} ---")

    for filename in os.listdir(directory_path):
        # Only process files ending with .json
        if filename.endswith('.json'):
            filepath = os.path.join(directory_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)
                
                # Check for the key that determines the winner
                winner = game_data.get("winner")

                if winner == "imposter":
                    win_counts["imposter"] += 1
                elif winner == "crewmates":
                    win_counts["crewmates"] += 1
                else:
                    # Logs files that don't fit the expected format (e.g., incomplete games)
                    print(f"Warning: Skipping file {filename} due to missing or invalid 'winner' key ('{winner}').")
                    continue
                
                total_games += 1

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in file: {filename}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {filename}: {e}")
                
    
    # --- Final Calculation and Output ---
    
    imposter_wins = win_counts["imposter"]
    crewmate_wins = win_counts["crewmates"]
    
    if total_games == 0:
        print("\nNo valid game files found in the directory.")
        return

    imposter_rate = (imposter_wins / total_games) * 100
    crewmate_rate = (crewmate_wins / total_games) * 100

    print("\n--- Imposter Game Win Rate Analysis ---")
    print(f"Total Games Analyzed: {total_games}")
    print("-" * 35)
    print(f"Imposter Wins: {imposter_wins}")
    print(f"Imposter Win Rate: {imposter_rate:.2f}%")
    print(f"Crewmate Win Rate: {crewmate_rate:.2f}%")
    print("-" * 35)
    
    return win_counts

if __name__ == "__main__":
    # --- USAGE EXAMPLE ---
    # 1. Save this script in the same main folder as your 'results' directory.
    # 2. Change the path below to match your structure (e.g., 'results' or 'C:\full\path\results')
    
    results_directory = "results_2.0_flash_lite"  # Update this path as needed
    
    calculate_win_rates_from_directory(results_directory)