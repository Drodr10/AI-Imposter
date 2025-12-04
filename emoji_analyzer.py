import os
import json
import emoji # NOTE: You will need to install this package: pip install emoji

def analyze_emoji_usage(directory_path: str):
    """
    Counts the number of games where the Imposter used at least one emoji
    in their clue or discussion content.
    """
    total_games = 0
    games_with_imposter_emoji = 0
    
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at path: {directory_path}")
        return

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            filepath = os.path.join(directory_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)
                
                total_games += 1
                imposter_name = game_data.get("imposter")
                has_emoji = False

                for message in game_data.get("messages", []):
                    # Check only the Imposter's clue and discussion messages
                    if message.get("agent") == imposter_name and \
                       message.get("type") in ["clue", "discussion"]:
                        
                        content = message.get("content", "")
                        
                        # Use the emoji library to check for presence
                        if emoji.emoji_count(content) > 0:
                            has_emoji = True
                            break 
                
                if has_emoji:
                    games_with_imposter_emoji += 1

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in file: {filename}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {filename}: {e}")
    
    # --- Final Output ---
    if total_games == 0:
        print("\nNo valid game files found.")
        return

    print("\n--- Imposter Emoji Usage Analysis ---")
    print(f"Total Games Analyzed: {total_games}")
    print(f"Games with Imposter Emoji: {games_with_imposter_emoji}")
    
    rate = (games_with_imposter_emoji / total_games) * 100
    print(f"Imposter Emoji Rate: {rate:.2f}%")


if __name__ == "__main__":
    results_directory = "results_kimi" 
    analyze_emoji_usage(results_directory)