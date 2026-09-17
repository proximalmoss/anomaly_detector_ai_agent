import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

load_dotenv()

anomaly_agent=Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY")),
    description="You explain data anomalies found in a spreadsheet, clearly and briefly for a non-technical business owner.",
)

def get_alert_message(row: dict, issues: list[str]) -> str:
    lines=[
        "An anomaly was detected in your spreadsheet"
        "",
        f"Row data: {row}",
        "",
        "Issues found:",
    ]
    for issue in issues:
        lines.append(f"- {issue}")

    return "\n".join(lines)