from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# openai/gpt-oss-120b

class LLM:
    def __init__(self, model_name="openai/gpt-oss-120b"):
        if not model_name:
            raise ValueError("model name is not defined")
        self.model_name = model_name
        self.gpt_model = chatgroq(model_name=self.model_name)
        # self.gpt_model = ChatOpenAI(
        #     model_name=model_name, 
        #     temperature=0.0
        # )

    def get_model(self):
        return self.gpt_model

if __name__ == "__main__":
    llm_instance = LLM()
    llm_model = llm_instance.get_model()
    response = llm_model.invoke("Hi")
    print(response)
