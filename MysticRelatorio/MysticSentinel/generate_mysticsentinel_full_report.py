from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent  # MysticSentinel/
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

def generate_full_report():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = LOG_DIR / f"mysticsentinel_full_report_{timestamp}.txt"

    py_files = sorted(BASE_DIR.glob("*.py"))
    report_lines = [
        f"[MysticSentinel] Relatório Completo de Código-Fonte",
        f"Data: {timestamp}",
        f"Arquivos analisados: {len(py_files)}",
        "-" * 80
    ]

    for file in py_files:
        report_lines.append(f"\n📄 Arquivo: {file.name}")
        report_lines.append(f"🔢 Linhas: {sum(1 for _ in file.open(encoding='utf-8'))}")
        report_lines.append("-" * 40)
        try:
            content = file.read_text(encoding="utf-8")
            report_lines.append(content)
        except Exception as e:
            report_lines.append(f"[Erro ao ler o arquivo: {e}]")
        report_lines.append("\n" + "=" * 80)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n✅ Relatório completo gerado: {report_path}")

if __name__ == "__main__":
    generate_full_report()
# -*- coding: utf-8 -*-