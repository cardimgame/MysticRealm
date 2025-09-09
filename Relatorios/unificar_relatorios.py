import os

def unificar_relatorios(imports_path, unused_path, destino):
    # Verifica existência dos arquivos
    if not os.path.exists(imports_path):
        print(f"❌ Arquivo não encontrado: {imports_path}")
        return
    if not os.path.exists(unused_path):
        print(f"❌ Arquivo não encontrado: {unused_path}")
        return

    # Verifica se os arquivos têm conteúdo
    with open(imports_path, 'r', encoding='utf-8') as f:
        imports = f.readlines()
    if not imports:
        print(f"⚠️ Arquivo vazio: {imports_path}")
        return

    with open(unused_path, 'r', encoding='utf-8') as f:
        unused = f.readlines()
    if not unused:
        print(f"⚠️ Arquivo vazio: {unused_path} (sem imports não utilizados)")
        unused_set = set()
    else:
        unused_set = set()
        for linha in unused:
            if 'unused import' in linha:
                partes = linha.strip().split("'")
                if len(partes) >= 2:
                    nome = partes[1].split('.')[0]
                    unused_set.add(nome)

    # Monta relatório final
    relatorio_final = []
    for linha in imports:
        linha_limpa = linha.strip()
        if linha_limpa.startswith('- import') or linha_limpa.startswith('- from'):
            partes = linha_limpa.split()
            if len(partes) >= 2:
                nome_import = partes[1].split('.')[0]
                status = '❌ Não utilizado' if nome_import in unused_set else '✅ Usado'
                relatorio_final.append(f"{linha_limpa}  [{status}]")
            else:
                relatorio_final.append(linha_limpa)
        else:
            relatorio_final.append(linha_limpa)

    with open(destino, 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio_final))

    print(f"\n📄 Relatório final gerado: {destino}")
    print(f"✅ Linhas processadas: {len(relatorio_final)}")
    print(f"❌ Imports não utilizados detectados: {len(unused_set)}")

# Chamada direta:
unificar_relatorios(
    'relatorio_imports.txt',
    'relatorio_nao_utilizados.txt',
    'relatorio_final_mystic.txt'
)
