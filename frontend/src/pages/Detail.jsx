import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, AlertTriangle, ShieldCheck, Settings2, Loader2 } from 'lucide-react';
import { 
  PieChart, Pie, Cell, Tooltip, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
  ScatterChart, Scatter
} from 'recharts';

const mockHistogram = Array.from({ length: 20 }).map((_, i) => ({
  prob: (i * 0.05).toFixed(2),
  count: Math.floor(Math.random() * 80)
}));

const mockScatterData = Array.from({ length: 50 }).map(() => ({
  fico: Math.floor(Math.random() * (850 - 300) + 300),
  dti: (Math.random() * 40).toFixed(1),
  prob: Math.random()
}));

const pieColors = ['#22c55e', '#ef4444'];

export function Detail() {
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [threshold, setThreshold] = useState(0.5);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetch(`http://127.0.0.1:8000/transaction/${transactionId}`);
        if (!res.ok) throw new Error('Failed to load transaction data');
        const json = await res.json();
        setData(json);
        setThreshold(json.transaction.threshold);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [transactionId]);

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 mt-10 max-w-3xl mx-auto bg-danger/20 border border-danger text-danger rounded-lg">
        <h2 className="text-xl font-bold mb-2">Error Loading Transaction</h2>
        <p>{error || "Transaction not found."}</p>
        <button onClick={() => navigate(-1)} className="mt-4 px-4 py-2 bg-black/20 hover:bg-black/40 rounded transition">
          Go Back
        </button>
      </div>
    );
  }

  const { transaction, predictions } = data;
  const numAnalyzed = predictions.length;
  const flaggedDefaults = predictions.filter(p => p.probability >= threshold).length;
  const numHealthy = numAnalyzed - flaggedDefaults;

  const dynamicPieData = [
    { name: 'Healthy', value: numHealthy },
    { name: 'Default', value: flaggedDefaults },
  ];

  return (
    <>
      <header className="mb-8 p-1 flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-300">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Batch Details</h1>
          <p className="text-slate-400 mt-1 font-mono text-sm">
            ID: {transaction.id} | File: {transaction.file_name} | Date: {new Date(transaction.timestamp).toLocaleString()}
          </p>
        </div>
      </header>

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <Users className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Total Analyzed</p>
            <h2 className="text-2xl font-bold text-white">{numAnalyzed}</h2>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-danger/20 rounded-xl text-danger">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Flagged Defaults</p>
            <h2 className="text-2xl font-bold text-white">{flaggedDefaults}</h2>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-success/20 rounded-xl text-success">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Healthy</p>
            <h2 className="text-2xl font-bold text-white">{numHealthy}</h2>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-slate-700/50 rounded-xl text-slate-300">
            <Settings2 className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Default Threshold</p>
            <h2 className="text-2xl font-bold text-white">{threshold.toFixed(2)}</h2>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <GlassCard interactive={false} className="lg:col-span-2 p-8">
          <h3 className="font-semibold text-lg text-white mb-4">Real-time Threshold Control</h3>
          <div className="px-4 py-8 bg-black/20 rounded-xl border border-white/5">
            <input 
              type="range" 
              min="0" max="1" step="0.01" 
              value={threshold} 
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full accent-primary h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between mt-4 text-xs font-medium text-slate-400">
              <span>0.0 (Lenient)</span>
              <span className="text-primary text-base font-bold bg-primary/10 px-4 py-1 rounded-full">{threshold.toFixed(2)}</span>
              <span>1.0 (Strict)</span>
            </div>
          </div>
          <p className="text-sm text-slate-400 mt-4 text-center">Changing the slider updates the high risk candidates instantly.</p>
        </GlassCard>
        
        <GlassCard interactive={false} className="flex flex-col h-64">
           <h3 className="font-semibold text-lg text-white mb-4">Composition</h3>
           <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={dynamicPieData} innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                  {dynamicPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Charts (Partially Mocked for Visual Consistency) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <GlassCard interactive={false} className="h-80 flex flex-col">
          <h3 className="font-semibold text-lg text-white mb-4">Probability Distribution (Sample)</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockHistogram}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="prob" stroke="#94a3b8" fontSize={10} />
                <YAxis stroke="#94a3b8" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                <Bar dataKey="count" fill="#3b82f6" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard interactive={false} className="h-80 flex flex-col">
          <h3 className="font-semibold text-lg text-white mb-4">FICO vs Probability (Mock)</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="fico" type="number" domain={[300, 850]} name="FICO Score" stroke="#94a3b8" fontSize={10} />
                <YAxis dataKey="prob" type="number" domain={[0, 1]} name="Probability" stroke="#94a3b8" fontSize={10} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                <Scatter name="Loans" data={mockScatterData} fill="#ef4444" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard interactive={false} className="h-80 flex flex-col">
          <h3 className="font-semibold text-lg text-white mb-4">DTI vs Probability (Mock)</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="dti" type="number" name="DTI" stroke="#94a3b8" fontSize={10} />
                <YAxis dataKey="prob" type="number" domain={[0, 1]} name="Probability" stroke="#94a3b8" fontSize={10} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                <Scatter name="Loans" data={mockScatterData} fill="#eab308" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* High Risk Table */}
      <GlassCard interactive={false}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg text-white">Flagged High Risk Candidates</h3>
          <span className="text-xs bg-danger/10 text-danger px-3 py-1 rounded-full font-medium">Based on current threshold &ge; {threshold.toFixed(2)}</span>
        </div>
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 text-sm sticky top-0 bg-slate-900/90 backdrop-blur">
                <th className="py-4 px-4 font-medium">ID</th>
                <th className="py-4 px-4 font-medium">Name</th>
                <th className="py-4 px-4 font-medium">Probability</th>
                <th className="py-4 px-4 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((row) => {
                const isFlagged = row.probability >= threshold;
                if (!isFlagged) return null;
                
                return (
                  <tr key={row.customer_id || row.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-4 px-4 font-mono text-sm text-slate-300">{row.customer_id || row.id}</td>
                    <td className="py-4 px-4 text-white font-medium">{row.name}</td>
                    <td className="py-4 px-4 text-danger font-medium">{(row.probability * 100).toFixed(1)}%</td>
                    <td className="py-4 px-4">
                      <button className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-xs transition-colors font-medium">
                        Review
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {predictions.filter(r => r.probability >= threshold).length === 0 && (
            <div className="p-8 text-center text-slate-500 text-sm font-medium">
              No high risk candidates found with current threshold.
            </div>
          )}
        </div>
      </GlassCard>
    </>
  );
}
