from langchain import PromptTemplate
from langchain.schema import  HumanMessage, SystemMessage
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from summarizer import Summarizer
import streamlit

class Summarization:
    def __init__(self,llm,llmName,model) -> None:
        self.formattedPrompt=''
        self.llm=llm
        self.llmName=llmName
        self.lex_rank=model

        
    def lexRank(self,text,sentenceCount=40):
        sentenceCount=sentenceCount
        tokenizer=Tokenizer("english")
        parser=PlaintextParser(text, tokenizer)
        most_important_sents= self.lex_rank(parser.document, sentences_count=sentenceCount)
        most_important_sents =[str(sent) for sent in most_important_sents if str(sent)]
        return most_important_sents
       
    def bertExtractiveSummarize(self,text,sentenceCount=40):
        model = Summarizer()
        most_important_sents = model(text, num_sentences=sentenceCount) # We specify a number of sentences
        return most_important_sents
    
    def generateSummary(self,input,most_important_sents,text):
        prompt= PromptTemplate(template=input, input_variables=["most_important_sents", 'text'])
         
        if(self.llmName!='gpt-3.5-turbo'):
            return self.llm(prompt=prompt.format(most_important_sents=most_important_sents , text=text))
        else:
            return self.llm.predict_messages([HumanMessage(content= prompt.format(most_important_sents=most_important_sents, text=text))]).content
    
   