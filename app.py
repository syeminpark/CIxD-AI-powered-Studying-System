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
from src.config import LLMList

def handle_userInput(user_question):
    response = streamlit.session_state.conversation({'question': user_question})
    streamlit.session_state.chat_history = response['chat_history']

def main():
    #########variables##############
    pageTitle= "CIxD AIPowered Studying System"
    pageIcon=':robot_face:'
    modeOptions=['Summary','Question Generation','Answer Generation', 'Topic Recommendation']
    header= "CIxD AIPowered Studying System :robot_face:"
    fileUploadText="Upload a CHI, DIS format paper and click on 'Process'"
    accept_multiple_files=False
    subheaderText="CIxD Papers"
    captionText="Select one or more papers to learn."
    pdfFolderPath='./pdf/'
    pdfFiles=[]
    pdf_checkbox=[]
    llm=''
    
    #############others#######################
    load_dotenv()
    pdfHandler=PDFHandler('./ExtractTextInfoFromPDF.zip')

    ########initialize#######################
    streamlit.set_page_config(page_title=pageTitle,page_icon=pageIcon)
    streamlit.write(css, unsafe_allow_html=True)
    streamlit.header(header)
    modeselect = streamlit.selectbox('Select the Mode: ', options=[*modeOptions])
    streamlit.write('Selected Mode: ', modeselect)
    
    response_container = streamlit.container()
    container = streamlit.container()
    
    model_name = streamlit.sidebar.radio("Choose a model:", ([*LLMList]))
    llm=switchLLM(model_name)
    
    if "conversation" not in streamlit.session_state:
        streamlit.session_state.conversation = None
    if  "chat_history" not in streamlit.session_state:
        streamlit.session_state.chat_history = None
    if  "section_text" not in streamlit.session_state:
        streamlit.session_state.section_text = None
    if  "full_text" not in streamlit.session_state:
        streamlit.session_state.full_text = None

    with container:
        #유저가 텍스트 입력할 수 있는 곳 
        with streamlit.form(key='my_form', clear_on_submit=True):
            user_input = streamlit.text_area("You:", key='input', height=100)
            submit_button = streamlit.form_submit_button(label='Send')
            
        if submit_button and user_input:
            handle_userInput(user_input,response_container)
                
        if streamlit.session_state['chat_history']:
             with response_container:
                for i, conversation in enumerate(streamlit.session_state.chat_history):
                    if i % 2 == 0:
                        message(conversation.content, is_user=True, avatar_style= 'pixel-art',key=str(i) + '_user')
                    else:
                        message(conversation.content, key=str(i))
    with streamlit.sidebar:
        pdf_docs = streamlit.file_uploader(
                fileUploadText, accept_multiple_files= accept_multiple_files,type="pdf") #this just lets us enable this function
        streamlit.subheader(subheaderText)
        streamlit.caption(captionText)
        
        pdfFiles = [f for f in listdir( pdfFolderPath) if isfile(join( pdfFolderPath, f))]
        
        for pdf in pdfFiles:
            pdf_checkbox.append(streamlit.checkbox(pdf))
        
     ########interaction#######################
    with streamlit.sidebar:
            if streamlit.button("Process"):
                with streamlit.spinner("Processing"): 
                    for index, checkedpdf in enumerate(pdf_checkbox):
                        if(checkedpdf):
                            pdfHandler.setPdfFile(pdfFolderPath+pdfFiles[index])
                            pdfHandler.structurePDF('local_file')
                            full_text=pdfHandler.getFilteredText()
                        
                            text_chunks = get_text_chunks(full_text)
                            
                            # vectorstore = get_vectorstore(text_chunks)
                            # query="summarize"
                            # response=qa(vectorstore,llm,query)
                            # print(response)
                    
                            # streamlit.session_state.conversation = get_conversation_chain(
                            # vectorstore,llm)
                            streamlit.session_state.full_text=full_text
                            streamlit.session_state.section_text =pdfHandler.getFilteredTextBySection()
                            
                            
                    if(pdf_docs):
                        pdfHandler.setStreamData(pdf_docs)
                        pdfHandler.structurePDF('stream')
                        streamlit.session_state.full_text=full_text=pdfHandler.getFilteredText()
                        streamlit.session_state.section_text =pdfHandler.getFilteredTextBySection()
                        
    summarySectionButtonsList=[]
    if(len(summarySectionButtonsList)==0 and  streamlit.session_state.section_text!= None):  
        summarySectionButtonsList.append(streamlit.button('Summarize: ' + 'ALL'))
        for sectionName in streamlit.session_state.section_text:
            summarySectionButtonsList.append(streamlit.button('Summarize: ' + sectionName))
            print(sectionName)
    

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
                
                with response_container:
                    message(summary)
                        
        #summarize the entire text 
        elif summaryButton and i==0:
            with streamlit.spinner("Processing"): 
              
                dict={}
                r_prompt  =  """You will be given a title: {title} and a dictionary: {most_important_sents} that contains section titles as its keys and descriptions of those sections as its values.
           
                Your first goal is to add the title at the top of your response. 
                Your next goal is to deconstruct the dictionary, and place the section titles and elaborate each section's descriptions in bullet points
                SUMMARY :"""
                
                sectionNameList=[]
                for sectionName in streamlit.session_state.section_text:
                    sectionNameList.append(sectionName)
                    
                for i in range(len(streamlit.session_state.section_text)):
                    summarization=Summarization(r_prompt,llm,model_name,10)
                    most_important_sents =summarization.lexRank(streamlit.session_state.section_text[sectionNameList[i]])
                    dict[sectionNameList[i]]=most_important_sents 
                print('done')
                summarization=Summarization(r_prompt,llm,model_name)
                summary=summarization.generateSummary(str(dict),pdfHandler.getTitle())
              
                with response_container:
                    message(summary)
            
  #########################################
if __name__ == '__main__': 
    main()
