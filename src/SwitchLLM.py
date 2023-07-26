
from langchain.llms import HuggingFaceHub # hugging face can replace the openAI model
from src.api.wz13 import wizardVicuna13
from src.api.repli import Replicate
from langchain.chat_models import ChatOpenAI
from langchain.llms.octoai_endpoint import OctoAIEndpoint
from src.api.octoAICloud import OctoAiCloudLLM
from src.api.huggingface_endpoint import HuggingFaceEndpoint
import os

def switchLLM(model_name):
    llm=None
   
    if model_name=='gpt-3.5-turbo':
        llm = ChatOpenAI()
        
    elif model_name=='flan-t5-xxl_huggingface':
        llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs=
                         {"temperature":0.5, "max_length":1024,
                           "top_k": 30,"top_p": 0.9, "repetition_penalty": 1.02})
    elif model_name=='huggingCustomEndpoint':
        llm= HuggingFaceEndpoint(endpoint_url=os.getenv('ENDPOINT_URL'),task="text-generation",
                              model_kwargs={"max_new_tokens": 512, "top_k": 30, "top_p": 0.9, "temperature": 0.2, "repetition_penalty": 1.02,})
    elif model_name=='wizardVicuna13_local':
        llm=wizardVicuna13()
    elif model_name=='vicuna13b_replicate':
        llm = Replicate(model="replicate/vicuna-13b:6282abe6a492de4145d7bb601023762212f9ddbbe78278bd6771c8b3b2f2a13b",
                        input= {"max_length":8000,"max_new_tokens": 8000})
    elif model_name=='llama_v2_13b_replicate':
        llm = Replicate(model="a16z-infra/llama13b-v2-chat:d5da4236b006f967ceb7da037be9cfc3924b20d21fed88e1e94f19d56e2d3111",
                        input= {"max_length":2048,"max_new_tokens": 2048})
    elif model_name=='llama_v2_70b_replicate':
        llm = Replicate(model="replicate/llama70b-v2-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
                        input= {"max_length":2048,"max_new_tokens": 2048})
    elif model_name=='falcon7b_octoAI':
        llm = OctoAIEndpoint(
            model_kwargs={
                "max_new_tokens": 200,
                "temperature": 0.75,
                "top_p": 0.95,
                "repetition_penalty": 1,
                "seed": None,
                "stop": [],
            },
        )
    print('llm_model: ',model_name)
    return llm