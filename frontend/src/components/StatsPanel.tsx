import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './StatsPanel.css';

interface StatsPanelProps {
  stats: {
    total: number;
    by_severity: { [key: string]: number };
    by_type: { [key: string]: number };
    sandbox_executed: number;
  };
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats }) => {
  const severityData = Object.entries(stats.by_severity)
    .filter(([_, count]) => count > 0)
    .map(([severity, count]) => ({
      name: severity.charAt(0).toUpperCase() + severity.slice(1),
      value: count,
    }));

  const typeData = Object.entries(stats.by_type)
    .filter(([_, count]) => count > 0)
    .map(([type, count]) => ({
      name: type.toUpperCase(),
      value: count,
    }));

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="stats-panel">
      <h3>Security Statistics</h3>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Threats</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.sandbox_executed}</div>
          <div className="stat-label">Sandbox Executions</div>
        </div>
      </div>

      <div className="charts-grid">
        {severityData.length > 0 && (
          <div className="chart-container">
            <h4>Threats by Severity</h4>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {typeData.length > 0 && (
          <div className="chart-container">
            <h4>Threats by Type</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" />
                <YAxis stroke="rgba(255,255,255,0.7)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatsPanel;


