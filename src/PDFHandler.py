
# https://developer.adobe.com/document-services/docs/overview/pdf-extract-api/quickstarts/python/
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import (
    ServiceApiException,
    ServiceUsageException,
    SdkException,
)
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import (
    ExtractPDFOptions,
)
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import (
    ExtractElementType,
)
import os.path
import zipfile
import json
import logging
from dotenv import load_dotenv
import re
from PyPDF2 import PdfReader
from shutil import move
import shutil


class PDFHandler:

    def __init__(self, zipFileName=None,inputPDFName=None) -> None:
        load_dotenv()
        self.input_pdf = inputPDFName
        self.zip_file = zipFileName
        self.startingSection = "intro"
        self.streamData=''
        
    def setPdfFile(self,inputPDFName):
        self.input_pdf=inputPDFName
    
    def setStreamData(self,data):
        self.streamData=data
        
    def structurePDF(self,type):
        
        print(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
        
    
        if os.path.isfile(os.getcwd()+"/tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip"):
            os.remove(os.getcwd()+"/tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip")

        if os.path.isfile(os.getcwd()+"tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip"):
            os.remove(os.getcwd()+"tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip")
        
       
        if os.path.isfile(os.getcwd()+ self.zip_file):
                os.remove(os.getcwd()+ self.zip_file)
                

        try:
            credentials = (
                Credentials.service_principal_credentials_builder()
                .with_client_id(os.getenv("PDF_SERVICES_CLIENT_ID"))
                .with_client_secret(os.getenv("PDF_SERVICES_CLIENT_SECRET"))
                .build()
            )
            execution_context = ExecutionContext.create(credentials)
            extract_pdf_operation = ExtractPDFOperation.create_new()
            source=None
            if type=='stream':
                source = FileRef.create_from_stream(self.streamData, self.streamData.type)
              
            elif type=='local_file':
                source = FileRef.create_from_local_file(self.input_pdf)

            extract_pdf_operation.set_input(source)
            extract_pdf_options: ExtractPDFOptions = (
                ExtractPDFOptions.builder()
                .with_element_to_extract(ExtractElementType.TEXT)
                .build()
            )
            extract_pdf_operation.set_options(extract_pdf_options)
            result: FileRef = extract_pdf_operation.execute(execution_context)
            print( )
             #windows
            if os.name == 'nt':
                result.save_as("tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip")
                shutil.copy2("tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip", os.getcwd()+ self.zip_file)
            else: 
                result.save_as("/tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip")
                shutil.copy2("/tmp/sdk_result/4b0868b22fcc11ee8830de912ef49a28.zip", os.getcwd()+ self.zip_file)
            


        except (ServiceApiException, ServiceUsageException, SdkException):
            logging.exception("Exception encountered while executing operation")

            
    def getStructuredData(self):
        archive = zipfile.ZipFile(os.getcwd()+ self.zip_file, "r")
        jsonentry = archive.open("structuredData.json")
        jsondata = jsonentry.read()
        structuredData = json.loads(jsondata)
        return structuredData
    def getSections(self):
        structuredData = self.getStructuredData()
        
        H1_sections = {}
        sections = {}
        startIndex = 0
        endIndex = 0
        sectionsIndex = []
        sectionHList=['/H1','/H2']
        startFormat=''
        endFormat=''
        
        ###################PDF Section detection is impossible########
        for sectionH in sectionHList:
            for index, element in enumerate(structuredData["elements"]):
                    if sectionH in element["Path"]:
                            sectionName = re.sub(r"\d+", "", element["Text"].lower().strip())
                            if 'intro' in sectionName:
                                startIndex = index
                                startFormat=sectionH
                            elif ("acknowledg" in sectionName or "reference" in sectionName) :
                                endIndex = index
                                endFormat=sectionH
                                break
            if(startIndex!=0 and endIndex!=0):
                break
                
        for index, element in enumerate(structuredData["elements"]):  
            if startFormat in element["Path"]:
                sectionName = re.sub(r"\d+", "", element["Text"].lower().strip())
                H1_sections[index] = element["Text"] 
                    
            if startFormat!=endFormat:  
                if(index==endIndex):
                    H1_sections[endIndex] = element["Text"] 
                    

        for H1_sectionIndex in H1_sections:
            if H1_sectionIndex >= startIndex and H1_sectionIndex <= endIndex:
                sections[H1_sectionIndex] = H1_sections[H1_sectionIndex]
        
        for index in sections:
            sectionsIndex.append(index)
    
       
        return sections,sectionsIndex
        

    def getFilteredTextBySection(self) :
        sections, sectionsIndex = self.getSections()
        structuredData = self.getStructuredData()
        sectionText = {}
        for x in range(len(sectionsIndex) - 1):
            text = ""

            for raw_index, element in enumerate(structuredData["elements"]):
                if "P" in element["Path"]:
                    if raw_index >= sectionsIndex[x] and raw_index < sectionsIndex[x + 1]:
                        text += element["Text"]

            sectionName = sections[sectionsIndex[x]]
            sectionText[sectionName] = text
        return sectionText
    
    def getFilteredText(self) :
        structuredData = self.getStructuredData()
        sections,sectionsIndex = self.getSections()
        fullText=''
        
        for index, element in enumerate(structuredData["elements"]):
            if "Title" in element["Path"]:
                    fullText +='Title:'+ element["Text"]
                
            if "P" in element["Path"]in element["Path"]:
                if index >= sectionsIndex[0] and index < sectionsIndex[-1]:
                    fullText += element["Text"]
        return fullText
        
    
    def getUnfilteredText(pdf):
        text = ""
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def getTitle(self):
        structuredData = self.getStructuredData()
        for element in structuredData["elements"]:
                if "Title" in element["Path"]:
                    return element["Text"]
                

