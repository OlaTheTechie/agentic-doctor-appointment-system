from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class LLM:
    def __init__(self, model_name="gpt-3.5-turbo"):
        if not model_name:
            raise ValueError("model name is not defined")
        self.model_name = model_name
        self.gpt_model = ChatOpenAI(model_name=self.model_name)

    def get_model(self):
        return self.gpt_model

if __name__ == "__main__":
    llm_instance = LLM()
    llm_model = llm_instance.get_model()
    response = llm_model.invoke("Hi")
    print(response)
