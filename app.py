"""Streamlit front end for FixIt Booking Agent. It calls the FastAPI back end."""

import html

import requests
import streamlit as st

# Address of the FastAPI back end
API_URL = "http://127.0.0.1:8000"

# Shown when the back end cannot be reached
BACKEND_DOWN_MESSAGE = "Start the back end first: uvicorn api:app --reload"

# Example requests the customer can click to fill the text box
EXAMPLE_PRICE = "How much for fixing a leaking pipe under my kitchen sink on Wednesday? I live in 411004."
EXAMPLE_BOOKING = "My kitchen tap is leaking. Please send a plumber on Tuesday morning. Meera Joshi, 9876543210, pin 411038."
EXAMPLE_CANCEL = "Please cancel my booking FX-1001."

# How each status is shown: a label and a colour name used by the CSS
STATUS_LABELS = {
    "booked": ["Booked", "green"],
    "quote_only": ["Price quote", "blue"],
    "cancelled": ["Cancelled", "grey"],
    "need_more_info": ["More details needed", "amber"],
    "cannot_help": ["We cannot help with this", "red"],
    "stopped": ["Stopped", "red"],
}

# The look of the page (colours, cards, badges)
PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', 'Segoe UI', sans-serif; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.stApp { background: #F4F6FA; }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 3rem; }

.topbar { display: flex; justify-content: space-between; align-items: center; background: #0B2A4A;
  color: #FFFFFF; padding: 14px 24px; border-radius: 14px; }
.brand { display: flex; align-items: baseline; gap: 12px; }
.logo { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }
.logo span { color: #F26B21; }
.brand-sub { font-size: 0.85rem; color: #B8C7DB; }
.week-pill { background: rgba(255,255,255,0.12); padding: 6px 14px; border-radius: 999px; font-size: 0.82rem; }

.hero { padding: 38px 4px 8px 4px; text-align: center; }
.hero h1 { font-size: 2.3rem; font-weight: 800; color: #0B2A4A; margin: 0 0 8px 0; letter-spacing: -1px; }
.hero p { font-size: 1.05rem; color: #51607A; margin: 0 auto; max-width: 720px; line-height: 1.55; }

.trust { display: flex; gap: 12px; margin: 24px 0 28px 0; flex-wrap: wrap; justify-content: center; }
.trust-item { background: #FFFFFF; border: 1px solid #E3E8F0; border-radius: 12px; padding: 12px 18px; min-width: 190px; text-align: center; }
.trust-item b { display: block; color: #0B2A4A; font-size: 1.05rem; }
.trust-item span { color: #6B7A93; font-size: 0.8rem; }

.section-title { font-size: 1.05rem; font-weight: 700; color: #0B2A4A; margin: 0 0 4px 0; }
.section-sub { font-size: 0.85rem; color: #6B7A93; margin: 0 0 12px 0; }

div[data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; border-radius: 16px;
  border: 1px solid #E3E8F0; box-shadow: 0 2px 10px rgba(11,42,74,0.05); }
.stTextArea, .stTextArea > div, .stTextArea div[data-baseweb] { width: 100% !important; }
.stTextArea textarea { width: 100% !important; white-space: pre-wrap; border-radius: 10px; border: 1px solid #CBD5E3; font-size: 0.97rem; }
.stTextArea textarea:focus { border-color: #F26B21; box-shadow: 0 0 0 1px #F26B21; }
.stButton > button { border-radius: 10px; font-weight: 600; padding: 0.55rem 1rem; border: 1px solid #CBD5E3; }
.stButton > button[kind="primary"] { background: #F26B21; border: none; color: #FFFFFF; }
.stButton > button[kind="primary"]:hover { background: #D95A14; color: #FFFFFF; }

.result { padding: 4px 2px 8px 2px; }
.empty { color: #6B7A93; text-align: center; padding: 70px 20px; }
.empty b { display: block; color: #0B2A4A; font-size: 1.05rem; margin-bottom: 6px; }
.badge { display: inline-block; padding: 5px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.4px; }
.badge.green { background: #DDF5E7; color: #12703A; }
.badge.blue { background: #DDEBFF; color: #1553A8; }
.badge.grey { background: #E8ECF2; color: #44526B; }
.badge.amber { background: #FFF0CF; color: #8A5A00; }
.badge.red { background: #FFE0E0; color: #A32020; }
.message { margin: 14px 0 0 0; font-size: 1.02rem; color: #14213D; line-height: 1.55; }
.booking-id { margin: 18px 0 0 0; padding: 14px 18px; background: #F4F6FA; border-radius: 12px; }
.booking-id small { color: #6B7A93; display: block; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
.booking-id b { font-size: 1.7rem; color: #0B2A4A; letter-spacing: 0.5px; }
.details { margin: 14px 0 0 0; color: #51607A; font-size: 0.92rem; }
.details b { color: #14213D; }
div[data-testid="stMarkdownContainer"] table.price { width: 100%; border-collapse: collapse; border: none; margin-top: 16px; font-size: 0.95rem; }
div[data-testid="stMarkdownContainer"] table.price td { border: none; border-bottom: 1px solid #EDF0F5; padding: 11px 4px; color: #34435E; background: transparent; }
div[data-testid="stMarkdownContainer"] table.price td.amount { text-align: right; font-variant-numeric: tabular-nums; }
div[data-testid="stMarkdownContainer"] table.price tr.total td { border-bottom: none; border-top: 2px solid #0B2A4A; font-weight: 800; font-size: 1.15rem; color: #0B2A4A; padding-top: 14px; }
.fee-box { margin-top: 16px; padding: 16px 18px; border-radius: 12px; background: #F4F6FA; }
.fee-box small { color: #6B7A93; display: block; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
.fee-box b { font-size: 1.7rem; color: #0B2A4A; }

div[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #E3E8F0; border-radius: 12px; padding: 14px 18px; }
div[data-testid="stMetricLabel"] p { color: #6B7A93; font-size: 0.82rem; }
div[data-testid="stMetricValue"] { color: #0B2A4A; font-weight: 800; }
.footer { text-align: center; color: #8A97AD; font-size: 0.8rem; margin-top: 36px; }
</style>
"""


def error_text(response) -> str:
    """Get the error message from a back-end response."""
    try:
        return str(response.json()["detail"])
    except (ValueError, KeyError):
        return "Something went wrong in the back end. Please try again."


def call_fixit(message: str) -> dict:
    """Send the customer's message to POST /request. Return the result or an error."""
    try:
        response = requests.post(f"{API_URL}/request", json={"message": message}, timeout=120)
    except requests.exceptions.ConnectionError:
        return {"error": BACKEND_DOWN_MESSAGE}
    except requests.exceptions.Timeout:
        return {"error": "The agent took too long to answer. Please try again."}

    if response.status_code != 200:
        return {"error": error_text(response)}
    return response.json()


def use_example(example_text: str) -> None:
    """Put an example request into the text box."""
    st.session_state["request_text"] = example_text


# ----- Pieces of the page -----
def show_header() -> None:
    """Show the top bar, the headline and the trust strip."""
    st.markdown(
        '<div class="topbar"><div class="brand"><div class="logo">Fix<span>It</span></div>'
        '<div class="brand-sub">Home Services, Pune</div></div>'
        '<div class="week-pill">Booking week: 2 to 8 November 2026</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero"><h1>Book a trusted technician in one message</h1>'
        "<p>Type what you need in plain words. The agent books a visit, gives a price or cancels "
        "a booking, and follows the company rules every time.</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="trust">'
        '<div class="trust-item"><b>4 types of work</b><span>Plumber, electrician, AC, carpenter</span></div>'
        '<div class="trust-item"><b>3 slots a day</b><span>Morning, afternoon, evening</span></div>'
        '<div class="trust-item"><b>Clear pricing</b><span>Visit charge and GST included</span></div>'
        '<div class="trust-item"><b>30-day warranty</b><span>On every repair</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def show_request_form() -> None:
    """Show the text box, the example buttons and the Send button."""
    st.markdown('<p class="section-title">Your request</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Tell us the problem, your name, mobile number, pin code, day and time.</p>',
        unsafe_allow_html=True,
    )
    st.text_area(
        "Your request",
        key="request_text",
        height=150,
        label_visibility="collapsed",
        placeholder="Example: My kitchen tap is leaking. Please send a plumber on Tuesday morning. "
        "Meera Joshi, 9876543210, pin 411038.",
    )

    # Example buttons
    st.caption("Try an example")
    first, second, third = st.columns(3)
    first.button("Get a price", on_click=use_example, args=[EXAMPLE_PRICE], width="stretch")
    second.button("Book a visit", on_click=use_example, args=[EXAMPLE_BOOKING], width="stretch")
    third.button("Cancel a booking", on_click=use_example, args=[EXAMPLE_CANCEL], width="stretch")

    # Run the agent when the button is clicked
    if st.button("Send request", type="primary", width="stretch"):
        if st.session_state["request_text"].strip() == "":
            st.warning("Please type a request first.")
        else:
            with st.spinner("The agent is working on your request..."):
                st.session_state["result"] = call_fixit(st.session_state["request_text"])


def price_table_html(result: dict) -> str:
    """Build the price breakdown table."""
    price_rows = [
        ["Service price", result["job_price"]],
        ["Visit charge", result["visit_charge"]],
        ["Weekend extra", result["weekend_extra"]],
        ["GST (18%)", result["gst"]],
    ]
    table = '<table class="price">'
    for row in price_rows:
        table += f'<tr><td>{row[0]}</td><td class="amount">Rs. {row[1]}</td></tr>'
    table += f'<tr class="total"><td>Total</td><td class="amount">Rs. {result["total_price"]}</td></tr>'
    return table + "</table>"


def result_html(result: dict) -> str:
    """Build the result card for one agent answer."""
    label, colour = STATUS_LABELS.get(result["status"], ["Result", "grey"])
    card = f'<div class="result"><span class="badge {colour}">{label}</span>'
    card += f'<p class="message">{html.escape(result["message"])}</p>'

    # A booking ID, if there is one
    if result["booking_id"] != "":
        card += f'<div class="booking-id"><small>Booking ID</small><b>{html.escape(result["booking_id"])}</b></div>'

    # What was booked, priced or cancelled
    if result["service_name"] != "":
        details = f'<b>{html.escape(result["service_name"])}</b>'
        if result["date"] != "":
            details += f' on {html.escape(result["date"])}'
        if result["slot"] != "":
            details += f', {html.escape(result["slot"])}'
        card += f'<p class="details">{details}</p>'

    # The price table for a booking or a quote, the fee for a cancellation
    if result["status"] in ["booked", "quote_only"]:
        card += price_table_html(result)
    if result["status"] == "cancelled":
        card += f'<div class="fee-box"><small>Cancellation fee</small><b>Rs. {result["cancellation_fee"]}</b></div>'
    return card + "</div>"


def show_result() -> None:
    """Show the agent's answer, an error, or an empty box."""
    st.markdown('<p class="section-title">Our answer</p>', unsafe_allow_html=True)
    if "result" not in st.session_state:
        st.markdown(
            '<div class="result"><div class="empty"><b>Your answer will appear here</b>'
            "Send a request to get a price, a booking or a cancellation.</div></div>",
            unsafe_allow_html=True,
        )
        return

    result = st.session_state["result"]
    if "error" in result:
        st.error(result["error"])
        return
    st.markdown(result_html(result), unsafe_allow_html=True)


def make_table_rows(rows: list) -> list:
    """Build the rows for the bookings table, newest first."""
    table_rows = []
    for row in reversed(rows):
        table_rows.append({
            "Booking ID": row["booking_id"],
            "Customer": row["name"],
            "Phone": "******" + row["phone"][-4:],
            "Service": row["service_name"],
            "Date": row["date"],
            "Slot": row["slot"],
            "Area": row["area"],
            "Total (Rs.)": row["total_price"],
            "Status": row["status"].capitalize(),
        })
    return table_rows


def show_bookings() -> None:
    """Show all bookings from GET /bookings as numbers and a table."""
    st.markdown('<p class="section-title">All bookings</p>', unsafe_allow_html=True)
    try:
        response = requests.get(f"{API_URL}/bookings", timeout=10)
    except requests.exceptions.RequestException:
        st.error(BACKEND_DOWN_MESSAGE)
        return

    rows = response.json()
    confirmed = 0
    cancelled = 0
    for row in rows:
        if row["status"] == "confirmed":
            confirmed = confirmed + 1
        else:
            cancelled = cancelled + 1

    first, second, third = st.columns(3)
    first.metric("Total bookings", len(rows))
    second.metric("Confirmed", confirmed)
    third.metric("Cancelled", cancelled)

    if len(rows) == 0:
        st.info("No bookings yet. Send a request above to make the first one.")
    else:
        st.dataframe(make_table_rows(rows), hide_index=True, width="stretch")


# ----- Page -----
st.set_page_config(page_title="FixIt Home Services", layout="wide")
st.markdown(PAGE_CSS, unsafe_allow_html=True)

show_header()

# Request on the left, answer on the right
left_column, right_column = st.columns([5, 6], gap="large")
with left_column:
    with st.container(border=True):
        show_request_form()
with right_column:
    with st.container(border=True):
        show_result()

st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
show_bookings()

st.markdown('<div class="footer">FixIt Home Services, Pune. All repairs come with a 30-day warranty.</div>', unsafe_allow_html=True)
