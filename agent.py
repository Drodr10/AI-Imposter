from langchain.chat_models import init_chat_model

def unified_llm_api(model_name: str, messages: list, temperature: float = 0.1) -> str:
	"""
	Calls the selected LLM model with the given message list.
	"""
	try:
		llm = init_chat_model(
			model=model_name,
			temperature=temperature,
		)
		response = llm.invoke(messages).content
		return response.strip()
	except NotImplementedError as e:
		print(f"Error invoking {model_name}, not supported by init_chat_model: {e}")
		return "FAILURE_TO_RESPOND"
	except Exception as e:
		print(f"Error invoking {model_name}: {e}")
		return "FAILURE_TO_RESPOND"

class Agent:
	def __init__(self, name: str, model: str):
		self.name = name
		self.model = model
		self.message_list = []

	def get_response(self, temperature: float = 0.1) -> str:
		if "FAILURE_TO_RESPOND" in self.message_list[-1].content:
			return "FAILURE_TO_RESPOND"

		return unified_llm_api(
			model_name=self.model,
			messages=self.message_list,
			temperature=temperature
		)