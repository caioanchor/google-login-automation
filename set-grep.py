import os
import time
import glob
import threading

DIR_RELATORIOS = "/root/.set/reports"


def ler_arquivo_em_tempo_real(caminho):
    """
    Leitura contínua (tail -f).
    Captura apenas EMAIL= e PASSWD=
    """
    print(f"[+] Monitorando arquivo: {caminho}")

    try:
        with open(caminho, "r", errors="ignore") as f:
            f.seek(0, os.SEEK_END)  # Vai para o fim

            while True:
                linha = f.readline()

                if not linha:
                    time.sleep(0.1)
                    continue

                linha = linha.strip()

                # Normaliza para evitar case sensitividade
                lower = linha.lower()

                # ---------------------------------------------------------
                # CAPTURA EMAIL
                # ---------------------------------------------------------
                if "email=" in lower:
                    # Obtém a parte depois do '='
                    valor = linha.split("=", 1)[1]
                    print(f"[EMAIL] {valor}")

                # ---------------------------------------------------------
                # CAPTURA SENHA
                # ---------------------------------------------------------
                if "passwd=" in lower:
                    valor = linha.split("=", 1)[1]
                    print(f"[PASSWD] {valor}")

    except FileNotFoundError:
        pass


def aguardar_arquivo():
    """
    Fica parado até que a pasta tenha pelo menos UM arquivo.
    """
    print("[*] Aguardando arquivos aparecerem em /root/.set/reports ...")

    while True:
        lista = glob.glob(os.path.join(DIR_RELATORIOS, "**/*"), recursive=True)
        lista = [f for f in lista if os.path.isfile(f)]

        if lista:
            print(f"[+] {len(lista)} arquivo(s) encontrado(s). Iniciando monitoramento...")
            return lista

        time.sleep(1)


def monitorar_diretorio():
    """
    Monitora toda a pasta por novos arquivos e começa a ler em tempo real.
    """
    arquivos_monitorados = set()

    # Primeiro espera aparecer arquivos
    arquivos_iniciais = aguardar_arquivo()

    # Começa lendo os existentes
    for arquivo in arquivos_iniciais:
        arquivos_monitorados.add(arquivo)
        threading.Thread(target=ler_arquivo_em_tempo_real, args=(arquivo,), daemon=True).start()

    # Agora monitora por novos arquivos
    while True:
        lista = glob.glob(os.path.join(DIR_RELATORIOS, "**/*"), recursive=True)
        lista = [f for f in lista if os.path.isfile(f)]

        for arquivo in lista:
            if arquivo not in arquivos_monitorados:
                arquivos_monitorados.add(arquivo)
                print(f"[+] Novo arquivo detectado: {arquivo}")
                threading.Thread(target=ler_arquivo_em_tempo_real, args=(arquivo,), daemon=True).start()

        time.sleep(1)


def main():
    if not os.path.exists(DIR_RELATORIOS):
        print(f"Diretório não encontrado: {DIR_RELATORIOS}")
        return

    monitorar_diretorio()


if __name__ == "__main__":
    main()
