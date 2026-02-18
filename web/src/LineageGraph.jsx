import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { RefreshCw } from 'lucide-react';

mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
    flowchart: { curve: 'basis' }
});

const LineageGraph = () => {
    const [graphDefinition, setGraphDefinition] = useState('');
    const [svgContent, setSvgContent] = useState('');
    const [error, setError] = useState('');
    const containerRef = useRef(null);

    useEffect(() => {
        fetchGraph();
    }, []);

    useEffect(() => {
        if (graphDefinition) {
            renderGraph(graphDefinition);
        }
    }, [graphDefinition]);

    const fetchGraph = async () => {
        try {
            const res = await fetch('http://localhost:5001/lineage');
            const data = await res.json();
            if (data.mermaid) {
                setGraphDefinition(data.mermaid);
            }
        } catch (e) {
            setError('Could not connect to API. Is api.py running?');
            console.error('Failed to fetch graph', e);
        }
    };

    const renderGraph = async (definition) => {
        try {
            const id = 'mermaid-' + Date.now();
            const { svg } = await mermaid.render(id, definition);
            setSvgContent(svg);
            setError('');
        } catch (e) {
            setError('Graph render error: ' + e.message);
            console.error('Mermaid render error', e);
        }
    };

    return (
        <div className="h-full flex flex-col rounded-xl overflow-hidden shadow-2xl" style={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)' }}>
            <div className="p-4 flex justify-between items-center" style={{ background: '#0f172a', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <h2 className="text-lg font-semibold" style={{ color: '#e2e8f0', textShadow: '0 0 10px rgba(59,130,246,0.5)' }}>
                    Live Data Lineage
                </h2>
                <button
                    onClick={fetchGraph}
                    className="p-2 rounded-full transition-colors hover:bg-white/10"
                >
                    <RefreshCw size={18} style={{ color: '#3b82f6' }} />
                </button>
            </div>

            <div
                ref={containerRef}
                className="flex-1 p-4 overflow-auto flex items-center justify-center"
                style={{ background: '#0d121f' }}
            >
                {error ? (
                    <div style={{ color: '#f87171', textAlign: 'center', padding: '1rem' }}>
                        <p>⚠️ {error}</p>
                    </div>
                ) : svgContent ? (
                    <div dangerouslySetInnerHTML={{ __html: svgContent }} style={{ maxWidth: '100%' }} />
                ) : (
                    <div style={{ color: '#6b7280' }} className="animate-pulse">Loading Lineage Graph...</div>
                )}
            </div>
        </div>
    );
};

export default LineageGraph;
