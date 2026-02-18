import React, { useState } from 'react';
import Chatbot from './Chatbot';
import LineageGraph from './LineageGraph';
import { Database, FileText, Layers, Activity } from 'lucide-react';

const COLORS = {
  bg: '#0f172a',
  card: '#1e293b',
  accent: '#3b82f6',
  border: 'rgba(255,255,255,0.08)',
  text: '#e2e8f0',
  muted: '#94a3b8',
};

const StatCard = ({ icon, label, value, color }) => (
  <div style={{
    background: COLORS.card,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '12px',
    padding: '16px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  }}>
    <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.05)', color }}>
      {icon}
    </div>
    <div>
      <div style={{ fontSize: '11px', color: COLORS.muted, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
      <div style={{ fontSize: '24px', fontWeight: 700, color: COLORS.text, textShadow: '0 0 10px rgba(59,130,246,0.4)' }}>{value}</div>
    </div>
  </div>
);

const FileItem = ({ name, type }) => (
  <div style={{
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 10px',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid transparent',
    cursor: 'pointer',
    marginBottom: '6px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span style={{ fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: '4px', background: '#334155', color: '#94a3b8' }}>{type}</span>
      <span style={{ fontSize: '13px', color: COLORS.text }}>{name}</span>
    </div>
  </div>
);

function App() {
  return (
    <div style={{ minHeight: '100vh', background: COLORS.bg, color: COLORS.text, fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Navbar */}
      <nav style={{
        height: '60px',
        borderBottom: `1px solid ${COLORS.border}`,
        background: 'rgba(15,23,42,0.8)',
        backdropFilter: 'blur(10px)',
        position: 'fixed',
        width: '100%',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        boxSizing: 'border-box',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Activity size={20} color="white" />
          </div>
          <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 700, letterSpacing: '-0.02em' }}>
            XRS <span style={{ color: COLORS.accent }}>NEXUS</span>
          </h1>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: '13px', color: COLORS.muted }}>
          AI Data Lineage Platform
        </div>
      </nav>

      {/* Main */}
      <main style={{ paddingTop: '76px', padding: '76px 24px 24px', height: '100vh', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <StatCard icon={<FileText size={20} />} label="Unstructured Sources" value="5 Files" color="#a78bfa" />
          <StatCard icon={<Database size={20} />} label="Structured Tables" value="3 Tables" color="#60a5fa" />
          <StatCard icon={<Layers size={20} />} label="Lineage Paths" value="8 Edges" color="#34d399" />
          <StatCard icon={<Activity size={20} />} label="Quality Score" value="98.2%" color="#fb923c" />
        </div>

        {/* Dashboard Grid */}
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', minHeight: 0 }}>
          {/* Left: Lineage + Discovery */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', minHeight: 0 }}>
            <div style={{ flex: 1, minHeight: 0 }}>
              <LineageGraph />
            </div>

            {/* Discovery Registry */}
            <div style={{
              height: '180px',
              background: COLORS.card,
              borderRadius: '12px',
              border: `1px solid ${COLORS.border}`,
              padding: '16px',
              overflowY: 'auto',
            }}>
              <h3 style={{ margin: '0 0 12px', fontSize: '11px', color: COLORS.muted, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Discovery Registry
              </h3>
              <FileItem name="vendor_contracts.csv" type="CSV" />
              <FileItem name="unstructured_data.xlsx" type="EXCEL" />
              <FileItem name="system_runtime.log" type="LOG" />
              <FileItem name="etl_pipeline_v1.py" type="PYSPARK" />
              <FileItem name="discovery_notes.txt" type="TXT" />
            </div>
          </div>

          {/* Right: Chatbot */}
          <div style={{ minHeight: 0 }}>
            <Chatbot />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
