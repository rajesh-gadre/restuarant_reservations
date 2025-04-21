import streamlit as st
from twilio.rest import Client
import openai
import os
import time

st.set_page_config(page_title="Restaurant Reservation Caller", page_icon="🍽️")
st.title("🍽️ Restaurant Reservation Caller")

st.markdown("""
Enter the restaurant details and your reservation request. When you submit, the app will call the restaurant using Twilio and deliver your reservation details via a voice call.
""")

# Twilio credentials (read from environment variables for security)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

OPENAI_API_KEY = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else os.getenv("OPENAI_API_KEY")
if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER and OPENAI_API_KEY):
    st.warning("Please set your Twilio credentials as environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, and OPENAI_API_KEY (or add openai_api_key to Streamlit secrets).")
    st.stop()
openai.api_key = OPENAI_API_KEY

with st.form("reservation_form"):
    restaurant_name = st.text_input("Restaurant Name", max_chars=64)
    restaurant_phone = st.text_input("Restaurant Phone Number (in E.164 format, e.g. +14155552671)")
    reservation_time = st.text_input("Reservation Time (e.g. 7:00 PM)")
    party_size = st.number_input("Party Size", min_value=1, max_value=50, value=2)
    flex_time = st.checkbox("I'm open to an earlier or later reservation if my requested time isn't available.")
    flex_minutes = 0
    if flex_time:
        flex_minutes = st.number_input("How many minutes earlier or later?", min_value=5, max_value=120, value=15, step=5)
    submitted = st.form_submit_button("Call Restaurant")

if submitted:
    if not all([restaurant_name, restaurant_phone, reservation_time, party_size]):
        st.error("Please fill in all fields.")
    else:
        st.info("Placing call and starting multi-turn AI-powered conversation...")
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            # Build params for webhook
            params = {
                'restaurant_name': restaurant_name,
                'reservation_time': reservation_time,
                'party_size': str(party_size),
                'flex_minutes': str(flex_minutes if flex_time else 0),
            }
            # Place call with Twilio, using webhook_server.py endpoint
            webhook_url = os.getenv("WEBHOOK_URL", "https://your-server.com/twilio_webhook")
            call = client.calls.create(
                to=restaurant_phone,
                from_=TWILIO_FROM_NUMBER,
                url=webhook_url + '?' + '&'.join(f"{k}={v}" for k, v in params.items())
            )
            st.success(f"Call placed! Twilio Call SID: {call.sid}")
            st.markdown(
                "The AI will now converse with the restaurant until a reservation is made or declined. "
                "You can view the conversation history below once the call completes."
            )
            # Poll for conversation result (demo: simulate)
            import time
            from conversation_manager import ConversationManager
            conv_mgr = ConversationManager()
            status = None
            for _ in range(30):
                time.sleep(2)
                status = conv_mgr.get_status(call.sid)
                if status == "done":
                    break
            if status == "done":
                history = conv_mgr.get_history(call.sid)
                st.markdown("**Full Conversation:**")
                for turn in history:
                    st.markdown(f"**{turn['role'].capitalize()}:** {turn['content']}")
            else:
                st.warning("The conversation is still ongoing or could not be retrieved. Please check Twilio logs or your webhook server.")
        except Exception as e:
            st.error(f"Failed to place call: {e}")
