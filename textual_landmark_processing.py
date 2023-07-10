# -Programmer Name: Gan Qian Chao TP055444
# -Program Name : Textual Landmark Preprocessing (IDFD Textual Landmark Verification)
# -Description : Use for detect textual landmarks such as surname, given_name, id number, birth date. granted date, expired date, area code, detect missing or unmatched details
# -First Written on: 27 March 2023
# -Editted on: 10 April 2023
#import libraries such as google vision to load Google Vision API
import os
import re
from google.protobuf.json_format import MessageToJson
from google.cloud import vision_v1
from google.cloud.vision_v1 import AnnotateImageResponse
from google.cloud import vision
import io
from datetime import datetime
import Levenshtein
#credential key for Google Vision API(replace the credential if error confuse to connect)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "static/ocr/mineral-origin-367413-9c6ca72ec487.json"

#start google vision text ocr on uploaded card
def text_verification(path,include):
    # main_arr=[]
    client = vision.ImageAnnotatorClient()
    with io.open(os.path.join(path), 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.document_text_detection(image=image,image_context={"language_hints": ["fi"]})

    texts = response.text_annotations
    
    #update to capital letter
    include[0] = include[0].upper()
    include[1] = include[1].upper()
    date_indexes = [4, 5, 6]  # the indexes of the date strings in the list
    #update to dd.mm.yyyy
    for index in date_indexes:
        date_string = include[index]
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
        formatted_date = parsed_date.strftime('%d.%m.%Y')
        include[index] = formatted_date
        
    excluded = ['SUOMI','FINLAND','Henkilökortti', 'Identitetskort','Identity','card']
                
    target_regex = "|".join(excluded)
    max_similarity = 0.2
    surname_found = False
    given_name_found = False
    id_num_found = False
    # gender_found = False
    birth_date_found = False
    granted_date_found = False
    expired_date_found = False
    area_code_found = False
    # start_ocr = False
    for text in texts:
        if text == texts[0]:
            content = text.description
            # print("content: ",content)
            #print("line 1: ", content.split('\n')[0])
            for line in content.split('\n'):
                # if re.search(target_regex, line):
                # Calculate the similarity using Levenshtein distance
                similarity = Levenshtein.ratio(line, target_regex)
                # print(similarity)
                #exclude line that is in exclude list
                if similarity > max_similarity:
                    # start_ocr = True
                    continue
                #find surname
                if not surname_found:
                    # print("line:",line)
                    name_regex = re.compile(r"\b([A-Z]|[À-Ü])+\b")
                    if re.search(name_regex,line):
                        for x in re.finditer(name_regex,line):
                            potential_surname = x.group()
                            # print("potential_surname: ", potential_surname)
                            # print(include[0])
                            if  include[0] in potential_surname:
                                surname_found = True
                                continue
                #find given_name                  
                if not given_name_found:                    
                    if re.search(name_regex,line):
                        for x in re.finditer(name_regex,line):
                            potential_given_name = x.group()
                            #print("potential_given_name: ", potential_given_name)
                            #print(include[1])
                            if include[1] in potential_given_name:
                                given_name_found = True
                                continue 
                
                #find birth date                         
                if given_name_found and not birth_date_found:
                    date_regex = re.compile(r'\b(0[1-9]|[1-2]\d|3[0-1])\s?\.\s?(0[1-9]|1[0-2])\s?\.\s?\d{4}\b')                  
                    if re.search(date_regex,line):
                        for x in re.finditer(date_regex,line):
                            potential_date = x.group()
                            # print("potential_date: ", potential_date)
                            # print(include[4])
                            potential_date = potential_date.replace(" ","")
                            if include[4] in potential_date:
                                birth_date_found = True                                                  
                    #find area code
                    if birth_date_found and not area_code_found:
                        area_code_regex = re.compile(r'[A-Z-]?\d{3}[A-Z\d]?')
                        potential_code = re.findall(area_code_regex,line) 
                        # print("potential_code: ", potential_code)
                        for code in potential_code:
                            if include[7] in code:
                                area_code_found = True
                                continue
                                
                #find granted date
                if birth_date_found and not granted_date_found:
                    if re.search(date_regex,line):
                        for x in re.finditer(date_regex,line):
                            potential_date = x.group()
                            #print("potential_date: ", potential_date)
                            #print(include[5])
                            potential_date = potential_date.replace(" ","")
                            if include[5] in potential_date:
                                granted_date_found = True
                                continue  
                            
                #find expired date
                if granted_date_found and not expired_date_found:
                    if re.search(date_regex,line):
                        for x in re.finditer(date_regex,line):
                            potential_date = x.group()
                            # print("potential_date: ", potential_date)
                            # print(include[6])
                            potential_date = potential_date.replace(" ","")
                            if potential_date == include[6]:
                                expired_date_found = True
                                continue   
                                
                #find id_num
                if expired_date_found and not id_num_found:
                    id_num_regex = re.compile(r'\b.*\d{9}.*\b')
                    if re.search(id_num_regex,line):
                        for x in re.finditer(id_num_regex,line):
                            potential_id = x.group()
                            # print("potential_date: ", potential_id)
                            # print(include[2])
                            if include[2] in potential_id:
                                id_num_found = True
                                continue           
                        
            print("surname: ",surname_found)
            print("given_name:", given_name_found)
            print("birth_date:", birth_date_found)      
            print("granted_date:", granted_date_found)  
            print("expired_date:", expired_date_found)    
            print("area_code: ", area_code_found)  
            print("id num: ", id_num_found)
                
    return surname_found, given_name_found, id_num_found, birth_date_found, granted_date_found, expired_date_found, area_code_found
