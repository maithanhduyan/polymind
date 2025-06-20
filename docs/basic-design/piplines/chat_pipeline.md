🔤 User Input (Frontend)
    ↓ WebSocket
💬 chat_handler.py (WebSocket Handler)
    ↓ Message Processing  
🎯 agent_manager.py (Router)
    ↓ Agent Selection
🤖 deepseek.py (AI Agent)
    ↓ API Call
🌐 Together.xyz API (DeepSeek V3)
    ↓ AI Response
🤖 deepseek.py (Response Processing)
    ↓ Agent Response
🎯 agent_manager.py (Return)
    ↓ WebSocket Response
💬 chat_handler.py (Send Response)
    ↓ WebSocket
📱 Frontend (Display Response)