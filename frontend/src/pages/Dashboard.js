import React, { useState } from 'react';
import SkinAnalysisResults from '../components/SkinAnalysisResults';
import './Dashboard.css';

const Dashboard = () => {
  const [activeModule, setActiveModule] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedImageData, setUploadedImageData] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [triageMessage, setTriageMessage] = useState('');

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      
      // Create image data object similar to UploadImage component
      const reader = new FileReader();
      reader.onload = () => {
        setUploadedImageData({
          file,
          preview: reader.result,
          name: file.name,
          size: file.size
        });
      };
      reader.readAsDataURL(file);
      
      setAnalysisResult(null);
      setError(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const file = event.dataTransfer.files[0];
    if (file) {
      setUploadedFile(file);
      
      // Create image data object
      const reader = new FileReader();
      reader.onload = () => {
        setUploadedImageData({
          file,
          preview: reader.result,
          name: file.name,
          size: file.size
        });
      };
      reader.readAsDataURL(file);
      
      setAnalysisResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedFile) {
      setError('Please select a file first');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    const startTime = Date.now();

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      let endpoint = '';
      if (activeModule === 'skin') {
        endpoint = '/api/v1/skin-analysis/analyze';
      } else if (activeModule === 'radiology') {
        endpoint = '/api/v1/radiology/analyze?scan_type=chest_xray';
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      const processingTime = (Date.now() - startTime) / 1000;
      
      // Add client-side processing time if not provided by server
      if (!result.processing_time_seconds) {
        result.processing_time_seconds = processingTime;
      }
      
      // Set results and keep the module active to show results
      setAnalysisResult(result);
      
      // Log successful analysis
      console.log('Analysis completed:', {
        filename: uploadedFile.name,
        processingTime: result.processing_time_seconds,
        topPrediction: result.top_prediction || result.findings?.[0]?.condition,
        confidence: result.confidence || result.findings?.[0]?.confidence
      });
      
    } catch (err) {
      setError(err.message || 'An error occurred during analysis');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTriageSubmit = async (message) => {
    if (!message.trim()) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/triage/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symptoms: message,
          language: 'en'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Triage assessment failed');
      }

      const result = await response.json();
      setAnalysisResult(result);
      setTriageMessage(''); // Clear the message after successful submission
    } catch (err) {
      setError(err.message || 'An error occurred during triage assessment');
      console.error('Triage error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const modules = [
    {
      id: 'skin',
      title: 'Skin Cancer Detection',
      description: 'Upload a skin lesion image for AI-powered analysis with enhanced insights, reference materials, and medical keywords.',
      icon: (
        <svg className="module-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      color: 'primary',
      bgColor: 'bg-primary-100',
      textColor: 'text-primary-600',
      buttonColor: 'btn-primary',
      acceptedFiles: '.jpg,.jpeg,.png,.bmp,.tiff',
      features: ['AI Summary', 'Reference Images', 'Medical Articles', 'Keyword Extraction']
    },
    {
      id: 'radiology',
      title: 'Radiology Analysis',
      description: 'Analyze chest X-rays and CT scans for pathological findings and anomalies.',
      icon: (
        <svg className="module-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      ),
      color: 'secondary',
      bgColor: 'bg-secondary-100',
      textColor: 'text-secondary-600',
      buttonColor: 'btn-secondary',
      acceptedFiles: '.jpg,.jpeg,.png,.dcm,.dicom',
      features: ['Multi-pathology Detection', 'Urgency Assessment', 'Clinical Findings']
    },
    {
      id: 'triage',
      title: 'Virtual Triage Assistant',
      description: 'Describe symptoms for intelligent triage assessment and guidance.',
      icon: (
        <svg className="module-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      color: 'info',
      bgColor: 'bg-info-100',
      textColor: 'text-info-600',
      buttonColor: 'btn-outline',
      features: ['Symptom Analysis', 'Urgency Triage', 'Medical Guidance']
    }
  ];

  const renderAnalysisResults = () => {
    if (!analysisResult) return null;

    if (activeModule === 'skin') {
      return (
        <div className="analysis-results-container">
          <SkinAnalysisResults 
            analysisResult={analysisResult} 
            uploadedImage={uploadedImageData}
            isLoading={isAnalyzing}
          />
        </div>
      );
    }

    if (activeModule === 'radiology') {
      return (
        <div className="result-card">
          <div className="result-header">
            <h3 className="text-lg font-semibold">Radiology Analysis Results</h3>
            <div className="flex items-center gap-2">
              <span className={`badge ${
                analysisResult.urgency_level === 'routine' ? 'badge-success' : 
                analysisResult.urgency_level === 'urgent' ? 'badge-warning' : 'badge-error'
              }`}>
                {analysisResult.urgency_level?.toUpperCase()}
              </span>
              {analysisResult.processing_time_seconds && (
                <span className="text-xs text-neutral-500">
                  {analysisResult.processing_time_seconds.toFixed(2)}s
                </span>
              )}
            </div>
          </div>

          <div className="result-content">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">Detected Findings</h4>
                <div className="space-y-2">
                  {analysisResult.findings?.map((finding, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-neutral-50 rounded">
                      <span className="text-sm">{finding.condition}</span>
                      <span className="text-xs font-medium">
                        {(finding.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Clinical Summary</h4>
                <p className="text-sm text-neutral-600 mb-4">
                  {analysisResult.clinical_summary}
                </p>

                <h4 className="font-medium mb-2">Recommendations</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.recommendations?.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-primary-500 mt-1">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (activeModule === 'triage') {
      return (
        <div className="result-card">
          <div className="result-header">
            <h3 className="text-lg font-semibold">Triage Assessment Results</h3>
            <span className={`badge ${
              analysisResult.urgency_level === 'routine' ? 'badge-success' : 
              analysisResult.urgency_level === 'urgent' ? 'badge-warning' : 'badge-error'
            }`}>
              {analysisResult.urgency_level?.toUpperCase()}
            </span>
          </div>

          <div className="result-content">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">Possible Conditions</h4>
                <div className="space-y-2">
                  {analysisResult.possible_conditions?.map((condition, index) => (
                    <div key={index} className="p-2 bg-neutral-50 rounded">
                      <span className="text-sm font-medium">{condition.condition}</span>
                      <span className="text-xs text-neutral-500 ml-2">
                        {(condition.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Recommendations</h4>
                <ul className="text-sm text-neutral-600 space-y-1 mb-4">
                  {analysisResult.recommendations?.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-primary-500 mt-1">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>

                <h4 className="font-medium mb-2">Next Steps</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.next_steps?.map((step, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-info-500 mt-1">{index + 1}.</span>
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  const renderUploadArea = (module) => (
    <div className="upload-section">
      <div
        className={`upload-area ${dragOver ? 'drag-over' : ''} ${uploadedFile ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {uploadedFile ? (
          <div className="uploaded-file-info">
            <div className="file-icon">📄</div>
            <div className="file-details">
              <p className="file-name">{uploadedFile.name}</p>
              <p className="file-size">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button
              onClick={() => {
                setUploadedFile(null);
                setUploadedImageData(null);
                setAnalysisResult(null);
              }}
              className="btn btn-sm btn-outline"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">📁</div>
            <p className="upload-text">
              Drag & drop your {module.title.toLowerCase()} file here, or{' '}
              <label className="upload-link">
                browse
                <input
                  type="file"
                  accept={module.acceptedFiles}
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </p>
            <p className="upload-hint">
              Supported formats: {module.acceptedFiles.replace(/\./g, '').toUpperCase()}
            </p>
          </div>
        )}
      </div>

      {uploadedFile && (
        <div className="upload-actions">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className={`btn ${module.buttonColor} ${isAnalyzing ? 'loading' : ''}`}
          >
            {isAnalyzing ? (
              <>
                <span className="loading-spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                <span>🔬</span>
                Analyze {module.title}
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );

  const renderTriageArea = () => {
    return (
      <div className="triage-section">
        <div className="triage-input">
          <label className="block text-sm font-medium mb-2">
            Describe your symptoms or medical concerns:
          </label>
          <textarea
            value={triageMessage}
            onChange={(e) => setTriageMessage(e.target.value)}
            placeholder="Please describe your symptoms, their duration, severity, and any other relevant details..."
            className="w-full p-3 border border-neutral-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={4}
          />
        </div>

        <div className="triage-actions">
          <button
            onClick={() => handleTriageSubmit(triageMessage)}
            disabled={isAnalyzing || !triageMessage.trim()}
            className={`btn btn-outline ${isAnalyzing ? 'loading' : ''}`}
          >
            {isAnalyzing ? (
              <>
                <span className="loading-spinner"></span>
                Assessing...
              </>
            ) : (
              <>
                <span>🩺</span>
                Get Triage Assessment
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">MediScan-AI Dashboard</h1>
          <p className="dashboard-subtitle">
            AI-powered medical analysis with enhanced insights and comprehensive reporting
          </p>
        </div>
      </div>

      {!activeModule ? (
        <div className="modules-grid">
          {modules.map((module) => (
            <div
              key={module.id}
              className={`module-card ${module.bgColor} ${module.textColor}`}
              onClick={() => {
                setActiveModule(module.id);
                setUploadedFile(null);
                setUploadedImageData(null);
                setAnalysisResult(null);
                setError(null);
                setTriageMessage('');
              }}
            >
              <div className="module-icon">{module.icon}</div>
              <div className="module-content">
                <h3 className="module-title">{module.title}</h3>
                <p className="module-description">{module.description}</p>
                
                {module.features && (
                  <div className="module-features">
                    <p className="features-label">Features:</p>
                    <ul className="features-list">
                      {module.features.map((feature, index) => (
                        <li key={index} className="feature-item">
                          <span className="feature-bullet">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <div className="module-action">
                <button className={`btn ${module.buttonColor}`}>
                  Get Started
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="active-module">
          <div className="module-header">
            <button
              onClick={() => {
                setActiveModule(null);
                setUploadedFile(null);
                setUploadedImageData(null);
                setAnalysisResult(null);
                setError(null);
                setTriageMessage('');
              }}
              className="btn btn-outline btn-sm"
            >
              ← Back to Modules
            </button>
            <h2 className="module-title">
              {modules.find(m => m.id === activeModule)?.title}
            </h2>
          </div>

          {error && (
            <div className="error-alert">
              <div className="error-content">
                <span className="error-icon">⚠️</span>
                <span className="error-message">{error}</span>
                <button
                  onClick={() => setError(null)}
                  className="error-close"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          <div className="module-content">
            {activeModule === 'triage' ? renderTriageArea() : renderUploadArea(modules.find(m => m.id === activeModule))}
          </div>

          {renderAnalysisResults()}
        </div>
      )}

      {/* Medical Disclaimer */}
      <div className="medical-disclaimer">
        <div className="disclaimer-content">
          <h4 className="disclaimer-title">⚠️ Important Medical Disclaimer</h4>
          <p className="disclaimer-text">
            This AI analysis tool is for informational and educational purposes only. It should not replace 
            professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare 
            providers for medical concerns. In case of emergency, call emergency services immediately.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
