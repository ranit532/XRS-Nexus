import React, { useState } from 'react';
import Chatbot from './Chatbot';
import LineageGraph from './LineageGraph';
import { Database, FileText, Layers, Activity, FileJson, FileCode, CheckCircle2 } from 'lucide-react';

const COLORS = {
  bg: '#0f172a',
  card: '#1e293b',
  accent: '#3b82f6',
  border: 'rgba(255,255,255,0.08)',
  text: '#e2e8f0',
  muted: '#94a3b8',
  success: '#10b981',
};

const StepIndicator = ({ step, currentStep, label }) => {
  const isActive = currentStep === step;
  const isCompleted = currentStep > step;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', opacity: isActive || isCompleted ? 1 : 0.4 }}>
      <div style={{
        width: '28px', height: '28px', borderRadius: '50%',
        background: isCompleted ? COLORS.success : isActive ? COLORS.accent : 'rgba(255,255,255,0.1)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontWeight: 'bold', fontSize: '14px', color: '#fff',
        boxShadow: isActive ? `0 0 15px ${COLORS.accent}66` : 'none'
      }}>
        {isCompleted ? <CheckCircle2 size={16} /> : step}
      </div>
      <span style={{ fontSize: '14px', fontWeight: 600, color: isActive ? '#fff' : COLORS.muted }}>{label}</span>
      {step < 3 && <div style={{ width: '40px', height: '2px', background: 'rgba(255,255,255,0.1)', margin: '0 8px' }} />}
    </div>
  );
};

const DiscoveryPanel = () => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
    {[
      { name: 'vendor_contracts.csv', type: 'CSV', icon: <FileText color="#60a5fa" />, size: '1.2 MB' },
      { name: 'unstructured_data.xlsx', type: 'Excel (Macro)', icon: <FileText color="#34d399" />, size: '4.5 MB' },
      { name: 'system_runtime.log', type: 'Log', icon: <FileCode color="#fb923c" />, size: '840 KB' },
      { name: 'discovery_notes.txt', type: 'Text', icon: <FileText color="#a78bfa" />, size: '12 KB' },
      { name: 'etl_pipeline_v1.py', type: 'PySpark', icon: <FileJson color="#f472b6" />, size: '24 KB' },
    ].map((file, idx) => (
      <div key={idx} style={{
        background: 'rgba(255,255,255,0.03)', border: `1px solid ${COLORS.border}`,
        borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px',
        transition: 'all 0.2s', cursor: 'pointer'
      }}
        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.06)'}
        onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div style={{ padding: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>{file.icon}</div>
          <span style={{ fontSize: '10px', background: '#334155', padding: '2px 6px', borderRadius: '4px', color: '#cbd5e1' }}>{file.type}</span>
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{file.name}</div>
          <div style={{ fontSize: '12px', color: COLORS.muted }}>{file.size}</div>
        </div>
      </div>
    ))}
  </div>
);

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ minHeight: '100vh', background: COLORS.bg, color: COLORS.text, fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Navbar */}
      <nav style={{
        height: '70px', borderBottom: `1px solid ${COLORS.border}`, background: 'rgba(15,23,42,0.9)',
        backdropFilter: 'blur(10px)', position: 'fixed', width: '100%', zIndex: 50,
        display: 'flex', alignItems: 'center', padding: '0 32px', boxSizing: 'border-box',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Activity size={22} color="white" />
          </div>
          <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 700, letterSpacing: '-0.02em' }}>
            XRS <span style={{ color: COLORS.accent }}>NEXUS</span>
          </h1>
        </div>

        {/* Step Wizard in Navbar */}
        <div style={{ marginLeft: '60px', display: 'flex', alignItems: 'center' }}>
          <StepIndicator step={1} currentStep={currentStep} label="Discovery" />
          <StepIndicator step={2} currentStep={currentStep} label="Lineage & HITL" />
          <StepIndicator step={3} currentStep={currentStep} label="Glossary" />
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ paddingTop: '90px', padding: '90px 32px 32px', height: '100vh', boxSizing: 'border-box', display: 'flex', gap: '24px' }}>

        {/* Left Side: Content Area (Change based on Step) */}
        <div style={{ flex: 2, display: 'flex', flexDirection: 'column', gap: '24px', minHeight: 0 }}>
          {/* Context Header */}
          <div>
            <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
              {currentStep === 1 && "Data Discovery & Sources"}
              {currentStep === 2 && "Intelligence Lineage Journey"}
              {currentStep === 3 && "Business Glossary"}
            </h2>
            <p style={{ color: COLORS.muted, fontSize: '16px' }}>
              {currentStep === 1 && "AI-detected unstructured and structured data assets across the enterprise."}
              {currentStep === 2 && "Visualizing the flow of data with specialized agents and human oversight."}
              {currentStep === 3 && "Standardized definitions and metadata for governance."}
            </p>
          </div>

          {/* Dynamic Content */}
          <div style={{ flex: 1, minHeight: 0, background: COLORS.card, borderRadius: '16px', border: `1px solid ${COLORS.border}`, padding: '24px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            {currentStep === 1 && <DiscoveryPanel />}
            {currentStep === 2 && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
                <LineageGraph />
              </div>
            )}
            {/* Glossary Content Placeholder */}
            {currentStep === 3 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {['Customer ID', 'Transaction Amount', 'Vendor Code'].map(term => (
                  <div key={term} style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: `4px solid ${COLORS.accent}` }}>
                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>{term}</div>
                    <div style={{ fontSize: '14px', color: COLORS.muted }}>Unique identifier derived from the master vendor contract database.</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Step Navigation */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button
              disabled={currentStep === 1}
              onClick={() => setCurrentStep(prev => prev - 1)}
              style={{ padding: '10px 20px', borderRadius: '8px', border: `1px solid ${COLORS.border}`, background: 'transparent', color: COLORS.text, cursor: currentStep === 1 ? 'not-allowed' : 'pointer', opacity: currentStep === 1 ? 0.5 : 1 }}>
              Back
            </button>
            <button
              disabled={currentStep === 3}
              onClick={() => setCurrentStep(prev => prev + 1)}
              style={{ padding: '10px 24px', borderRadius: '8px', background: COLORS.accent, border: 'none', color: '#fff', fontWeight: 600, cursor: currentStep === 3 ? 'not-allowed' : 'pointer', opacity: currentStep === 3 ? 0.5 : 1 }}>
              Next Step
            </button>
          </div>
        </div>

        {/* Right Side: Chatbot (Always Visible) */}
        <div style={{ flex: 1, minWidth: '350px', maxWidth: '450px' }}>
          <Chatbot />
        </div>

      </main>
    </div>
  );
}

export default App;
