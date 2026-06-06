import { useMemo, useState, type FormEvent } from 'react';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

const promptSuggestions = [
  'Explain the Asura architecture.',
  'Which teams benefit most from this platform?',
  'How does security work in Asura?',
  'What does a typical deployment look like?',
];

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Welcome to Asura. Ask the platform about decisions, multimodal intelligence, or the Gemini integration.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) return;
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
    };

    setMessages((current) => [...current, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: userMessage.content }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail || response.statusText || 'Failed to contact Asura backend.');
      }

      const data = await response.json();
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.reply || 'Asura responded with no text. Please try again.',
      };

      setMessages((current) => [...current, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unexpected error sending your request.';
      setError(message);
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: 'assistant',
          content: `Error: ${message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const memoizedStats = useMemo(
    () => [
      { label: 'AI Model', value: 'Gemini 1.5' },
      { label: 'Platform', value: 'Asura' },
      { label: 'Response Target', value: '< 5s' },
    ],
    []
  );

  return (
    <div className="app-shell">
      <div className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">Asura</span>
          <h1>Enterprise Multimodal Decision Intelligence</h1>
          <p>Drive faster decisions with a unified AI platform built for documents, images, logs, and real-time signals.</p>
          <div className="hero-actions">
            <a className="button button-primary" href="#chat">Try the live AI assistant</a>
            <a className="button button-secondary" href="#features">Explore features</a>
          </div>
        </div>

        <div className="hero-card">
          <div className="hero-card-top">
            <div>
              <p className="small-label">Asura dashboard</p>
              <h2>Live chat, multimodal insights, and explainability.</h2>
            </div>
            <div className="pulse-dot" />
          </div>
          <div className="feature-grid">
            {memoizedStats.map((stat) => (
              <div key={stat.label} className="feature-stat">
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <section id="features" className="section-grid">
        <div className="feature-card">
          <h2>Unified Data Analysis</h2>
          <p>Analyze text, images, documents, and system data together to generate evidence-backed recommendations.</p>
        </div>
        <div className="feature-card">
          <h2>Explainable Decisions</h2>
          <p>Every response includes confidence, source citations, and underlying reasoning for audit-ready insights.</p>
        </div>
        <div className="feature-card">
          <h2>Cloud Native</h2>
          <p>Built for Google Cloud with Gemini, Vertex AI, BigQuery, Pub/Sub, and enterprise-scale deployment.</p>
        </div>
      </section>

      <section id="chat" className="chat-shell">
        <div className="chat-header">
          <div>
            <p className="eyebrow">Live Assistant</p>
            <h2>Ask Asura anything about the platform.</h2>
          </div>
          <div className="chat-note">Run the backend with your Gemini API key, then type your question below.</div>
        </div>

        <div className="chat-layout">
          <div className="chat-box">
            {messages.map((message) => (
              <div key={message.id} className={`chat-message ${message.role}`}>
                <span>{message.content}</span>
              </div>
            ))}
          </div>

          <form className="chat-input-row" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about Asura..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              {loading ? 'Thinking…' : 'Send'}
            </button>
          </form>

          <div className="quick-prompt-grid">
            {promptSuggestions.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="quick-prompt"
                onClick={() => setInput(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
          {error ? <div className="chat-error">{error}</div> : null}
        </div>
      </section>
    </div>
  );
}

export default App;
