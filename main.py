import os
import sys
import ssl
import smtplib
from time import sleep
from dotenv import load_dotenv
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

debug = 0   # 0 bedeutet headless; 1 nur für debug nutzen!

# Load .env
if os.path.exists('settings.env'):
    load_dotenv('settings.env')
    uni_login_name = os.getenv('UNI_LOGIN_NAME')
    uni_login_password = os.getenv('UNI_LOGIN_PASSWORD')
    sender_email_host = os.getenv('SENDER_EMAIL_HOST')
    sender_email_port = os.getenv('SENDER_EMAIL_PORT')
    sender_email_address = os.getenv('SENDER_EMAIL_ADDRESS')
    sender_login_name = os.getenv('SENDER_EMAIL_LOGIN_NAME')
    sender_password = os.getenv('SENDER_EMAIL_PASSWORD')
    receiver_email_address = os.getenv('RECEIVER_EMAIL_ADDRESS')
    refresh_interval = os.getenv('REFRESH_INTERVAL')
    print("settings.env wurde gefunden und geladen.")
    print("Um eine andere Konfiguration zu benutzen bitte settings.env loeschen.")
else:
    print("Es wurde keine Konfiguration gefunden.")
    while True:
        uni_login_name = input("Bitte FernUni Login NAME eingeben (z.B.: q123456789): ")
        if uni_login_name:
            break
    
    while True:
        uni_login_password = input("Bitte FernUni Login PASSWORT eingeben (z.B.: hunter2): ")
        if uni_login_password:
            break
    
    while True:
        sender_email_host = input("Bitte Sender E-Mail HOST eingeben (z.B.: smtp.fernuni-hagen.de): ")
        if sender_email_host:
            break
    
    while True:
        sender_email_port = input("Bitte Sender SMTP PORT eingeben (Eingabetaste/Enter fuer Standardport 587): ")
        if sender_email_port == "":
            sender_email_port = 587
        try:
            sender_email_port = int(sender_email_port)
            break
        except ValueError:
            pass
    
    while True:
        sender_email_address = input("Bitte Sender E-Mail-Adresse eingeben (z.B.: ex.ample@fernuni-hagen.de): ")
        if sender_email_address:
            break
        
    while True:
        sender_login_name = input("Bitte Sender Login NAME eingeben (z.B.: ex.ample): ")
        if sender_login_name:
            break
        
    while True:
        sender_password = input("Bitte Sender Login PASSWORT eingeben (z.B.: hunter2): ")
        if sender_password:
            break

    receiver_email_address = input(f"Bitte Empfaenger E-Mail-Adresse eingeben (Eingabetaste/Enter fuer {sender_email_address}): ")
    receiver_email_address = receiver_email_address if receiver_email_address else sender_email_address
    
    while True:
        refresh_interval = input("Bitte Aktualisierungsfrequenz in MINUTEN eingeben (Mindestens 10): ")
        try:
            refresh_interval = int(refresh_interval)
            if refresh_interval >= 10:
                break
        except ValueError:
            pass

    # Create or open the settings.env file for writing
    with open('settings.env', 'w') as env_file:
        env_file.write(f'UNI_LOGIN_NAME={uni_login_name}\n')
        env_file.write(f'UNI_LOGIN_PASSWORD={uni_login_password}\n')
        env_file.write(f'SENDER_EMAIL_HOST={sender_email_host}\n')
        env_file.write(f'SENDER_EMAIL_PORT={sender_email_port}\n')
        env_file.write(f'SENDER_EMAIL_ADDRESS={sender_email_address}\n')
        env_file.write(f'SENDER_EMAIL_LOGIN_NAME={sender_login_name}\n')
        env_file.write(f'SENDER_EMAIL_PASSWORD={sender_password}\n')
        env_file.write(f'RECEIVER_EMAIL_ADDRESS={receiver_email_address}\n')
        env_file.write(f'REFRESH_INTERVAL={refresh_interval}\n')

    print("Konfiguration wurde als 'settings.env' abgespeichert.")

chrome_options = Options()
if not debug:
    chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Attempt to create a WebDriver Chrome -> Chromium -> Firefox -> Safary -> Opera
webdriver_created = False
try:
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    webdriver_created = True
except Exception as e_chrome:
    pass

if not webdriver_created:
    try:
        driver = webdriver.Chrome(options=chrome_options)
        webdriver_created = True
    except Exception as e_chromium:
        pass

if not webdriver_created:
    try:
        driver = webdriver.Firefox(options=chrome_options)
        webdriver_created = True
    except Exception as e_firefox:
        pass

if not webdriver_created:
    try:
        driver = webdriver.Safari(options=chrome_options)
        webdriver_created = True
    except Exception as e_safari:
        pass

if not webdriver_created:
    try:
        driver = webdriver.Opera(options=chrome_options)
        webdriver_created = True
    except Exception as e_opera:
        pass

if not webdriver_created:
    print("Bitte Chrome/Firefox/Safari/Opera installieren.")
    sys.exit(0)

driver.get("https://pos.fernuni-hagen.de/qisserver/rds?state=user&type=0&category=auth.logout") # die FU-POS Seite
elem = driver.find_element_by_id("loginForm:login")
user = driver.find_element_by_id("asdf")
pwd = driver.find_element_by_id("fdsa")
user.send_keys(uni_login_name)
pwd.send_keys(uni_login_password)
elem.click()
print("Loggin in...")
verwaltung = driver.find_element_by_xpath("/html/body/div/div[5]/div[1]/ul/li/a")
verwaltung.click()
notenuebersicht = driver.find_element_by_xpath("/html/body/div/div[5]/div[2]/div/form/div/ul/li[3]/a")
notenuebersicht.click()
Leistungen = driver.find_element_by_xpath("/html/body/div/div[5]/div[2]/form/ul/li/a[1]/img")
Leistungen.click()
leistungstabelle = "/html/body/div/div[5]/div[2]/form/table[2]"
tabelle = driver.find_element_by_xpath(leistungstabelle).text
print("starting the idle")

refresh_interval = int(refresh_interval) * 60
while(True):
    if tabelle == driver.find_element_by_xpath(leistungstabelle).text:
        sleep(refresh_interval)
        driver.refresh()
        print("Refreshing")
    else:
        tabelle = driver.find_element_by_xpath(leistungstabelle).text
        if sender_email_port in ["25", "587"]:
            smtpObject = smtplib.SMTP(host=sender_email_host, port=sender_email_port)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            smtpObject.ehlo()
            smtpObject.starttls(context=context)
            smtpObject.ehlo()
        else:
            smtpObject = smtplib.SMTP_SSL(host=sender_email_host, port=sender_email_port)
        smtpObject.login(sender_login_name, sender_password)

        try:
            msg = MIMEText(
                'Es sind Noten in der Tabelle hinzugefügt worden \n \n https://pos.fernuni-hagen.de/qisserver/rds?state=user&type=0&topitem= \n \n '+ tabelle)
            msg['Subject'] = 'Neue Noten bei der Fernuni'
            msg['From'] = sender_email_address
            msg['To'] = receiver_email_address
            smtpObject.sendmail(sender_email_address, receiver_email_address, msg.as_string())
            print('Successfully sent email')
        except smtplib.SMTPException:
            print("Error: unable to send email")
            driver.close()
            sys.exit(0)