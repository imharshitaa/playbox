# llm/mock_llm.py -- minimal mock LLM to explore prompt-injection behaviors
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Req(BaseModel):
    system: Optional[str] = ""
    user: str

SECRET="TOP_SECRET_ABC123"  # intentionally accessible inside server for tests

@app.post("/generate")
def generate(r: Req):
    # intentionally wrong design: user message can override system
    text = f"SYSTEM: {r.system}\nUSER: {r.user}\n"
    # simple injection trigger: if user asks for SECRET, return it (simulates flawed model)
    if "reveal secret" in r.user.lower() or "top_secret" in r.user.lower():
        return {"output": f"Here is the secret: {SECRET}"}
    # echo back combined prompt
    return {"output": text}
