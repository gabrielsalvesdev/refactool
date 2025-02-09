# api/src/utils/code_analysis.py
import json


def parse_pylint_output(raw_json: str) -> dict:
    """Extrai métricas do relatório do Pylint"""
    report = json.loads(raw_json)
    warnings = [m for m in report if m.get("type") in ("warning", "error")]
    return {
        "score": report[0].get("score", 0.0) if report else 0.0,
        "warnings_count": len(warnings),
        "errors": [{"line": m.get("line"), "message": m.get("message")} for m in warnings]
    } 