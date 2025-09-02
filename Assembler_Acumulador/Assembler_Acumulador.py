import re

# Cores ANSI
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

# Dicionário de mnemônicos
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

def converte_argumento(arg: str, label_table: dict) -> str:
    if arg.startswith('@'):
        valor = int(arg[1:])
        return "'0' & x\"" + format(valor, "02X") + "\""
    elif arg.startswith('$'):
        valor = int(arg[1:])
        return "'1' & x\"" + format(valor, "02X") + "\""
    elif arg.startswith('.'):
        nome = arg[1:]
        if nome not in label_table:
            raise ValueError(f"Label não definido: {arg}")
        valor = label_table[nome]
        return "'0' & x\"" + format(valor, "02X") + "\""
    else:
        valor = int(arg)
        return "'0' & x\"" + format(valor, "02X") + "\""

def monta_instrucao(mnemonic: str, arg: str, comment: str, label_table: dict) -> tuple[str, str]:
    if mnemonic not in mne:
        raise ValueError(f"Mnemônico desconhecido: {mnemonic}")

    opcode = mne[mnemonic]
    comentario_final = f"{mnemonic} {arg or ''}".strip()

    if arg:
        if arg.startswith('.'):
            nome = arg[1:]
            if nome not in label_table:
                raise ValueError(f"Label não definido: {arg}")
            valor = label_table[nome]
            valor_hex = converte_argumento(arg, label_table)
            if not comment:
                comment = f"{arg} -> endereço {valor}"
        else:
            valor_hex = converte_argumento(arg, label_table)

        instrucao = opcode + "\" & " + valor_hex
    else:
        instrucao = opcode + "\" & '0' & x\"00"

    if comment:
        comentario_final += f"  #{comment}"

    return instrucao, comentario_final

def coleta_labels(linhas: list[str]) -> dict:
    label_table = {}
    contador = 0
    for line in linhas:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            label, resto = line.split(":", 1)
            label_table[label.strip()] = contador
            if resto.strip():
                contador += 1
        else:
            contador += 1
    print(f"{GREEN}[OK] Labels identificados: {label_table}{RESET}")
    return label_table

def processa_asm(linhas: list[str], label_table: dict) -> list[str]:
    saida = []
    contador = 0
    for line in linhas:
        original = line.strip()
        if not original or original.startswith("#"):
            continue

        if ":" in original:
            _, resto = original.split(":", 1)
            original = resto.strip()
            if not original:
                continue

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

def escreve_bin(saida: list[str], filename="BIN.txt"):
    with open(filename, "w") as f:
        for s in saida:
            f.write(s + "\n")
    print(f"{GREEN}[OK] Arquivo BIN gerado: {filename}{RESET}")

def escreve_mif(saida: list[str], filename="initROM.mif"):
    header = [
        "WIDTH=9;\n",
        "DEPTH=32;\n",
        "\n",
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
                bin_str = format(int(hex1, 16), "04b") + bit + format(int(hex2, 16), "08b")
                f.write(f"\t{i}\t:\t{bin_str};\t-- {comentario.strip()}\n")
        f.write("END;\n")
    print(f"{GREEN}[OK] Arquivo MIF gerado: {filename}{RESET}")

# MAIN
if __name__ == "__main__":
    with open("ASM.txt", "r") as f:
        linhas = f.readlines()

    print("[INFO] Iniciando processamento do arquivo ASM...")

    label_table = coleta_labels(linhas)
    saida = processa_asm(linhas, label_table)
    escreve_bin(saida)
    escreve_mif(saida)

    print(f"{GREEN}[OK] Todo o processamento concluído com sucesso!{RESET}")
