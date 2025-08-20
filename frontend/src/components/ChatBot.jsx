// Triage assistant chat interface component
import React, { useState, useRef, useEffect } from 'react';

const ChatBot = ({ onTriageComplete }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your virtual triage assistant. I can help assess your symptoms and provide guidance. What symptoms are you experiencing today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentAssessment, setCurrentAssessment] = useState({
    symptoms: [],
    responses: []
  });
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentAssessment(prev => ({
      ...prev,
      responses: [...prev.responses, inputMessage]
    }));
    
    setInputMessage('');
    setIsTyping(true);

    try {
      // Send message to triage API
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/triage/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const botMessage = {
        id: messages.length + 2,
        text: data.response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      // Check if we have enough information for assessment
      if (currentAssessment.responses.length >= 3) {
        setTimeout(() => {
          performTriageAssessment();
        }, 1000);
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: "I'm sorry, I'm having trouble processing your message right now. Please try again.",
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const performTriageAssessment = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/triage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symptoms: extractSymptoms(currentAssessment.responses),
          // Add other relevant data
        }),
      });

      if (!response.ok) {
        throw new Error('Assessment failed');
      }

      const assessment = await response.json();
      
      const assessmentMessage = {
        id: messages.length + 1,
        text: formatAssessmentMessage(assessment),
        sender: 'bot',
        timestamp: new Date(),
        isAssessment: true
      };

      setMessages(prev => [...prev, assessmentMessage]);
      
      if (onTriageComplete) {
        onTriageComplete(assessment);
      }

    } catch (error) {
      console.error('Assessment error:', error);
    }
  };

  const extractSymptoms = (responses) => {
    // Simple symptom extraction - in practice, use NLP
    const commonSymptoms = [
      'headache', 'fever', 'cough', 'pain', 'nausea', 'fatigue',
      'dizziness', 'shortness of breath', 'chest pain'
    ];
    
    const extractedSymptoms = [];
    responses.forEach(response => {
      commonSymptoms.forEach(symptom => {
        if (response.toLowerCase().includes(symptom)) {
          extractedSymptoms.push(symptom);
        }
      });
    });
    
    return [...new Set(extractedSymptoms)]; // Remove duplicates
  };

  const formatAssessmentMessage = (assessment) => {
    return `
Based on our conversation, here's my assessment:

**Urgency Level:** ${assessment.urgency_level.toUpperCase()}

**Possible Conditions:**
${assessment.possible_conditions.map(condition => `• ${condition}`).join('\n')}

**Recommendations:**
${assessment.recommendations.map(rec => `• ${rec}`).join('\n')}

**Next Steps:**
${assessment.next_steps.map(step => `• ${step}`).join('\n')}

*Please note: This assessment is for informational purposes only and should not replace professional medical advice.*
    `;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickResponses = [
    "I have a headache",
    "I'm feeling nauseous",
    "I have chest pain",
    "I'm having trouble breathing",
    "I have a fever"
  ];

  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <h3>🩺 Virtual Triage Assistant</h3>
        <p>Describe your symptoms for personalized guidance</p>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender} ${message.isError ? 'error' : ''} ${message.isAssessment ? 'assessment' : ''}`}
          >
            <div className="message-content">
              <pre className="message-text">{message.text}</pre>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message bot typing">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-responses">
        {quickResponses.map((response, index) => (
          <button
            key={index}
            className="quick-response-btn"
            onClick={() => setInputMessage(response)}
          >
            {response}
          </button>
        ))}
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your symptoms..."
            rows="2"
            disabled={isTyping}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="send-btn"
          >
            Send
          </button>
        </div>
      </div>

      <div className="chat-disclaimer">
        <p>⚠️ This is not a substitute for professional medical advice. 
           In case of emergency, call 911 immediately.</p>
      </div>
    </div>
  );
};

export default ChatBot;
