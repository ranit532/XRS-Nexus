import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { RefreshCw, ScanSearch, CheckCircle2 } from 'lucide-react';

mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
        primaryColor: '#ffffff',
        primaryTextColor: '#1e293b',
        primaryBorderColor: '#cbd5e1',
        lineColor: '#64748b',
        secondaryColor: '#f1f5f9',
        tertiaryColor: '#ffffff'
    },
    securityLevel: 'loose',
    flowchart: { curve: 'basis' }
});

const LineageGraph = () => {
    const [graphDefinition, setGraphDefinition] = useState('');
    const [svgContent, setSvgContent] = useState('');
    const [error, setError] = useState('');
    const [isScanning, setIsScanning] = useState(false);
    const [scanStatus, setScanStatus] = useState('');
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

    const handleScan = async () => {
        setIsScanning(true);
        setScanStatus('Scanning data/simulation...');
        try {
            const res = await fetch('http://localhost:5001/scan', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                setScanStatus('Scan Complete!');
                await fetchGraph(); // Refresh graph
                setTimeout(() => setScanStatus(''), 2000);
            }
        } catch (e) {
            setScanStatus('Scan Failed');
        } finally {
            setIsScanning(false);
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
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>Live Data Lineage</h3>
                    <span style={{ fontSize: '12px', background: '#3b82f6', padding: '2px 8px', borderRadius: '12px', color: 'white' }}>Live</span>
                </div>

                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {scanStatus && (
                        <span className="animate-pulse" style={{ fontSize: '12px', color: '#10b981', display: 'flex', gap: '6px', alignItems: 'center' }}>
                            {scanStatus === 'Scan Complete!' ? <CheckCircle2 size={14} /> : <ScanSearch size={14} />}
                            {scanStatus}
                        </span>
                    )}
                    <button
                        onClick={handleScan}
                        disabled={isScanning}
                        style={{
                            padding: '6px 12px', borderRadius: '8px', background: isScanning ? 'rgba(59,130,246,0.2)' : 'rgba(59,130,246,0.1)',
                            border: '1px solid #3b82f6', cursor: isScanning ? 'wait' : 'pointer', color: '#3b82f6',
                            fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px'
                        }}
                    >
                        <ScanSearch size={14} />
                        {isScanning ? 'Scanning...' : 'Runtime Scan'}
                    </button>
                    <button
                        onClick={fetchGraph}
                        style={{ padding: '8px', borderRadius: '50%', background: 'rgba(255,255,255,0.05)', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
                    >
                        <RefreshCw size={18} />
                    </button>
                </div>
            </div>

            <div
                ref={containerRef}
                style={{
                    flex: 1, background: '#ffffff', borderRadius: '12px', overflow: 'hidden',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    border: '1px solid #e2e8f0', position: 'relative'
                }}
            >
                {error ? (
                    <div style={{ color: '#f87171', textAlign: 'center', padding: '1rem' }}>
                        <p>⚠️ {error}</p>
                    </div>
                ) : svgContent ? (
                    <div dangerouslySetInnerHTML={{ __html: svgContent }} style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }} />
                ) : (
                    <div style={{ color: '#6b7280', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                        <RefreshCw className="animate-spin" />
                        <span>Analyzing Lineage...</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LineageGraph;
