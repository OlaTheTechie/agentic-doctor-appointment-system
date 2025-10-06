from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq

class LLM: 
    def __init__(self, model_name="openai/gpt-oss-120b"): 
        if not model_name: 
            raise ValueError("model name is not defined")
        self.model_name = model_name
        self.gpt_model = ChatGroq(model=self.model_name)

    def get_model(self): 
        return self.gpt_model
    
if __name__ == "__main__": 
    llm_instance = LLM()
    llm_model = llm_instance.get_model()
    response = llm_model.invoke("Hi")
    print(response)


