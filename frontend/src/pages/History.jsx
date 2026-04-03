import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { Clock, CheckCircle2, ChevronRight, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function History() {
  const navigate = useNavigate();
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        const res = await fetch('http://127.0.0.1:8000/history');
        if (!res.ok) throw new Error('Failed to load history');
        const data = await res.json();
        setHistoryItems(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <>
      <header className="mb-8 p-1">
        <h1 className="text-3xl font-bold text-white tracking-tight">Prediction History</h1>
        <p className="text-slate-400 mt-2">Past transaction batches and model prediction records.</p>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-danger/20 border border-danger text-danger rounded-lg">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : historyItems.length === 0 ? (
        <div className="text-center py-12 text-slate-400 bg-white/5 rounded-xl border border-white/10">
          No transactions found. Go to Dashboard to run a prediction and save it.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {historyItems.map((txn) => {
            const date = new Date(txn.timestamp);
            const timeAgo = date.toLocaleString();
            
            return (
              <GlassCard 
                key={txn.id} 
                onClick={() => navigate(`/history/${txn.id}`)}
                className="cursor-pointer group flex flex-col justify-between"
              >
                <div className="flex justify-between items-start mb-6">
                  <div className="flex items-center gap-2 text-primary font-bold">
                    <CheckCircle2 className="w-5 h-5 text-success" />
                    <span>#{txn.id}</span>
                  </div>
                  <div className="flex items-center gap-1 text-slate-400 text-xs font-medium bg-black/30 px-2 py-1 rounded-full">
                    <Clock className="w-3 h-3" />
                    {timeAgo}
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Records</p>
                    <p className="font-medium text-white">{txn.prediction_count}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-xs text-slate-400 mb-1">Threshold / Default Cutoff</p>
                    <p className="font-medium text-amber-400">{Number(txn.threshold).toFixed(2)}</p>
                  </div>
                </div>

                <div className="flex justify-end items-center text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                  View Details <ChevronRight className="w-4 h-4 ml-1" />
                </div>
              </GlassCard>
            );
          })}
        </div>
      )}
    </>
  );
}
