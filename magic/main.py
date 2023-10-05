from fastapi import FastAPI
from pydantic import BaseModel

class Prompt(BaseModel):
    data: str

app = FastAPI()

@app.post("/")
async def dymmy(prompt: Prompt):
        return prompt