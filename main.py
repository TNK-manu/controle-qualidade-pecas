import sqlite3
import random
from colorama import init, Fore, Style

init(autoreset=True)

NOME_BANCO = "controle_qualidade.db"

# PADRAO DE CORES
def mensagem_sucesso(texto):
    print(Fore.GREEN + texto + Style.RESET_ALL)

def mensagem_erro(texto):
    print(Fore.RED + texto + Style.RESET_ALL)

def mensagem_alerta(texto):
    print(Fore.YELLOW + texto + Style.RESET_ALL)

def mensagem_info(texto):
    print(Fore.CYAN + texto + Style.RESET_ALL)


# BANCO DE DADOS
def conectar_banco():
    return sqlite3.connect(NOME_BANCO)

def criar_tabelas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso REAL NOT NULL,
            cor TEXT NOT NULL,
            comprimento REAL NOT NULL,
            situacao TEXT NOT NULL,
            motivo_reprovacao TEXT,
            numero_caixa INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_caixa INTEGER NOT NULL UNIQUE,
            quantidade_pecas INTEGER NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


# AVALIACAO
def avaliar_peca(peso, cor, comprimento):
    motivos = []

    cor = cor.lower().strip()

    if peso < 95 or peso > 105:
        motivos.append("Peso fora do intervalo permitido (95g a 105g)")

    if cor != "azul" and cor != "verde":
        motivos.append("Cor inválida (somente azul ou verde)")

    if comprimento < 10 or comprimento > 20:
        motivos.append("Comprimento fora do intervalo permitido (10cm a 20cm)")

    if len(motivos) == 0:
        situacao = "Aprovada"
        motivo_reprovacao = ""
    elif len(motivos) == 1:
        situacao = "Reprovada"
        motivo_reprovacao = motivos[0]
    else:
        situacao = "Reprovada"
        motivo_reprovacao = " | ".join(motivos)

    return situacao, motivo_reprovacao


# CONTROLE DE CAIXAS
def obter_caixa_atual():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT numero_caixa
        FROM pecas
        WHERE situacao = 'Aprovada' AND numero_caixa IS NOT NULL
        ORDER BY numero_caixa DESC
        LIMIT 1
    """)
    resultado = cursor.fetchone()

    conexao.close()

    if resultado:
        return resultado[0]
    return 1

def contar_pecas_na_caixa(numero_caixa):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM pecas
        WHERE situacao = 'Aprovada' AND numero_caixa = ?
    """, (numero_caixa,))

    quantidade = cursor.fetchone()[0]
    conexao.close()
    return quantidade

def fechar_caixa(numero_caixa):
    quantidade = contar_pecas_na_caixa(numero_caixa)

    if quantidade == 10:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO caixas (numero_caixa, quantidade_pecas)
            VALUES (?, ?)
        """, (numero_caixa, quantidade))

        conexao.commit()
        conexao.close()

        mensagem_info(f"\nCaixa {numero_caixa} fechada com 10 peças aprovadas.")

def armazenar_em_caixa(id_peca):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    numero_caixa = obter_caixa_atual()
    quantidade_atual = contar_pecas_na_caixa(numero_caixa)

    if quantidade_atual >= 10:
        numero_caixa += 1

    cursor.execute("""
        UPDATE pecas
        SET numero_caixa = ?
        WHERE id = ?
    """, (numero_caixa, id_peca))

    conexao.commit()
    conexao.close()

    fechar_caixa(numero_caixa)

def caixa_esta_fechada(numero_caixa):
    if numero_caixa is None:
        return False

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT 1
        FROM caixas
        WHERE numero_caixa = ?
        LIMIT 1
    """, (numero_caixa,))

    resultado = cursor.fetchone()
    conexao.close()

    return resultado is not None


# CADASTRO DE PECAS
def cadastrar_peca():
    try:
        peso = float(input("Digite o peso da peça (g): ").replace(",", "."))
        cor = input("Digite a cor da peça: ").strip().lower()
        comprimento = float(input("Digite o comprimento da peça (cm): ").replace(",", "."))

        situacao, motivo = avaliar_peca(peso, cor, comprimento)

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO pecas (peso, cor, comprimento, situacao, motivo_reprovacao, numero_caixa)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (peso, cor, comprimento, situacao, motivo, None))

        id_peca = cursor.lastrowid
        conexao.commit()
        conexao.close()

        if situacao == "Aprovada":
            armazenar_em_caixa(id_peca)

        mensagem_sucesso("\nPeça cadastrada com sucesso.")
        if situacao == "Aprovada":
            mensagem_sucesso(f"Situação: {situacao}")
        else:
            mensagem_erro(f"Situação: {situacao}")
            mensagem_alerta(f"Motivo: {motivo}")

    except ValueError:
        mensagem_erro("\nErro: digite valores numéricos válidos para peso e comprimento.")

def cadastrar_pecas_automaticas():
    mensagem_info("\nGerando 20 peças automáticas...\n")

    cores_possiveis = ["azul", "verde", "vermelho", "amarelo", "preto"]

    for indice in range(20):
        peso = round(random.uniform(90, 110), 2)
        cor = random.choice(cores_possiveis)
        comprimento = round(random.uniform(8, 22), 2)

        situacao, motivo = avaliar_peca(peso, cor, comprimento)

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO pecas (peso, cor, comprimento, situacao, motivo_reprovacao, numero_caixa)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (peso, cor, comprimento, situacao, motivo, None))

        id_peca = cursor.lastrowid
        conexao.commit()
        conexao.close()

        if situacao == "Aprovada":
            armazenar_em_caixa(id_peca)

        texto_peca = (
            f"Peça {indice + 1}: "
            f"Peso={peso}g | Cor={cor} | Comprimento={comprimento}cm | Situação={situacao}"
        )

        if situacao == "Aprovada":
            print(Fore.GREEN + texto_peca + Style.RESET_ALL)
        else:
            print(Fore.RED + texto_peca + Style.RESET_ALL)


# LISTAGEM
def listar_pecas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    print("\n1 - Listar todas")
    print("2 - Somente aprovadas")
    print("3 - Somente reprovadas")
    opcao = input("Escolha: ").strip()

    if opcao == "1":
        cursor.execute("""
            SELECT id, peso, cor, comprimento, situacao, motivo_reprovacao, numero_caixa
            FROM pecas
            ORDER BY id
        """)
    elif opcao == "2":
        cursor.execute("""
            SELECT id, peso, cor, comprimento, situacao, motivo_reprovacao, numero_caixa
            FROM pecas
            WHERE situacao = 'Aprovada'
            ORDER BY id
        """)
    elif opcao == "3":
        cursor.execute("""
            SELECT id, peso, cor, comprimento, situacao, motivo_reprovacao, numero_caixa
            FROM pecas
            WHERE situacao = 'Reprovada'
            ORDER BY id
        """)
    else:
        mensagem_erro("\nOpção inválida.")
        conexao.close()
        return

    pecas = cursor.fetchall()
    conexao.close()

    if not pecas:
        mensagem_alerta("\nNenhuma peça encontrada.")
        return

    print("\n===== LISTA DE PEÇAS =====")
    for peca in pecas:
        texto = f"""
ID: {peca[0]}
Peso: {peca[1]} g
Cor: {peca[2]}
Comprimento: {peca[3]} cm
Situação: {peca[4]}
Motivo: {peca[5] if peca[5] else '-'}
Caixa: {peca[6] if peca[6] else '-'}
-----------------------------
"""
        if peca[4] == "Aprovada":
            print(Fore.GREEN + texto + Style.RESET_ALL)
        else:
            print(Fore.RED + texto + Style.RESET_ALL)

def listar_caixas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT numero_caixa, quantidade_pecas
        FROM caixas
        ORDER BY numero_caixa
    """)

    caixas = cursor.fetchall()
    conexao.close()

    if not caixas:
        mensagem_alerta("\nNenhuma caixa fechada encontrada.")
        return

    print(Fore.CYAN + "\n===== CAIXAS FECHADAS =====" + Style.RESET_ALL)
    for caixa in caixas:
        print(Fore.CYAN + f"Caixa {caixa[0]} - Quantidade de peças: {caixa[1]}" + Style.RESET_ALL)

def mostrar_caixa_aberta_atual():
    numero_caixa_atual = obter_caixa_atual()
    quantidade_atual = contar_pecas_na_caixa(numero_caixa_atual)

    if quantidade_atual >= 10:
        numero_caixa_atual += 1
        quantidade_atual = 0

    faltam = 10 - quantidade_atual

    print(Fore.CYAN + "\n===== CAIXA ABERTA ATUAL =====" + Style.RESET_ALL)
    print(f"Número da caixa em andamento: {numero_caixa_atual}")
    print(f"Peças aprovadas armazenadas: {quantidade_atual}")
    print(f"Faltam para fechar a caixa: {faltam}")


# REMOCAO
def remover_peca():
    try:
        id_peca = int(input("\nDigite o ID da peça que deseja remover: "))

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM pecas WHERE id = ?", (id_peca,))
        peca = cursor.fetchone()

        if not peca:
            mensagem_erro("\nPeça não encontrada.")
            conexao.close()
            return

        numero_caixa = peca[6]

        print("\n===== DADOS DA PEÇA =====")
        print(f"ID: {peca[0]}")
        print(f"Peso: {peca[1]} g")
        print(f"Cor: {peca[2]}")
        print(f"Comprimento: {peca[3]} cm")
        print(f"Situação: {peca[4]}")
        print(f"Motivo: {peca[5] if peca[5] else '-'}")
        print(f"Caixa: {numero_caixa if numero_caixa else '-'}")

        if caixa_esta_fechada(numero_caixa):
            mensagem_erro("\nNão é permitido excluir esta peça, pois a caixa já foi fechada.")
            conexao.close()
            return

        confirmacao = input("\nTem certeza que deseja remover esta peça? (s/n): ").strip().lower()

        if confirmacao == "s":
            cursor.execute("DELETE FROM pecas WHERE id = ?", (id_peca,))
            conexao.commit()
            mensagem_sucesso("\nPeça removida com sucesso.")
        else:
            mensagem_alerta("\nRemoção cancelada.")

        conexao.close()

    except ValueError:
        mensagem_erro("\nErro: digite um ID válido.")


# RELATORIO
def gerar_relatorio():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM pecas")
    total_pecas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pecas WHERE situacao = 'Aprovada'")
    total_aprovadas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pecas WHERE situacao = 'Reprovada'")
    total_reprovadas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM caixas")
    total_caixas_fechadas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT motivo_reprovacao, COUNT(*)
        FROM pecas
        WHERE situacao = 'Reprovada'
        GROUP BY motivo_reprovacao
    """)
    motivos_reprovacao = cursor.fetchall()

    conexao.close()

    print(Fore.CYAN + "\n===== RELATÓRIO FINAL =====" + Style.RESET_ALL)
    print(f"Total de peças cadastradas: {total_pecas}")
    print(Fore.GREEN + f"Total de peças aprovadas: {total_aprovadas}" + Style.RESET_ALL)
    print(Fore.RED + f"Total de peças reprovadas: {total_reprovadas}" + Style.RESET_ALL)
    print(Fore.CYAN + f"Total de caixas fechadas: {total_caixas_fechadas}" + Style.RESET_ALL)

    print("\nMotivos de reprovação:")
    if motivos_reprovacao:
        for motivo, quantidade in motivos_reprovacao:
            print(Fore.YELLOW + "\n-----------------------------" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Quantidade: {quantidade}" + Style.RESET_ALL)
            print("Motivos:")

            lista_motivos = motivo.split(" | ")

            for m in lista_motivos:
                print(Fore.RED + f"- {m}" + Style.RESET_ALL)
    else:
        mensagem_sucesso("- Nenhuma peça reprovada.")


# LIMPEZA DO BANCO
def limpar_banco_dados():
    confirmacao = input(
        "\nTem certeza que deseja apagar todo o banco de dados? (s/n): "
    ).strip().lower()

    if confirmacao == "s":
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("DELETE FROM pecas")
        cursor.execute("DELETE FROM caixas")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='pecas'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='caixas'")

        conexao.commit()
        conexao.close()

        mensagem_sucesso("\nBanco de dados limpo com sucesso. Novo lote iniciado.")
    else:
        mensagem_alerta("\nOperação cancelada.")


# MENU PRINCIPAL
def menu():
    while True:
        print(Fore.CYAN + "\n========== MENU ==========" + Style.RESET_ALL)
        print("1. Cadastrar nova peça manualmente")
        print("2. Registrar 20 peças automáticas")
        print("3. Listar peças")
        print("4. Remover peça cadastrada")
        print("5. Listar caixas fechadas")
        print("6. Mostrar caixa aberta atual")
        print("7. Gerar relatório final")
        print("8. Limpar banco de dados / iniciar novo lote")
        print("0. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_peca()
        elif opcao == "2":
            cadastrar_pecas_automaticas()
        elif opcao == "3":
            listar_pecas()
        elif opcao == "4":
            remover_peca()
        elif opcao == "5":
            listar_caixas()
        elif opcao == "6":
            mostrar_caixa_aberta_atual()
        elif opcao == "7":
            gerar_relatorio()
        elif opcao == "8":
            limpar_banco_dados()
        elif opcao == "0":
            mensagem_info("\nEncerrando o sistema...")
            break
        else:
            mensagem_erro("\nOpção inválida. Tente novamente.")


# EXECUCAO PRINCIPAL
if __name__ == "__main__":
    criar_tabelas()
    menu()