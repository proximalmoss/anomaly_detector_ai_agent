from fastapi import FastAPI
import json
from tools import run_rule_checks
from stats import check_zscore, check_iqr
from db import init_db, get_column_stats, update_column_stats
from agent import get_alert_message

app=FastAPI()

with open("sheets_config.json") as f:
    SHEETS_CONFIG=json.load(f)
init_db()

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

    #statistical checks
    for column_name, value in row_dict.items():
        if not isinstance(value, (int, float)):
            continue

        stats=get_column_stats(sheet_id, column_name)
        z_issue=check_zscore(value, stats)

        if z_issue:
            issues.append(f"{column_name}: {z_issue}")

        update_column_stats(sheet_id, column_name, value)

    if issues:
        print(f"Anomalies found in row {row_dict}:")
        for issue in issues:
            print("   -", issue)

        alert_message=get_alert_message(row_dict, issues)
        print("\nGenerated alert message")
        print(alert_message)
        print("end\n")
    else:
        print(f"Row OK: {row_dict}")

    return {"status": "received", "checked": True, "issues": issues}