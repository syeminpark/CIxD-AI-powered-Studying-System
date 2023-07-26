from langchain import PromptTemplate
from langchain.schema import  HumanMessage, SystemMessage
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from summarizer import Summarizer

class Summarization:
    def __init__(self,prompt,llm,llmName,sentenceCount=40) -> None:
        self.prompt=prompt
        self.formattedPrompt=''
        self.llm=llm
        self.llmName=llmName
        self.sentenceCount=sentenceCount

    def lexRank(self,text):
        tokenizer=Tokenizer("english")
        parser=PlaintextParser(text, tokenizer)
        lex_rank=LexRankSummarizer()
        most_important_sents= lex_rank(parser.document, sentences_count=self.sentenceCount)
        most_important_sents =[str(sent) for sent in most_important_sents if str(sent)]
        return most_important_sents
       
    def bertExtractiveSummarize(self,text):
        model = Summarizer()
        most_important_sents = model(text, num_sentences=self.sentenceCount) # We specify a number of sentences
        return most_important_sents
    
    def generateSummary(self,most_important_sents,title):
        prompt_summarize_most_important_sents   = PromptTemplate(template=self.prompt, input_variables=["most_important_sents", 'title'])
         
        if(self.llmName!='gpt-3.5-turbo'):
            return self.llm(prompt=prompt_summarize_most_important_sents.format(most_important_sents=most_important_sents , title=title))
        else:
            return self.llm.predict_messages([HumanMessage(content= prompt_summarize_most_important_sents.format(most_important_sents=most_important_sents, title=title))]).content