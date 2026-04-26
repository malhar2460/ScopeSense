import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertTriangle, ChevronLeft, Download, Info, ShieldCheck } from 'lucide-react';
import { fetchJobStatus } from '../lib/api';
import styles from './Dashboard.module.css';

function riskClass(level = '') {
  const normalized = level.toLowerCase();
  if (normalized === 'high') return styles.riskHigh;
  if (normalized === 'medium') return styles.riskMedium;
  return styles.riskLow;
}

function renderList(items, emptyText) {
  if (!items || items.length === 0) {
    return <li className={styles.emptyItem}>{emptyText}</li>;
  }
  return items.map((item) => <li key={item}>{item}</li>);
}

export default function Dashboard() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!jobId) {
      setError('Missing job id. Please upload a document again.');
      setLoading(false);
      return undefined;
    }

    let isMounted = true;
    let timeoutId;

    const loadDashboard = async () => {
      try {
        const payload = await fetchJobStatus(jobId);
        if (!isMounted) return;

        if (payload.status === 'failed') {
          setError(payload.error || 'Analysis failed before dashboard generation.');
          setLoading(false);
          return;
        }

        if (payload.status === 'completed' && payload.result) {
          setData(payload.result);
          setLoading(false);
          return;
        }

        timeoutId = window.setTimeout(loadDashboard, 1200);
      } catch (err) {
        if (!isMounted) return;
        setError(err.message || 'Unable to fetch dashboard data.');
        setLoading(false);
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [jobId]);

  const metrics = useMemo(() => {
    if (!data) return { risks: 0, deliverables: 0, technologies: 0 };

    return {
      risks: data.risk_assessment?.risks?.length || 0,
      deliverables: data.extracted_entities?.deliverables?.length || 0,
      technologies: data.extracted_entities?.technologies?.length || 0,
    };
  }, [data]);

  if (loading) {
    return <div className={styles.loading}>Loading dashboard...</div>;
  }

  if (error || !data) {
    return (
      <div className={styles.loading}>
        <p>{error || 'No data available for this analysis.'}</p>
        <button className="btn-outline" onClick={() => navigate('/upload')}>
          <ChevronLeft size={14} /> Back to Upload
        </button>
      </div>
    );
  }

  const { document_classification, extracted_entities, risk_assessment, summary, similar_projects } = data;
  const exportTimestamp = new Date().toLocaleString();

  return (
    <section className={styles.dashboard}>
      <header className={styles.printReportHeader}>
        <p className={styles.printEyebrow}>ScopeSense Intelligence Report</p>
        <h1>{data.file_name}</h1>
        <p>
          Generated on {exportTimestamp} | Job ID: {jobId}
        </p>
      </header>

      <div className={`${styles.headerRow} ${styles.noPrint}`}>
        <div className={styles.headerLeft}>
          <button className="btn-outline" onClick={() => navigate('/upload')}>
            <ChevronLeft size={14} /> New Analysis
          </button>
          <div>
            <h2>{data.file_name}</h2>
            <p className={styles.metaLine}>
              {document_classification?.document_type || 'Unknown type'} | Confidence:{' '}
              {Math.round((document_classification?.confidence || 0) * 100)}%
            </p>
          </div>
        </div>

        <button className="btn-primary" onClick={() => window.print()}>
          <Download size={14} /> Export PDF
        </button>
      </div>

      <div className={styles.metricsRow}>
        <div className={`card ${styles.metricCard}`}>
          <span className={styles.metricLabel}>Flagged Risks</span>
          <strong>{metrics.risks}</strong>
        </div>
        <div className={`card ${styles.metricCard}`}>
          <span className={styles.metricLabel}>Deliverables</span>
          <strong>{metrics.deliverables}</strong>
        </div>
        <div className={`card ${styles.metricCard}`}>
          <span className={styles.metricLabel}>Technologies</span>
          <strong>{metrics.technologies}</strong>
        </div>
      </div>

      <div className={styles.layoutGrid}>
        <div className={styles.mainColumn}>
          <article className={`card ${styles.sectionCard}`}>
            <h3>Business Summary</h3>
            <p>{summary?.business_summary || 'No summary available.'}</p>
          </article>

          <article className={`card ${styles.sectionCard}`}>
            <h3>Technical Summary</h3>
            <p>{summary?.technical_summary || 'No technical summary available.'}</p>
          </article>

          <article className={`card ${styles.sectionCard}`}>
            <h3>Extracted Scope Details</h3>
            <div className={styles.twoColGrid}>
              <div className={styles.kvItem}>
                <span>Client</span>
                <strong>{extracted_entities?.client_name || 'Not found'}</strong>
              </div>
              <div className={styles.kvItem}>
                <span>Timeline</span>
                <strong>{extracted_entities?.timeline || 'Not found'}</strong>
              </div>
            </div>

            <div className={styles.listBlock}>
              <h4>Deliverables</h4>
              <ul>{renderList(extracted_entities?.deliverables, 'No deliverables extracted')}</ul>
            </div>

            <div className={styles.listBlock}>
              <h4>Stakeholders</h4>
              <ul>{renderList(extracted_entities?.stakeholders, 'No stakeholders extracted')}</ul>
            </div>

            <div className={styles.listBlock}>
              <h4>Dependencies</h4>
              <ul>{renderList(extracted_entities?.dependencies, 'No dependencies extracted')}</ul>
            </div>

            <div className={styles.tagWrap}>
              {(extracted_entities?.technologies || []).map((tech) => (
                <span key={tech} className={styles.tag}>
                  {tech}
                </span>
              ))}
              {(!extracted_entities?.technologies || extracted_entities.technologies.length === 0) && (
                <span className={styles.emptyItem}>No technologies extracted</span>
              )}
            </div>
          </article>
        </div>

        <aside className={styles.sideColumn}>
          <article className={`card ${styles.sectionCard}`}>
            <h3>Risk Assessment</h3>
            <div className={`${styles.overallRisk} ${riskClass(risk_assessment?.overall_risk_score)}`}>
              <ShieldCheck size={16} /> Overall Risk: {risk_assessment?.overall_risk_score || 'Unknown'}
            </div>

            <div className={styles.riskList}>
              {(risk_assessment?.risks || []).map((risk) => (
                <div key={`${risk.risk_level}-${risk.description}`} className={`${styles.riskItem} ${riskClass(risk.risk_level)}`}>
                  <p className={styles.riskTitle}>
                    <AlertTriangle size={14} /> {risk.risk_level} Risk
                  </p>
                  <p>{risk.description}</p>
                  {risk.section && (
                    <p className={styles.sectionRef}>
                      <Info size={12} /> {risk.section}
                    </p>
                  )}
                </div>
              ))}
              {(!risk_assessment?.risks || risk_assessment.risks.length === 0) && (
                <p className={styles.emptyItem}>No explicit risks identified.</p>
              )}
            </div>
          </article>

          <article className={`card ${styles.sectionCard}`}>
            <h3>Similar Projects</h3>
            {(similar_projects || []).map((project) => (
              <div key={project.project_name} className={styles.similarItem}>
                <p className={styles.projectName}>{project.project_name}</p>
                <p className={styles.projectScore}>Similarity: {Math.round((project.similarity_score || 0) * 100)}%</p>
                {(project.document_type || project.sector) && (
                  <p className={styles.projectMeta}>
                    {[project.document_type, project.sector].filter(Boolean).join(' | ')}
                  </p>
                )}
                <p className={styles.projectSummary}>{project.summary}</p>
              </div>
            ))}
            {(!similar_projects || similar_projects.length === 0) && (
              <p className={styles.emptyItem}>No strong historical matches were found.</p>
            )}
          </article>
        </aside>
      </div>
    </section>
  );
}
