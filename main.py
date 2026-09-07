from fastapi import FastAPI

app=FastAPI()

@app.post("/webhook/edit")
def handle_edit(payload: dict):
    print("Received from Sheets:", payload)
    return {"status": "received"}