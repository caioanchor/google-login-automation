from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

# Configura caminhos absolutos baseados na localização do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ALVO = os.path.join(BASE_DIR, "captura.txt")

print(f"[Selenium] Iniciado PID: {os.getpid()} | User ID: {os.getuid()}")
print("[Selenium] Aguardando arquivo de credenciais...")

email = ""
senha = ""

while True:
    if os.path.exists(ARQUIVO_ALVO):
        try:
            # Tenta ler com permissão de leitura/escrita
            with open(ARQUIVO_ALVO, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if content and " " in content:
                parts = content.split(" ", 1)
                if len(parts) == 2:
                    temp_email, temp_senha = parts
                    if len(temp_email) > 3:
                        email = temp_email
                        senha = temp_senha
                        print(f"[Selenium] Credenciais recebidas: {email}")
                        try:
                            os.remove(ARQUIVO_ALVO)
                        except OSError as e:
                            print(f"[Selenium] Aviso: Não consegui deletar arquivo (permissão?): {e}")
                        break
            time.sleep(1)
        except Exception as e:
            print(f"[Selenium] Erro de leitura (tentando novamente): {e}")
            time.sleep(1)
    else:
        time.sleep(0.5)

# Configuração do Browser
try:
    options = Options()
    # options.add_argument("--headless") # Descomente se não quiser ver o browser abrindo
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    print(f"[Selenium] Acessando site para login: {email}")
    driver.get("https://accounts.google.com/")  # URL do seu laboratório

    # --- EMAIL ---
    print("[Selenium] Preenchendo Email...")
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "identifierId")))
    email_input.clear()
    email_input.send_keys(email)

    driver.find_element(By.ID, "identifierNext").click()

    # --- SENHA ---
    print("[Selenium] Aguardando campo de senha...")
    # O wait aqui é crucial pois a transição do Google/Login tem animação
    password_input = wait.until(
        EC.visibility_of_element_located((By.NAME, "Passwd"))
    )
    password_input.clear()
    password_input.send_keys(senha)

    # Clicar no botão de login
    password_next = wait.until(
        EC.element_to_be_clickable((By.ID, "passwordNext"))
    )
    driver.execute_script("arguments[0].click();", password_next)

    # Verificação básica de sucesso (opcional: esperar URL mudar ou elemento da home)
    time.sleep(5)
    print('[Selenium] Tentativa finalizada. Verifique o browser.')

    # Mantém aberto por um tempo para ver o resultado
    # driver.quit()

except Exception as e:
    print(f'[Selenium] Falha Crítica: {e}')
    # Garante limpeza em caso de erro
    if os.path.exists(ARQUIVO_ALVO):
        os.remove(ARQUIVO_ALVO)