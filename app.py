from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key here directly or use an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    transcript = data.get('transcript', '')

    if not transcript:
        return jsonify({'error': 'No transcript provided'}), 400

    # Save transcript to a temporary file
    with open("transcript.txt", "w") as f:
        f.write(transcript)

    # Upload file to OpenAI
    file_response = openai.files.create(
        file=open("transcript.txt", "rb"),
        purpose='assistants'
    )

    # Create thread and store message
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Here is a new transcription.",
    attachments=[
    {
        "file_id": file_response.id,
        "tools": [{"type": "file_search"}]
    }
]

)


    return jsonify({
        "status": "success",
        "thread_id": thread.id,
        "file_id": file_response.id
    }), 200

if __name__ == '__main__':
    app.run(port=5000)
