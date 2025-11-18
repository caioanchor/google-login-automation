from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def expand_shadow(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

try:
    print("Enter the gmailid and password")
    gmailId, passWord = map(str, input().split())

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    wait = WebDriverWait(driver, 20)

    driver.get("https://accounts.google.com/")

    # --- EMAIL ---
    email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
    email_input.send_keys(gmailId)

    driver.find_element(By.ID, "identifierNext").click()

    # --- SENHA ---
    # Espera a senha
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, "Passwd"))
    )
    password_input.send_keys(passWord)

    # Espera a div que contém o botão
    password_next_div = wait.until(
        EC.presence_of_element_located((By.ID, "passwordNext"))
    )

    # Clica com JavaScript dentro da div
    driver.execute_script("arguments[0].click();", password_next_div)

    print('Login Successful...!!')

except:
    print('Login Failed')