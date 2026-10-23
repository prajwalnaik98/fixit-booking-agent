"""Delete bookings.json, send the 6 practice requests in order and write test_results.md.
Run with: python run_practice.py (needs your OpenAI key in .env)"""

import asyncio
import os

import tools
from agent import run_agent

# What each practice request should give: status, booking ID, total or fee
EXPECTED = [
    ("quote_only", "", 529),
    ("booked", "FX-1001", 352),
    ("booked", "FX-1002", 588),
    ("booked", "FX-1001", 352),
    ("cancelled", "FX-1002", 0),
    ("cannot_help", "", 0),
]


def read_requests() -> list:
    """Read practice_requests.txt. Requests are separated by a line with ---."""
    with open("practice_requests.txt", "r", encoding="utf-8") as file:
        parts = file.read().split("---")
    requests_list = []
    for part in parts:
        if part.strip() != "":
            requests_list.append(part.strip())
    return requests_list


def write_section(number: int, request: str, result, row_count: int) -> str:
    """Build the test_results.md section for one request."""
    expected_status, expected_id, expected_number = EXPECTED[number - 1]
    label = "Total"
    got_number = result.total_price
    if result.status == "cancelled":
        label = "Fee"
        got_number = result.cancellation_fee

    is_right = result.status == expected_status and result.booking_id == expected_id and got_number == expected_number
    if number == 4 and row_count != 2:
        is_right = False
    verdict = "Right. It matches the expected result."
    if not is_right:
        verdict = f"Check this one. Expected {expected_status} {expected_id} {expected_number}."

    print(f"Request {number}: {result.status} {result.booking_id} {got_number} -> {verdict}")
    return (
        f"## Request {number}\n\nRequest: {request}\n\n"
        f"- Status: {result.status}\n"
        f"- Booking ID: {result.booking_id or 'none'}\n"
        f"- {label}: Rs. {got_number}\n"
        f"- Rows in bookings.json: {row_count}\n"
        f"- Verdict: {verdict}\n"
    )


async def run_all() -> None:
    """Run every practice request in one event loop and write test_results.md."""
    if os.path.exists(tools.BOOKINGS_FILE):
        os.remove(tools.BOOKINGS_FILE)

    sections = ["# Test results\n"]
    number = 1
    for request in read_requests():
        result = await run_agent(request)
        sections.append(write_section(number, request, result, len(tools.load_bookings())))
        number = number + 1

    with open("test_results.md", "w", encoding="utf-8") as file:
        file.write("\n".join(sections))
    print("Wrote test_results.md")


if __name__ == "__main__":
    asyncio.run(run_all())
