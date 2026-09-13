import { useState } from "react";
import { askQuestion } from "../api";

export default function AskAssistant() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    "Show me the top 5 candidates.",
    "Who is the best candidate for this role?",
    "Which candidates know Python?",
    "Which candidates are missing Docker?",
  ];

  async function handleAsk(q) {
    const questionText = q || question;
    if (!questionText.trim()) return;

    setLoading(true);
    setQuestion("");
    setChatHistory((prev) => [...prev, { role: "user", text: questionText }]);

    try {
      const answer = await askQuestion(questionText);
      setChatHistory((prev) => [...prev, { role: "assistant", text: answer }]);
    } catch (err) {
      const errMsg = err?.response?.data?.detail || "Something went wrong.";
      setChatHistory((prev) => [...prev, { role: "assistant", text: `Error: ${errMsg}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>3. Ask the Recruitment Assistant</h2>

      <div className="sample-questions">
        {sampleQuestions.map((q) => (
          <button key={q} type="button" className="chip" onClick={() => handleAsk(q)}>
            {q}
          </button>
        ))}
      </div>

      <div className="chat-window">
        {chatHistory.length === 0 && (
          <p className="hint">Ask a question about your candidates to get started.</p>
        )}
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="chat-bubble assistant">Thinking...</div>}
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Type your question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
        />
        <button type="button" onClick={() => handleAsk()} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
