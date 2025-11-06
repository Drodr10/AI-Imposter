from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

# --- Configuration ---
# Uncomment the model you want to test.

# --- GOOGLE ---
# https://ai.google.dev/gemini-api/docs/rate-limits
# MODEL_ID = "google_genai:gemini-2.0-flash-lite"

# --- OPENAI ---
# MODEL_ID = "openai:gpt-3.5-turbo"

# --- ANTHROPIC ---
# https://www.anthropic.com/docs/api/reference/rate-limits
# MODEL_ID = "anthropic:claude-haiku-4-5-20251001"

# --- GROQ ---
# https://console.groq.com/docs/rate-limits
# MODEL_ID = "groq:allam-2-7b" # Good
# MODEL_ID = "groq:qwen/qwen3-32b" # warning: this guy can think, and I don't know how to lobotomize him
# MODEL_ID = "groq:moonshotai/kimi-k2-instruct" # Good
# MODEL_ID = "groq:llama-3.1-8b-instant" # Most API calls allowed
# MODEL_ID = "groq:openai/gpt-oss-120b" # Good

def test_unified_connection(model_id: str):
    """Initializes and tests a chat model using the unified factory function."""

    messages = [
        SystemMessage(content="You are a machine that must ONLY output a single English word. Do not explain."),
        HumanMessage(content="What is the color of a stop sign?"),
    ]

    try:
        llm = init_chat_model(
            model_id,
            temperature=0.1,
            # api_key=api_key (not needed to pass if named correctly in .env)
        )

        print(f"--- Testing Connection to {model_id} ---")
        
        response = llm.invoke(messages)
        
        response_word = response.content.strip()
        
        print("Success! Response received.")
        print(f"Model Output: '{response_word}'")

        if response_word.lower() in ["red", "red."]:
            print("Output is a valid response.")
        else:
            print(f"Warning: Model did not output the expected single word. Actual output: '{response_word}'")
            
    except Exception as e:
        print(f"API Connection FAILED for {model_id}:")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    test_unified_connection(MODEL_ID)