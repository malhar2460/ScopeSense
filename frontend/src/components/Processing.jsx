import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { fetchJobStatus } from '../lib/api';
import styles from './Processing.module.css';

const STEP_LABELS = {
  queued: 'Queued',
  parsing: 'Parsing Document',
  classify: 'Classifying Type',
  extract: 'Extracting Entities',
  analyze_risk: 'Analyzing Risk',
  summarize: 'Summarizing',
  retrieve: 'Finding Similar Projects',
  compile: 'Compiling Output',
  done: 'Complete',
};

const DISPLAY_STEPS = ['queued', 'parsing', 'classify', 'extract', 'analyze_risk', 'summarize', 'retrieve', 'compile', 'done'];

export default function Processing() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Preparing analysis pipeline...');
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('queued');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!jobId) {
      setStatus('failed');
      setError('Missing job id. Please upload a document again.');
      return undefined;
    }

    let isMounted = true;
    let timeoutId;

    const pollStatus = async () => {
      try {
        const data = await fetchJobStatus(jobId);
        if (!isMounted) return;

        setStatus(data.status);
        setProgress(Math.min(100, Math.max(0, data.progress || 0)));
        setCurrentStep(data.current_step || 'queued');
        setMessage(data.message || 'Running analysis...');

        if (data.status === 'failed') {
          setError(data.error || 'Analysis failed.');
          return;
        }

        if (data.status === 'completed') {
          timeoutId = window.setTimeout(() => {
            navigate(`/dashboard/${jobId}`);
          }, 900);
          return;
        }

        timeoutId = window.setTimeout(pollStatus, 1500);
      } catch (err) {
        if (!isMounted) return;
        setStatus('failed');
        setError(err.message || 'Unable to connect to backend service.');
      }
    };

    pollStatus();

    return () => {
      isMounted = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [jobId, navigate]);

  const activeIndex = useMemo(() => DISPLAY_STEPS.indexOf(currentStep), [currentStep]);

  if (status === 'failed') {
    return (
      <section className={styles.processingLayout}>
        <div className={`card ${styles.errorCard}`}>
          <AlertCircle size={46} />
          <h2>Analysis Failed</h2>
          <p>{error || 'Unexpected processing failure.'}</p>
          <button className="btn-primary" onClick={() => navigate('/upload')}>
            Back to Upload
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className={styles.processingLayout}>
      <div className={`card ${styles.processingCard}`}>
        <div className={styles.statusIcon}>
          {status === 'completed' ? <CheckCircle2 size={46} /> : <Loader2 size={46} className={styles.spinner} />}
        </div>

        <h2>{status === 'completed' ? 'Analysis Complete' : 'Running Analysis'}</h2>
        <p className={styles.message}>{message}</p>

        <div className={styles.progressShell} aria-label="analysis progress">
          <div className={styles.progressBar} style={{ width: `${progress}%` }} />
        </div>
        <p className={styles.progressValue}>{progress}%</p>

        <div className={styles.stepGrid}>
          {DISPLAY_STEPS.map((step, index) => {
            const state = index <= activeIndex ? styles.stepDone : styles.stepPending;
            return (
              <div key={step} className={`${styles.stepItem} ${state}`}>
                <span className={styles.stepIndex}>{index + 1}</span>
                <span>{STEP_LABELS[step]}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
