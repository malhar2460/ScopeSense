import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, File, UploadCloud } from 'lucide-react';
import { startAnalysis } from '../lib/api';
import styles from './Upload.module.css';

const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = ['pdf', 'docx', 'txt'];

function extensionOf(fileName = '') {
  const parts = fileName.toLowerCase().split('.');
  return parts.length > 1 ? parts.pop() : '';
}

function validateFile(file) {
  if (!file) return 'Please select a file to upload.';

  const extension = extensionOf(file.name);
  if (!ACCEPTED_EXTENSIONS.includes(extension)) {
    return 'Unsupported file type. Use PDF, DOCX, or TXT.';
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return 'File exceeds the 15 MB upload limit.';
  }

  return '';
}

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState('');

  const fileSize = useMemo(() => {
    if (!file) return '';
    return `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
  }, [file]);

  const selectFile = (candidate) => {
    const validationMessage = validateFile(candidate);
    if (validationMessage) {
      setFile(null);
      setError(validationMessage);
      return;
    }

    setFile(candidate);
    setError('');
  };

  const handleInputChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      selectFile(event.target.files[0]);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragActive(false);
    const candidate = event.dataTransfer.files?.[0];
    if (candidate) {
      selectFile(candidate);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleUpload = async () => {
    const validationMessage = validateFile(file);
    if (validationMessage) {
      setError(validationMessage);
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      const data = await startAnalysis(file);
      navigate(`/processing/${data.job_id}`);
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
      setIsUploading(false);
    }
  };

  return (
    <section className={styles.uploadLayout}>
      <div className={`card ${styles.uploadCard}`}>
        <div className={styles.headerRow}>
          <h2>Analyze New Document</h2>
          <span className={styles.supportedFiles}>PDF, DOCX, TXT</span>
        </div>
        <p className={styles.subtitle}>Upload an RFP, SOW, or requirements document to generate risk and scope intelligence.</p>

        <div
          className={`${styles.dropzone} ${isDragActive ? styles.dropzoneActive : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <input
            type="file"
            id="file-upload"
            className={styles.fileInput}
            onChange={handleInputChange}
            accept=".pdf,.docx,.txt"
            disabled={isUploading}
          />

          <label htmlFor="file-upload" className={styles.dropzoneLabel}>
            {file ? (
              <div className={styles.selectedFile}>
                <File size={30} />
                <span className={styles.fileName}>{file.name}</span>
                <span className={styles.fileMeta}>{fileSize}</span>
                <span className={styles.changeHint}>Click to replace file</span>
              </div>
            ) : (
              <div className={styles.emptyState}>
                <UploadCloud size={44} />
                <span className={styles.title}>Drop your file here</span>
                <span className={styles.hint}>or click to browse from your device</span>
                <span className={styles.detail}>Maximum file size: 15 MB</span>
              </div>
            )}
          </label>
        </div>

        {error && (
          <div className={styles.errorAlert} role="alert">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className={styles.actions}>
          <button className="btn-primary" onClick={handleUpload} disabled={!file || isUploading}>
            {isUploading ? 'Uploading and starting analysis...' : 'Start Analysis'}
          </button>
        </div>
      </div>
    </section>
  );
}
