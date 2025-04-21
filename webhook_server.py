from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from conversation_manager import ConversationManager

app = Flask(__name__)
conv_mgr = ConversationManager()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = "You are an automated reservation administrator calling a restaurant on behalf of a guest. Your job is to politely introduce yourself, request a reservation for the specified time and party size, and negotiate if the exact time is unavailable (user may be flexible). Keep the conversation natural and confirm the outcome. End the conversation if the reservation is confirmed or not possible."

@app.route("/twilio_webhook", methods=["POST"])
def twilio_webhook():
    call_sid = request.values.get("CallSid")
    speech_result = request.values.get("SpeechResult")
    digits = request.values.get("Digits")
    is_new = False

    # On first call, start conversation history
    if not conv_mgr.get_history(call_sid):
        # Get reservation details from custom params (sent in Twilio API call)
        restaurant_name = request.values.get("restaurant_name", "the restaurant")
        reservation_time = request.values.get("reservation_time", "7:00 PM")
        party_size = request.values.get("party_size", "2")
        flex_minutes = request.values.get("flex_minutes", "0")
        user_prompt = f"Call {restaurant_name}. Request a reservation for {party_size} people at {reservation_time}."
        if flex_minutes and int(flex_minutes) > 0:
            user_prompt += f" If not available, accept a time up to {flex_minutes} minutes earlier or later."
        else:
            user_prompt += " Do not accept other times."
        conv_mgr.start_conversation(call_sid, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])
        is_new = True

    # If not new, append restaurant's response
    if not is_new and (speech_result or digits):
        restaurant_reply = speech_result or f"Pressed {digits}"
        conv_mgr.append(call_sid, "user", restaurant_reply)

    # Get LLM's next reply
    history = conv_mgr.get_history(call_sid)
    ai_response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=history,
        max_tokens=300,
        temperature=0.6
    ).choices[0].message.content.strip()
    conv_mgr.append(call_sid, "assistant", ai_response)

    # Check for end of conversation
    if any(x in ai_response.lower() for x in ["reservation is confirmed", "cannot make the reservation", "goodbye", "thank you, goodbye"]):
        conv_mgr.set_status(call_sid, "done")
        resp = VoiceResponse()
        resp.say(ai_response)
        resp.hangup()
        return Response(str(resp), mimetype="text/xml")

    # Otherwise, continue the loop
    resp = VoiceResponse()
    gather = Gather(input="speech dtmf", timeout=6, num_digits=1, action="/twilio_webhook", method="POST")
    gather.say(ai_response)
    resp.append(gather)
    return Response(str(resp), mimetype="text/xml")

if __name__ == "__main__":
    app.run(port=5000)
