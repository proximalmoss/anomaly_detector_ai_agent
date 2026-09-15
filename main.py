from fastapi import FastAPI
import json
from tools import run_rule_checks

app=FastAPI()

with open("sheets_config.json") as f:
    SHEETS_CONFIG=json.load(f)

@app.post("/webhook/edit")
def handle_edit(payload: dict):
    sheet_id=payload["sheetId"]
    row_values=payload["row"]

    sheet_config= SHEETS_CONFIG.get(sheet_id)
    if sheet_config is None:
        print(f"No config found for sheet {sheet_id} - skipping checks")
        return{"status": "received", "checked": False}

    columns=sheet_config["columns"]
    column_rules=sheet_config["column_rules"]

    row_dict=dict(zip(columns, row_values))

    issues=run_rule_checks(row_dict, column_rules)

    if issues:
        print(f"Anomalies found in row {row_dict}:")
        for issue in issues:
            print("   -", issues)
    else:
        print(f"Row OK: {row_dict}")

    return {"status":"received", "checked":True, "issues": issues}