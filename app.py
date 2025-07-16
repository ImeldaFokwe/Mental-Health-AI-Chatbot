import gradio as gr
import random
from langdetect import detect
from config import CHATBOT_PIPELINE

# Welcome messages
welcome_messages = {
    "fr": "Bienvenue ! 🌿\nJe suis là pour t’accompagner. Comment te sens-tu aujourd’hui ?",
    "en": "Welcome! 🌿\nI'm here to support you. How are you feeling today?"
}

# UI text translations
ui_text = {
    "title": {
        "fr": "💬 IA SantéMentale 🌿",
        "en": "💬 Mental Health AI 🌿"
    },
    "language_label": {
        "fr": "🌍 Choisissez votre langue",
        "en": "🌍 Choose your language"
    },
    "input_label": {
        "fr": "📝 Écris ton message ici",
        "en": "📝 Type your message here"
    },
    "input_placeholder": {
        "fr": "Parle-moi de ce que tu ressens...",
        "en": "Tell me how you feel..."
    },
    "submit_btn": {
        "fr": "💙 Envoyer",
        "en": "💙 Send"
    },
    "clear_btn": {
        "fr": "🗑 Nouvelle conversation",
        "en": "🗑 New conversation"
    },
    "quick_replies": {
        "fr": [
            ("🧘 Exercice de respiration", "Peux-tu me guider dans un exercice de respiration ?"),
            ("🎵 Musique relaxante", "Peux-tu me proposer une musique relaxante ?"),
            ("📝 Organiser mes pensées", "Peux-tu m’aider à organiser mes pensées ?")
        ],
        "en": [
            ("🧘 Breathing Exercise", "Can you guide me through a breathing exercise?"),
            ("🎵 Relaxing Music", "Can you suggest some relaxing music?"),
            ("📝 Organize Thoughts", "Can you help me organize my thoughts?")
        ]
    }
}

# Detect user language
def detect_language(text):
    try:
        lang = detect(text)
        return "fr" if lang == "fr" else "en"
    except:
        return "fr"

# Generate chatbot response
def chatbot_response(user_input, selected_language, chat_history):
    if not user_input.strip():
        return chat_history, " Veuillez entrer un message." if selected_language == "fr" else " Please enter a message."

    prompt = f"Respond strictly in {selected_language}. User: {user_input}\nChatbot:"
    try:
        response = CHATBOT_PIPELINE.generate_content(prompt)
        chatbot_reply = response.text
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": chatbot_reply})
        return chat_history, ""
    except Exception:
      friendly_message = {
        "fr": "⚠️ Une erreur est survenue lors de la connexion au serveur. Veuillez réessayer dans quelques instants.",
        "en": "⚠️ An error occurred while connecting to the server. Please try again in a few moments."
      }
      return chat_history, friendly_message.get(selected_language, "An error occurred.")


# Handle quick replies
def handle_quick_reply(message, selected_language, chat_history):
    return chatbot_response(message, selected_language, chat_history)

# Reset chat
def reset_chat():
    return [], ""

# Interface
def launch_chatbot():
    with gr.Blocks(css="""
        body { background-color: #f5f5f5; font-family: 'Arial', sans-serif; }
        .chat-container { width: 60%; margin: auto; padding: 20px; background: #fff; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
        .chat-title { color: #2c3e50; font-size: 22px; text-align: center; font-weight: bold; }
        .chat-message-container { display: flex; flex-direction: column; }
    """) as demo:

        selected_language = gr.Radio(["fr", "en"], label="🌍 Choisissez votre langue / Choose your language", value="fr")

        chat_title = gr.Markdown()
        welcome_text = gr.Markdown()
        chat_box = gr.Chatbot(label="💬 Discussion", elem_id="chatbox", type="messages")
        user_input = gr.Textbox()
        submit_btn = gr.Button()
        clear_btn = gr.Button()

        # Function to update all text elements when language changes
        def update_ui_texts(lang):
            return (
                ui_text["title"][lang],
                welcome_messages[lang],
                gr.update(label=ui_text["input_label"][lang], placeholder=ui_text["input_placeholder"][lang]),
                gr.update(value=""),
                gr.update(value=ui_text["submit_btn"][lang]),
                gr.update(value=ui_text["clear_btn"][lang]),
                *[gr.update(value=btn[0]) for btn in ui_text["quick_replies"][lang]]
            )

        quick_option_1 = gr.Button()
        quick_option_2 = gr.Button()
        quick_option_3 = gr.Button()

        selected_language.change(
            update_ui_texts,
            inputs=[selected_language],
            outputs=[chat_title, welcome_text, user_input, user_input, submit_btn, clear_btn, quick_option_1, quick_option_2, quick_option_3]
        )

        # Chatbot submission
        submit_btn.click(chatbot_response, inputs=[user_input, selected_language, chat_box], outputs=[chat_box, user_input])
        clear_btn.click(reset_chat, outputs=[chat_box, user_input])

        # Quick reply logic
        def reply_1(lang, chat_history): return handle_quick_reply(ui_text["quick_replies"][lang][0][1], lang, chat_history)
        def reply_2(lang, chat_history): return handle_quick_reply(ui_text["quick_replies"][lang][1][1], lang, chat_history)
        def reply_3(lang, chat_history): return handle_quick_reply(ui_text["quick_replies"][lang][2][1], lang, chat_history)

        quick_option_1.click(reply_1, inputs=[selected_language, chat_box], outputs=[chat_box, user_input])
        quick_option_2.click(reply_2, inputs=[selected_language, chat_box], outputs=[chat_box, user_input])
        quick_option_3.click(reply_3, inputs=[selected_language, chat_box], outputs=[chat_box, user_input])

        # Initial text load
        demo.load(fn=update_ui_texts, inputs=[selected_language], outputs=[chat_title, welcome_text, user_input, user_input, submit_btn, clear_btn, quick_option_1, quick_option_2, quick_option_3])

    demo.launch()

# Run it
if __name__ == "__main__":
    launch_chatbot()
