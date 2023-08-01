#from streamlit_chat import message
from st_chat_message import message
import streamlit  #streamlit is the GUI 
from dotenv import load_dotenv
from src.PDFHandler import PDFHandler
from src.QA import QA
from src.SwitchLLM import switchLLM
from src.Summarization import Summarization

from src.StreamlitWrapper import StreamlitWrapper
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
from langchain.schema import  HumanMessage, SystemMessage

@streamlit.cache_resource
def load_model():
    nltk.download('punkt')
    return LexRankSummarizer()

def main():
    load_dotenv()
    
    #main configs
    configs={
        'page_title':'PIXIE',
        'page_icon': ':robot_face:',
        'header': "PIXIE: Papers In uX & Interaction Exploration"
    }
    streamlitWrapper = StreamlitWrapper(configs)
    #streamlit sidebar configs
    sidebarConfigs={
        'fileUploadText':'Upload a pdf"',
        'subHeaderText': "CIxD Papers",
        'captionText' : "Select one or more papers to learn."
    }
    lexRank=load_model()
    streamlitWrapper.setSidebarConfigs(sidebarConfigs,)
    model_name=streamlitWrapper.getModelName()
    llm=switchLLM(streamlitWrapper.getModelName())
    responseContainer=streamlitWrapper.getResponseContainer()
    
    pdfHandler=PDFHandler('/ExtractTextInfoFromPDF.zip')
    qa= QA()
    streamlitWrapper.handlePDFOperation(pdfHandler,qa,llm)
    
    modeOptions=['Summary','Q/A','Comments & Feedback']
    userAvatar='pixel-art'
    userName='Cixd Member'
    summarization=Summarization(llm,model_name,lexRank)
    

  ######## Mode changer #################################
    if not streamlitWrapper.isFileProcessed():
        with responseContainer:
            message('Hello. This is Pixie Park (박픽시) :) I am a 1st year master student in CIxD Lab.')
            message("Lets explore our lab's papers together!")
            message('Although I am a newbie, I can still decently summarize, answer questions, and provide feeback on HCI papers.')
            message("To talk with me, upload or select a publication, then click the 'SHARE WITH PIXIE` button. ")
            message("See you soon!")
    else:
     
        streamlitWrapper.setMode('Select the Mode: ', modeOptions)
        mode=streamlitWrapper.getMode()
        
        
################################# Mode:Summary #################################
        if mode== "Summary":
                streamlitWrapper.resetConversation()
                streamlit.session_state.default_chat= [
                'Pixie here!', 'After reading the paper, I wanted to organize my thoughts and wrote down some of my own summaries. You can investigate them by pressing the buttons below :)',
                    "You can also ask me to do summaries in different ways, if there is something wrong... What do you think makes a summary great?", "But I recommend reading the paper first and then seeing my summaries. This way you can compare what you think is important, to what I thought was the essence of the text. "]
                 
                summarySectionButtonsList=[]
                if(len(summarySectionButtonsList)==0 and  streamlit.session_state.section_text!= None):  
                    summarySectionButtonsList.append(streamlit.button('Summarize: ' + 'ALL'))
                    for sectionName in streamlit.session_state.section_text:
                        summarySectionButtonsList.append(streamlit.button('Summarize: ' + sectionName))
                
                for i, summaryButton in enumerate(summarySectionButtonsList):
                    #if a button is clicked except for the 'summarize All' Button
                    index=i-1
                    if summaryButton and i> 0:  
                        with streamlit.spinner("Pixie is thinking..."): 
                            sectionNameList=[]
                            for sectionName in streamlit.session_state.section_text:
                                sectionNameList.append(sectionName)
                            
                            prompt  =   """You will be given a title and a series of sentences from a paper. Your first goal is to add the title at the top of your response. Your next goal is to organize the main structure of the paper in bullet points.
                            The title will be enclosed in double backtrips (``).
                            The sentences will be enclosed in triple backtrips (```).
                            title: 
                            ``{text}``
                            sentences : 
                            ```{most_important_sents}```
                            SUMMARY :"""
                            
                            most_important_sents =summarization.lexRank(streamlit.session_state.section_text[sectionNameList[index]])
                            summary=summarization.generateWithSummary(prompt,most_important_sents, sectionNameList[index])
                            streamlit.session_state.default_chat.append(summary)
                            
                                    
                    #################summarize the entire text 
                    elif summaryButton and i==0:
                        with streamlit.spinner("Pixie is thinking..."): 
                        
                            dictionary={}
                            prompt  =  """You will be given a title: {text} and a dictionary: {most_important_sents} that contains section titles as its keys and the content of those sections as its values.
                    
                            Your first goal is to add the title at the top of your response. 
                            Your next goal is to deconstruct the dictionary, and place the section title, and summarize each section's content under the section title.
                            
                            Section Titles and Content :"""
                            
                            sectionNameList=[]
                            for sectionName in streamlit.session_state.section_text:
                                sectionNameList.append(sectionName)
                                
                            for i in range(len(streamlit.session_state.section_text)):
                                most_important_sents= summarization.lexRank(streamlit.session_state.section_text[sectionNameList[i]],10)
                                dictionary[sectionNameList[i]]=most_important_sents 
                     
                            summary= summarization.generateWithSummary(prompt,str(dictionary),pdfHandler.getTitle())
                            streamlit.session_state.default_chat.append(summary)
                
                ##############INPUT############    
                streamlitWrapper.setInputContainer('Ask PIXIE: ')
                if streamlitWrapper.userInput():
                    userInput=streamlitWrapper.userInput()
                    with streamlit.spinner("Processing"): 
                        prompt  =  """
                            You will be given a series of sentences from a paper.
                            Your goal is to manipulate this paper with an additional instruction:
                            
                            The instruction will be enclosed in double backtrips (``)
                            The sentences will be enclosed in triple backtrips (```)
                            
                            instruction: ``{text}``
                            sentences : ```{most_important_sents}```

                            Response :"""
                        
                        most_important_sents= summarization.lexRank(streamlit.session_state.full_text,60)
                        summary=summarization.generateWithSummary(prompt,most_important_sents,userInput)
                        if streamlit.session_state.chat_history==None:
                            streamlit.session_state.chat_history=[]
                        streamlit.session_state.chat_history.append(userInput)
                        streamlit.session_state.chat_history.append(summary)
                        
            
                #########################Chat
                with responseContainer:
                    for chat in streamlit.session_state.default_chat:
                        message(chat)
                    for i, chat in enumerate(streamlit.session_state.chat_history):
                        if i % 2 == 0:
                            message(chat, is_user=True, avatar_style= userAvatar ,key=str(i) + userName)
                        else:
                            message(chat, key=str(i)) 
                    
################################# Mode: Question & Answers #################################
        elif mode== "Q/A":
                streamlitWrapper.resetConversation()
                streamlit.session_state.default_chat= [
                'Pixie here!', "Phew. Did I say this paper was really hard? Because it was! I was forced to utilize my note taking skills to the max and wrote down factual details regarding this paper.", 
                "You can look at some of my notes by pressing the 'OPEN PIXIE's NOTES' button below. ", 'If you have any other factual questions from the paper, just ask me and I will search my notes to help you.']
                
                if streamlit.button("OPEN PIXIE's NOTES"):
                    with streamlit.spinner("Pixie is thinking..."): 
                        prompt  =  """ 
                        You will be given a series of sentences from a paper. The sentences will be enclosed in triple backtrips (```).
                        Your goal is to create a list of meaningful questions that have answers in the series of sentence.
                        Write the answers for each question under each question. 
                        sentences : ```{most_important_sents}{text}```
                        Response :"""
                        
                        most_important_sents= summarization.lexRank(streamlit.session_state.full_text,60)
                        response=summarization.generateWithSummary(prompt,most_important_sents,"")
                        #prompt  =  """Create a list of questions that may be of interest to a reader. These questions must have specific answers in the provided text. Then find and write their answers under each question"""
                        # response = streamlit.session_state.qaChain({'query': prompt})
                        #streamlit.session_state.default_chat.append(response['result'])
                        
                        streamlit.session_state.default_chat.append(response)
                            
                           
                streamlitWrapper.setInputContainer('Ask PIXIE: ')
                if streamlitWrapper.userInput():
                    userInput=streamlitWrapper.userInput()
                    with streamlit.spinner("Pixie is thinking..."): 
                     
                        response = streamlit.session_state.conversationChain({'question': userInput})
                        streamlit.session_state.default_chat = response['chat_history']
                        
               
                with responseContainer:
                    for chat in streamlit.session_state.default_chat:
                        message(chat)
                    for i, chat in enumerate(streamlit.session_state.chat_history):
                        if i % 2 == 0:
                            message(chat.content, is_user=True, avatar_style= userAvatar ,key=str(i) + userName)
                        else:
                            message(chat.content, key=str(i)) 
                     
################################# Mode: Comments & Feedback #################################

        elif mode== 'Comments & Feedback':
            streamlitWrapper.resetConversation()
            streamlit.session_state.default_chat= [
            'Pixie here!', 
            "Oh, I really enjoyed this paper. I can't wait to tell you my thoughts on this one",
            "Click the provided feedback buttons below to see my enthusiastic feedback!",
            'I might be a little critical, but it is just that I want to learn more :-) '
            ]
            
            buttonNames=[ "Novel? ","Clear Research Gap?", "Limitation?", 'Well Structured?']
            buttons=[]
            feedbackQuuestions=[
                "what is the novelty of this paper?",
                "what research gap or limitations from different research does this paper build upon?",
                "What is the limitation, hindsight, weakness, or future work needed for this paper?",
                "What is the structure, overall flow of this paper?"
            ]
            feedbackInstructions=["is truly novel or not , or could have been novel when first published or not",
                                  "has or does not have a clear research gap",
                                  "has or does not have at least one limitation, hindsight, weakness, future work needed that can hamper the paper's credibility.",
                                  "has a well built strucutre or not"
            ]
                                  
                                
            
            for buttonName in buttonNames:
               buttons.append(streamlit.button(buttonName))
            
            for i, button in enumerate(buttons):
                if button:
                    with streamlit.spinner("Pixie is thinking..."): 
                            response = streamlit.session_state.qaChain({'query': feedbackQuuestions[i]})
                            print(response)
                            
                            secondPrompt  =  """ 
                            "Be critical with your previous opinion. Use general thinking to counter argue the extractions of this paper.
                            Finally decide your final opinion whether the paper{question}. 
                          
                            Remember to keep your response concise.
                            Your previous opinion will be enclosed in triple backtrips (```).
                            The extractions from the paper will be enclosed in double backtrips (``).
                            previous opinion: ```{idea}```
                            Extractions from the paper: ``{context}``
                            
                            Response:
                            """
                            
                            output=''
                            if(model_name!='gpt-3.5-turbo'):
                                output=llm(prompt=secondPrompt.format(question = feedbackInstructions[i], idea= response['result'],context= response['source_documents']))
                            else:
                                output=llm.predict_messages([HumanMessage(question =  feedbackInstructions[i],content= secondPrompt.format(question = feedbackInstructions[i],idea=response['result'], context= response['source_documents']))]).content
                        
                            
                            streamlit.session_state.default_chat.append(output)
            
            
            
            with  responseContainer:
                for chat in streamlit.session_state.default_chat:
                    message(chat)
            
if __name__ == '__main__': 
    main()
