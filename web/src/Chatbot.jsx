import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const Chatbot = () => {
    const [messages, setMessages] = useState([
        { role: 'system', content: 'Welcome to XRS Nexus Synergy. Active agents: Structure, Lineage, Quality, Glossary.', agent: 'Orchestrator' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [threadId, setThreadId] = useState(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async (text, action = null) => {
        if (!text && !action) return;
        if (!action) {
            setMessages(prev => [...prev, { role: 'user', content: text, agent: 'User' }]);
            setInput('');
        }
        setIsLoading(true);

        try {
            const payload = { message: text, thread_id: threadId, action };
            const response = await fetch('http://localhost:5001/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            setThreadId(data.thread_id);
            setMessages(prev => [...prev, {
                role: 'system',
                content: data.response || data.error || 'No response.',
                agent: data.agent || 'system',
                isHitl: data.requires_approval
            }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'system', content: '⚠️ Error: Could not connect to API. Is api.py running on port 5001?', agent: 'system' }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleApproval = (approved) => {
        if (approved) {
            sendMessage('Approving correction...', 'approve_correction');
        } else {
            setMessages(prev => [...prev, { role: 'system', content: 'Correction Rejected. Workflow stopped.', agent: 'system' }]);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#1e293b', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}>
            {/* Header */}
            <div style={{ padding: '16px', background: '#0f172a', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ position: 'relative' }}>
                    <Bot size={24} color="#3b82f6" />
                    <div style={{ position: 'absolute', bottom: 0, right: -2, width: '8px', height: '8px', background: '#10b981', borderRadius: '50%', border: '2px solid #0f172a' }}></div>
                </div>
                <div>
                    <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#e2e8f0' }}>Nexus Assistant</h2>
                    <div style={{ fontSize: '10px', color: '#94a3b8' }}>Powered by Ollama (Phi3)</div>
                </div>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                        <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px', marginLeft: '4px' }}>
                            {msg.agent || 'User'}
                        </div>

                        <div style={{
                            maxWidth: '85%',
                            padding: '12px 16px',
                            borderRadius: msg.role === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                            background: msg.role === 'user' ? '#3b82f6' : msg.isHitl ? 'rgba(56, 26, 12, 0.4)' : 'rgba(255,255,255,0.05)',
                            border: msg.isHitl ? '1px solid #78350f' : '1px solid rgba(255,255,255,0.05)',
                            color: '#e2e8f0',
                            fontSize: '14px',
                            lineHeight: '1.5',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}>
                            {msg.isHitl && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#fbbf24', fontWeight: 600 }}>
                                    <AlertTriangle size={16} /> Action Required
                                </div>
                            )}

                            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>

                            {msg.isHitl && (
                                <div style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
                                    <button onClick={() => handleApproval(true)} style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px', padding: '8px 12px', background: '#16a34a', border: 'none', borderRadius: '8px', color: 'white', cursor: 'pointer', fontSize: '13px', fontWeight: '600', transition: 'background 0.2s' }}>
                                        <CheckCircle size={16} /> Approve
                                    </button>
                                    <button onClick={() => handleApproval(false)} style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px', padding: '8px 12px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0', cursor: 'pointer', fontSize: '13px', fontWeight: '600' }}>
                                        <XCircle size={16} /> Reject
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                        <div style={{ padding: '8px 16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', color: '#6b7280', fontSize: '12px', display: 'flex', gap: '6px', alignItems: 'center' }}>
                            <div className="animate-pulse" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#6b7280' }}></div>
                            <div className="animate-pulse" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#6b7280', animationDelay: '0.2s' }}></div>
                            <div className="animate-pulse" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#6b7280', animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{ padding: '16px', background: '#0f172a', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '10px' }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
                    placeholder="Ask agents..."
                    style={{ flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', padding: '10px 16px', color: '#e2e8f0', fontSize: '14px', outline: 'none', transition: 'border-color 0.2s' }}
                />
                <button
                    onClick={() => sendMessage(input)}
                    disabled={isLoading || !input.trim()}
                    style={{ padding: '10px', background: '#3b82f6', border: 'none', borderRadius: '10px', color: 'white', cursor: 'pointer', opacity: isLoading || !input.trim() ? 0.5 : 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
