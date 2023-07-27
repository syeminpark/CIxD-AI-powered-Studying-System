from st_chat_message import message
import streamlit  #streamlit is the GUI 
from src.htmlTemplates import css, bot_template, user_template
from src.chain import get_conversation_chain, get_text_chunks, get_vectorstore, get_embeddings, qa
from dotenv import load_dotenv
from src.PDFHandler import PDFHandler
from os import listdir
from os.path import isfile, join
from src.SwitchLLM import switchLLM
from src.Summarization import Summarization

from src.StreamlitWrapper import StreamlitWrapper


def main():
    load_dotenv()
    #main configs
    configs={
        'page_title':'PoXIE',
        'page_icon': ':robot_face:',
        'header': "PIXIE: Papers In uX & Interaction Exploration"
    }
    streamlitWrapper = StreamlitWrapper(configs)
    #streamlit sidebar configs
    sidebarConfigs={
        'fileUploadText':'Upload a CHI, DIS format paper and click on "Process"',
        'subHeaderText': "CIxD Papers",
        'captionText' : "Select one or more papers to learn."
    }
    modeOptions=['Summary','Question Generation','Answer Generation']
    pdfHandler=PDFHandler('./ExtractTextInfoFromPDF.zip')
    streamlitWrapper.setSidebarConfigs(sidebarConfigs,pdfHandler)
    model_name=streamlitWrapper.getModelName()
    llm=switchLLM(streamlitWrapper.getModelName())
    responseContainer=streamlitWrapper.getResponseContainer()
    

  ######## Mode changer #################################
    if not streamlitWrapper.isFileProcessed():
        with responseContainer:
            message('Hello. This is PIXIE :)')
            message('Lets explore UX & Interaction Papers together!')
            message('I can 1. Summarize 2. Generate Questions 3. Generate Answers based on CHI, DIS format publications')
            message("To talk with me, upload a paper or select a publication, then click on the 'SHARE WITH PIXIE` Button. ")
            message("See you soon!")

    else:
     
        streamlitWrapper.setMode('Select the Mode: ', modeOptions)
        mode=streamlitWrapper.getMode()
        
        match mode:
            case "Summary":
                streamlit.session_state.chat_history=['Welcome to the ' + mode +'  mode!', 
                          'I prepared some of my own prompts to create summaries. You can try them by pressing the buttons below :)',
                          "You can also write your own prompts for summarization! "]
                 
                summarySectionButtonsList=[]
         
                if(len(summarySectionButtonsList)==0 and  streamlit.session_state.section_text!= None):  
                    summarySectionButtonsList.append(streamlit.button('Summarize: ' + 'ALL'))
                    for sectionName in streamlit.session_state.section_text:
                        summarySectionButtonsList.append(streamlit.button('Summarize: ' + sectionName))
                
                for i, summaryButton in enumerate(summarySectionButtonsList):
                    #if a button is clicked except for the 'summarize All' Button
                    index=i-1
                    if summaryButton and i> 0:  
                        with streamlit.spinner("Processing"): 
                            sectionNameList=[]
                            for sectionName in streamlit.session_state.section_text:
                                sectionNameList.append(sectionName)
                            
                            prompt  =   """You will be given a title and a series of sentences from a paper. Your first goal is to add the title at the top of your response. Your next goal is to give a summary of the paper in approximately 10 bulletpoints. 
                            The title will be enclosed in double backtrips (``).
                            The sentences will be enclosed in triple backtrips (```).
                            title: 
                            ``{title}``
                            sentences : 
                            ```{most_important_sents}```
                            SUMMARY :"""
                            summarization=Summarization(prompt,llm,model_name)
                        
                            most_important_sents =summarization.lexRank(streamlit.session_state.section_text[sectionNameList[index]])
                            summary=summarization.generateSummary(most_important_sents, sectionNameList[index])
                            streamlit.session_state.chat_history.append(summary)
                            
                                    
                    #################summarize the entire text 
                    elif summaryButton and i==0:
                        with streamlit.spinner("Processing"): 
                        
                            dict={}
                            r_prompt  =  """You will be given a title: {title} and a dictionary: {most_important_sents} that contains section titles as its keys and the content of those sections as its values.
                    
                            Your first goal is to add the title at the top of your response. 
                            Your next goal is to deconstruct the dictionary, and place the section title, and summarize each section's content under the section title.
                            
                            Section Titles and Content :"""
                            
                            sectionNameList=[]
                            for sectionName in streamlit.session_state.section_text:
                                sectionNameList.append(sectionName)
                                
                            for i in range(len(streamlit.session_state.section_text)):
                                summarization=Summarization(r_prompt,llm,model_name,10)
                                most_important_sents =summarization.lexRank(streamlit.session_state.section_text[sectionNameList[i]])
                                dict[sectionNameList[i]]=most_important_sents 
                            summarization=Summarization(r_prompt,llm,model_name)
                            summary=summarization.generateSummary(str(dict),pdfHandler.getTitle())
                            streamlit.session_state.chat_history.append(summary)
            
                with responseContainer:
                    for chat in streamlit.session_state.chat_history:
                        print(chat)
                        message(chat)
                streamlitWrapper.setInputContainer('Ask PIXIE: ')
                   
            
            case "Question Generation":
               
                with  responseContainer:
                     message('Welcome to the ' + mode +' mode.')
                     streamlitWrapper.setInputContainer('Ask PIXIE: ')
                
            case 'Answer Generation':
                with  responseContainer:
                    message('Welcome to the ' + mode +' mode.')
                    streamlitWrapper.setInputContainer('Ask PIXIE: ')
            
    
     
        
  #########################################
if __name__ == '__main__': 
    main()
