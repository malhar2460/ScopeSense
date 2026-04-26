import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LockKeyhole, Sparkles } from 'lucide-react';
import styles from './Login.module.css';

const CAPABILITIES = [
  'Cross-document requirement extraction',
  'Risk scoring for delivery and scope ambiguity',
  'Stakeholder-ready business and technical summaries',
];

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = (event) => {
    event.preventDefault();
    navigate('/upload');
  };

  return (
    <section className={styles.loginLayout}>
      <aside className={`card ${styles.infoPanel}`}>
        <div className={styles.infoHeader}>
          <Sparkles size={18} />
          <span>What You Get</span>
        </div>
        <h2>Senior-level analysis in minutes</h2>
        <p className={styles.infoText}>
          ScopeSense transforms lengthy procurement documents into actionable decisions for delivery, engineering,
          and leadership teams.
        </p>
        <ul className={styles.capabilityList}>
          {CAPABILITIES.map((capability) => (
            <li key={capability}>{capability}</li>
          ))}
        </ul>
      </aside>

      <div className={`card ${styles.loginCard}`}>
        <div className={styles.loginHeader}>
          <div className={styles.loginIcon}>
            <LockKeyhole size={18} />
          </div>
          <div>
            <h2>Sign In</h2>
            <p className={styles.subtitle}>Demo access is enabled for this environment.</p>
          </div>
        </div>

        <form onSubmit={handleLogin} className={styles.form}>
          <div className={styles.inputGroup}>
            <label htmlFor="email">Corporate Email</label>
            <input
              id="email"
              className="input"
              type="email"
              placeholder="user@company.com"
              required
              defaultValue="demo@company.com"
              autoComplete="email"
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              className="input"
              type="password"
              placeholder="password"
              required
              defaultValue="password"
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="btn-primary">
            Enter Workspace
          </button>
        </form>
      </div>
    </section>
  );
}
