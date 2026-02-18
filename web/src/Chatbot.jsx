import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle, XCircle } from 'lucide-react';

const Chatbot = () => {
    const [messages, setMessages] = useState([
        { role: 'system', content: 'Welcome to XRS Nexus Synergy. Ask me about data lineage, quality, or definitions.', agent: 'system' }
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
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#1e293b', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', overflow: 'hidden' }}>
            {/* Header */}
            <div style={{ padding: '16px', background: '#0f172a', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Bot size={20} color="#3b82f6" />
                <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#e2e8f0', textShadow: '0 0 10px rgba(59,130,246,0.5)' }}>Synergy Chat</h2>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                        <div style={{
                            maxWidth: '80%',
                            padding: '10px 14px',
                            borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                            background: msg.role === 'user' ? '#3b82f6' : msg.isHitl ? 'rgba(234,179,8,0.15)' : 'rgba(255,255,255,0.05)',
                            border: msg.isHitl ? '1px solid rgba(234,179,8,0.4)' : '1px solid transparent',
                            color: '#e2e8f0',
                            fontSize: '14px',
                            lineHeight: '1.5'
                        }}>
                            <div style={{ fontSize: '10px', opacity: 0.5, marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                {msg.agent || 'User'}
                            </div>
                            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                            {msg.isHitl && (
                                <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
                                    <button onClick={() => handleApproval(true)} style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 12px', background: '#16a34a', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}>
                                        <CheckCircle size={14} /> Approve
                                    </button>
                                    <button onClick={() => handleApproval(false)} style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 12px', background: '#dc2626', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}>
                                        <XCircle size={14} /> Reject
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                        <div style={{ padding: '10px 14px', borderRadius: '12px 12px 12px 2px', background: 'rgba(255,255,255,0.05)', color: '#6b7280', fontSize: '14px' }}>
                            Thinking...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{ padding: '16px', background: '#0f172a', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '8px' }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
                    placeholder="Ask about lineage, quality, or definitions..."
                    style={{ flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '8px 16px', color: '#e2e8f0', fontSize: '14px', outline: 'none' }}
                />
                <button
                    onClick={() => sendMessage(input)}
                    disabled={isLoading || !input.trim()}
                    style={{ padding: '8px 12px', background: '#3b82f6', border: 'none', borderRadius: '8px', color: 'white', cursor: 'pointer', opacity: isLoading || !input.trim() ? 0.5 : 1 }}
                >
                    <Send size={20} />
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
