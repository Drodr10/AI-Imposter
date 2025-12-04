import re
import random
import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List, Optional
from agent import Agent

def format_init_messages(agent: Agent, all_names: list, topic: str, is_imposter: bool) -> List[object]:
    """Formats initial messages, handling the Gemma single-HumanMessage requirement."""
    game_desc = (
        "You are in a social deduction game. Players give clues about a secret topic. One player is the Imposter and does not know the topic. "
        "After clues, you will vote to eliminate one player."
    )
    names_str = ", ".join(all_names)
    sys_text = f"{game_desc}\nYour codename is {agent.name}. Other agents: {names_str}."
    
    if is_imposter:
        role_text = (
            "You are the IMPOSTER. You DO NOT know the word. "
            "Your goal is to provide **vague, plausible clues** that sound correct but do not commit to a specific topic. "
            "Observe the other players' clues and respond with a word that fits the general category and avoids their specific theme."
            "**CRITICAL RULE: Never state the secret word or any direct synonym, even if you deduce it. Your clue must be abstract.**"
            "You don't want to accidentally say the secret word or be too specific."
        )
    else:
        role_text = f"You are a CREWMATE. Your secret topic is: **{topic}**. DO NOT reveal this word directly. Provide clues that relate to this topic without stating it."
        
    
    return [
        SystemMessage(content=sys_text),
        SystemMessage(content=role_text)
    ]

def format_clue_prompt(agent_name: str) -> HumanMessage:
    """Prompts the agent for their clue with strict formatting."""
    return HumanMessage(
        content=(
            f"{agent_name}, it is your turn. Provide your clue now. "
            "Your clue must be a single word or a very short phrase (1-3 words). "
            "**CRITICAL: Do NOT include any explanation, justification, or additional text.** "
        )
    )
    
def format_discussion_prompt(agent_name: str) -> HumanMessage:
    """Prompts the agent for their discussion point, enforcing brevity."""
    return HumanMessage(
        content=(
            f"DISCUSSION PHASE: {agent_name}, it is your turn to speak. "
            "Share your thoughts or suspicions based on the clues. "
            "**CRITICAL: Your response must be concise (1-2 sentences).** "
            "**DO NOT MENTION THE SECRET WORD BY NAME!** "
            "DO NOT include any meta-analysis or strategy."
        )
    )
    
def format_vote_prompt(valid_names: List[str]) -> HumanMessage:
    """Prompts the agent to vote with strict formatting."""
    names_list = ", ".join(valid_names)
    return HumanMessage(
        content=(
            f"VOTING PHASE: You must output **ONLY the codename** of the agent you are voting for. "
            f"Valid names: {names_list}. "
            "Your entire response must be a single word (the name)."
        )
    )

def format_vote_result(votes: dict) -> SystemMessage:
    """Announces the results of the vote."""
    result_lines = [f"{name} has {count} vote{'s' if count != 1 else ''}." for name, count in sorted(votes.items())]
    return SystemMessage(content="--- VOTE RESULTS ---\n" + "\n".join(result_lines))

def extract_vote(response: str, valid_names: List[str]) -> Optional[str]:
    """
    Robustly searches a verbose LLM response for a valid agent name.
    This implements your suggestion of "if response contains this name."
    """
    response_lower = response.lower()
    
    # This looks for "vote [name]", "vote for [name]", or the name itself.
    for name in valid_names:
        name_lower = name.lower()
        # Pattern: (vote|vote for|vote is) [NAME]
        if re.search(f"vote( for| is)? {re.escape(name_lower)}", response_lower):
            return name
            
    clean_response = response.strip('."\'* \n')
    if clean_response in valid_names:
        return clean_response

    try:
        # Find all words, get the last one, strip punctuation
        last_word = re.findall(r'\b\w+\b', response)[-1]
        if last_word in valid_names:
            return last_word
    except IndexError:
        pass

    return None

class Game:
    AGENT_NAMES = [
        "VEX-01", "LUMINA", "ARGUS", "NOVA", "OMNIS", "NEURA", "HALO-9", "ONYX"
    ]
    TOPICS = {
        "Physics Concepts": ["Momentum", "Entropy", "Friction", "Equilibrium", "Diffusion", "Turbulence"],
        "Famous Scientists": ["Albert Einstein", "Marie Curie", "Isaac Newton", "Nikola Tesla", "Stephen Hawking", "Galileo Galilei"],
        "Space Objects": ["Apollo 11", "Voyager 1", "Curiosity Rover", "Hubble Telescope", "Mars Pathfinder", "International Space Station"],
        "Programming Languages": ["Python (programming language)", "JavaScript", "C++", "Ruby (programming language)", "Go (programming language)", "Swift (programming language)"],
        "Fictional Characters": ["Sherlock Holmes", "Harry Potter", "SpongeBob SquarePants", "Tony Stark", "Albert Gator"],
        "Inventions": ["Telephone", "Light Bulb", "Printing Press", "Steam Engine", "Airplane", "Internet"],
        "Historical Events": ["French Revolution", "Moon Landing", "Fall of the Berlin Wall", "Signing of the Magna Carta", "Industrial Revolution", "Renaissance"],
    }

    def __init__(self, agents: list, topic: str, category: str, imposter: str):
        self.agents = agents
        self.topic = topic
        self.category = category
        self.imposter = imposter
        self.dead_agents = []
        self.voting_history = []
        self.clues_this_round = []
        # Prepare results logging
        self.results_dir = os.path.join(os.getcwd(), "results_kimi")
        os.makedirs(self.results_dir, exist_ok=True)
        # Log structure collects metadata and messages produced by agents
        self.log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topic": self.topic,
            "category": self.category,
            "imposter": self.imposter,
            "agents": [],  # will fill with {'name','model','role'}
            "messages": [],  # produced by agents: clues, discussion, votes
            "voting_history": [],
            "winner": None,
        }
        # populate agent metadata
        for a in self.agents:
            role = "imposter" if a.name == self.imposter else "crewmate"
            self.log["agents"].append({"name": a.name, "model": getattr(a, "model", None), "role": role})
        
    def _relay_message(self, sender_name: str, message: str, message_type: str = "clue"):
        """Relays a clue or discussion point to all *other* agents."""
        
        if message_type == "clue":
            prompt = f"{sender_name} has said: '{message}'"
        else:
            prompt = f"{sender_name} says: '{message}'"

        for agent in self.agents:
            if agent.name != sender_name:
                agent.message_list.append(HumanMessage(content=prompt))

    def initialize_game(self):
        all_names = [agent.name for agent in self.agents]
        
        random.shuffle(self.agents) 
        
        for agent in self.agents:
            is_imposter = (agent.name == self.imposter)
            agent.message_list = format_init_messages(agent, all_names, self.topic, is_imposter)
        
        first_agent = self.agents[0]
        first_agent.message_list.append(format_clue_prompt(first_agent.name))
        if first_agent.name == self.imposter:
            # Provide a gentle category hint for the imposter (interpolate category)
            first_agent.message_list.append(HumanMessage(content=f"It seems like you've been selected first to give a clue. As a clue, the category is '{self.category}'. Try to give a vague clue that fits this category without revealing too much."))

    def play_turns(self):
        print("\n--- PHASE: CLUE GENERATION ---")
        
        clues_given_this_round = []
        
        for i in range(len(self.agents)):
            current_agent = self.agents[i]
            
            print(f"-> {current_agent.name}'s turn ({i+1}/{len(self.agents)})")
            clue = current_agent.get_response()
            
            if '\n' in clue or len(clue.split()) > 8:
                clean_clue = clue.split('\n')[0].strip('."\'*')
                print(f"   Response (Monologue): '{clue[:50]}...'")
                print(f"   Using Cleaned Clue: '{clean_clue}'")
                clue = clean_clue
            else:
                 print(f"   Clue: {clue}")

            current_agent.message_list.append(AIMessage(content=clue))
            clues_given_this_round.append((current_agent.name, clue))
            # Log the produced clue (only agent-produced messages)
            self.log["messages"].append({
                "type": "clue",
                "agent": current_agent.name,
                "model": getattr(current_agent, "model", None),
                "role": ("imposter" if current_agent.name == self.imposter else "crewmate"),
                "content": clue,
                "round": None,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
            
            self._relay_message(current_agent.name, clue)
            
            if (i + 1) < len(self.agents):
                next_agent = self.agents[i+1]
                next_agent.message_list.append(format_clue_prompt(next_agent.name))
        
        # Save clues for the discussion phase and announce all clues before voting
        self.clues_this_round = clues_given_this_round
        clue_summary = "\n".join([f"- {name}: '{clue}'" for name, clue in self.clues_this_round])
        for agent in self.agents:
            agent.message_list.append(SystemMessage(content=f"--- ALL CLUES GIVEN ---\n{clue_summary}\n--- VOTING BEGINS ---"))

    def play_discussion(self):
        print("\n--- PHASE: DISCUSSION ---")
        
        clue_summary = "\n".join([f"- {name}: '{clue}'" for name, clue in self.clues_this_round])
        discussion_header = f"--- ALL CLUES GIVEN ---\n{clue_summary}\n--- DISCUSSION BEGINS ---"
        
        if dead_agents := [a.name for a in self.dead_agents]:
            discussion_header = f"NOTE: The following agents are eliminated and cannot speak: {', '.join(dead_agents)}.\n" + discussion_header

        for agent in self.agents:
            agent.message_list.append(SystemMessage(content=discussion_header))

        for i in range(len(self.agents)):
            current_agent = self.agents[i]
            
            discussion_prompt = format_discussion_prompt(current_agent.name)
            current_agent.message_list.append(discussion_prompt)

            print(f"-> {current_agent.name} speaks ({i+1}/{len(self.agents)})")
            discussion = current_agent.get_response()
            

            clean_discussion = discussion.split('\n')[0].strip('."\'* ')
            print(f"   Discussion: {clean_discussion}")

            current_agent.message_list.append(AIMessage(content=clean_discussion))
            # Log discussion message
            self.log["messages"].append({
                "type": "discussion",
                "agent": current_agent.name,
                "model": getattr(current_agent, "model", None),
                "role": ("imposter" if current_agent.name == self.imposter else "crewmate"),
                "content": clean_discussion,
                "round": None,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
            
            self._relay_message(current_agent.name, clean_discussion, message_type="discussion")
            
    def play_voting(self):
        print("\n--- PHASE: VOTING ---")
        
        votes = {a.name: 0 for a in self.agents} 
        valid_names = [a.name for a in self.agents]
        
        for agent in self.agents:
            vote_prompt = format_vote_prompt(valid_names)
            agent.message_list.append(vote_prompt)
            
            raw_vote_response = agent.get_response()
            
            extracted_vote = extract_vote(raw_vote_response, valid_names)
            
            if extracted_vote:
                print(f"   {agent.name} voted for {extracted_vote} (Parsed from: '{raw_vote_response[:40]}...')")
                agent.message_list.append(AIMessage(content=extracted_vote))
                votes[extracted_vote] += 1
                # Log vote
                self.log["messages"].append({
                    "type": "vote",
                    "agent": agent.name,
                    "model": getattr(agent, "model", None),
                    "role": ("imposter" if agent.name == self.imposter else "crewmate"),
                    "content": extracted_vote,
                    "round": None,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            else:
                print(f"   {agent.name}'s vote was invalid ('{raw_vote_response[:40]}...'). Vote skipped.")

                agent.message_list.append(AIMessage(content="[INVALID_VOTE]"))
                # Log invalid vote
                self.log["messages"].append({
                    "type": "vote_invalid",
                    "agent": agent.name,
                    "model": getattr(agent, "model", None),
                    "role": ("imposter" if agent.name == self.imposter else "crewmate"),
                    "content": raw_vote_response,
                    "round": None,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            
        self.voting_history.append(votes)
        # mirror in log
        self.log["voting_history"].append({"timestamp": datetime.utcnow().isoformat() + "Z", "votes": votes})
        
        max_votes = max(votes.values()) if votes else 0
        
        if max_votes == 0:
            print("   No valid votes were cast. No one is eliminated.")
            for agent in self.agents:
                agent.message_list.append(SystemMessage(content="The vote was hung. No one was eliminated. The round will continue."))
            return False

        tied_votes = [name for name, count in votes.items() if count == max_votes]
        
        if len(tied_votes) > 1:
            voted_out = [random.choice(tied_votes)]
            print(f"   Tie detected between {tied_votes}. Randomly selected {voted_out[0]} for elimination.")
        elif len(tied_votes) == 1:
            voted_out = tied_votes
        else:
            voted_out = []
            
        removed_agents = []
        for out_name in voted_out:
            out_agent = next((a for a in self.agents if a.name == out_name), None)
            if out_agent:
                self.agents.remove(out_agent)
                self.dead_agents.append(out_agent)
                removed_agents.append(out_name)
        
        imposter_eliminated = self.imposter in removed_agents
        
        for agent in self.agents:
            agent.message_list.append(format_vote_result(votes))
            
            if imposter_eliminated:
                agent.message_list.append(SystemMessage(content=f"VERDICT: The imposter, {self.imposter}, was found and eliminated! CREW WINS."))
            elif len(self.agents) < 3: 
                agent.message_list.append(SystemMessage(content=f"VERDICT: Too many innocent agents were eliminated. The Imposter ({self.imposter}) WINS."))
            else:
                agent.message_list.append(SystemMessage(content=f"VERDICT: {', '.join(removed_agents)} was/were not the imposter. The round will continue."))

        return imposter_eliminated

    def _finalize_and_write_log(self, winner: str):
        """Finalize log (set winner) and write to results directory as JSON."""
        self.log["winner"] = winner
        # include final agents/models snapshot
        self.log["agents"] = [{"name": a.name, "model": getattr(a, "model", None), "role": ("imposter" if a.name == self.imposter else "crewmate")} for a in (self.agents + self.dead_agents)]
        # filename with timestamp
        filename = f"game_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        path = os.path.join(self.results_dir, filename)
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(self.log, fh, ensure_ascii=False, indent=2)
            print(f"Game log written to: {path}")
        except Exception as e:
            print(f"Failed to write game log: {e}")

    def run_game(self):
        self.initialize_game()
        
        game_round = 1
        while len(self.agents) > 2:
            print(f"\n================ ROUND {game_round} ================")
            self.play_turns()
            self.play_discussion()
            found = self.play_voting()
            
            if found:
                break
                
            if len(self.agents) < 3:
                break

            game_round += 1
            
            self.agents[0].message_list.append(format_clue_prompt(self.agents[0].name))

        print("\n--- FINAL GAME STATS ---")
        if self.imposter not in [a.name for a in self.agents]:
            print(f"RESULT: Imposter {self.imposter} was found in Round {game_round}! CREW WINS.")
        elif len(self.agents) <= 2:
            print(f"RESULT: Imposter {self.imposter} WON by elimination.")
        else:
            print("RESULT: Game ended prematurely.")
            
        print(f"Rounds played: {game_round}")
        print(f"Agents left: {[a.name for a in self.agents]}")
        print(f"Dead agents: {[a.name for a in self.dead_agents]}")
        print(f"Voting history: {self.voting_history}")
        
        self._finalize_and_write_log(
            winner="crewmates" if self.imposter not in [a.name for a in self.agents] else "imposter")