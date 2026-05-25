import sys
import os
from datetime import datetime

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.chatservice.handler import ChatHandler
from core.config import get_settings
from services.sessionservice.memory import InMemorySessionStore
from services.ragservice import (
    KnowledgeBaseBuilder,
    Retriever,
    SimpleEmbedder,
)
from services.escalationservice.trigger import EscalationEngine
from core.guardrails import Guardrails

# Initialize all components
settings = get_settings()
session_store = InMemorySessionStore()
embedder = SimpleEmbedder()
kb_builder = KnowledgeBaseBuilder(embedder)
retriever = Retriever(embedder)
escalation_engine = EscalationEngine()
guardrails = Guardrails()
chat_handler = ChatHandler(
    retriever=retriever,
    session_store=session_store,
    escalation_engine=escalation_engine,
    guardrails=guardrails,
)

# Test messages to send
TEST_MESSAGES = [
    "Hello!",
    "How do I track my order?",
    "This product is terrible! I'm so frustrated!",
    "I need to speak to a human agent please.",
    "Thank you for your help!",
]

# Company to use for testing
COMPANY_SLUG = "demo-company"

def main():
    print("=" * 60)
    print("AI Customer Care Bot - Test Demo")
    print("=" * 60)
    print()
    
    conversation = []
    
    # Create a session
    session_id = None
    
    for i, user_message in enumerate(TEST_MESSAGES):
        print(f"Message {i+1}/{len(TEST_MESSAGES)}: {user_message}")
        print("-" * 60)
        
        # Get chat response
        response = chat_handler.handle_chat(
            user_message=user_message,
            company_slug=COMPANY_SLUG,
            session_id=session_id,
        )
        
        # Store session ID for continuity
        if session_id is None:
            session_id = response.session_id
        
        # Store in conversation
        conversation.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_message,
            "bot": response.response,
            "is_escalated": response.is_escalated,
            "confidence": response.confidence,
            "sources": response.retrieved_sources,
        })
        
        print(f"Bot Response: {response.response}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Escalated: {response.is_escalated}")
        if response.retrieved_sources:
            print(f"Sources: {', '.join(response.retrieved_sources)}")
        print()
    
    # Generate HTML file
    html_content = generate_html(conversation)
    
    html_path = os.path.join(os.path.dirname(__file__), "chatbot_responses.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("=" * 60)
    print(f"✅ Test complete! HTML file generated at: {html_path}")
    print("=" * 60)

def generate_html(conversation):
    """Generate an HTML file with the chat conversation."""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Customer Care Bot - Test Responses</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        
        .chat-container {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .message {{
            margin-bottom: 25px;
            padding: 20px;
            border-radius: 12px;
            animation: fadeIn 0.3s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .user-message {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 50px;
        }}
        
        .bot-message {{
            background: #f0f4ff;
            color: #333;
            margin-right: 50px;
        }}
        
        .message-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .message-content {{
            font-size: 16px;
            line-height: 1.6;
        }}
        
        .message-meta {{
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.2);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 12px;
        }}
        
        .bot-message .message-meta {{
            border-top-color: rgba(0,0,0,0.1);
        }}
        
        .meta-tag {{
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 500;
        }}
        
        .meta-tag.confidence {{
            background: rgba(255,255,255,0.2);
        }}
        
        .bot-message .meta-tag.confidence {{
            background: #e0e7ff;
            color: #3730a3;
        }}
        
        .meta-tag.escalated {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .meta-tag.sources {{
            background: #f0fdf4;
            color: #166534;
        }}
        
        .footer {{
            margin-top: 20px;
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Customer Care Bot - Test Responses</h1>
            <p>Generated on {timestamp} • {count} messages tested</p>
        </div>
        
        <div class="chat-container">
            {messages_html}
        </div>
        
        <div class="footer">
            <p>Built with ❤️ using Gemini API and FastAPI</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Build messages HTML
    messages_html = ""
    for msg in conversation:
        # User message
        messages_html += f"""
        <div class="message user-message">
            <div class="message-header">
                <span>👤 You</span>
                <span>{msg['timestamp']}</span>
            </div>
            <div class="message-content">{msg['user']}</div>
        </div>
        """
        
        # Bot message with meta info
        meta_tags = []
        meta_tags.append(f'<span class="meta-tag confidence">Confidence: {msg["confidence"]:.2f}</span>')
        
        if msg['is_escalated']:
            meta_tags.append('<span class="meta-tag escalated">ESCALATED</span>')
        
        if msg['sources']:
            sources = ', '.join(msg['sources'])
            meta_tags.append(f'<span class="meta-tag sources">Sources: {sources}</span>')
        
        messages_html += f"""
        <div class="message bot-message">
            <div class="message-header">
                <span>🤖 Bot</span>
                <span>{msg['timestamp']}</span>
            </div>
            <div class="message-content">{msg['bot']}</div>
            <div class="message-meta">
                {' '.join(meta_tags)}
            </div>
        </div>
        """
    
    # Render final HTML
    return html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d at %H:%M:%S"),
        count=len(conversation),
        messages_html=messages_html
    )

if __name__ == "__main__":
    main()
