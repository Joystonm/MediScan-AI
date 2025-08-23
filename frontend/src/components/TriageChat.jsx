import React, { useState, useRef, useEffect } from 'react';
import './TriageChat.css';

const TriageChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm your Virtual Triage Assistant. I'm here to help assess your symptoms and provide medical guidance. Please describe your symptoms or medical concerns.",
      timestamp: new Date(),
      typing: false
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isTyping) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Add typing indicator
      const typingMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '',
        timestamp: new Date(),
        typing: true
      };
      setMessages(prev => [...prev, typingMessage]);

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/triage/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          timestamp: userMessage.timestamp.toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from triage assistant');
      }

      const result = await response.json();

      // Remove typing indicator and add actual response
      setMessages(prev => {
        const withoutTyping = prev.filter(msg => !msg.typing);
        return [...withoutTyping, {
          id: Date.now() + 2,
          type: 'bot',
          content: result.response || result.message || "I'm here to help. Could you provide more details about your symptoms?",
          timestamp: new Date(),
          urgency: result.urgency_level,
          medicalKeywords: result.medical_keywords,
          resources: result.medical_resources,
          nextQuestions: result.next_questions
        }];
      });

    } catch (error) {
      console.error('Chat error:', error);
      
      // Remove typing indicator and add better error message
      setMessages(prev => {
        const withoutTyping = prev.filter(msg => !msg.typing);
        return [...withoutTyping, {
          id: Date.now() + 2,
          type: 'bot',
          content: "I'm experiencing some technical difficulties. Let me try to help you with a different approach. Could you describe your main symptom?",
          timestamp: new Date(),
          isError: true
        }];
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'emergency': return 'text-red-600';
      case 'urgent': return 'text-orange-600';
      case 'routine': return 'text-green-600';
      default: return 'text-blue-600';
    }
  };

  return (
    <div className="triage-chat-container">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="flex items-center gap-3">
          <div className="bot-avatar">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-white">Virtual Triage Assistant</h3>
            <p className="text-sm text-blue-100">AI-powered medical guidance</p>
          </div>
        </div>
        <div className="status-indicator">
          <div className="status-dot"></div>
          <span className="text-sm text-blue-100">Online</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="messages-container">
        <div className="messages-list">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                {message.typing ? (
                  <div className="typing-indicator">
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span className="typing-text">Assistant is typing...</span>
                  </div>
                ) : (
                  <>
                    <div className="message-text">
                      {message.content}
                    </div>
                    
                    {/* Urgency Badge */}
                    {message.urgency && (
                      <div className={`urgency-badge ${message.urgency}`}>
                        <span className="urgency-label">
                          {message.urgency.charAt(0).toUpperCase() + message.urgency.slice(1)} Priority
                        </span>
                      </div>
                    )}

                    {/* Medical Keywords - displayed naturally */}
                    {message.medicalKeywords && message.medicalKeywords.length > 0 && (
                      <div className="medical-keywords">
                        <div className="keywords-list">
                          {message.medicalKeywords.slice(0, 5).map((keyword, index) => (
                            <span key={index} className="keyword-tag">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Medical Resources - embedded naturally */}
                    {message.resources && message.resources.length > 0 && (
                      <div className="medical-resources">
                        <div className="resources-list">
                          {message.resources.slice(0, 2).map((resource, index) => (
                            <div key={index} className="resource-item">
                              <a 
                                href={resource.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="resource-link"
                              >
                                📚 {resource.title}
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
              <div className="message-timestamp">
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="chat-input-container">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your symptoms or ask a medical question..."
            className="chat-input"
            rows={1}
            disabled={isTyping}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="send-button"
          >
            {isTyping ? (
              <div className="loading-spinner"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TriageChat;
