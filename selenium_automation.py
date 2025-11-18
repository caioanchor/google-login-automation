from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def expand_shadow(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

email = ""
senha = ""

try:
    with open("captura.txt", "r", encoding="utf-8") as f:
        linha = f.readline().strip()  # lê a primeira linha
        if linha:
            partes = linha.split(" ", 1)  # separa em 2 partes: email e senha
            email = partes[0]
            senha = partes[1] if len(partes) > 1 else ""
except FileNotFoundError:
    print("Arquivo captura.txt não encontrado.")

try:
    print("Enter the gmailid and password")

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    wait = WebDriverWait(driver, 20)

    driver.get("https://accounts.google.com/")

    # --- EMAIL ---
    email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
    email_input.send_keys(email)

    driver.find_element(By.ID, "identifierNext").click()

    # --- SENHA ---
    # Espera a senha
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, "Passwd"))
    )
    password_input.send_keys(senha)

    # Espera a div que contém o botão
    password_next_div = wait.until(
        EC.presence_of_element_located((By.ID, "passwordNext"))
    )

    # Clica com JavaScript dentro da div
    driver.execute_script("arguments[0].click();", password_next_div)

    print('Login Successful...!!')

except:
    print('Login Failed')