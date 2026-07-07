import React from 'react';
import { Rocket, Server, Layout as LayoutIcon, Briefcase, ChevronRight, Activity, Cpu, Shield, Zap } from 'lucide-react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  RadialBarChart, RadialBar, Legend
} from 'recharts';
import './LabProjects.css';

const radarData = [
  { subject: 'React / UI', A: 95, fullMark: 100 },
  { subject: '.NET Core', A: 85, fullMark: 100 },
  { subject: 'Cloud Native', A: 75, fullMark: 100 },
  { subject: 'WebRTC', A: 80, fullMark: 100 },
  { subject: 'Event-Driven', A: 90, fullMark: 100 },
  { subject: 'Microservices', A: 80, fullMark: 100 },
];

const areaData = [
  { name: '08:00', throughput: 1200, latency: 150 },
  { name: '09:00', throughput: 2100, latency: 130 },
  { name: '10:00', throughput: 3400, latency: 180 },
  { name: '11:00', throughput: 2800, latency: 140 },
  { name: '12:00', throughput: 4200, latency: 120 },
  { name: '13:00', throughput: 3800, latency: 110 },
  { name: '14:00', throughput: 5100, latency: 90 },
];

const radialData = [
  { name: 'Architecture', uv: 85, fill: '#0d9488' },
  { name: 'Performance', uv: 92, fill: '#9333ea' },
  { name: 'Security', uv: 78, fill: '#06b6d4' },
];

export default function LabProjects() {
  return (
    <div className="lab-projects-container">
      <div className="lab-content">
        
        <div className="dev-badge">
          <Activity size={16} />
          <span>In Development</span>
        </div>

        <h1 className="lab-title">
          Lab Projects
        </h1>
        
        <p className="lab-subtitle">
          Crafting next-generation applications. A showcase of architectural excellence using <strong>React Frontend</strong> and <strong>.NET Backend</strong>.
        </p>

        {/* Development Analytics Hub */}
        <div className="analytics-hub">
          <div className="hub-header">
            <h2>Development Analytics Hub</h2>
            <p>Real-time insights and architectural maturity metrics</p>
          </div>

          <div className="charts-grid">
            {/* Tech Stack Breadth Coverage - Radar Chart */}
            <div className="chart-card">
              <h3>Tech Stack Breadth Coverage</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="rgba(30, 41, 59, 0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 12 }} />
                    <Radar name="Coverage" dataKey="A" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.3} />
                    <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* RTC Data Throughput and Latency Forecast - Area Chart */}
            <div className="chart-card">
              <h3>RTC Data Throughput & Latency Forecast</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={areaData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorThroughput" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#9333ea" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#9333ea" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0d9488" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#0d9488" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(30, 41, 59, 0.1)" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 11 }} stroke="rgba(30, 41, 59, 0.1)" />
                    <YAxis yAxisId="left" tick={{ fill: '#475569', fontSize: 11 }} stroke="rgba(30, 41, 59, 0.1)" />
                    <YAxis yAxisId="right" orientation="right" tick={{ fill: '#475569', fontSize: 11 }} stroke="rgba(30, 41, 59, 0.1)" />
                    <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                    <Area yAxisId="left" type="monotone" dataKey="throughput" stroke="#9333ea" fillOpacity={1} fill="url(#colorThroughput)" name="Throughput (msg/s)" />
                    <Area yAxisId="right" type="monotone" dataKey="latency" stroke="#0d9488" fillOpacity={1} fill="url(#colorLatency)" name="Latency (ms)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Circular Maturity Dials */}
            <div className="chart-card">
              <h3>Architectural Maturity Dials</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="30%" outerRadius="90%" barSize={12} data={radialData}>
                    <RadialBar
                      minAngle={15}
                      background={{ fill: 'rgba(30, 41, 59, 0.05)' }}
                      clockWise
                      dataKey="uv"
                      cornerRadius={10}
                    />
                    <Legend iconSize={10} layout="vertical" verticalAlign="middle" wrapperStyle={{ right: '5%', fontSize: '12px', color: '#475569' }} />
                    <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} cursor={{ fill: 'rgba(0,0,0,0.05)' }}/>
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Insight Panel */}
            <div className="insight-card">
              <div className="insight-header">
                <Cpu size={20} className="insight-icon" />
                <h3>AI Insight</h3>
              </div>
              <p className="insight-text">
                "Architectural pattern reuse is high across both applications. Consider extracting the common Event-Driven messaging abstraction into a shared .NET NuGet package and a companion React hook library to further accelerate future development."
              </p>
              <div className="insight-metrics">
                <div className="metric">
                  <Shield size={16} />
                  <span>Security: <strong>Robust</strong></span>
                </div>
                <div className="metric">
                  <Zap size={16} />
                  <span>Performance: <strong>Optimal</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="projects-grid">
          {/* Project 1 Card */}
          <div className="project-card teal">
            <div className="card-bg-icon">
              <Briefcase size={160} />
            </div>
            
            <div className="card-header">
              <div className="icon-wrapper teal">
                <Server size={28} />
              </div>
              <h3 className="card-title">Cloud SaaS Localization</h3>
            </div>
            
            <p className="card-description">
              Automating enterprise translation lifecycles with an event-driven architecture, bridging client-side extraction with a distributed .NET Core backend and a React-powered dashboard.
            </p>
            
            <div className="tags-container">
              <span className="tag">.NET Core</span>
              <span className="tag">React</span>
            </div>
          </div>

          {/* Project 2 Card */}
          <div className="project-card purple">
            <div className="card-bg-icon" style={{ transform: 'rotate(-15deg)' }}>
              <LayoutIcon size={160} />
            </div>

            <div className="card-header">
              <div className="icon-wrapper purple">
                <Rocket size={28} />
              </div>
              <h3 className="card-title">Smart Factory WMS</h3>
            </div>
            
            <p className="card-description">
              A real-time WebRTC enabled Warehouse Management System (WMS) with predictive inventory algorithms to track shipments, calculate assembly capacities, and automate restocking.
            </p>
            
            <div className="tags-container">
              <span className="tag">WebRTC</span>
              <span className="tag">.NET Core</span>
            </div>
          </div>
        </div>
        
        <div className="lab-footer">
          <p className="footer-text">Coming soon to</p>
          <div className="footer-link">
            <ChevronRight size={16} /> <span>github.com/raghuram-balaji</span>
          </div>
        </div>

      </div>
    </div>
  );
}
