import easyocr as ocr
import streamlit as st
from PIL import Image
import numpy as np
import re
import pymysql
import pandas as pd
import io
import Levenshtein

st.set_page_config(layout='wide')


# Getting Secrets from Streamlit Secret File
username = st.secrets['aws_rds_username']
password = st.secrets['aws_rds_password']
Endpoint = st.secrets['endpoint']
Db = st.secrets['database']
# Connect to AWS-RDS-MYSQL
connection = pymysql.connect(
    host=Endpoint,
    user=username,
    password=password,
    db=Db
)

cursor = connection.cursor()
# def format_title(title: str):
#     """
#     Formats the given title with a colored box and padding
#     """
#     frm_title = f"<div style='padding:10px;background-color:rgb(230, 0, 172, 0.1);
#                   border-radius:5px'><h1 style='color:rgb(204, 0, 153);text-align:center;'>{title}</h1></div>"
#     return frm_title
#
#
# Use the function to format your title
# st.markdown(format_title("UNLOCKING DATA FROM BUSINESS CARDS USING OCR"), unsafe_allow_html=True)

st.header(":green[Extracting data from Business card]")

st.write("")
st.write("")
with st.container():
    file = st.file_uploader("Upload image file", type=['png', 'jpg', 'jpeg'])


@st.cache_data
def model():
    img_reader = ocr.Reader(['en'])
    return img_reader


reader = model()
if file is not None:
    inp_img = Image.open(file)

    c1, c2 = st.columns([6, 6])
    with c1:
        st.image(inp_img)

    content = reader.readtext(np.array(inp_img), adjust_contrast=2)
    data = []
    for text in content:
        data.append(text[1])
    # print(data)

    phone = []
    address = []
    street = ''
    state = ''
    email = ''
    pincode = ''
    website = set()
    designation = ''
    company_details = []
    add_str = []
    add1 = ''
    add2 = ''

    for i, string in enumerate(data):
        if re.search(r'@', string.lower()):
            email = string.lower()

        match = re.search(r'\d{6,7}', string.lower())
        if match:
            pincode = match.group()

        # match = re.search(r'(?:ph|phone|phno)?\s*(?:[+-]?\d-*[\(\)]*){7,11}', string)
        match = re.search(r'^[+\-]?\d{2,3}-\d{3}-\d{3}', string)
        if match:
            phone.append(string)

        if re.search(r'\d+\s\w+$', string):
            add1 = string.lstrip()

        if re.search(r'\w+\s\,', string):
            add2 = string
            # street = add1 + ' ' + add2

        if re.search(r'\w+\,', string):
            address.append(string)

        if re.search(r'\bwww\b', string.lower()):
            website.add(string.lower())

        if re.search(r'^\w*\.com$|\.in$|\.net$', string.lower()):
            website.add(string.lower())

        states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
                  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
                  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'TamilNadu',
                  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']


        def string_similarity(s1, s2):
            distance = Levenshtein.distance(s1, s2)
            similarity = 1 - (distance / max(len(s1), len(s2)))
            return similarity * 100


        for x in states:
            score = string_similarity(x.lower(), string.lower())
            if score > 50:
                state = string
                address.append(string)

        # post = ['Chief Executive Officer', 'COO', 'Founder', 'HR Executive', 'General Manager',
        #         'Marketing Executive', 'Data Manager', 'Technical Manager']
        #
        # for x in post:
        #     score = string_similarity(x.lower(), string.lower())
        #     if score > 50:
        #         designation = string
    street = add1 + ' ' + add2 + ' '
    add_str.append(street)
    # print(add_str)

    with c2:
        st.write("#### Extracted text")
        for i, string in enumerate(data):
            if len(string) >= 4 and ',' not in string and '.' not in string and 'www' not in string.lower():
                if not re.match("^[0-9]{0,3}$", string) and not re.match("^[^a-zA-Z0-9]+$", string):
                    numbers = re.findall('\d', string)
                    print(numbers)
                    # if len(numbers) == 0 or all(len(num) < 3 for num in numbers) and not any(
                    #         num in string for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']*3):
                    if len(numbers) == 0 or all(len(num) < 3 for num in numbers) and not any(
                            num in string for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                        company_details.append(string)
        st.write("##### <span style='color:#AD18E8;'>Name:</span>", company_details[0], unsafe_allow_html=True)
        st.write("##### <span style='color:#AD18E8;'>Designation:</span>", company_details[1], unsafe_allow_html=True)
        if len(company_details) > 3:
            c = company_details[2] + ' ' + company_details[3]
        else:
            c = company_details[2]
        st.write("##### <span style='color:#AD18E8;'>Company name:</span>", c, unsafe_allow_html=True)

        if street not in address:
            add_st = street + ' '.join([str(elem) for elem in address])
        elif add_str not in address:
            add_st = ' '.join([str(elem) for elem in address])
        else:
            add_st = add_str + state

        st.write('##### :blue[Address: ] ', add_st)
        st.write('##### :blue[Pincode: ] ' + str(pincode))
        web = '.'.join([str(elem) for elem in website])
        st.write('##### :yellow[Website: ] ', web)
        # st.write('##### :blue[Website: ] ' + str(website))
        st.write('##### :blue[Email: ] ' + str(email))
        ph_str = ', '.join(phone)
        st.write('##### :blue[Phone Number(S): ] ' + ph_str)

        # print(address)

UP = st.button('UPLOAD')

for i, string in enumerate(data):
    if len(string) >= 4 and ',' not in string and '.' not in string and 'www' not in string.lower():
        if not re.match("^[0-9]{0,3}$", string) and not re.match("^[^a-zA-Z0-9]+$", string):
            numbers = re.findall('\d', string)
            print(numbers)
            # if len(numbers) == 0 or all(len(num) < 3 for num in numbers) and not any(
            #         num in string for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']*3):
            if len(numbers) == 0 or all(len(num) < 3 for num in numbers) and not any(
                    num in string for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                company_details.append(string)
Name = str(company_details[0])
Designation = str(company_details[1])
if len(company_details) > 3:
    c = company_details[2] + ' ' + company_details[3]
else:
    c = company_details[2]
Company_name = str(c)
Website = str(web)
Email = str(email)
Pincode = str(pincode)
Phone_no = ph_str
Address = add_st
file.seek(0)
image_data = file.read()

if UP:
    if file is not None:
        data = (Name, Designation, Company_name, Website, Email, Pincode, Phone_no, Address, image_data)
        sql = "INSERT INTO CARD (Name, Designation, Company_name, Website, Email, Pincode, Phone_no, Address, card) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, data)
        connection.commit()
    else:
        st.write('Upload business card in the file upload')
st.write(' ')
st.write(' ')
st.write(' ')
st.write('### Data in Business card')

query = "SELECT * FROM CARD"
dataframe = pd.read_sql(query, connection)
st.dataframe(dataframe)

c3, c4 = st.columns([6, 6])
with c3:
    st.write(' ')
    st.write("#### BUSINESS CARDS AVAILABLE IN DATABASE")
    cursor.execute("SELECT id FROM CARD")
    rows = cursor.fetchall()
    l = []
    # DISPLAY ALL THE CARDS AS BUTTONS
    for row in rows:
        l.append(row[0])
        button_label = f"SHOW BUSINESS CARD: {row[0]}"
        if st.button(button_label):
            cursor.execute("SELECT * FROM CARD WHERE id ="+str(row[0]))
            row1 = cursor.fetchone()
            name = row1[1]
            designation = row1[2]
            company = row1[3]
            website_url = row1[4]
            email = row1[5]
            pin_code = row1[6]
            phone_numbers = row1[7]
            address = row1[8]

            # DISPLAY SELECTED CARD DETAILS
            with c3:
                st.write(f"#### BUSINESS CARD {row[0]} DETAILS ")
                st.write(f"Website: {name}")
                st.write(f"Website: {designation}")
                st.write(f"Website: {company}")
                st.write(f"Website: {website_url}")
                st.write(f"Email: {email}")
                st.write(f"PIN Code: {pin_code}")
                st.write(f"Phone Numbers: {phone_numbers}")
                st.write(f"Address: {address}")

                # If the button is clicked, display the corresponding row
                cursor.execute("SELECT card FROM CARD WHERE id ="+str(row[0]))
                r = cursor.fetchone()
                if r is not None:
                    image_data = r[0]
                    image = Image.open(io.BytesIO(image_data))
                    st.image(image)
                st.write(' ')

# DELETE MULTIPLE ENTRIES
with c4:
    st.write(' ')
    st.write(f"#### SELECT ENTRIES TO DELETE")
    selected_options = st.multiselect('', l)

    if st.button('DELETE SELECTED ENTRIES'):
        for option in selected_options:
            cursor.execute("DELETE FROM CARD WHERE id = " +str(option))
        connection.commit()
        st.write("DELETED SELECTED BUSINESS CARD ENTRIES SUCCESSFULLY")
    st.write(' ')