import re

# ==========================
# Códigos ANSI para cores no terminal
# ==========================
RED = "\033[91m"      # Erros
YELLOW = "\033[93m"   # Avisos
GREEN = "\033[92m"    # Sucesso
RESET = "\033[0m"     # Reset da cor

# ==========================
# Dicionário de mnemônicos
# Cada instrução recebe um opcode hexadecimal
# ==========================
mne = {
    "NOP": "x\"0",
    "LDA": "x\"1",
    "SOMA": "x\"2",
    "SUB": "x\"3",
    "LDI": "x\"4",
    "STA": "x\"5",
    "JMP": "x\"6",
    "JEQ": "x\"7",
    "CEQ": "x\"8",
    "JSR": "x\"9",
    "RET": "x\"A",
}

# ==========================
# Função para converter argumentos da instrução
# Suporta: @ (endereços), $ (valores) e labels (.NOME)
# ==========================
def converte_argumento(arg: str, label_table: dict) -> str:
    if arg.startswith('@'):  # Endereço numérico
        valor = int(arg[1:])
        return "'0' & x\"" + format(valor, "02X") + "\""
    elif arg.startswith('$'):  # Valor imediato
        valor = int(arg[1:])
        return "'1' & x\"" + format(valor, "02X") + "\""
    elif arg.startswith('.'):  # Label
        nome = arg[1:]
        if nome not in label_table:
            raise ValueError(f"Label não definido: {arg}")
        valor = label_table[nome]
        return "'0' & x\"" + format(valor, "02X") + "\""
    else:  # Caso geral
        valor = int(arg)
        return "'0' & x\"" + format(valor, "02X") + "\""

# ==========================
# Função que monta a instrução completa (opcode + argumento + comentário)
# ==========================
def monta_instrucao(mnemonic: str, arg: str, comment: str, label_table: dict) -> tuple[str, str]:
    if mnemonic not in mne:
        raise ValueError(f"Mnemônico desconhecido: {mnemonic}")

    opcode = mne[mnemonic]  # Recupera opcode do mnemônico
    comentario_final = f"{mnemonic} {arg or ''}".strip()  # Comentário padrão

    # Trata argumento, se houver
    if arg:
        valor_hex = converte_argumento(arg, label_table)
        if not comment and arg.startswith('.'):
            # Se o argumento é label e não há comentário, adiciona informação do endereço
            comment = f"{arg} -> endereço {label_table[arg[1:]]}"

        instrucao = opcode + "\" & " + valor_hex
    else:
        # Instruções sem argumento recebem x"00"
        instrucao = opcode + "\" & '0' & x\"00"

    if comment:
        comentario_final += f"  #{comment}"

    return instrucao, comentario_final

# ==========================
# Função que coleta todas as labels do código
# Retorna um dicionário {label: endereço}
# ==========================
def coleta_labels(linhas: list[str]) -> dict:
    label_table = {}
    contador = 0  # Contador de posição de memória
    for line in linhas:
        line = line.strip()
        if not line or line.startswith("#"):  # Ignora linhas vazias ou comentários
            continue
        if ":" in line:  # Linha com label
            label, resto = line.split(":", 1)
            label_table[label.strip()] = contador
            if resto.strip():  # Se houver instrução após o label
                contador += 1
        else:
            contador += 1
    print(f"{GREEN}[OK] Labels identificados: {label_table}{RESET}")
    return label_table

# ==========================
# Função que processa cada linha ASM e gera instrução BIN
# ==========================
def processa_asm(linhas: list[str], label_table: dict) -> list[str]:
    saida = []
    contador = 0
    for line in linhas:
        original = line.strip()
        if not original or original.startswith("#"):
            continue  # Ignora linhas vazias ou comentários

        # Remove label da linha, se houver
        if ":" in original:
            _, resto = original.split(":", 1)
            original = resto.strip()
            if not original:
                continue

        # Regex para separar mnemônico, argumento e comentário
        match = re.match(r"^(?P<mnemonic>\w+)(?:\s+(?P<arg>[.@$\w\d]+))?(?:\s*#(?P<comment>.*))?$", original)
        if not match:
            print(f"{YELLOW}[Aviso] Linha ignorada: {original}{RESET}")
            continue

        mnemonic = match.group("mnemonic")
        arg = match.group("arg")
        comment = match.group("comment")

        try:
            instrucao, comentario = monta_instrucao(mnemonic, arg, comment, label_table)
            saida.append(f'tmp({contador}) := {instrucao};\t-- {comentario}')
            contador += 1
        except Exception as e:
            print(f"{RED}[Erro] Linha {contador}: {e}{RESET}")
            continue

    print(f"{GREEN}[OK] Processamento ASM -> BIN concluído. {contador} instruções geradas.{RESET}")
    return saida

# ==========================
# Função que escreve arquivo BIN
# ==========================
def escreve_bin(saida: list[str], filename="BIN.txt"):
    with open(filename, "w") as f:
        for s in saida:
            f.write(s + "\n")
    print(f"{GREEN}[OK] Arquivo BIN gerado: {filename}{RESET}")

# ==========================
# Função que escreve arquivo MIF
# ==========================
def escreve_mif(saida: list[str], filename="initROM.mif"):
    header = [
        "WIDTH=13;\n",
        "DEPTH=256;\n",
        "ADDRESS_RADIX=DEC;\n",
        "DATA_RADIX=BIN;\n",
        "\n",
        "CONTENT BEGIN\n",
    ]
    with open(filename, "w") as f:
        f.writelines(header)
        for i, s in enumerate(saida):
            m = re.search(r"x\"([0-9A-F])\" & '([01])' & x\"([0-9A-F]{2})\"", s)
            comentario = s.split("--")[1] if "--" in s else ""
            if m:
                hex1, bit, hex2 = m.groups()
                # Converte opcode + bit + imediato para binário 9 bits
                bin_str = format(int(hex1, 16), "04b") + bit + format(int(hex2, 16), "08b")
                f.write(f"\t{i}\t:\t{bin_str};\t-- {comentario.strip()}\n")
        f.write("END;\n")
    print(f"{GREEN}[OK] Arquivo MIF gerado: {filename}{RESET}")

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    with open("ASM.txt", "r") as f:
        linhas = f.readlines()

    print("[INFO] Iniciando processamento do arquivo ASM...")

    # Coleta todas as labels do código
    label_table = coleta_labels(linhas)

    # Processa cada linha e gera saída BIN
    saida = processa_asm(linhas, label_table)

    # Escreve arquivo BIN
    escreve_bin(saida)

    # Escreve arquivo MIF
    escreve_mif(saida)

    print(f"{GREEN}[OK] Todo o processamento concluído com sucesso!{RESET}")
