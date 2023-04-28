# Business_card_reader

This project is mainly done to get the text data from business cards uploaded by users. It 
was developed with the help of easyOCR library and streamlit. The app allows the user to 
upload the extracted data into the database and also enable to delete them.

### Skills used
- Python - EasyOCR, Regular expression
- Streamlit 
- AWS-RDS

### To run the app locally
1. Either clone the repository or copy the code.
2. Download the sample business cards image in the repository
3. Run the app using the command streamlit run (app_name).py
4. Upload the image you wish to extract data

### Usage of the app
- Extract data in a short time period
- Used to extract details from huge amount of business cards with good accuracy
- Can alternate the code based on the requirement and used in other areas similar 
to extraction of text data from images

### Disadvantages
1. It might give some inaccurate results due to image quality and changes in the 
format of the data extracted.
2. It is also limited to extract contents only in English language.
3. Used only for business cards.