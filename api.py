"""FastAPI back end for FixIt Booking Agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import FixItResult, run_agent
from tools import load_bookings

app = FastAPI(title="FixIt Booking Agent API")


# The JSON body of POST /request
class RequestBody(BaseModel):
    message: str


@app.post("/request", summary="Book a visit, get a price or cancel a booking", response_model=FixItResult)
async def handle_request(body: RequestBody):
    # Check that the message is not empty
    if body.message.strip() == "":
        raise HTTPException(status_code=400, detail="Please type a request.")

    # Run the agent on the message
    return await run_agent(body.message.strip())


@app.get("/bookings", summary="List all bookings")
def bookings():
    return load_bookings()


@app.get("/health", summary="Check that the back end is running")
def health():
    return {"status": "ok"}
