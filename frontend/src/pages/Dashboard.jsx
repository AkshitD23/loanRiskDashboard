import React, { useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { Upload, Play, Activity, Users, AlertTriangle, ShieldCheck, CheckCircle } from 'lucide-react';
import {
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';
import { useNavigate } from 'react-router-dom';

const mockPurposeData = [
  { name: 'Debt Cons.', default: 120, healthy: 400 },
  { name: 'Credit Card', default: 40, healthy: 200 },
  { name: 'Home Impr.', default: 10, healthy: 120 },
  { name: 'Other', default: 10, healthy: 100 },
];

const mockHomeData = [
  { name: 'Mortgage', default: 60, healthy: 450 },
  { name: 'Rent', default: 100, healthy: 300 },
  { name: 'Own', default: 20, healthy: 70 },
];

const mockHistogram = Array.from({ length: 20 }).map((_, i) => ({
  prob: (i * 0.05).toFixed(2),
  count: Math.floor(Math.random() * 50) + (i > 10 ? Math.floor(Math.random() * 20) : 0)
}));

const pieColors = ['#22c55e', '#ef4444'];

export function Dashboard() {
  const [threshold, setThreshold] = useState(0.5);
  const [file, setFile] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savedTxId, setSavedTxId] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handlePredict = async () => {
    if (!file) {
      setError("Please upload a CSV file first.");
      return;
    }
    setError(null);
    setLoading(true);
    setSavedTxId(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("threshold", threshold);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const data = await res.json();
      setPredictions(data.predictions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (predictions.length === 0) return;
    setLoading(true);
    try {
      const payload = {
        threshold,
        file_name: file ? file.name : "uploaded.csv",
        predictions
      };
      const res = await fetch("http://127.0.0.1:8000/save_transaction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSavedTxId(data.transaction_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Derived metrics from actual predictions if available
  const totalApps = predictions.length > 0 ? predictions.length : 0;
  const numDefaults = predictions.length > 0 ? predictions.filter(p => (p.probability >= threshold)).length : 0;
  const numHealthy = totalApps - numDefaults;
  let defaultRate = ((numDefaults / totalApps) * 100).toFixed(1);
  if (isNaN(defaultRate)) {
    defaultRate = 0
  }

  const dynamicPieData = [
    { name: 'Healthy', value: numHealthy },
    { name: 'Default', value: numDefaults },
  ];

  return (
    <>
      <header className="mb-8 p-1">
        <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard</h1>
        <p className="text-slate-400 mt-2">Overall risk metrics and live predictions.</p>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-danger/20 border border-danger text-danger rounded-lg">
          {error}
        </div>
      )}

      {savedTxId && (
        <div className="mb-6 p-4 bg-success/20 border border-success text-success rounded-lg flex items-center justify-between">
          <span>Transaction saved successfully with ID: {savedTxId}</span>
          <button
            onClick={() => navigate(`/history/${savedTxId}`)}
            className="px-4 py-2 bg-success text-white rounded font-medium hover:bg-success/80 transition"
          >
            View Details
          </button>
        </div>
      )}

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <Users className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Total Applications</p>
            <h2 className="text-2xl font-bold text-white">{totalApps}</h2>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-danger/20 rounded-xl text-danger">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Predicted Defaults</p>
            <h2 className="text-2xl font-bold text-white">{numDefaults}</h2>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-success/20 rounded-xl text-success">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Non Defaults</p>
            <h2 className="text-2xl font-bold text-white">{numHealthy}</h2>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Default Rate</p>
            <h2 className="text-2xl font-bold text-white">{defaultRate}%</h2>
          </div>
        </GlassCard>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <GlassCard className="relative flex flex-col justify-center items-center py-8 border-dashed border-2 border-slate-600 hover:border-primary/50 cursor-pointer overflow-hidden">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="absolute inset-0 opacity-0 cursor-pointer z-10"
          />
          {file ? (
            <>
              <CheckCircle className="w-10 h-10 text-success mb-4" />
              <h3 className="font-semibold text-lg text-white">File Selected</h3>
              <p className="text-sm text-success">{file.name}</p>
            </>
          ) : (
            <>
              <Upload className="w-10 h-10 text-slate-400 mb-4" />
              <h3 className="font-semibold text-lg text-white">Upload Data</h3>
              <p className="text-sm text-slate-400">Drag & drop CSV file here or click</p>
            </>
          )}
        </GlassCard>

        <GlassCard interactive={false} className="flex flex-col justify-center">
          <h3 className="font-semibold text-lg text-white mb-2">Decision Threshold</h3>
          <p className="text-sm text-slate-400 mb-4">Adjust threshold for default prediction.</p>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0" max="1" step="0.01"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full accent-primary cursor-pointer"
            />
            <span className="font-mono bg-white/10 px-3 py-1 rounded-md">{threshold.toFixed(2)}</span>
          </div>
        </GlassCard>

        <GlassCard
          onClick={handlePredict}
          className={`flex flex-col justify-center items-center py-8 group ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer bg-gradient-to-br from-primary/80 to-primary/40 hover:from-primary hover:to-primary/60'}`}
        >
          {loading ? (
            <div className="w-10 h-10 border-4 border-white/20 border-t-white rounded-full animate-spin mb-2"></div>
          ) : (
            <Play className="w-10 h-10 text-white mb-2 group-hover:scale-110 transition-transform" />
          )}
          <h3 className="font-bold text-xl text-white">{loading ? 'Processing...' : 'Run Prediction'}</h3>
        </GlassCard>
      </div>

      {predictions.length > 0 && (
        <div className="mb-6 flex justify-end">
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-6 py-3 bg-gradient-to-r from-success to-emerald-600 font-bold text-white rounded-lg shadow-lg hover:shadow-xl hover:scale-105 transition disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Transaction to DB'}
          </button>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <GlassCard interactive={false} className="h-96 flex flex-col">
          <h3 className="font-semibold text-lg text-white mb-4">Default vs Non-Default</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={dynamicPieData} innerRadius={80} outerRadius={120} paddingAngle={5} dataKey="value">
                  {dynamicPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard interactive={false} className="h-96 flex flex-col">
          <h3 className="font-semibold text-lg text-white mb-4">Probability Distribution (Sample)</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockHistogram}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="prob" stroke="#94a3b8" fontSize={12} tickMargin={10} />
                <YAxis stroke="#94a3b8" fontSize={12} tickMargin={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Table Card */}
      <GlassCard interactive={false}>
        <h3 className="font-semibold text-lg text-white mb-4">
          {predictions.length > 0 ? "Prediction Results" : "Recent High Risk Applications (Mock)"}
        </h3>
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 text-sm sticky top-0 bg-slate-900/90 backdrop-blur">
                <th className="py-4 px-4 font-medium">ID</th>
                <th className="py-4 px-4 font-medium">Name</th>
                <th className="py-4 px-4 font-medium">Probability</th>
                <th className="py-4 px-4 font-medium">Prediction</th>
              </tr>
            </thead>
            <tbody>
              {predictions.length > 0 ? predictions.map((row, i) => {
                const dynamicPrediction = row.probability >= threshold ? "High Risk" : "Low Risk";
                const isDefault = dynamicPrediction === "High Risk";
                return (
                  <tr
                    key={row.id || i}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <td className="py-4 px-4 font-mono text-sm text-slate-300">{row.id}</td>
                    <td className="py-4 px-4 text-white font-medium">{row.name}</td>
                    <td className="py-4 px-4 text-slate-300">{(row.probability * 100).toFixed(1)}%</td>
                    <td className="py-4 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${isDefault ? 'bg-danger/20 text-danger' : 'bg-success/20 text-success'}`}>
                        {dynamicPrediction}
                      </span>
                    </td>
                  </tr>
                );
              }) : (
                <tr>
                  <td colSpan="4" className="py-8 text-center text-slate-500 italic">
                    Upload a file and run prediction to see results.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </>
  );
}
