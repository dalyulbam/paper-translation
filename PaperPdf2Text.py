# from pypdf import * 
import openai 
import pdfplumber 
from pdfplumber.utils import cluster_objects

from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askdirectory
import os, glob 

import threading # you cant' waste your time until the answer comes ! 

##################################################################
# adjustment 

TOLERANCE_X = 2
TOLERANCE_Y = 4
LINE_SPACE_RATE = 1.4 
LINE_INDENT_COL = 80 
openai_use_cnt = 0 
USE_OPENAI = True 

import time 

##################################################################

def selectFolder():
    Tk().withdraw()
    try: 
        folder_name = askdirectory(initialdir='.') 
        if not folder_name : 
            raise Exception("NoDirectoryError")
    except:
        print("Folder Open Error")
        return  
    return folder_name    

def selectFiles():
    Tk().withdraw()
    try: 
        file_names = askopenfilenames(initialdir='.') 
        if not file_names : 
            raise Exception("NoFileError")
    except:
        print("Folder Open Error")
        return  
    return file_names  

SCRIPT_DIR = current_path = os.getcwd()

##################################################################
# Specify the Text to be translated, source language (English) and target language (Korean)

def trnsltOpenAI(tgt_text):
    
    # dalyulbam API Key 
    openai.api_key='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'

    # Use the OpenAI API to translate the text
    try: 
        response = openai.chat.completions.create(
            model= 'gpt-4o', 
            messages= [{'role' : 'user', 
                        'content' : f"please translate the senstences into Korean below and do not write down except the translation. \n{tgt_text}\n" }], 
            temperature= 0,
        )
    except Exception as e:
        print(e) 
        print("hard to translate -> " + tgt_text)
        return "\n"

    # response = openai.completions.create(
    #     # Specify the engine (e.g., davinci-codex)
    #     model="ada-search-document",

    #     # The prompt to complete.
    #     prompt= f"please translate the senstences into Korean below and do not write down except the translation. \n{tgt_text}\n",

    # )

    # Extract the translated text from the API response
    #print(response)
    print(response.choices[0].message.content)
    return response.choices[0].message.content
    # print(response.choices[0].text.strip())
    # return response.choices[0].text.strip()

def save_txt_safe(file_name, trnslt_text):
    if os.path.isfile(file_name):
        with open(file_name , 'a', encoding='utf-8') as txt_file:
            txt_file.write(trnslt_text)
    else : 
        with open(file_name , 'w', encoding='utf-8') as txt_file:
            txt_file.write(trnslt_text)

def massiveTrnslt(text_list, file_name):

    final_file_name = SCRIPT_DIR + '\\' + '_' + file_name + '.txt'
    for _, text in enumerate(text_list):
        time_bef = time.time()
        response = trnsltOpenAI(text) + '\n\n'
        print("OpenAI API spend : " + str(time_bef - time.time()) + "(sec) time")
        save_txt_safe(final_file_name, response)


##################################################################
pdf_list = selectFiles()
for single_pdf in pdf_list: 
    thread_list = []
    with pdfplumber.open(single_pdf) as pdf: 
        new_text_list = [""]; new_pdf_indent_rate = []; new_idx = 0
        page_cnt = len(pdf.pages)
        file_name = single_pdf.split('/')[-1].split('.')[0]

        for page_num in range(page_cnt):
            single_page = pdf.pages[page_num]
            text_list = single_page.extract_text_lines(layout=True, use_text_flow=True, x_tolerance=TOLERANCE_X, y_tolerance=TOLERANCE_Y, keep_blank_chars=False)

            # if x0 corner of next line is suddenly moved x direction (1) or the x0 corner distance is too far from each other, 
            # slice the contents and save it into another list             
            for idx, line in enumerate(text_list):
                try: 
                    if idx != 0 : 
                        idx_former = idx - 1 
                        y0_former = text_list[idx_former]["top"]; y1_former = text_list[idx_former]["bottom"] ; y0_now = text_list[idx]["top"]  
                        x0_former = text_list[idx_former]["x0"]; x0_now = text_list[idx]["x0"]
                        if (y0_now - y0_former > (y1_former - y0_former)*(LINE_SPACE_RATE)) or (x0_now - x0_former > LINE_INDENT_COL):
                            new_pdf_indent_rate.append((y0_now - y0_former)/(y1_former - y0_former))
                            new_idx += 1 
                            new_text_list.append("") 
                except Exception as e:
                    print(e)
                    print("error line : ", line) 
                new_text_list[new_idx] += ('\n' + line["text"])
        
        if (USE_OPENAI):
            massiveTrnslt(new_text_list, file_name)

        else : 
            final_file_name = SCRIPT_DIR + '\\' + '_' + file_name + '_original.txt'
            tot_text = '\n\n'.join(new_text_list) 
            save_txt_safe(final_file_name, tot_text)


        # msg = "Connecting the OpenAI API and sending questions..."
        # th = threading.Thread(target = massiveTrnslt, name="[Daemon]", args=(new_text_list,single_pdf.split('/')[-1].split('.')[0], openai_use_cnt))
        # th.start()
        # thread_list.append(th)
    
    # for th in thread_list:z
    #     th.join()
        

##################################################################

