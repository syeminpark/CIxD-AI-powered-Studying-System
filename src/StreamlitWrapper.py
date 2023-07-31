import streamlit  #streamlit is the GUI 
from src.htmlTemplates import css, bot_template, user_template
from streamlit_chat import message
from os import listdir
from os.path import isfile, join
from src.config import LLMList
class StreamlitWrapper:
    def __init__(self,args) -> None:
        
        streamlit.set_page_config(page_title=args['page_title'], page_icon=args['page_icon'])
        streamlit.write(css, unsafe_allow_html=True)
        streamlit.header(args['header'])
    
          ##############global variables
        if "conversation" not in streamlit.session_state:
            streamlit.session_state.conversation = None
        if  "chat_history" not in streamlit.session_state:
            streamlit.session_state.chat_history = []
        if  "default_chat" not in streamlit.session_state:
            streamlit.session_state.default_chat = None
        if  "section_text" not in streamlit.session_state:
            streamlit.session_state.section_text = None
        if  "full_text" not in streamlit.session_state:
            streamlit.session_state.full_text = None
        
            
        self.pdf_checkbox=[]
        self.inputContainer = streamlit.container()
        self.responseContainer = streamlit.container()
        self.defaultContainer=streamlit.container()
      
    def resetConversation(self):
        if  "chat_history" in streamlit.session_state:
            streamlit.session_state.chat_history = []
        
          
    def setInputContainer(self,name):
         ##########containers
            #유저가 텍스트 입력할 수 있는 곳 
            with streamlit.form(key='my_form', clear_on_submit=True):
                self.user_input = streamlit.text_area(name, key='input', height=100)
                self.submit_button = streamlit.form_submit_button(label='Send')
   
      
    def setSidebarConfigs(self,args):
        with streamlit.sidebar:
            self.model_name = streamlit.sidebar.radio("Choose a model:", [*LLMList])
            self.uploadedPDF = streamlit.file_uploader(
                    args['fileUploadText'], accept_multiple_files= False,type="pdf") #this just lets us enable this function
            streamlit.subheader(args['subHeaderText'])
            streamlit.caption(args['captionText'])
    
    def handlePDFOperation(self,pdfHandler,qa,llm):
        with streamlit.sidebar:
            pdfFiles = [f for f in listdir('./pdf/') if isfile(join( './pdf/', f))]
            for pdf in pdfFiles:
                self.pdf_checkbox.append(streamlit.checkbox(pdf))
            
            if streamlit.button("SHARE WITH PIXIE"):
                with streamlit.spinner("Pixie is reading..."): 
                    for index, checkedpdf in enumerate(self.pdf_checkbox):
                        if(checkedpdf):
                            pdfHandler.setPdfFile('./pdf/' +pdfFiles[index])
                            pdfHandler.structurePDF('local_file')
                            
                            streamlit.session_state.full_text=pdfHandler.getFilteredText()
                            streamlit.session_state.section_text =pdfHandler.getFilteredTextBySection()
                            
                            text_chunks= qa.get_text_chunks(streamlit.session_state.full_text)
                            vectorstore=qa. get_vectorstore(text_chunks,'intfloat/e5-large-v2')
                            streamlit.session_state.conversation=qa.get_conversation_chain(vectorstore,llm)
                            
                    if(self.uploadedPDF):
                     
                        pdfHandler.setStreamData(self.uploadedPDF)
                        pdfHandler.structurePDF('stream')
                        streamlit.session_state.full_text=pdfHandler.getFilteredText()
                        streamlit.session_state.section_text =pdfHandler.getFilteredTextBySection()
                        
                        text_chunks= qa.get_text_chunks(streamlit.session_state.full_text)
                        vectorstore=qa. get_vectorstore(text_chunks,'intfloat/e5-large-v2')
                        streamlit.session_state.conversation=qa.get_conversation_chain(vectorstore,llm)
                        
    def isFileProcessed(self):
        if streamlit.session_state.section_text != None or  streamlit.session_state.full_text != None:
            return True
        else:
            return False
      
        
    def setMode(self,text, modeOptions,):
        with self.inputContainer:
            self.mode= streamlit.selectbox(text,options=[*modeOptions])
        
        
    def getMode(self):
        return self.mode
    
    def getModelName(self):
        return self.model_name
    
    def getResponseContainer(self):
        return self.responseContainer
    
    def getDefaultContainer(self):
        return self.defaultContainer
    
    def userInput(self):
        
        if self.submit_button and self.user_input:
            return self.user_input
        else:
            return False
    
    