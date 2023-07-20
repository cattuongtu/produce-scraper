import time, re, os, ssl, smtplib
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from email.message import EmailMessage

MAX_PRICE = 2500

def find_first_dollar_amount(input_string):
    # Define the regex pattern to match the dollar amount format
    pattern = r'\$([0-9,]+)'

    # Search for the pattern in the input_string
    match = re.search(pattern, input_string)

    # If a match is found, extract and return the dollar amount
    if match:
        dollar_amount = match.group(1)
        # Remove commas from the dollar amount before returning
        return int(dollar_amount.replace(',', ''))
    else:
        # If no match is found, return None or raise an exception, depending on your use case.
        return None
    
def send_email(email_text):
    # Setup SMTP server and send email notifications
    email_sender = "cattuongtu39@gmail.com"
    email_password = "firipfncydsrwygu"
    email_receiver = "cattuongtu3@gmail.com"

    subject = 'Apartment Price Alert'
    body = """
    Apartment prices for Santa Fe Ranch dropped!
    Prices Below:

    """ + email_text

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

# All prices under the max score
prices = []
# the following options are only for setup purposes
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

URL = "https://www.santaferanchapthomes.com/floorplans/1x1-renovated"

driver.get(URL)
time.sleep(7)  # any number > 3 should work fine
html = driver.page_source
f = open("index.html", "w")
f.write(html)
f.close()


# Grab all rent cards and see if any of them drop under $2500
with open("index.html") as fp:
    soup = BeautifulSoup(fp, "html.parser")
email_text = ""
for tag in soup.find_all('td', class_="td-card-rent"):
    amount = find_first_dollar_amount(tag.text)
    if amount < MAX_PRICE:
        email_text = email_text + "Apartment found for ${}!\n".format(amount)

send_email(email_text)
        



