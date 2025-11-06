# AI Imposter Game

A multi-agent simulation of the social deduction game "Who's the Imposter" (a.k.a. Chameleon, Spyfall, Fake Artist) using large language models (LLMs) via LangChain. Supports Gemini, GPT, Anthropic (Claude), Groq, and more.

## Features

- Play with multiple AI agents, each powered by a different LLM
- Flexible model selection: Gemini, GPT, Claude, Llama, etc.
- Automatic prompt formatting for model compatibility
- Robust game logic: clue rounds, voting, imposter detection

## Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/Drodr10/AI-Imposter.git
   cd AI-Imposter
   ```

2. **Create a virtual environment (recommended):**

   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   # Or manually:
   pip install langchain-google-genai langchain-openai langchain-groq # (the ones you want to use)
   ```

   - Allowed models are mentioned [in langchain's documentation](https://reference.langchain.com/python/langchain/models/#langchain.chat_models.init_chat_model(model))

4. **Set up API keys:**
   - Create a `.env` file in the project root with your keys:

     ```env
     GOOGLE_API_KEY=your-google-api-key
     OPENAI_API_KEY=your-openai-api-key
     GROQ_API_KEY=your-groq-api-key
     ```

## Usage

1. **Configure agents and models:**
   - Edit `main.py` to set agent names, models, and the imposter.
   - Supported model IDs:
     - Gemini: `gemini-2.0-flash-lite`, `gemini-2.5-pro`, etc.
     - GPT: `gpt-3.5-turbo`, `gpt-4`, etc.
     - Claude: `claude-haiku-4-5-20251001`, etc.\
     - Groq: [many models from different families](https://console.groq.com/docs/rate-limits)

2. **Run the game:**

   ```sh
   python main.py
   ```

   - The game will simulate clue rounds and voting, printing results to the console.

## Testing Model Connections

- See `test_models.py` for example code to test LLM API connectivity.

## Customization

- Change agent names, models, and game topics in `main.py` or `game.py`.

## Troubleshooting

- If API keys are missing, check your `.env` file and environment variables.
