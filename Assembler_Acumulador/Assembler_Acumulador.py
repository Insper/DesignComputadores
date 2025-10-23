import re
import sys

# ==========================
# Códigos ANSI para cores no terminal
# ==========================
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

# ==========================
# Dicionário de mnemônicos
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
# Regras de prefixos permitidos por instrução
# Agora NÃO existe 'raw' — argumentos sem prefixo são inválidos.
# Labels ('.') são permitidas somente para instruções de salto: JMP, JEQ, JSR.
# ==========================
allowed_prefixes = {
    "LDI": {"$"},
    "LDA": {"@"},
    "STA": {"@"},
    "JMP": {"@", "."},
    "JEQ": {"@", "."},
    "JSR": {"@", "."},
    "CEQ": {"@"},
    "SOMA": {"@"},
    "SUB": {"@"},
    "NOP": set(),
    "RET": set(),
}
# por segurança, mnemônicos não listados explicitamente não aceitam argumentos
allowed_default = set()

# ==========================
# Auxiliares
# ==========================
def _arg_prefix_kind(arg: str) -> str:
    """
    Retorna um dos: '$', '@', '.', ou 'noprefix' (quando não há símbolo).
    """
    if arg is None:
        return None
    if arg.startswith("$"):
        return "$"
    if arg.startswith("@"):
        return "@"
    if arg.startswith("."):
        return "."
    return "noprefix"  # agora tratamos como erro posteriormente

def _validate_arg_for_mnemonic(mnemonic: str, arg: str):
    """
    Valida se o tipo de prefixo do argumento é permitido para o mnemônico.
    Levanta ValueError com mensagem clara quando inválido.
    """
    pref = _arg_prefix_kind(arg)
    allowed = allowed_prefixes.get(mnemonic, allowed_default)

    if pref is None:
        # nenhum argumento — tudo bem se a instrução aceitar sem argumento
        return

    if pref == "noprefix":
        raise ValueError(f"Mnemônico {mnemonic} não aceita argumento sem prefixo. Use '@', '$' ou '.' conforme apropriado.")

    if pref not in allowed:
        pref_name = f"'{pref}'"
        allowed_readable = []
        for p in sorted(allowed):
            if p == ".":
                allowed_readable.append("'.' (label)")
            else:
                allowed_readable.append(f"'{p}'")
        allowed_str = ", ".join(allowed_readable) if allowed_readable else "nenhum"
        raise ValueError(f"Mnemônico {mnemonic} não aceita argumento do tipo {pref_name}. Tipos permitidos: {allowed_str}.")

# ==========================
# Conversão de argumentos
# ==========================
def converte_argumento(arg: str, label_table: dict) -> str:
    """
    Converte apenas argumentos com prefixo '$', '@' ou '.'.
    Argumentos sem prefixo são considerados inválidos — essa validação deve ocorrer antes.
    """
    if arg is None:
        return "'0' & x\"00\""

    if arg.startswith('@'):
        try:
            valor = int(arg[1:])
        except ValueError:
            raise ValueError(f"Argumento inválido para endereço: {arg}")
        if valor > 0xFF:
            print(f"{YELLOW}[Aviso] @{valor} > 255 — truncando para {valor & 0xFF} e marcando como imediato.{RESET}")
            valor &= 0xFF
            return "'1' & x\"" + format(valor, "02X") + "\""
        return "'0' & x\"" + format(valor, "02X") + "\""

    elif arg.startswith('$'):
        try:
            valor = int(arg[1:])
        except ValueError:
            raise ValueError(f"Argumento inválido para imediato: {arg}")
        if valor < 0 or valor > 0xFF:
            print(f"{YELLOW}[Aviso] ${valor} fora de 8 bits — truncando para {valor & 0xFF}.{RESET}")
        return "'1' & x\"" + format(valor & 0xFF, "02X") + "\""

    elif arg.startswith('.'):
        nome = arg[1:]
        if nome not in label_table:
            raise ValueError(f"Label não definido: {arg}")
        valor = label_table[nome]
        if valor > 0xFF:
            print(f"{YELLOW}[Aviso] Label {nome}={valor} > 255 — truncando para {valor & 0xFF}.{RESET}")
            return "'1' & x\"" + format(valor & 0xFF, "02X") + "\""
        return "'0' & x\"" + format(valor, "02X") + "\""

    else:
        # não deve ocorrer: validamos antes para rejeitar 'noprefix'
        raise ValueError(f"Argumento sem prefixo inválido: {arg}")

# ==========================
# Monta instrução completa
# ==========================
def monta_instrucao(mnemonic: str, arg: str, comment: str, label_table: dict):
    if mnemonic not in mne:
        raise ValueError(f"Mnemônico desconhecido: {mnemonic}")
    if arg is not None:
        _validate_arg_for_mnemonic(mnemonic, arg)

    opcode = mne[mnemonic]
    comentario_final = f"{mnemonic} {arg or ''}".strip()

    if arg:
        valor_hex = converte_argumento(arg, label_table)
        if not comment and arg.startswith('.'):
            comment = f"{arg} -> endereço {label_table[arg[1:]]}"
        instrucao = opcode + "\" & " + valor_hex
    else:
        instrucao = opcode + "\" & '0' & x\"00\""

    if comment:
        comentario_final += f"  #{comment}"

    return instrucao, comentario_final

# ==========================
# Coleta labels
# ==========================
def coleta_labels(linhas):
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
    print(f"{GREEN}[OK] Labels: {label_table}{RESET}")
    return label_table

# ==========================
# Processa ASM -> BIN
# ==========================
def processa_asm(linhas, label_table):
    saida = []
    errors = []
    contador = 0
    for lineno, line in enumerate(linhas, start=1):
        original = line.strip()
        if not original or original.startswith("#"):
            continue
        if ":" in original:
            _, resto = original.split(":", 1)
            original = resto.strip()
            if not original:
                continue

        match = re.match(r"^(?P<mnemonic>\w+)(?:\s+(?P<arg>\S+))?(?:\s*#(?P<comment>.*))?$", original)
        if not match:
            msg = f"Linha {lineno}: sintaxe inválida -> '{original}'"
            print(f"{RED}[Erro] {msg}{RESET}")
            errors.append(msg)
            continue

        mnemonic = match.group("mnemonic")
        arg = match.group("arg")
        comment = match.group("comment")

        try:
            instrucao, comentario = monta_instrucao(mnemonic, arg, comment, label_table)
            saida.append(f'tmp({contador}) := {instrucao};\t-- {comentario}')
            contador += 1
        except Exception as e:
            msg = f"Linha {lineno}: {e}"
            print(f"{RED}[Erro] {msg}{RESET}")
            errors.append(msg)

    print(f"{GREEN}[OK] Processamento concluído: {contador} instruções válidas.{RESET}")
    return saida, errors

# ==========================
# Escrita de arquivos
# ==========================
def escreve_bin(saida, filename="BIN.txt"):
    with open(filename, "w") as f:
        for s in saida:
            f.write(s + "\n")
    print(f"{GREEN}[OK] BIN gerado: {filename}{RESET}")

def escreve_mif(saida, filename="initROM.mif"):
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
                bin_str = format(int(hex1, 16), "04b") + bit + format(int(hex2, 16), "08b")
                f.write(f"\t{i}\t:\t{bin_str};\t-- {comentario.strip()}\n")
        f.write("END;\n")
    print(f"{GREEN}[OK] MIF gerado: {filename}{RESET}")

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    try:
        with open("ASM.txt", "r") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"{RED}[Erro] Arquivo ASM.txt não encontrado.{RESET}")
        sys.exit(1)

    print("[INFO] Iniciando montagem...")

    label_table = coleta_labels(linhas)
    saida, errors = processa_asm(linhas, label_table)

    if errors:
        # Se houve erro — gerar BIN com banner centralizado (53 caracteres por linha)
        print(f"{RED}[ERRO] {len(errors)} erro(s) detectado(s). Gerando BIN de erro...{RESET}")
        with open("BIN.txt", "w") as f:
            f.write("#####################################################\n")
            f.write("################## ERRO NO ASSEMBLY ##################\n")
            f.write("#####################################################\n")
        print(f"{RED}[ERRO] Assembly inválido — BIN.txt gerado com aviso de erro.{RESET}")
        # opcional: imprimir resumo dos erros no terminal (já impresso durante parsing)
        sys.exit(1)
    else:
        escreve_bin(saida)
        escreve_mif(saida)
        print(f"{GREEN}[OK] Montagem concluída com sucesso!{RESET}")
