from streamlit_chat import message
import streamlit  #streamlit is the GUI 
from dotenv import load_dotenv
from src.PDFHandler import PDFHandler
from src.QA import QA
from src.SwitchLLM import switchLLM
from src.Summarization import Summarization

from src.StreamlitWrapper import StreamlitWrapper


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
 
    streamlitWrapper.setSidebarConfigs(sidebarConfigs,)
    model_name=streamlitWrapper.getModelName()
    llm=switchLLM(streamlitWrapper.getModelName())
    responseContainer=streamlitWrapper.getResponseContainer()
    
    pdfHandler=PDFHandler('/ExtractTextInfoFromPDF.zip')
    qa= QA()
    streamlitWrapper.handlePDFOperation(pdfHandler,qa,llm)
    
    modeOptions=['Summary','Q/A','Answer Generation']
    userAvatar='pixel-art'
    userName='Cixd Member'

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
                            
                            prompt  =   """You will be given a title and a series of sentences from a paper. Your first goal is to add the title at the top of your response. Your next goal is to give a summary of the paper in approximately 10 bulletpoints. 
                            The title will be enclosed in double backtrips (``).
                            The sentences will be enclosed in triple backtrips (```).
                            title: 
                            ``{text}``
                            sentences : 
                            ```{most_important_sents}```
                            SUMMARY :"""
                            sectionSummarization=Summarization(llm,model_name)
                        
                            most_important_sents =sectionSummarization.lexRank(streamlit.session_state.section_text[sectionNameList[index]])
                            summary=sectionSummarization.generateSummary(prompt,most_important_sents, sectionNameList[index])
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
                                sectionSummarization=Summarization(llm,model_name,10)
                                most_important_sents= sectionSummarization.lexRank(streamlit.session_state.section_text[sectionNameList[i]])
                                dictionary[sectionNameList[i]]=most_important_sents 
                            fullTextSummarization=Summarization(llm,model_name)
                            summary= fullTextSummarization.generateSummary(prompt,str(dictionary),pdfHandler.getTitle())
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
                            
                            instrcition: ``{text}``
                            sentences : ```{most_important_sents}```

                            Response :"""
                        
                        fullTextSummarization=Summarization(llm,model_name,60)
                        most_important_sents= fullTextSummarization.lexRank(streamlit.session_state.full_text)
                        summary=fullTextSummarization.generateSummary(prompt,most_important_sents,userInput)
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
                    
################################# Mode: Question Generation #################################
        elif mode== "Q/A":
                streamlitWrapper.resetConversation()
                streamlit.session_state.default_chat= [
                'Pixie here!', "Phew. Did I say this paper was really hard? Because it was! I was forced to utilize my note taking skills to the max and wrote down factual details regarding this paper.", 
                "You can look at some of my notes by pressing the 'OPEN PIXIE's NOTES' button below. ", 'If you have any other factual questions from the paper, just ask me and I will search my notes to help you.']
                 
                streamlitWrapper.setInputContainer('Ask PIXIE: ')
                if streamlitWrapper.userInput():
                    userInput=streamlitWrapper.userInput()
                    with streamlit.spinner("Pixie is thinking..."): 
                     
                        response = streamlit.session_state.conversation({'question': userInput})
                        streamlit.session_state.chat_history = response['chat_history']
                        
               
                with responseContainer:
                    for chat in streamlit.session_state.default_chat:
                        message(chat)
                    for i, chat in enumerate(streamlit.session_state.chat_history):
                        if i % 2 == 0:
                            message(chat.content, is_user=True, avatar_style= userAvatar ,key=str(i) + userName)
                        else:
                            message(chat.content, key=str(i)) 
                     
################################# Mode: Question Answering #################################

        elif mode== 'Answer Generation':
                with  responseContainer:
                    message('Welcome to the ' + mode +' mode.')
                    streamlitWrapper.setInputContainer('Ask PIXIE: ')
            
if __name__ == '__main__': 
    main()


