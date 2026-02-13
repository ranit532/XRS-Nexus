import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Activity,
  Zap,
  Search,
  AlertTriangle,
  Database,
  FileCheck,
  Cpu,
  ArrowRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const MOCK_AI_LOGS = [
  { id: 1, type: 'info', text: 'Initiating deep scan on silver/customers...' },
  { id: 2, type: 'process', text: 'Analyzing field mappings for 2,000 records...' },
  { id: 3, type: 'warning', text: 'PII detected in dataset silver/customers. Field: email' },
  { id: 4, type: 'success', text: 'Validation complete. ai_powered: true (via Ollama)' },
  { id: 5, type: 'info', text: 'Updating lineage graph for silver -> gold transition.' },
];

// --- Console Modal Component (Defined Outside to prevent re-renders) ---
const PipelineConsoleModal = ({ showModal, setShowModal, actionStatus, displayLogs }) => {
  const scrollRef = React.useRef(null);

  // Auto-scroll to bottom of logs
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [displayLogs]);

  return (
    <AnimatePresence>
      {showModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl overflow-hidden border border-blue-100 flex flex-col h-[600px] pointer-events-auto"
          >
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-50 bg-slate-50/50 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg bg-blue-600 text-white ${actionStatus.is_running ? 'animate-spin' : ''}`}>
                  <Cpu size={20} />
                </div>
                <div>
                  <h3 className="text-sm font-black text-slate-900 uppercase tracking-tight">
                    {actionStatus.last_action || 'Pipeline Console'}
                  </h3>
                  <p className="text-[10px] text-blue-500 font-bold uppercase tracking-widest leading-none mt-1">
                    {actionStatus.is_running ? 'Live Execution Logging' : 'Action Results'}
                  </p>
                </div>
              </div>
            </div>

            {/* Console Body */}
            <div
              ref={scrollRef}
              className="flex-1 bg-slate-900 p-6 overflow-y-auto font-mono text-[11px] space-y-2 scrollbar-thin scrollbar-thumb-slate-700"
            >
              {displayLogs.length === 0 && (
                <div className="h-full flex items-center justify-center text-slate-500 italic">
                  Initializing secure channel to backend...
                </div>
              )}
              {displayLogs.map((log, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`${log.includes('✅') ? 'text-green-400 font-bold' : log.includes('❌') || log.includes('🚨') ? 'text-red-400' : 'text-blue-300'}`}
                >
                  <span className="text-slate-600 mr-2 opacity-50">$</span> {log}
                </motion.div>
              ))}
              {actionStatus.is_running && (
                <motion.div
                  animate={{ opacity: [0, 1] }}
                  transition={{ repeat: Infinity, duration: 0.8 }}
                  className="text-white ml-5 inline-block"
                > █ </motion.div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-white border-t border-slate-50 flex justify-end gap-3">
              <button
                onClick={() => setShowModal(false)}
                disabled={actionStatus.is_running}
                className={`px-6 py-3 rounded-xl text-xs font-black tracking-widest transition-all shadow-md active:scale-95 ${actionStatus.is_running ? 'bg-slate-100 text-slate-400 cursor-not-allowed opacity-50' : 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-100'}`}
              >
                {actionStatus.is_running ? 'WAITING FOR COMPLETION...' : 'CLOSE CONSOLE'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

const Dashboard = () => {
  const [logs, setLogs] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const [simulationMode, setSimulationMode] = useState(false);
  const [simData, setSimData] = useState(null);
  const [trustScore, setTrustScore] = useState(94);
  const [latestRun, setLatestRun] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [lastValidAiInsights, setLastValidAiInsights] = useState(null); // STATE FREEZE for AI insights

  const steps = [
    { name: 'SYNTHETIC', label: 'FAKER GENERATOR', icon: FileCheck, color: 'text-pink-500' },
    { name: 'BRONZE', label: 'ADLS LANDING', icon: Database, color: 'text-amber-500' },
    { name: 'SILVER', label: 'ADF TRANSFORM', icon: Activity, color: 'text-gray-400' },
    { name: 'AI VALIDATION', label: 'AI PRIVACY AUDIT', icon: Cpu, color: 'text-blue-400' },
    { name: 'GOLD', label: 'ANALYTICS HUB', icon: Zap, color: 'text-yellow-400' }
  ];

  const [actionStatus, setActionStatus] = useState({ is_running: false, last_action: null, logs: [], error: null });
  const [unifiedProgress, setUnifiedProgress] = useState({
    SYNTHETIC: "Pending",
    BRONZE: "Pending",
    SILVER: "Pending",
    AI_VALIDATION: "Pending",
    GOLD: "Pending"
  });
  const [displayLogs, setDisplayLogs] = useState([]);
  const logQueue = React.useRef([]);
  const displayedLogSet = React.useRef(new Set());

  // --- AI Audit Dashboard Component ---
  const AIAuditBoard = ({ aiInsights }) => {
    if (!aiInsights) return null;

    const { scan_stats, pii_details, classification, confidence, risk_level } = aiInsights;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mt-12 p-8 bg-white rounded-[2.5rem] border border-blue-100 shadow-xl shadow-blue-900/5 space-y-8 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50/50 rounded-full blur-3xl -mr-32 -mt-32 z-0" />

        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg text-white">
                <ShieldCheck size={18} />
              </div>
              <h3 className="text-lg font-black tracking-tight text-slate-800 uppercase">AI Privacy Audit Board</h3>
            </div>
            <p className="text-xs text-slate-400 font-mono">Deep scan results from Ollama (PHI-3) local inference</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl text-center">
              <p className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Confidence</p>
              <p className="text-sm font-black text-blue-600">{(confidence * 100).toFixed(0)}%</p>
            </div>
            <div className={`px-4 py-2 border rounded-xl text-center ${risk_level === 'Critical' || risk_level === 'High' ? 'bg-red-50 border-red-100 text-red-600' : 'bg-green-50 border-green-100 text-green-600'}`}>
              <p className="text-[8px] font-bold opacity-60 uppercase tracking-widest">Risk Level</p>
              <p className="text-sm font-black">{risk_level || 'Low'}</p>
            </div>
            <div className="px-4 py-2 bg-purple-50 border border-purple-100 rounded-xl text-center">
              <p className="text-[8px] font-bold text-purple-400 uppercase tracking-widest">Class</p>
              <p className="text-sm font-black text-purple-600">{classification || 'Internal'}</p>
            </div>
          </div>
        </div>

        {/* Scan Stats Grid */}
        <div className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase">Records Scanned</p>
            <p className="text-xl font-black text-slate-700">{scan_stats?.records_scanned || 0}</p>
          </div>
          <div className="p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase">Fields Analyzed</p>
            <p className="text-xl font-black text-slate-700">{scan_stats?.fields_scanned || 0}</p>
          </div>
          <div className="p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase">PII Flagged</p>
            <p className="text-xl font-black text-red-500">{pii_details?.length || 0}</p>
          </div>
          <div className="p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase">Policy Applied</p>
            <p className="text-sm font-black text-blue-600">GDPR / HIPAA (Local)</p>
          </div>
        </div>

        {/* Findings Table */}
        {pii_details && pii_details.length > 0 && (
          <div className="relative z-10 overflow-hidden rounded-2xl border border-slate-100">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-tighter">
                <tr>
                  <th className="px-6 py-3">Field Name</th>
                  <th className="px-6 py-3">PII Category</th>
                  <th className="px-6 py-3">Audit Action</th>
                  <th className="px-6 py-3 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {pii_details.map((item, idx) => (
                  <tr key={idx} className="hover:bg-blue-50/30 transition-colors">
                    <td className="px-6 py-4 font-mono font-bold text-slate-700">{item.field}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-amber-50 text-amber-600 border border-amber-100 rounded text-[9px] font-black uppercase">
                        {item.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 italic">{item.recommendation}</td>
                    <td className="px-6 py-4 text-right font-bold text-blue-500">{(item.confidence * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    );
  };

  // Log Pacing Engine: Drains logQueue into displayLogs every 300ms
  useEffect(() => {
    const drainQueue = setInterval(() => {
      if (logQueue.current.length > 0) {
        const nextLog = logQueue.current.shift();
        setDisplayLogs(prev => [...prev, nextLog]);
      }
    }, 300);

    return () => clearInterval(drainQueue);
  }, []);

  const triggerAction = async (endpoint) => {
    try {
      setShowModal(true);
      setDisplayLogs([]); // Immediate clear on user action
      logQueue.current = [];
      displayedLogSet.current = new Set();
      await fetch(`http://localhost:5001/api/pipeline/${endpoint}`, { method: 'POST' });
    } catch (error) {
      console.error(`Error triggering ${endpoint}:`, error);
    }
  };

  // --- Unified Polling Logic (Source of Truth) ---
  useEffect(() => {
    const fetchEverything = async () => {
      try {
        if (simulationMode) {
          const response = await fetch('http://localhost:5001/api/simulation');
          const data = await response.json();
          setSimData(data);
          if (activeStep < steps.length - 1) {
            setTimeout(() => setActiveStep(prev => prev + 1), 5000);
          }
        } else {
          // 1. Fetch Action Status & Logs
          const statusRes = await fetch('http://localhost:5001/api/pipeline/status');
          const statusData = await statusRes.json();

          if (statusData.is_running && statusData.last_action !== actionStatus.last_action) {
            setDisplayLogs([]);
            displayedLogSet.current = new Set();
            logQueue.current = [];

            // SESSION RESET: Clear live logs and insights on new journey
            if (statusData.last_action === "Data Generation") {
              setLogs([]);
              setLastValidAiInsights(null);
            }
          }
          setActionStatus(statusData);
          if (statusData.unified_progress) {
            setUnifiedProgress(statusData.unified_progress);
            if (statusData.unified_progress.ai_insights) {
              setLastValidAiInsights(statusData.unified_progress.ai_insights);
            }
          }

          // Add new logs from backend to the queue
          statusData.logs.forEach(log => {
            if (!displayedLogSet.current.has(log)) {
              displayedLogSet.current.add(log);
              logQueue.current.push(log);
            }
          });

          // Auto-open modal if an action starts running
          if (statusData.is_running && !showModal) {
            setShowModal(true);
          }

          // 2. Fetch ADF/AI Stream Data
          const latestRes = await fetch('http://localhost:5001/api/latest-run');
          const latestData = await latestRes.json();

          if (latestData.status === 'no_runs' || latestData.status === 'waiting') {
            setLatestRun(null);
            // setLogs([]); // Don't clear logs here to prevent flickering if a poll is slow
            // If no runs, and action is not running, clear logs
            if (!statusData.is_running) {
              setLogs([]);
            }
            return;
          }

          if (latestData.run_id || latestData.status === 'manual_validation' || latestData.status === 'Succeeded') {
            setLatestRun(latestData);

            // Sync inference stream
            if (latestData.ai_thoughts) {
              const formattedLogs = latestData.ai_thoughts.map((t) => ({
                id: t.id,
                type: t.type,
                text: t.text
              }));
              setLogs(formattedLogs);
            }

            // Calculate Active Step
            let maxStep = 0;
            if (statusData.unified_progress?.SYNTHETIC === 'Succeeded') maxStep = 1;
            if (statusData.unified_progress?.BRONZE === 'Succeeded') maxStep = 2;
            if (statusData.unified_progress?.AI_VALIDATION === 'Succeeded') maxStep = 3;
            if (statusData.unified_progress?.GOLD === 'Succeeded') maxStep = 4;

            // Override with live ADF activities if they are running
            if (latestData.activities && latestData.activities.length > 0) {
              latestData.activities.forEach(act => {
                const name = act.name.toLowerCase();
                if (name.includes('copy') || name.includes('ingest')) maxStep = Math.max(maxStep, 1);
                if (name.includes('transform') || name.includes('silver')) maxStep = Math.max(maxStep, 2);
                if (name.includes('validate') || name.includes('ai')) maxStep = Math.max(maxStep, 3);
              });
            }
            if (latestData.status === 'Succeeded' && statusData.unified_progress?.GOLD === 'Succeeded') maxStep = 4;
            setActiveStep(maxStep);
          }
        }
      } catch (error) {
        console.error("Unified Poll Error:", error);
      }
    };

    const interval = setInterval(fetchEverything, 3000);
    fetchEverything();
    return () => clearInterval(interval);
  }, [simulationMode, activeStep, actionStatus.last_action, showModal]);

  // Update trust score occasionally
  useEffect(() => {
    const interval = setInterval(() => {
      setTrustScore(prev => +(prev + (Math.random() * 0.2 - 0.1)).toFixed(1));
    }, 3000);
    return () => clearInterval(interval);
  }, []);


  return (
    <div className="min-h-screen w-full bg-[#f8fafc] text-slate-900 p-8 font-sans overflow-x-hidden selection:bg-blue-100">
      {/* Background Particles - Enhanced for Light Mode */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden opacity-50">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400 rounded-full"
            animate={{
              y: [Math.random() * 1000, -10],
              opacity: [0, 0.6, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 5,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{ left: `${Math.random() * 100}%` }}
          />
        ))}
      </div>

      {/* Header */}
      <div className="relative z-10 flex justify-between items-center mb-8 glass-card p-6 rounded-2xl border-b border-blue-100 backdrop-blur-xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] bg-white/70">
        <div className="flex items-center gap-4">
          <motion.div
            whileHover={{ rotate: 180 }}
            className="w-12 h-12 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/10"
          >
            <Zap size={28} className="text-white fill-white" />
          </motion.div>
          <div>
            <h1 className="text-3xl font-black tracking-tighter text-slate-900">
              NEXUS <span className="font-light text-slate-400 mx-2">|</span> AI PIPELINE MONITOR
            </h1>
            <p className="text-[10px] text-blue-600 font-mono tracking-[0.3em] uppercase">End-to-End Synthetic-to-Gold Lineage</p>
          </div>
        </div>
        <div className="flex items-center gap-8">
          <button
            onClick={() => {
              setSimulationMode(!simulationMode);
              setActiveStep(0);
              setLogs([]);
            }}
            className={`px-4 py-2 rounded-lg border text-xs font-bold transition-all ${simulationMode ? 'bg-red-50 border-red-200 text-red-600' : 'bg-blue-50 border-blue-200 text-blue-600'} hover:scale-105 shadow-sm`}
          >
            {simulationMode ? 'STOP SIMULATION' : 'RUN RUNTIME SIMULATION'}
          </button>
          <div className="flex items-center gap-6 text-xs font-medium">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${simulationMode ? 'bg-amber-500' : 'bg-green-500'} animate-pulse`}></div>
              <span className="text-slate-600 uppercase tracking-widest">{simulationMode ? 'SIMULATOR ACTIVE' : 'LIVE AZURE'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Manual Pipeline Orchestrator - NEW SECTION */}
      <div className="relative z-10 mb-8 glass-card p-6 rounded-3xl border border-blue-50 bg-white/40 backdrop-blur-md shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xs font-black tracking-[0.2em] text-slate-400 uppercase flex items-center gap-2">
            <Cpu size={14} className="text-blue-500" /> Manual Pipeline Orchestrator
          </h2>
          {actionStatus.is_running && (
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-100 rounded-full animate-pulse">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              <span className="text-[9px] font-bold text-blue-600 uppercase italic">Executing: {actionStatus.last_action}</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { id: 'generate', label: '1. Generate Data', icon: FileCheck, color: 'bg-pink-50 text-pink-600 border-pink-100 hover:bg-pink-100' },
            { id: 'upload', label: '2. Push to ADLS', icon: Database, color: 'bg-amber-50 text-amber-600 border-amber-100 hover:bg-amber-100' },
            { id: 'trigger', label: '3. Run ADF Pipeline', icon: Zap, color: 'bg-blue-50 text-blue-600 border-blue-100 hover:bg-blue-100' },
            { id: 'validate', label: '4. AI Validation', icon: Cpu, color: 'bg-purple-50 text-purple-600 border-purple-100 hover:bg-purple-100' }
          ].map((action, i) => (
            <button
              key={action.id}
              disabled={actionStatus.is_running}
              onClick={() => triggerAction(action.id)}
              className={`flex items-center justify-between p-4 rounded-2xl border-2 transition-all duration-300 group ${action.color} ${actionStatus.is_running ? 'opacity-50 grayscale cursor-not-allowed' : 'hover:scale-[1.02] active:scale-95'}`}
            >
              <div className="flex items-center gap-4">
                <div className="p-2 bg-white rounded-xl shadow-sm group-hover:shadow-md transition-shadow">
                  <action.icon size={20} />
                </div>
                <span className="text-sm font-black tracking-tighter uppercase">{action.label}</span>
              </div>
              <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 transition-opacity translate-x-[-10px] group-hover:translate-x-0 group-hover:duration-300" />
            </button>
          ))}
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-12 gap-8">
        {/* Left Column: Lineage & KPIs */}
        <div className="col-span-12 lg:col-span-8 space-y-8">

          {/* KPI Cards */}
          <div className="grid grid-cols-3 gap-6">
            {[
              { label: 'AI TRUST SCORE', value: `${trustScore}%`, icon: ShieldCheck, color: 'text-blue-400', barColor: 'bg-blue-500' },
              { label: 'ANOMALIES FLAG', value: simulationMode ? '42' : '1,247', icon: AlertTriangle, color: 'text-purple-400', barColor: 'bg-purple-500' },
              { label: 'DATA VELOCITY', value: '4.2 TB/H', icon: Activity, color: 'text-cyan-400', barColor: 'bg-cyan-500' },
            ].map((kpi, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="glass-card p-6 rounded-2xl flex flex-col gap-4 border border-blue-100 bg-white shadow-sm hover:shadow-md transition-all duration-500 group"
              >
                <div className="flex justify-between items-start">
                  <p className="text-[10px] font-bold text-slate-400 tracking-[0.2em]">{kpi.label}</p>
                  <kpi.icon className={`${kpi.color} group-hover:scale-125 transition-transform`} size={20} />
                </div>
                <h2 className="text-4xl font-black text-slate-800">{kpi.value}</h2>
                <div className="w-full h-1 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full ${kpi.barColor} shadow-[0_0_10px_rgba(59,130,246,0.3)]`}
                    animate={{ width: kpi.label.includes('TRUST') ? `${trustScore}%` : '85%' }}
                  />
                </div>
              </motion.div>
            ))}
          </div>

          {/* Lineage Graph - Redesigned for Light Mode */}
          <div className="glass-card p-10 rounded-3xl min-h-[500px] border border-blue-50" style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9fafb 100%)' }}>
            <div className="mb-12">
              <h3 className="text-sm font-bold text-blue-600 flex items-center gap-2 tracking-widest uppercase">
                <Database size={16} /> Data Journey Lineage Map
              </h3>
              <p className="text-xs text-slate-400 mt-1 font-mono">Real-time status of pipeline units</p>
            </div>

            <div className="flex justify-between items-start h-full px-4 gap-2 relative z-10">
              {steps.map((step, i) => (
                <React.Fragment key={i}>
                  <div className="flex flex-col items-center flex-1 max-w-[160px]">
                    <motion.div
                      className={`relative w-24 h-24 rounded-2xl flex items-center justify-center border-2 transition-all duration-700 ${unifiedProgress[step.name.replace(' ', '_')] === 'InProgress'
                        ? 'bg-blue-50 border-blue-500 shadow-[0_10px_30px_rgba(59,130,246,0.15)] scale-110'
                        : unifiedProgress[step.name.replace(' ', '_')] === 'Succeeded'
                          ? 'bg-green-50 border-green-400 grayscale-0'
                          : 'bg-slate-50 border-slate-200 grayscale opacity-40'
                        }`}
                    >
                      <step.icon size={36} className={unifiedProgress[step.name.replace(' ', '_')] === 'InProgress' ? 'text-blue-600' : unifiedProgress[step.name.replace(' ', '_')] === 'Succeeded' ? 'text-green-500' : 'text-slate-400'} />

                      {unifiedProgress[step.name.replace(' ', '_')] === 'InProgress' && (
                        <motion.div
                          className="absolute inset-0 rounded-2xl border-2 border-blue-300"
                          animate={{ scale: [1, 1.2], opacity: [0.5, 0] }}
                          transition={{ duration: 1, repeat: Infinity }}
                        />
                      )}

                      {unifiedProgress[step.name.replace(' ', '_')] === 'Succeeded' && (
                        <div className="absolute -top-2 -right-2 bg-green-500 rounded-full p-1 border-2 border-white shadow-sm">
                          <ShieldCheck size={12} className="text-white" />
                        </div>
                      )}
                    </motion.div>

                    <div className="text-center mt-6">
                      <p className={`text-xs font-black tracking-tighter uppercase ${activeStep === i ? 'text-blue-600' : 'text-slate-500'}`}>{step.name}</p>
                      {step.name === 'AI VALIDATION' && <p className="text-[8px] bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full font-black mt-1 inline-block">SILVER ➔ GOLD BRIDGE</p>}
                      <p className="text-[10px] text-slate-400 font-mono mt-1 leading-tight">{step.label}</p>
                    </div>

                    {activeStep === i && simulationMode && simData?.steps[i] && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-[10px] text-blue-600 font-mono w-full shadow-sm"
                      >
                        {simData.steps[i].details}
                      </motion.div>
                    )}
                  </div>

                  {i < steps.length - 1 && (
                    <div className="flex-none pt-10 px-2">
                      <motion.div
                        animate={activeStep > i ? { opacity: 1 } : { opacity: 0.2 }}
                        className="flex items-center"
                      >
                        <ArrowRight size={20} className={activeStep > i ? 'text-blue-400' : 'text-slate-300'} />
                        <div className={`h-[1px] w-8 ${activeStep > i ? 'bg-gradient-to-r from-blue-400 to-transparent' : 'bg-slate-200'}`} />
                      </motion.div>
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>

            {/* Connection Lines Background */}
            <div className="absolute top-[165px] left-[50px] right-[50px] h-[1px] bg-slate-100 -z-1" />
          </div>

          {/* AI Audit Board - Isolated outside the glass card to prevent shifts */}
          {lastValidAiInsights && (
            <div className="col-span-12">
              <AIAuditBoard aiInsights={lastValidAiInsights} />
            </div>
          )}
        </div>

        {/* Right Column: AI Thoughts Feed */}
        <div className="col-span-12 lg:col-span-4 space-y-8">
          <div className="glass-card rounded-[2rem] flex flex-col h-full min-h-[665px] border border-blue-50 bg-white shadow-sm">
            <div className="p-8 border-b border-slate-50 flex justify-between items-center bg-slate-50/30 rounded-t-[2rem]">
              <h3 className="text-xs font-bold flex items-center gap-3 text-purple-600 tracking-[0.2em] uppercase">
                <Search size={18} className="animate-pulse" /> Live Inference Stream
              </h3>
              <div className="px-3 py-1 bg-purple-50 border border-purple-100 rounded-md text-[10px] text-purple-600 font-bold font-mono">
                PHI-3_V2
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8 font-mono text-[11px] space-y-5 scrollbar-hide">
              <AnimatePresence initial={false}>
                {logs.length === 0 && !latestRun && !simulationMode && (
                  <div className="h-full flex flex-col items-center justify-center text-slate-300 italic gap-4">
                    <div className="w-12 h-12 rounded-full border-2 border-slate-100 border-t-blue-500 animate-spin" />
                    <p className="text-center px-8">Searching for latest ADF runs in the last 24h...</p>
                    <p className="text-[9px] text-slate-400 not-italic uppercase tracking-widest mt-2 border-t pt-4">Make sure to trigger the pipeline via Azure CLI or Portal</p>
                  </div>
                )}
                {logs.length === 0 && (latestRun || simulationMode) && (
                  <div className="h-full flex items-center justify-center text-slate-300 italic">
                    Waiting for analytics processing...
                  </div>
                )}
                {logs.map((log) => (
                  <motion.div
                    key={log.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex gap-4 group cursor-help border-l-2 border-transparent hover:border-blue-200 pl-2 transition-all"
                  >
                    <span className="text-slate-300 hidden group-hover:inline">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                    <span className={
                      log.type === 'warning' ? 'text-red-500' :
                        log.type === 'success' ? 'text-green-500' :
                          log.type === 'process' ? 'text-blue-500' : 'text-slate-400'
                    }>
                      {log.type === 'warning' ? '●' : log.type === 'success' ? '●' : '○'}
                    </span>
                    <p className={`flex-1 transition-colors ${log.type === 'warning' ? 'text-red-700 font-medium' : 'text-slate-600 group-hover:text-slate-900'}`}>
                      {log.text}
                    </p>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            <div className="p-8 bg-slate-50 border-t border-slate-100 rounded-b-[2rem]">
              <div className="flex items-center gap-5 p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center border border-blue-100 shadow-inner">
                  <Activity size={18} className="text-blue-600" />
                </div>
                <div className="flex-1">
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
                      initial={{ width: '20%' }}
                      animate={{ width: ['20%', '85%', '20%'] }}
                      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    />
                  </div>
                  <div className="flex justify-between mt-2">
                    <p className="text-[9px] text-slate-400 uppercase font-black tracking-widest italic">{activeStep === 3 ? 'AI Deep Analysis...' : 'Processor Idle'}</p>
                    <p className="text-[9px] text-blue-600 font-mono">842 OPS</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <PipelineConsoleModal
        showModal={showModal}
        setShowModal={setShowModal}
        actionStatus={actionStatus}
        displayLogs={displayLogs}
      />
    </div>
  );
};

export default Dashboard;
