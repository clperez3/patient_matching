#given pdf, extract [last, first, dob, doctype]
import re
from datetime import date

import pdf2image
import pytesseract
from pytesseract import Output, TesseractError


#takes pdf and returns [dob, doctype, today's date, is_flagged]
def extract_info(filename):
    is_flagged = False
    imgs = pdf2image.convert_from_path(filename)
    ocr_dict = pytesseract.image_to_data(imgs[0], lang='eng', output_type=Output.DICT)

    text = " ".join(ocr_dict['text']).lower()
    if (text == None):
        return []
    #assuming mm/dd/yyyy format
    matches = re.findall(r'(\d\d+/\d\d+/\d\d+)',text)

    #extract dob as oldest found date in doc
    dob = date.today()
    for d in matches:
        year = str(d[6:11])
        month = d[0:2]
        day = d[3:5]
        if len(year)<4:
            year = "20"+str(year)
            if len(year)<4:
                year = "0000"
        try:
            d = date.fromisoformat( year + "-" + month + "-" + day)
        except:
            #flag for review
            is_flagged = True
            d = dob
        if d<dob:
            dob=d
    
    doc_type = "other"
    kws={"test result", "lab"}
    for kw in kws:
        if (text.count(kw)>0):
            doc_type= "LAB RESULTS"
            break

    kws={"consult", "visit"}
    for kw in kws:
        if (text.count(kw)>0):
            doc_type= "CONSULT"
            break
    kws={"radio"}
    for kw in kws:
        if (text.count(kw)>0):
            doc_type= "RADIOLOGY"
            break
    kws={"hospital"}
    for kw in kws:
        if (text.count(kw)>0):
            doc_type= "HOSPITAL"
            break

    return[filename, dob, doc_type, date.today(), is_flagged]


#assumes path is text file with listed pdf file names
#returns list of info for each corresponding pdf file
def filenames_to_fileinfo(path):
    to_return = list()
    files = list()
    with open(path, 'r') as io:
        for line in io:
            if(line.endswith('.pdf\n') or line.endswith('.pdf')):
                files.append(line.strip('\n'))
    for file in files:
        to_return.append(extract_info(file))
    return to_return




