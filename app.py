import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Load your OpenAI API key from the environment
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# You can change this to your custom Cortex model if you like,
# or set MODEL via env var.
MODEL = os.environ.get("MODEL_NAME", "gpt-4o-mini")

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Receives JSON from Zapier with keys like:
      { "transcript": "...",
        "summary": "...",
        "title": "...",
        "timestamp": "..." }
    Forwards to OpenAI and returns the assistant's response.
    """
    data = request.get_json(force=True)  # parse JSON
    transcript = data.get("transcript", "")
    summary    = data.get("summary", "")
    title      = data.get("title", "")
    timestamp  = data.get("timestamp", "")

    prompt = f"""
New file received:
Title: {title}
Timestamp: {timestamp}

Transcript:
{transcript}

Summary:
{summary}

Please ingest this into your knowledge base.
"""
    try:
        resp = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that ingests transcripts into memory."},
                {"role": "user",   "content": prompt},
            ],
        )
        answer = resp.choices[0].message.content
        return jsonify({"status": "ok", "response": answer}), 200

    except Exception as e:
        # Log the error and return a 500 so Zapier knows it failed
        app.logger.error(f"OpenAI API error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Use the PORT Render gives you, default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 so Render’s port scanner can detect it
    app.run(host="0.0.0.0", port=port)
