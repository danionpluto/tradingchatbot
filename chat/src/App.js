import React, { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // when asking new question, show that one at the bottom

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate greeting prompt on first load
  useEffect(() => {
  fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_first: true }),
  })
    .then(res => res.json())
    .then(data => {
      setMessages([{ sender: "bot", text: data.answer }]);
    });
}, []);

  // message to send question to API
  const sendMessage = async () => {
    const question = input.trim();
    if (!question) return;

    // Add user message
    setMessages((prev) => [...prev, { sender: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (data.error) {
        setMessages((prev) => [...prev, { sender: "bot", text: "Error: " + data.error }]);
      } else {
        setMessages((prev) => [...prev, { sender: "bot", text: data.answer }]);
      }
    } catch {
      setMessages((prev) => [...prev, { sender: "bot", text: "Failed to connect to the backend." }]);
    }

    setLoading(false);
  };

  // detect when something is typed in box

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="App" >
      <h1 className='gradient-title' style={{ textAlign: "center" }}>TradeBot</h1>
      <div className="chat-window">
        {messages.length === 0 && !loading && (
          <div className="chat-loading"></div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender === "user" ? "user" : "bot"}`}>
            <div className="chat-bubble">{msg.text}</div>
          </div>
        ))}
        {loading && (
          <div className="chat-message bot">
            <div className="chat-bubble">...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className = 'submit-question'>
        <textarea rows={2} placeholder="Type your question and press Enter..." value={input}
        onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown} disabled={loading}
        className="chat-input"
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()} className="chat-send-button">
          <span className="arrow">➤</span>
        </button>

      </div>
    </div>
  );
}

export default App;
