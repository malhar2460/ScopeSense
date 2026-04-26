import React from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { FileText, ShieldCheck } from 'lucide-react';
import Login from './components/Login';
import Upload from './components/Upload';
import Processing from './components/Processing';
import Dashboard from './components/Dashboard';
import './App.css';

const ROUTE_COPY = {
  login: {
    title: 'Workspace Access',
    subtitle: 'Use demo credentials to enter the analysis workspace and start a new review.',
    badge: 'Sign In',
    stage: 'Step 1 of 4',
    status: 'Demo Authentication Enabled',
  },
  upload: {
    title: 'Document Intake',
    subtitle: 'Upload an RFP, SOW, contract, or proposal document to begin analysis.',
    badge: 'Upload',
    stage: 'Step 2 of 4',
    status: 'Supported: PDF, DOCX, TXT',
  },
  processing: {
    title: 'Analysis Pipeline',
    subtitle: 'Tracking extraction, classification, risk scoring, and summarization in real time.',
    badge: 'Processing',
    stage: 'Step 3 of 4',
    status: 'Live Job Status Tracking',
  },
  dashboard: {
    title: 'Analysis Results',
    subtitle: 'Review findings, risks, key entities, and comparable project patterns.',
    badge: 'Results',
    stage: 'Step 4 of 4',
    status: 'Ready for Export',
  },
};

function getRouteKey(pathname) {
  if (pathname.startsWith('/upload')) return 'upload';
  if (pathname.startsWith('/processing')) return 'processing';
  if (pathname.startsWith('/dashboard')) return 'dashboard';
  return 'login';
}

function AppShell() {
  const location = useLocation();
  const routeKey = getRouteKey(location.pathname);
  const routeCopy = ROUTE_COPY[routeKey];

  return (
    <div className="appShell">
      <div className="ambientGlow ambientGlowLeft" aria-hidden="true" />
      <div className="ambientGlow ambientGlowRight" aria-hidden="true" />

      <header className="appHeader">
        <div className="brandWrap">
          <div className="brandIcon" aria-hidden="true">
            <FileText size={20} />
          </div>
          <div>
            <p className="brandName">ScopeSense</p>
            <p className="brandSubhead">AI Procurement Intelligence</p>
          </div>
        </div>

        <div className="headerMeta">
          <div className="headerRoute">
            <span className="routeBadge">{routeCopy.badge}</span>
            <span className="routeStage">{routeCopy.stage}</span>
          </div>
          <span className="statusPill">
            <ShieldCheck size={14} /> {routeCopy.status}
          </span>
        </div>
      </header>

      <main className="appMain">
        <section className="pageIntro" aria-live="polite">
          <h1>{routeCopy.title}</h1>
          <p>{routeCopy.subtitle}</p>
        </section>

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/processing/:jobId" element={<Processing />} />
          <Route path="/dashboard/:jobId" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppShell />
    </Router>
  );
}

export default App;
