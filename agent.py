import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

load_dotenv()

anomaly_agent=Agent(
    model=Groq(id="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY")),
    description="You explain data anomalies found in a spreadsheet, clearly and briefly for a non-technical business owner.",
)

def get_alert_message(row: dict, issues: list[str]) -> str:
    issues_text="\n".join(f"- {issue}" for issue in issues)
    prompt=f"""A spreadsheet anomaly was detected.
Row data: {row}
Issues found:
{issues_text}

Write a short, clear email explaining this to a non-technical business owner.
Keep it brief- a few sentences. Do not use technical jargon."""

    response=anomaly_agent.run(prompt)
    return response.content

if __name__=="__main__":
    test_row = {"Date": "20/12/2026", "Category": "T-shirts", "Amount": -60}
    test_issues = ["Amount: Value -60 is below minimum allowed (0)."]

    message = get_alert_message(test_row, test_issues)
    print(message)