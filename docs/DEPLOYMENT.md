# Deployment Instructions: Restaurant Reservation LLM App

This document describes how to deploy the multi-turn, LLM-driven restaurant reservation system using Streamlit, Flask, Twilio, and OpenAI.

## 1. Prerequisites
- Python 3.8+
- Twilio account with Programmable Voice enabled
- OpenAI API key (for GPT-4.1-mini)
- Publicly accessible server or tunneling tool (e.g., ngrok) for the webhook

## 2. Set Up Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Verify you're in the virtual environment
which python  # Should point to the venv directory
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 4. Set Environment Variables
Create a `.env` file or set these variables in your environment:
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number
OPENAI_API_KEY=your_openai_api_key
WEBHOOK_URL=https://<your-public-domain-or-ngrok>/twilio_webhook
```

## 5. Run the Webhook Server
The webhook server handles the live conversation loop with the restaurant.
```bash
python webhook_server.py
```
If running locally, expose it to the internet (for Twilio to reach it) using ngrok:
```bash
ngrok http 5000
```
Copy the HTTPS URL from ngrok and set it as `WEBHOOK_URL`.

## 6. Configure Twilio
- Ensure your Twilio number has voice capability.
- When placing calls from the app, the webhook URL will be used as the TwiML callback.

## 7. Run the Streamlit App
```bash
streamlit run app.py
```

## 8. Usage
- Enter reservation details in the Streamlit UI and submit.
- The app will place a call to the restaurant and the LLM will converse until a reservation is confirmed or declined.
- The full conversation will be displayed in the UI after the call.

## 9. Notes
- For production, deploy the webhook server on a cloud VM or serverless platform with HTTPS.
- Conversation state is stored in memory—if the server restarts, active calls will lose context.
- For advanced logging or persistence, extend `conversation_manager.py`.

---
For troubleshooting or more advanced deployment (Docker, cloud, etc.), please ask for additional instructions.
