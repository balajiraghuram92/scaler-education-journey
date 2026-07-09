import React from 'react';
import { Home, Folder, BookOpen, ChevronLeft, ChevronRight, Cpu, ArrowRight } from 'lucide-react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, Tooltip
} from 'recharts';
import './LabProjects.css';

const radarData = [
  { subject: 'Backend', A: 80, fullMark: 100 },
  { subject: 'Frontend', A: 65, fullMark: 100 },
  { subject: 'Cloud-Native', A: 45, fullMark: 100 },
  { subject: 'LLM Design', A: 90, fullMark: 100 },
  { subject: 'Deployment', A: 60, fullMark: 100 },
  { subject: 'Data Flow', A: 75, fullMark: 100 },
];

const specializations = [
  { id: 0, title: 'Agentic AI Core', module: 'PREREQUISITE', done: 0, total: 12, adherence: 85, trend: [20, 30, 40, 35, 60, 80, 85] },
  { id: 1, title: 'FDE Foundations: Python, Workflow & Delivery', module: 'MODULE 1', done: 0, total: 12, adherence: 70, trend: [10, 20, 15, 30, 50, 60, 70] },
  { id: 2, title: 'Backend Engineering, Observability & Data Systems', module: 'MODULE 2', done: 2, total: 15, adherence: 65, trend: [30, 25, 45, 40, 55, 50, 65] },
  { id: 3, title: 'Full-Stack FDE: Typescript, React & AI Frontends', module: 'MODULE 3', done: 1, total: 15, adherence: 55, trend: [10, 15, 20, 35, 30, 45, 55] },
  { id: 4, title: 'Cloud, DevOps, Kubernetes & Infrastructure', module: 'MODULE 4', done: 1, total: 12, adherence: 45, trend: [5, 10, 8, 15, 25, 35, 45] },
  { id: 5, title: 'Enterprise Communication, Consulting & LLM Eng', module: 'MODULE 5', done: 0, total: 12, adherence: 80, trend: [40, 35, 50, 60, 55, 70, 80] },
  { id: 6, title: 'Agentic Systems & Enterprise Integrations', module: 'MODULE 6', done: 0, total: 11, adherence: 40, trend: [10, 15, 12, 20, 25, 30, 40] },
  { id: 7, title: 'Application Engineering, Security & Reliability', module: 'MODULE 7', done: 0, total: 12, adherence: 50, trend: [15, 25, 20, 30, 40, 45, 50] },
];

const focusLessons = [
  { title: 'GenAI World & LLM Landscape', skill: 90, chartData: [4, 6, 8, 7, 9, 10] },
  { title: 'Prompt Engineering Basics', skill: 95, chartData: [5, 7, 9, 8, 10, 10] },
  { title: 'Advanced Prompting & Safety Basics', skill: 95, chartData: [6, 8, 9, 10, 10, 10] },
  { title: 'LLM Built in Power Tools', skill: 32, chartData: [1, 2, 2, 3, 4, 3] },
  { title: 'RAG (Retrieval-Augmented Generation)', skill: 32, chartData: [1, 1, 2, 3, 3, 3] },
  { title: 'Agentic Automation Workflow', skill: 95, chartData: [5, 6, 8, 9, 10, 10] },
  { title: 'Building an AI Agent?', skill: 32, chartData: [2, 2, 3, 3, 4, 3] },
  { title: 'OpenClaw: Personal 24/7 Agent', skill: 32, chartData: [1, 2, 1, 3, 2, 3] },
  { title: 'Debugging AI', skill: 32, chartData: [1, 1, 2, 2, 3, 3] },
];

export default function LabProjects() {
  return (
    <div className="lab-projects-container dark-mode">
      {/* Ambient background orbs for premium dark glassmorphic effect */}
      <div className="ambient-orb orb-1"></div>
      <div className="ambient-orb orb-2"></div>
      
      {/* Top Navbar */}
      <div className="top-navbar glass-panel">
        <div className="nav-brand">
          <div className="brand-logo">R</div>
          <span className="brand-name">Raghuram Balaji</span>
        </div>
        <div className="nav-links">
          <div className="nav-link"><Home size={16}/> Home</div>
          <div className="nav-link active"><Folder size={16}/> Projects</div>
          <div className="nav-link"><BookOpen size={16}/> Lessons</div>
        </div>
      </div>

      <div className="content-wrapper">
        <button className="back-btn glass-btn">
          <ChevronLeft size={16} /> Back to Dashboard
        </button>

        {/* Hero Section */}
        <div className="hero-section">
          {/* Left: Maturity Network */}
          <div className="maturity-card glass-panel">
            <h3 className="panel-title">Core Architectural Maturity:</h3>
            <div className="maturity-content">
              <div className="score-block">
                <div className="dial-value">3.8<span className="max-val">/5</span></div>
                <div className="dial-label">Pattern Adherence Score:</div>
                <div className="dial-value highlight">78%</div>
                <div className="dial-label">Projected Next Milestone:</div>
                <div className="dial-value-small">8 Days</div>
                <p className="subtext">
                  Subtext description from fde-vertical-page. Overall P-DE Track Pattern Network Map as data-driven descriptive context.
                </p>
              </div>
              <div className="score-visual">
                 <div className="network-flow-mock">
                    <div className="flow-bubble">4%</div>
                    <svg viewBox="0 0 100 200" className="flow-svg">
                      <path d="M50 20 C 20 60, 80 140, 50 180" stroke="rgba(56, 189, 248, 0.4)" strokeWidth="2" fill="none" />
                      <path d="M50 20 C 80 60, 20 140, 50 180" stroke="rgba(168, 85, 247, 0.4)" strokeWidth="2" fill="none" />
                      <circle cx="50" cy="20" r="4" fill="#38bdf8" />
                      <circle cx="35" cy="100" r="3" fill="#a855f7" />
                      <circle cx="65" cy="100" r="3" fill="#38bdf8" />
                      <circle cx="50" cy="180" r="4" fill="#a855f7" />
                    </svg>
                 </div>
              </div>
            </div>
          </div>

          {/* Right: Competence Balance */}
          <div className="competence-card glass-panel">
             <h3 className="panel-title">FDE TRACK COMPETENCE BALANCE (Maturity Matrix)</h3>
             <div className="radar-container">
               <ResponsiveContainer width="100%" height={260}>
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.15)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
                    <Radar name="Competence" dataKey="A" stroke="#38bdf8" fill="url(#colorUv)" fillOpacity={0.6} />
                    <defs>
                      <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0.8}/>
                      </linearGradient>
                    </defs>
                    <Tooltip contentStyle={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}/>
                  </RadarChart>
               </ResponsiveContainer>
             </div>
             <div className="path-status">
               <div className="path-labels">
                 <span>Overall Path Status</span>
                 <span>Target Date</span>
               </div>
               <div className="progress-bar-bg">
                 <div className="progress-bar-fill" style={{ width: '70%' }}></div>
               </div>
               <div className="path-labels sub">
                 <span>Overall Path Milestone</span>
                 <span>Completion 28, 2023</span>
               </div>
             </div>
          </div>
        </div>

        {/* Specializations Grid */}
        <div className="specializations-section">
          <div className="section-header">
            <div className="header-title-wrap">
              <Folder size={24} className="header-icon"/>
              <h2>Specializations</h2>
            </div>
            <div className="nav-arrows">
              <button className="glass-btn icon-btn"><ChevronLeft size={16}/></button>
              <button className="glass-btn icon-btn"><ChevronRight size={16}/></button>
            </div>
          </div>
          
          <div className="specializations-grid">
            {specializations.map(spec => (
              <div key={spec.id} className={`spec-card glass-panel ${spec.id === 0 ? 'active' : ''}`}>
                <div className="spec-module">{spec.module}</div>
                <h4 className="spec-title">{spec.title}</h4>
                <div className="spec-metrics">
                  <div className="adherence">
                    <span className="label">Adherence Score</span>
                    <div className="mini-chart">
                       <ResponsiveContainer width="100%" height={40}>
                         <BarChart data={spec.trend.map((v, i) => ({name: i, val: v}))}>
                           <Bar dataKey="val" fill={spec.id === 0 ? '#38bdf8' : '#475569'} radius={[2,2,0,0]} />
                         </BarChart>
                       </ResponsiveContainer>
                    </div>
                  </div>
                </div>
                <div className="spec-footer">
                  <span className="progress-text">{spec.done}/{spec.total} Done</span>
                  <div className={`progress-ring ${spec.done > 0 ? 'started' : ''}`}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Focus Panel */}
        <div className="focus-panel glass-panel">
           <div className="focus-header">
             <div>
               <div className="focus-subtitle">SPECIALIZATION FOCUS</div>
               <h3 className="focus-title">Agentic AI Core (Prerequisite)</h3>
             </div>
             <div className="focus-progress">0 of 11 Completed</div>
           </div>

           <div className="focus-content">
             <div className="lessons-list">
               {focusLessons.map((lesson, idx) => (
                 <div key={idx} className="lesson-item glass-panel-inner">
                   <div className="lesson-info">
                     <div className="checkbox"></div>
                     <span className="lesson-title">{lesson.title}</span>
                   </div>
                   <div className="lesson-stats">
                     <div className="skill-label">
                       <span className="skill-text">skill</span>
                       <span className="skill-val">{lesson.skill}%</span>
                     </div>
                     <div className="skill-chart">
                        <ResponsiveContainer width="100%" height={24}>
                           <BarChart data={lesson.chartData.map((v,i)=>({name:i, val:v}))}>
                             <Bar dataKey="val" fill={lesson.skill > 50 ? '#38bdf8' : '#475569'} radius={[1,1,0,0]} />
                           </BarChart>
                        </ResponsiveContainer>
                     </div>
                     <ArrowRight size={16} className="arrow-icon"/>
                   </div>
                 </div>
               ))}
             </div>

             <div className="insight-panel-container">
               <div className="insight-panel glass-panel-highlight">
                 <div className="insight-header">
                   <h4 className="insight-title">AI PATH OPTIMIZATION INSIGHT PANEL</h4>
                 </div>
                 <p className="insight-text">
                   You are excelling in GenAI (95%), but your Cloud-Native knowledge is lower (32%). Prioritize the 'Cloud, DevOps & Infrastructure' module to maintain a balanced Agentic AI Architect path.
                 </p>
               </div>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}
