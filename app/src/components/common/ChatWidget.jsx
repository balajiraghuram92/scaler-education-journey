import { useState, useEffect, useRef } from 'react';
import { api, ApiError } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import {
  MessageSquare,
  X,
  Send,
  Sparkles,
  AlertCircle,
  ShieldAlert,
  Loader2,
  Lock,
  ChevronDown,
  Info
} from 'lucide-react';
import { Link } from 'react-router-dom';
import './ChatWidget.css';

export default function ChatWidget({ lessonId, lessonTitle }) {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(false);
  const [error, setError] = useState(null);
  const [budgetCapError, setBudgetCapError] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, loading]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && user && !loading) {
      inputRef.current?.focus();
    }
  }, [isOpen, user, loading]);

  // Initialize or reset conversation when lessonId changes
  useEffect(() => {
    setConversationId(null);
    setMessages([]);
    setError(null);
    setBudgetCapError(null);
  }, [lessonId]);

  const initializeConversation = async () => {
    if (!user || user.status !== 'Approved' || conversationId) return;

    setInitLoading(true);
    setError(null);
    try {
      const conv = await api.chat.createConversation(
        lessonId ? parseInt(lessonId, 10) : null,
        lessonTitle ? `Chat: ${lessonTitle}` : 'Lesson Inquiry'
      );
      setConversationId(conv.id);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setBudgetCapError(err.message);
      } else {
        setError(err.message || 'Failed to initialize chat session.');
      }
    } finally {
      setInitLoading(false);
    }
  };

  const handleToggle = () => {
    const nextState = !isOpen;
    setIsOpen(nextState);
    if (nextState && !conversationId && user && user.status === 'Approved') {
      initializeConversation();
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading || !conversationId) return;

    const userText = input.trim();
    const clientRequestId = crypto.randomUUID
      ? crypto.randomUUID()
      : `chat-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

    // Optimistic user message
    const tempUserMsg = {
      id: `client-${Date.now()}`,
      conversationId,
      role: 'user',
      content: userText,
      createdAt: new Date().toISOString()
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const assistantReply = await api.chat.sendMessage(conversationId, userText, clientRequestId);
      setMessages((prev) => [...prev, assistantReply]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setBudgetCapError(err.message);
      } else {
        setError(err.message || 'Unable to deliver message. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-widget-root">
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={handleToggle}
          className="chat-floating-btn"
          title="Open Lesson Assistant"
          aria-label="Open Lesson Assistant"
        >
          <Sparkles size={18} className="chat-btn-icon" />
          <span className="chat-btn-label">Ask Lesson AI</span>
        </button>
      )}

      {/* Floating Chat Window */}
      {isOpen && (
        <div className="chat-window-card" role="dialog" aria-label="Lesson Assistant Window">
          {/* Header */}
          <div className="chat-window-header">
            <div className="chat-header-info">
              <div className="chat-header-title-row">
                <Sparkles size={16} className="chat-sparkle-icon" />
                <h3 className="chat-header-title">Lesson Assistant</h3>
                <span className="chat-badge-model">Llama</span>
              </div>
              <span className="chat-header-subtitle">
                {lessonTitle ? lessonTitle : 'Interactive Study Companion'}
              </span>
            </div>

            <div className="chat-header-actions">
              <button
                type="button"
                onClick={handleToggle}
                className="chat-btn-close"
                title="Minimize chat"
                aria-label="Minimize chat"
              >
                <ChevronDown size={18} />
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="chat-window-body">
            {!user ? (
              <div className="chat-auth-prompt">
                <Lock size={32} className="chat-lock-icon" />
                <h4>Sign In Required</h4>
                <p>
                  Lesson-scoped AI assistance is available to approved learners.
                </p>
                <Link to="/login" className="chat-login-link">
                  Sign In to Continue
                </Link>
              </div>
            ) : user.status !== 'Approved' ? (
              <div className="chat-auth-prompt">
                <AlertCircle size={32} className="chat-lock-icon" />
                <h4>Approval Pending</h4>
                <p>Your registration is pending administrator review.</p>
              </div>
            ) : initLoading ? (
              <div className="chat-loading-chamber">
                <Loader2 size={24} className="spinning" />
                <p>Grounding assistant in lesson material...</p>
              </div>
            ) : (
              <>
                {/* Welcome Grounding Banner */}
                <div className="chat-grounding-banner">
                  <Info size={14} className="banner-info-icon" />
                  <p>
                    Grounded in <strong>{lessonTitle || 'this lesson'}</strong>. Ask about equations, proofs, code, or conceptual intuition.
                  </p>
                </div>

                {/* Message History */}
                <div className="chat-messages-scroll">
                  {messages.length === 0 && (
                    <div className="chat-empty-hint">
                      <p>How can I clarify this chapter for you today?</p>
                      <div className="chat-suggestion-chips">
                        <button
                          type="button"
                          className="chip-btn"
                          onClick={() => setInput('Can you summarize the core intuition of this lesson?')}
                        >
                          Summarize core intuition
                        </button>
                        <button
                          type="button"
                          className="chip-btn"
                          onClick={() => setInput('Can you give me an example application of this concept?')}
                        >
                          Real-world example
                        </button>
                      </div>
                    </div>
                  )}

                  {messages.map((m) => (
                    <div
                      key={m.id}
                      className={`chat-message-bubble ${m.role === 'user' ? 'user' : 'assistant'}`}
                    >
                      <div className="bubble-content">{m.content}</div>
                      {m.role === 'assistant' && (
                        <div className="bubble-meta">
                          {m.usageEstimated && <span className="meta-tag">Estimated usage</span>}
                          {m.latencyMs != null && <span className="meta-tag">{m.latencyMs}ms</span>}
                        </div>
                      )}
                    </div>
                  ))}

                  {loading && (
                    <div className="chat-message-bubble assistant loading">
                      <div className="typing-indicator">
                        <span />
                        <span />
                        <span />
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Error Notices */}
                {budgetCapError && (
                  <div className="chat-budget-notice">
                    <ShieldAlert size={16} className="notice-icon" />
                    <div>
                      <strong>Daily Compute Budget Reached</strong>
                      <p>{budgetCapError}</p>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="chat-error-notice">
                    <AlertCircle size={15} className="notice-icon" />
                    <span>{error}</span>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer Input */}
          {user && user.status === 'Approved' && (
            <form onSubmit={handleSendMessage} className="chat-window-footer">
              <div className="chat-input-wrapper">
                <textarea
                  ref={inputRef}
                  rows={1}
                  value={input}
                  disabled={loading || Boolean(budgetCapError)}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    budgetCapError
                      ? 'Cap reached for today (UTC)'
                      : 'Ask a question about this lesson...'
                  }
                  className="chat-textarea"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || loading || Boolean(budgetCapError)}
                  className="chat-send-btn"
                  title="Send message"
                  aria-label="Send message"
                >
                  {loading ? <Loader2 size={16} className="spinning" /> : <Send size={16} />}
                </button>
              </div>

              <div className="chat-sustainability-footer">
                <span>Shared $2.00/day hard cap &bull; Grounded via Meta Llama</span>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
