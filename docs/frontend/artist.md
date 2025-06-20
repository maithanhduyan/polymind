ONLY USE HTML, CSS AND JAVASCRIPT. 
If you want to use any library, make sure to import it first.
If you want to use any icon, make sure to import the library first.
If you want to use any image, make sure it exist.
Try to create the best UI possible by using only HTML5, CSS3 and JAVASCRIPT. 
Use as much as you can CSS3 for the CSS, if you can't do something with CSS3, 
Then use custom CSS make sure to import:
```html
    <!-- Import Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Import Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```
in the head tag. 
 
Mobile First Responsive.

Also, try to ellaborate as much as you can, to create something unique. 

For Example:
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POLYMIND - AI Agent Workspace</title>
    
    <!-- Import Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Import Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* --- 1. CSS Variables & Global Styles --- */
    :root {
        --bg-dark: #0F172A;
        --bg-panel: #1E293B;
        --bg-panel-secondary: #334155;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --accent-primary: #3B82F6;
        --accent-primary-hover: #2563EB;
        --accent-secondary: #475569;
        --border-color: #334155;
        --success-color: #10B981;
        --font-main: 'Inter', sans-serif;
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
        --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body {
        height: 100%;
        overflow: hidden;
        font-family: var(--font-main);
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-size: 15px;
        line-height: 1.5;
    }

    /* --- Custom Scrollbar --- */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--accent-secondary);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }

    /* --- 2. Main Workspace Layout (Mobile First) --- */
    .polymind-workspace {
        display: flex;
        height: 100vh;
        width: 100vw;
        position: relative;
    }

    /* --- Sidebar --- */
    .sidebar {
        width: 260px;
        background-color: var(--bg-panel);
        border-right: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        padding: 16px;
        transition: transform 0.3s ease-in-out;
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        z-index: 100;
        transform: translateX(-100%);
    }

    .polymind-workspace.sidebar-open .sidebar {
        transform: translateX(0);
    }
    
    .sidebar-overlay {
        display: none;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.3);
        backdrop-filter: blur(2px);
        z-index: 99;
    }
    
    .polymind-workspace.sidebar-open .sidebar-overlay {
        display: block;
    }

    /* --- Chat Interface --- */
    .chat-interface {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        height: 100%;
        background-color: var(--bg-dark);
    }

    /* --- Context Panel --- */
    .context-panel {
        display: none;
        width: 300px;
        background-color: var(--bg-panel);
        border-left: 1px solid var(--border-color);
        padding: 20px;
        flex-direction: column;
    }

    /* --- 3. Sidebar Components --- */
    .sidebar-header {
        display: flex;
        align-items: center;
        margin-bottom: 24px;
        padding: 8px 0;
    }
    
    .sidebar-header .logo {
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--text-primary);
    }
    
    .sidebar-header .logo i {
        color: var(--accent-primary);
    }

    .new-chat-btn {
        width: 100%;
        padding: 10px 16px;
        background-color: var(--accent-primary);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: var(--transition);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .new-chat-btn:hover {
        background-color: var(--accent-primary-hover);
        box-shadow: var(--shadow-sm);
    }

    .sidebar-section {
        margin-bottom: 20px;
    }
    
    .sidebar-section-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--text-secondary);
        padding: 8px 0;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }

    .nav-list {
        list-style: none;
        max-height: 25vh;
        overflow-y: auto;
    }
    
    .nav-list li a {
        display: flex;
        align-items: center;
        padding: 10px 12px;
        color: var(--text-primary);
        text-decoration: none;
        border-radius: var(--radius-sm);
        transition: var(--transition);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 14px;
        gap: 12px;
    }
    
    .nav-list li a:hover {
        background-color: var(--accent-secondary);
    }
    
    .nav-list li a.active {
        background-color: var(--accent-primary);
        color: white;
    }
    
    .nav-list li a i {
        color: var(--text-secondary);
        width: 18px;
        text-align: center;
    }
    
    .nav-list li a.active i {
        color: white;
    }

    .sidebar-footer {
        margin-top: auto;
        border-top: 1px solid var(--border-color);
        padding-top: 16px;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        padding: 8px;
        border-radius: var(--radius-sm);
        transition: var(--transition);
        gap: 12px;
    }
    
    .user-profile:hover {
        background-color: var(--accent-secondary);
    }
    
    .user-profile img {
        width: 36px;
        height: 36px;
        border-radius: 50%;
    }
    
    .user-info .name {
        font-weight: 500;
        font-size: 14px;
    }
    
    .user-info .role {
        font-size: 12px;
        color: var(--text-secondary);
    }

    /* --- 4. Chat Interface Components --- */
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-bottom: 1px solid var(--border-color);
        background-color: var(--bg-panel);
    }
    
    .chat-header-title {
        display: flex;
        align-items: center;
        font-size: 15px;
        font-weight: 500;
        gap: 12px;
    }
    
    .chat-header-title i {
        color: var(--accent-primary);
    }

    .mobile-menu-toggle {
        display: block;
        background: none;
        border: none;
        color: var(--text-secondary);
        font-size: 18px;
        cursor: pointer;
        padding: 8px;
        transition: var(--transition);
    }
    
    .mobile-menu-toggle:hover {
        color: var(--text-primary);
    }
    
    .chat-header-actions {
        display: flex;
        gap: 8px;
    }
    
    .chat-header-actions button {
        background: none;
        border: none;
        color: var(--text-secondary);
        font-size: 16px;
        cursor: pointer;
        padding: 8px;
        border-radius: var(--radius-sm);
        transition: var(--transition);
    }
    
    .chat-header-actions button:hover {
        color: var(--text-primary);
        background-color: var(--accent-secondary);
    }

    .chat-log {
        flex-grow: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    
    .chat-message {
        display: flex;
        gap: 12px;
        max-width: 85%;
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-message .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        flex-shrink: 0;
        color: white;
    }
    
    .chat-message.user .avatar {
        background-color: var(--accent-secondary);
    }
    
    .chat-message.ai .avatar {
        background-color: var(--accent-primary);
    }
    
    .message-content {
        background-color: var(--bg-panel-secondary);
        padding: 12px 16px;
        border-radius: var(--radius-md);
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .message-content p {
        white-space: pre-wrap;
    }
    
    .message-meta {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    
    .chat-message.user {
        align-self: flex-end;
        flex-direction: row-reverse;
    }
    
    .chat-message.user .message-content {
        background-color: var(--accent-primary);
        color: white;
    }
    
    .chat-message.user .message-meta {
        color: rgba(255,255,255,0.7);
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        gap: 8px;
    }
    
    .typing-indicator span {
        height: 6px;
        width: 6px;
        background-color: var(--text-secondary);
        border-radius: 50%;
        display: inline-block;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1.0); }
    }

    .chat-input-area {
        padding: 16px;
        border-top: 1px solid var(--border-color);
        background-color: var(--bg-panel);
    }
    
    .chat-input-form {
        display: flex;
        align-items: flex-end;
        background-color: var(--bg-panel-secondary);
        border-radius: var(--radius-md);
        padding: 8px;
        border: 1px solid var(--border-color);
        transition: var(--transition);
    }
    
    .chat-input-form:focus-within {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    .chat-input-form textarea {
        flex-grow: 1;
        border: none;
        background: none;
        color: var(--text-primary);
        font-size: 14px;
        resize: none;
        max-height: 150px;
        line-height: 1.5;
        padding: 8px;
        font-family: var(--font-main);
        outline: none;
        min-height: 24px;
    }
    
    .chat-input-form textarea::placeholder {
        color: var(--text-secondary);
    }
    
    .input-actions {
        display: flex;
        gap: 4px;
    }
    
    .input-actions button {
        background: none;
        border: none;
        color: var(--text-secondary);
        font-size: 16px;
        cursor: pointer;
        padding: 8px;
        border-radius: var(--radius-sm);
        transition: var(--transition);
    }
    
    .input-actions button:hover {
        color: var(--text-primary);
        background-color: var(--accent-secondary);
    }
    
    .send-btn {
        background-color: var(--accent-primary) !important;
        color: white !important;
    }
    
    .send-btn:hover {
        background-color: var(--accent-primary-hover) !important;
    }

    /* --- 5. Context Panel (Desktop) --- */
    .context-header {
        font-size: 15px;
        font-weight: 500;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .context-header i {
        color: var(--text-secondary);
    }
    
    .context-content .placeholder {
        text-align: center;
        color: var(--text-secondary);
        padding: 40px 0;
        font-size: 14px;
    }
    
    .agent-details {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .agent-details .detail-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .agent-details .detail-item strong {
        color: var(--text-secondary);
        font-size: 12px;
        font-weight: 500;
    }
    
    .agent-details .detail-item p {
        background-color: var(--bg-panel-secondary);
        padding: 12px;
        border-radius: var(--radius-md);
        font-size: 14px;
    }
    
    .agent-details .capabilities-list {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .agent-details .capabilities-list li {
        background-color: var(--bg-panel-secondary);
        padding: 12px;
        border-radius: var(--radius-md);
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .agent-details .capabilities-list li i {
        color: var(--success-color);
    }

    /* --- 6. Responsive Breakpoints --- */
    /* Tablet and larger */
    @media (min-width: 768px) {
        .sidebar {
            position: static;
            transform: translateX(0);
        }
        
        .mobile-menu-toggle {
            display: none;
        }
        
        .polymind-workspace.sidebar-open .sidebar-overlay {
            display: none;
        }
    }

    /* Desktop and larger */
    @media (min-width: 1200px) {
        .polymind-workspace {
            display: grid;
            grid-template-columns: 260px 1fr 300px;
        }
        
        .context-panel {
            display: flex;
        }
        
        .chat-message {
            max-width: 75%;
        }
    }
</style>
</head>
<body>

<div class="polymind-workspace" id="polymind-workspace">
    
    <!-- Sidebar Overlay for Mobile -->
    <div class="sidebar-overlay" id="sidebar-overlay"></div>

    <!-- ===== 1. SIDEBAR ===== -->
    <aside class="sidebar">
        <header class="sidebar-header">
            <span class="logo"><i class="fas fa-brain"></i>POLYMIND</span>
        </header>

        <button class="new-chat-btn">
            <i class="fas fa-plus"></i> New Chat
        </button>

        <div class="sidebar-section">
            <h3 class="sidebar-section-title">Conversations</h3>
            <ul class="nav-list">
                <li><a href="#" class="active"><i class="fas fa-comment"></i> X-25 Report Analysis</a></li>
                <li><a href="#"><i class="fas fa-comment"></i> Logistics Planning</a></li>
                <li><a href="#"><i class="fas fa-comment"></i> Document Translation</a></li>
            </ul>
        </div>
        
        <div class="sidebar-section">
            <h3 class="sidebar-section-title">AI Agents</h3>
            <ul class="nav-list" id="agent-list">
                <li><a href="#" data-agent="Strategos"><i class="fas fa-chess-king"></i> Strategos</a></li>
                <li><a href="#" data-agent="Analytica"><i class="fas fa-chart-pie"></i> Analytica</a></li>
                <li><a href="#" data-agent="Logistix"><i class="fas fa-truck"></i> Logistix</a></li>
                <li><a href="#" data-agent="Linguist"><i class="fas fa-language"></i> Linguist</a></li>
            </ul>
        </div>

        <div class="sidebar-section">
            <h3 class="sidebar-section-title">Knowledge Base</h3>
            <ul class="nav-list">
                <li><a href="#"><i class="fas fa-file-alt"></i> Report_X-25.pdf</a></li>
                <li><a href="#"><i class="fas fa-file-word"></i> Supply_Chain.docx</a></li>
                <li><a href="#"><i class="fas fa-database"></i> Personnel_DB.sql</a></li>
            </ul>
        </div>

        <footer class="sidebar-footer">
            <div class="user-profile">
                <img src="https://i.pravatar.cc/80?u=commander" alt="User Avatar">
                <div class="user-info">
                    <span class="name">Commander Bravo</span>
                    <span class="role">Administrator</span>
                </div>
            </div>
        </footer>
    </aside>

    <!-- ===== 2. CHAT INTERFACE ===== -->
    <main class="chat-interface">
        <header class="chat-header">
            <button class="mobile-menu-toggle" id="mobile-menu-toggle">
                <i class="fas fa-bars"></i>
            </button>
            <div class="chat-header-title" id="chat-header-title">
                <i class="fas fa-chess-king"></i>
                <span>Chat with Strategos</span>
            </div>
            <div class="chat-header-actions">
                <button title="Agent Info"><i class="fas fa-info-circle"></i></button>
                <button title="Export Chat"><i class="fas fa-download"></i></button>
                <button title="Clear Chat"><i class="fas fa-trash-alt"></i></button>
            </div>
        </header>

        <div class="chat-log" id="chat-log">
            <!-- AI Welcome Message -->
            <div class="chat-message ai">
                <div class="avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content">
                    <p>Strategos ready for commands. How can I assist with your mission?</p>
                    <span class="message-meta">Strategos • Just now</span>
                </div>
            </div>

            <!-- User Message Example -->
            <div class="chat-message user">
                <div class="avatar">CB</div>
                <div class="message-content">
                    <p>Analyze key strengths and weaknesses in X-25 Report. Propose 3 strategic action plans.</p>
                    <span class="message-meta">Commander Bravo • 10:32</span>
                </div>
            </div>
            
            <!-- AI Typing Indicator (Template) -->
            <div class="chat-message ai typing-indicator" id="typing-indicator" style="display: none;">
                <div class="avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content">
                    <div class="typing-indicator"><span></span><span></span><span></span></div>
                </div>
            </div>
        </div>

        <div class="chat-input-area">
            <form class="chat-input-form" id="chat-form">
                <textarea id="chat-input" placeholder="Enter your request... (Shift+Enter for new line)" rows="1"></textarea>
                <div class="input-actions">
                    <button type="button" title="Attach File"><i class="fas fa-paperclip"></i></button>
                    <button type="submit" class="send-btn" title="Send (Enter)"><i class="fas fa-paper-plane"></i></button>
                </div>
            </form>
        </div>
    </main>

    <!-- ===== 3. CONTEXT PANEL ===== -->
    <aside class="context-panel" id="context-panel">
        <header class="context-header">
            <i class="fas fa-info-circle"></i> <span>Agent Information</span>
        </header>
        <div class="context-content" id="context-content">
            <!-- Content will be dynamically inserted here by JS -->
        </div>
    </aside>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const chatLog = document.getElementById('chat-log');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const typingIndicator = document.getElementById('typing-indicator');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const workspace = document.getElementById('polymind-workspace');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const agentLinks = document.querySelectorAll('#agent-list a');
    const chatHeaderTitle = document.getElementById('chat-header-title').querySelector('span');
    const chatHeaderIcon = document.getElementById('chat-header-title').querySelector('i');
    const contextPanel = document.getElementById('context-panel');
    const contextContent = document.getElementById('context-content');

    // --- Agent Information Database ---
    const agentDatabase = {
        'Strategos': {
            icon: 'fa-chess-king',
            description: 'Specialized in strategic planning, intelligence analysis, and scenario simulation. Optimized for high-level decision making.',
            capabilities: ['SWOT Analysis', 'Scenario Simulation', 'Campaign Planning', 'Risk Management']
        },
        'Analytica': {
            icon: 'fa-chart-pie',
            description: 'Focused on big data analysis, pattern recognition, and complex information visualization.',
            capabilities: ['Big Data Processing', 'Predictive Analytics', 'Entity Recognition', 'Data Visualization']
        },
        'Logistix': {
            icon: 'fa-truck',
            description: 'Manages and optimizes supply chains, resource coordination, and logistics planning.',
            capabilities: ['Route Optimization', 'Inventory Management', 'Demand Forecasting', 'Asset Coordination']
        },
        'Linguist': {
            icon: 'fa-language',
            description: 'Specializes in translation, natural language processing, and multilingual text analysis in real-time.',
            capabilities: ['Military-grade Translation', 'Text Summarization', 'Sentiment Analysis', 'Multilingual Communication']
        }
    };
    
    // --- State ---
    let currentAgent = 'Strategos';

    // --- Functions ---
    
    /**
     * Appends a message to the chat log
     * @param {string} sender - 'user' or 'ai'
     * @param {string} text - The message content
     */
    const addMessage = (sender, text) => {
        const messageEl = document.createElement('div');
        messageEl.classList.add('chat-message', sender);

        const avatarContent = sender === 'user' ? 'CB' : '<i class="fas fa-robot"></i>';
        const senderName = sender === 'user' ? 'Commander Bravo' : currentAgent;
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageEl.innerHTML = `
            <div class="avatar">${avatarContent}</div>
            <div class="message-content">
                <p>${text}</p>
                <span class="message-meta">${senderName} • ${time}</span>
            </div>
        `;
        chatLog.appendChild(messageEl);
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    /**
     * Simulates an AI response after a delay
     */
    const simulateAIResponse = (userInput) => {
        typingIndicator.style.display = 'flex';
        chatLog.scrollTop = chatLog.scrollHeight;

        setTimeout(() => {
            typingIndicator.style.display = 'none';
            let response = "Request received. Processing...";
            
            if (userInput.toLowerCase().includes('hello') || userInput.toLowerCase().includes('hi')) {
                response = `Hello Commander. Agent ${currentAgent} at your service.`;
            } else if (userInput.toLowerCase().includes('analyze')) {
                response = `Analysis complete based on available data. Preliminary results show 3 risk points and 2 potential opportunities. Would you like details?`;
            } else if (userInput.toLowerCase().includes('plan')) {
                response = `Initiating plan development. Key considerations include: resources, timeline, and strategic objectives. Please provide additional details.`;
            }

            addMessage('ai', response);
        }, 1500 + Math.random() * 1000);
    };

    /**
     * Updates the context panel with agent information
     */
    const updateContextPanel = (agentName) => {
        const agentInfo = agentDatabase[agentName];
        if (!agentInfo) {
            contextContent.innerHTML = `<div class="placeholder">No information available for this agent.</div>`;
            return;
        }

        const capabilitiesList = agentInfo.capabilities.map(cap => 
            `<li><i class="fas fa-check-circle"></i> ${cap}</li>`
        ).join('');

        contextContent.innerHTML = `
            <div class="agent-details">
                <div class="detail-item">
                    <strong>Description</strong>
                    <p>${agentInfo.description}</p>
                </div>
                <div class="detail-item">
                    <strong>Core Capabilities</strong>
                    <ul class="capabilities-list">${capabilitiesList}</ul>
                </div>
            </div>
        `;
    };

    /**
     * Handles form submission
     */
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const userInput = chatInput.value.trim();
        if (userInput) {
            addMessage('user', userInput);
            chatInput.value = '';
            chatInput.style.height = 'auto';
            simulateAIResponse(userInput);
        }
    });

    /**
     * Handles keyboard shortcuts
     */
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    /**
     * Auto-resizes the textarea
     */
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    /**
     * Toggles the sidebar on mobile
     */
    const toggleSidebar = () => {
        workspace.classList.toggle('sidebar-open');
    }
    mobileMenuToggle.addEventListener('click', toggleSidebar);
    sidebarOverlay.addEventListener('click', toggleSidebar);

    /**
     * Handles switching between AI agents
     */
    agentLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active class
            agentLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Update state and UI
            currentAgent = link.dataset.agent;
            const agentInfo = agentDatabase[currentAgent];
            
            chatHeaderTitle.textContent = `Chat with ${currentAgent}`;
            chatHeaderIcon.className = `fas ${agentInfo.icon}`;
            
            // Clear chat and add welcome message
            chatLog.innerHTML = '';
            addMessage('ai', `Agent ${currentAgent} ready for commands. How may I assist you?`);
            
            // Update context panel
            updateContextPanel(currentAgent);
        });
    });

    // --- Initial Setup ---
    updateContextPanel(currentAgent);
    document.querySelector('#agent-list a').classList.add('active');
});
</script>

</body>
</html>
```

**ALWAYS  RESPONSE A FORMATTED HTML**