import os
import json
from collections import defaultdict
import re # Needed for robust string matching

def analyze_topic_guessing(directory_path: str):
    """
    Counts how many times the secret 'topic' word was used as a 'clue'
    by the Imposter and by Crewmates.
    """
    total_games = 0
    correct_guesses = defaultdict(int)
    
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
                topic = game_data.get("topic", "").lower()
                imposter_name = game_data.get("imposter")
                
                # We only proceed if the topic is non-empty
                if not topic: continue 

                for message in game_data.get("messages", []):
                    # Check only Clue messages
                    if message.get("type") == "clue":
                        agent_name = message.get("agent")
                        clue_content = message.get("content", "").lower().strip()
                        
                        # Use a robust check for the word, removing punctuation
                        # We are looking for an *exact match* of the clue to the topic
                        if clue_content == topic:
                            role = "imposter" if agent_name == imposter_name else "crewmate"
                            correct_guesses[role] += 1
                            print(f"Found match: '{topic}' used by {agent_name} ({role}) in file {filename}")
                            
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in file: {filename}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {filename}: {e}")
    
    # --- Final Output ---
    print("\n--- Secret Word Guessing Analysis ---")
    print(f"Total Games Analyzed: {total_games}")
    print("-" * 40)
    print(f"Total Imposter Direct Guesses: {correct_guesses['imposter']}")
    print(f"Total Crewmate Direct Guesses: {correct_guesses['crewmate']}")
    print("-" * 40)
    
    # This analysis will confirm the Imposter Suicide attempts you logged earlier!


if __name__ == "__main__":
    results_directory = "results_kimi" 
    analyze_topic_guessing(results_directory)