import os
import ast
import sys
import importlib.util
import subprocess
from collections import defaultdict, Counter
import stdlib_list

IGNORAR_PASTAS = {'venv', '.venv', 'archive_obsolete', '.gitignore'}
PASTA_PROJETO = 'MysticReal'
ARQUIVO_RAIZ_VALIDO = 'main.py'

def classificar_import(nome, std_libs):
    if nome in std_libs:
        return 'Biblioteca padrão'
    elif importlib.util.find_spec(nome) is not None:
        return 'Biblioteca de terceiros'
    else:
        return 'Import interno ou indefinido'

def arquivos_validos(caminho_raiz):
    arquivos = []
    for raiz, pastas, nomes in os.walk(caminho_raiz):
        pastas[:] = [p for p in pastas if p not in IGNORAR_PASTAS]
        for nome in nomes:
            if nome.endswith('.py'):
                caminho = os.path.join(raiz, nome)
                # inclui main.py da raiz ou qualquer .py dentro da pasta MysticReal
                if nome == ARQUIVO_RAIZ_VALIDO or PASTA_PROJETO in caminho:
                    arquivos.append(caminho)
    return arquivos

def extrair_imports(arquivos, std_libs):
    agrupados = defaultdict(list)
    estatisticas = Counter()

    for caminho_arquivo in arquivos:
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            arvore = ast.parse(conteudo, filename=caminho_arquivo)

            for node in ast.walk(arvore):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        nome = alias.name.split('.')[0]
                        tipo = classificar_import(nome, std_libs)
                        linha = f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        agrupados[caminho_arquivo].append((linha, tipo))
                        estatisticas[nome] += 1

                elif isinstance(node, ast.ImportFrom):
                    modulo = node.module if node.module else ""
                    nome = modulo.split('.')[0]
                    tipo = classificar_import(nome, std_libs)
                    for alias in node.names:
                        linha = f"from {modulo} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        agrupados[caminho_arquivo].append((linha, tipo))
                        estatisticas[nome] += 1

        except Exception as e:
            agrupados[caminho_arquivo].append((f"[Erro ao processar: {e}]", "Erro"))

    return agrupados, estatisticas

def rodar_vulture(arquivos):
    try:
        resultado = subprocess.run(['vulture'] + arquivos, capture_output=True, text=True)
        linhas = resultado.stdout.splitlines()
        unused = set()
        for linha in linhas:
            if 'unused import' in linha:
                partes = linha.strip().split("'")
                if len(partes) >= 2:
                    nome = partes[1].split('.')[0]
                    unused.add(nome)
        return unused
    except Exception as e:
        print(f"❌ Erro ao rodar vulture: {e}")
        return set()

def gerar_relatorio(caminho_raiz, destino):
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    std_libs = set(stdlib_list.stdlib_list(version))

    print("🔍 Coletando arquivos válidos...")
    arquivos = arquivos_validos(caminho_raiz)
    if not arquivos:
        print("⚠️ Nenhum arquivo .py válido encontrado.")
        return

    print("🔍 Extraindo imports...")
    agrupados, estatisticas = extrair_imports(arquivos, std_libs)

    print("🧹 Rodando vulture...")
    unused_set = rodar_vulture(arquivos)

    print("📄 Gerando relatório final...")
    relatorio = []

    for arquivo, imports in agrupados.items():
        relatorio.append(f"\n📄 Arquivo: {os.path.relpath(arquivo, caminho_raiz)}")
        for linha, tipo in imports:
            if linha.startswith("[Erro"):
                relatorio.append(f"  - {linha}")
                continue
            nome_import = linha.split()[1].split('.')[0]
            status = '❌ Não utilizado' if nome_import in unused_set else '✅ Usado'
            relatorio.append(f"  - {linha}  [{tipo}] [{status}]")

    relatorio.append("\n📊 Estatísticas gerais:")
    for nome, contagem in estatisticas.most_common():
        tipo = classificar_import(nome, std_libs)
        status = '❌' if nome in unused_set else '✅'
        relatorio.append(f"  - {nome}: {contagem}x  [{tipo}] [{status}]")

    with open(destino, 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio))

    print(f"\n✅ Relatório salvo em: {destino}")
    print(f"📦 Imports totais: {sum(estatisticas.values())}")
    print(f"❌ Imports não utilizados: {len(unused_set)}")

# Chamada direta
if __name__ == "__main__":
    raiz = os.path.dirname(os.path.abspath(__file__))
    destino = os.path.join(raiz, 'relatorio_final_mystic.txt')
    gerar_relatorio(raiz, destino)
