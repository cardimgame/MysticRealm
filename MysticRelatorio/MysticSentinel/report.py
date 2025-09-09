import json
from pathlib import Path
import time

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def generate_report(error_type: str, message: str, traceback_str: str, file_path: Path, fixed: bool):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_data = {
        "timestamp": timestamp,
        "error_type": error_type,
        "message": message,
        "file": str(file_path),
        "correction_applied": fixed,
        "traceback": traceback_str
    }

    # Salva como JSON
    json_path = LOG_DIR / f"report_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # Salva como TXT
    txt_path = LOG_DIR / f"report_{timestamp}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"[MysticSentinel] Relatório de Erro\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Arquivo: {file_path}\n")
        f.write(f"Tipo: {error_type}\n")
        f.write(f"Mensagem: {message}\n")
        f.write(f"Correção automática: {'✅ aplicada' if fixed else '❌ não aplicada'}\n")
        f.write("Traceback:\n")
        f.write(traceback_str)

    print(f"[MysticSentinel] Relatório salvo em:\n- {json_path}\n- {txt_path}")
