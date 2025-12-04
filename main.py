from agent import Agent
from game import Game
import random
import os 
from dotenv import load_dotenv
load_dotenv()

def loop_games_n_times(n: int):
    for _ in range(n):
        agent_names = random.sample(Game.AGENT_NAMES, 4)
        category = random.choice(list(Game.TOPICS.keys()))
        topic = random.choice(Game.TOPICS[category])
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

if __name__ == "__main__":
    IPOSTER_MODEL = "groq:moonshotai/kimi-k2-instruct"
    PLAYER_MODEL = "groq:llama-3.1-8b-instant"
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key

    if input("Loop games? (y/n): ").lower() == "y":
        n = int(input("How many games to play? "))
        loop_games_n_times(n)
        exit()
        
    agent_names = random.sample(Game.AGENT_NAMES, 4)
    category = random.choice(list(Game.TOPICS.keys()))
    topic = random.choice(Game.TOPICS[category])
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