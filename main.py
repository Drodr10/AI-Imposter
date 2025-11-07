from agent import Agent
from game import Game
import random

if __name__ == "__main__":
    IPOSTER_MODEL = "google_genai:gemini-2.0-flash-lite"
    PLAYER_MODEL = "groq:llama-3.1-8b-instant"
    agent_names = random.sample(Game.AGENT_NAMES, 4)
    topic = random.choice(Game.TOPICS)
    category = "Physics Concepts"
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
        
    game = Game(agents, topic, category, imposter)
    print(f"Starting game with topic: {topic}")
    game.run_game()
