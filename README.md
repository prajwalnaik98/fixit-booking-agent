# FixIt Booking Agent

FixIt Booking Agent works for a home repair company in Pune. A customer types a request in plain words. The agent books a visit, gives a price without booking, or cancels a booking, and follows the company rules every time. All prices and fees are worked out by Python code in `tools.py`; the model only chooses the tools and copies the numbers. Bookings are saved in `bookings.json`. It is built with the OpenAI Agents SDK, with a FastAPI back end and a Streamlit front end.

## Set up

Open the folder that directly contains `api.py` and `app.py` in VS Code (File, Open Folder). All commands below must be run from that folder.

1. Create and turn on a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate        (Windows)
   source .venv/bin/activate     (Mac / Linux)
   ```
2. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
3. Open the file named `.env` in this folder and put in your OpenAI key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

## Run

First test the tools on their own (no AI, no key needed):
```
python test_tools.py
```

Test only the agent in the terminal:
```
python agent.py
```

Run the 6 practice requests and write `test_results.md` (this deletes `bookings.json` first):
```
python run_practice.py
```

Run the full app. Open two terminals in this folder (with the virtual environment turned on).

Terminal 1, the back end:
```
uvicorn api:app --reload
```

Terminal 2, the front end:
```
streamlit run app.py
```

To test the back end on its own, open the test page: http://127.0.0.1:8000/docs

To start fresh, delete `bookings.json`.

## Troubleshooting

- `Could not import module "api"` or `File does not exist: app.py`: the terminal is in the wrong folder. Go to the folder that contains `api.py`.
- `AuthenticationError`: the key in `.env` is wrong. Fix it and restart uvicorn.
- `APIConnectionError`: run the commands from a terminal that does not show `(.venv)` if the virtual environment cannot reach OpenAI.
- The page says to start the back end: run `uvicorn api:app --reload` in its own terminal and leave it open.
