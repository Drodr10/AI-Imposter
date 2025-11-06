from agent import Agent
from game import Game
from dotenv import load_dotenv
import random

if __name__ == "__main__":
    load_dotenv()
    import os
    IPOSTER_MODEL = "google_genai:gemini-2.0-flash-lite"
    PLAYER_MODEL = "groq:llama-3.1-8b-instant"
    agent_names = random.sample(Game.AGENT_NAMES, 4)
    topic = "Spongebob" # random.choice(Game.TOPICS)
    imposter = random.choice(agent_names)
    print(f"Imposter is: {imposter}")
    agents = []
    for name in agent_names:
        if name == imposter:
            model = IPOSTER_MODEL
        else:
            model = PLAYER_MODEL
        
        agent = Agent(name=name, model=model)
        agents.append(agent)
        
    game = Game(agents, topic, imposter)
    print(f"Starting game with topic: {topic}")
    game.run_game()
