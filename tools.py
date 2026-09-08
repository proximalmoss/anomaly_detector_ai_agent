#generic rule based anomaly checks - works for any sheet

from datetime import datetime

def check_range_rule(value: float, min_val: float = None, max_val: float = None) -> str | None:
    if value is None:
        return None
    if min_val is not None and value<min_val:
        return f"Value {value} is below minimum allowed ({min_val})."
    if max_val is not None and value>max_val:
        return f"Value {value} exceeds mavimum allowed ({max_val})."
    return None

def check_allowed_values_rule(value: str, allowed_values: list) -> str | None:
    if value not in allowed_values:
        return f"Value '{value} is not in the list of recognized values: {allowed_values}."
    return None

def check_not_null_rule(value) -> str | None:
    if value is None or (isinstance(value, str) and value.strip()==""):
        return "This value is missing, but this column should not be blank"
    return None

def check_type_rule(value, expected_type: str) -> str | None:
    if expected_type=="number":
        if not isinstance(value, (int,float)):
            return f"Value '{value}' should be a number, but isn't"
    elif expected_type=="text":
        if not isinstance(value, str):
            return f"Value '{value}' should be text, but isn't"
    return None

def check_date_rule(value: str, date_format: str = "%d/%m/%Y") -> str | None:
    try:
        datetime.strptime(str(value), date_format)
        return None
    except ValueError:
        return f"Value '{value}' is not a valid date in format {date_format}."

def check_duplicate_rows(all_rows: list, columns_to_check: list = None) -> list[str]:
    seen=[]
    issues=[]

    for i, row in enumerate(all_rows):
        if columns_to_check:
            signature=tuple(row.get(col) for col in columns_to_check)
        else:
            signature=tuple(row.items())
        if signature in seen:
            issues.append(f"Row {i} appears to be duplicate: {row}")
        else:
            seen.append(signature)
    return issues

def run_rule_checks(row: dict, column_rules: dict) -> list[str]:
    issues=[]

    for column_name, rule in column_rules.items():
        if column_name not in row:
            continue
        value=row[column_name]
        rule_type=rule["type"]
        result=None

        if rule_type=="range":
            result= check_range_rule(value, rule.get("min"), rule.get("max"))
        elif rule_type=="allowed_values":
            result=check_allowed_values_rule(value, rule["values"])
        elif rule_type=="not null":
            result=check_not_null_rule(value)
        elif rule_type=="type":
            result=check_type_rule(value, rule["rexpected_type"])
        elif rule_type=="date":
            result=check_date_rule(value, rule.get("format", "%d/%m/%Y"))

        if result:
            issues.append(f"{column_name}:{result}")
    return issues

#Test Block
if __name__ == "__main__":
    my_sheet_rules = {
        "Date": {"type": "date", "format": "%d/%m/%Y"},
        "Category": {
            "type": "allowed_values",
            "values": ["Jackets", "Pants", "Tops", "Baby-Tees", "Dresses",
                       "Denims", "T-shirts", "Makeup", "Jewellery",
                       "Skincare", "Bags", "Heels", "Shoes", "Sneakers"]
        },
        "Amount": {"type": "range", "min": 0, "max": 10000},
    }

    test_rows = [
        {"Date": "24/03/2026", "Category": "Tops", "Amount": 40},
        {"Date": "24/03/2026", "Category": "Tops", "Amount": -15},
        {"Date": "24/03/2026", "Category": "Rocketships", "Amount": 40},
        {"Date": "24/03/2026", "Category": "Shoes", "Amount": 999999},
        {"Date": "not-a-date", "Category": "Shoes", "Amount": 40},
        {"Date": "24/03/2026", "Category": "Tops", "Amount": None},
        {"Date": "24/03/2026", "Category": "Tops", "Amount": 40},  # duplicate of row 1
    ]

    print("--- Row-level checks ---")
    for row in test_rows:
        result = run_rule_checks(row, my_sheet_rules)
        print(f"Row: {row}")
        if result:
            for issue in result:
                print("   -", issue)
        else:
            print("  No issues.")
        print()

    print("--- Duplicate check across all rows ---")
    dupes = check_duplicate_rows(test_rows)
    if dupes:
        for issue in dupes:
            print("   -", issue)
    else:
        print("  No duplicates found.")
