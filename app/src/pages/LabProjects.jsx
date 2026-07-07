import React from 'react';
import { Rocket, Server, Layout as LayoutIcon, Briefcase, ChevronRight, Activity } from 'lucide-react';
import './LabProjects.css';

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

        <div className="projects-grid">
          {/* Project 1 Card */}
          <div className="project-card cyan">
            <div className="card-bg-icon">
              <Briefcase size={160} />
            </div>
            
            <div className="card-header">
              <div className="icon-wrapper cyan">
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
