import React, { useState } from 'react';

const Dashboard = () => {
  const [activeModule, setActiveModule] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
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
    // Don't clear analysisResult here - let it show previous results until new ones arrive

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
      description: 'Upload a skin lesion image for AI-powered analysis and risk assessment.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      color: 'primary',
      bgColor: 'bg-primary-100',
      textColor: 'text-primary-600',
      buttonColor: 'btn-primary',
      acceptedFiles: '.jpg,.jpeg,.png,.bmp,.tiff'
    },
    {
      id: 'radiology',
      title: 'Radiology Analysis',
      description: 'Analyze chest X-rays and CT scans for pathological findings and anomalies.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      ),
      color: 'secondary',
      bgColor: 'bg-secondary-100',
      textColor: 'text-secondary-600',
      buttonColor: 'btn-secondary',
      acceptedFiles: '.jpg,.jpeg,.png,.dcm,.dicom'
    },
    {
      id: 'triage',
      title: 'Virtual Triage Assistant',
      description: 'Describe symptoms for intelligent triage assessment and guidance.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      color: 'info',
      bgColor: 'bg-info-100',
      textColor: 'text-info-600',
      buttonColor: 'btn-outline'
    }
  ];

  const renderAnalysisResults = () => {
    if (!analysisResult) return null;

    if (activeModule === 'skin') {
      return (
        <div className="result-card">
          <div className="result-header">
            <h3 className="text-lg font-semibold">Skin Analysis Results</h3>
            <div className="flex items-center gap-2">
              <span className={`badge ${
                analysisResult.risk_level === 'low' ? 'badge-success' : 
                analysisResult.risk_level === 'medium' ? 'badge-warning' : 'badge-error'
              }`}>
                {analysisResult.risk_level?.toUpperCase()} Risk
              </span>
              {analysisResult.processing_time_seconds && (
                <span className="text-xs text-neutral-500">
                  {analysisResult.processing_time_seconds.toFixed(2)}s
                </span>
              )}
            </div>
          </div>
          
          <div className="space-y-6">
            {/* Image Info */}
            {analysisResult.filename && (
              <div className="bg-neutral-50 p-3 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">Analyzed Image:</span>
                  <span className="text-neutral-600">{analysisResult.filename}</span>
                </div>
                {analysisResult.image_dimensions && (
                  <div className="flex items-center justify-between text-sm mt-1">
                    <span className="font-medium">Dimensions:</span>
                    <span className="text-neutral-600">{analysisResult.image_dimensions}</span>
                  </div>
                )}
              </div>
            )}

            {/* AI-Generated Explanation */}
            {analysisResult.ai_explanation && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                    AI
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-blue-800 mb-2">AI Explanation</h4>
                    <p className="text-sm text-blue-700 leading-relaxed mb-3">
                      {analysisResult.ai_explanation.summary}
                    </p>
                    {analysisResult.ai_explanation.confidence_interpretation && (
                      <p className="text-xs text-blue-600">
                        <strong>Confidence:</strong> {analysisResult.ai_explanation.confidence_interpretation}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div>
              <h4 className="font-medium mb-2">Top Prediction</h4>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">{analysisResult.top_prediction}</span>
                <span className="text-sm text-neutral-600">{Math.round(analysisResult.confidence * 100)}%</span>
              </div>
              <div className="confidence-bar">
                <div 
                  className={`confidence-fill ${
                    analysisResult.confidence > 0.7 ? 'confidence-high' : 
                    analysisResult.confidence > 0.4 ? 'confidence-medium' : 'confidence-low'
                  }`} 
                  style={{ width: `${analysisResult.confidence * 100}%` }} 
                />
              </div>
            </div>

            {analysisResult.predictions && (
              <div>
                <h4 className="font-medium mb-2">All Predictions</h4>
                <div className="space-y-2">
                  {Object.entries(analysisResult.predictions)
                    .sort(([,a], [,b]) => b - a) // Sort by confidence descending
                    .map(([condition, confidence]) => (
                    <div key={condition} className="flex justify-between items-center">
                      <span className="text-sm">{condition}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-neutral-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary-500 rounded-full transition-all duration-300"
                            style={{ width: `${confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-neutral-600 w-12 text-right">
                          {Math.round(confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Medical Keywords */}
            {analysisResult.medical_keywords && analysisResult.medical_keywords.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Key Medical Terms</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.medical_keywords.map((keyword, index) => (
                    <span 
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {analysisResult.recommendations && (
              <div>
                <h4 className="font-medium mb-2">Recommendations</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-secondary-500 mt-1">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Medical References */}
            {analysisResult.medical_references && analysisResult.medical_references.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Trusted Medical Resources</h4>
                <div className="space-y-3">
                  {analysisResult.medical_references.map((ref, index) => (
                    <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-green-800 text-sm mb-1">{ref.title}</h5>
                          <p className="text-xs text-green-700 mb-2">{ref.snippet}</p>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                              {ref.source}
                            </span>
                            <a 
                              href={ref.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-xs text-green-600 hover:text-green-800 underline"
                            >
                              Read more →
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysisResult.next_steps && (
              <div>
                <h4 className="font-medium mb-2">Next Steps</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.next_steps.map((step, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-info-500 mt-1">→</span>
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Analysis Metadata */}
            {analysisResult.analysis_id && (
              <div className="text-xs text-neutral-400 pt-2 border-t border-neutral-200">
                Analysis ID: {analysisResult.analysis_id}
                {analysisResult.timestamp && (
                  <span className="ml-4">
                    {new Date(analysisResult.timestamp).toLocaleString()}
                  </span>
                )}
              </div>
            )}
          </div>
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
          
          <div className="space-y-6">
            {/* Scan Info */}
            {analysisResult.filename && (
              <div className="bg-neutral-50 p-3 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">Analyzed Scan:</span>
                  <span className="text-neutral-600">{analysisResult.filename}</span>
                </div>
                {analysisResult.scan_type && (
                  <div className="flex items-center justify-between text-sm mt-1">
                    <span className="font-medium">Scan Type:</span>
                    <span className="text-neutral-600">{analysisResult.scan_type.replace('_', ' ').toUpperCase()}</span>
                  </div>
                )}
                {analysisResult.image_dimensions && (
                  <div className="flex items-center justify-between text-sm mt-1">
                    <span className="font-medium">Dimensions:</span>
                    <span className="text-neutral-600">{analysisResult.image_dimensions}</span>
                  </div>
                )}
              </div>
            )}

            {/* AI-Generated Explanation */}
            {analysisResult.ai_explanation && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                    AI
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-blue-800 mb-2">AI Explanation</h4>
                    <p className="text-sm text-blue-700 leading-relaxed mb-3">
                      {analysisResult.ai_explanation.summary}
                    </p>
                    {analysisResult.ai_explanation.urgency_interpretation && (
                      <p className="text-xs text-blue-600 mb-2">
                        <strong>Urgency:</strong> {analysisResult.ai_explanation.urgency_interpretation}
                      </p>
                    )}
                    {analysisResult.ai_explanation.scan_type_info && (
                      <p className="text-xs text-blue-600">
                        <strong>About this scan:</strong> {analysisResult.ai_explanation.scan_type_info}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            {analysisResult.findings && analysisResult.findings.length > 0 ? (
              <div>
                <h4 className="font-medium mb-2">Findings</h4>
                <div className="space-y-2">
                  {analysisResult.findings.map((finding, index) => (
                    <div key={index} className="bg-neutral-50 p-3 rounded-lg">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium">{finding.condition}</span>
                        <span className="text-sm text-neutral-600">{Math.round(finding.confidence * 100)}%</span>
                      </div>
                      {finding.description && (
                        <p className="text-sm text-neutral-600">{finding.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="text-neutral-600">No significant findings detected</p>
              </div>
            )}

            {/* Medical Keywords */}
            {analysisResult.medical_keywords && analysisResult.medical_keywords.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Key Findings</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.medical_keywords.map((keyword, index) => (
                    <span 
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {analysisResult.recommendations && (
              <div>
                <h4 className="font-medium mb-2">Recommendations</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-secondary-500 mt-1">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Medical References */}
            {analysisResult.medical_references && analysisResult.medical_references.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Medical Resources</h4>
                <div className="space-y-3">
                  {analysisResult.medical_references.map((ref, index) => (
                    <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-green-800 text-sm mb-1">{ref.title}</h5>
                          <p className="text-xs text-green-700 mb-2">{ref.snippet}</p>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                              {ref.source}
                            </span>
                            <a 
                              href={ref.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-xs text-green-600 hover:text-green-800 underline"
                            >
                              Read more →
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysisResult.next_steps && (
              <div>
                <h4 className="font-medium mb-2">Next Steps</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.next_steps.map((step, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-info-500 mt-1">→</span>
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Analysis Metadata */}
            {analysisResult.analysis_id && (
              <div className="text-xs text-neutral-400 pt-2 border-t border-neutral-200">
                Analysis ID: {analysisResult.analysis_id}
                {analysisResult.timestamp && (
                  <span className="ml-4">
                    {new Date(analysisResult.timestamp).toLocaleString()}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      );
    }

    if (activeModule === 'triage') {
      return (
        <div className="result-card">
          <div className="result-header">
            <h3 className="text-lg font-semibold">Triage Assessment</h3>
            <span className={`badge ${
              analysisResult.urgency_level === 'low' ? 'badge-success' : 
              analysisResult.urgency_level === 'medium' ? 'badge-warning' : 'badge-error'
            }`}>
              {analysisResult.urgency_level?.toUpperCase()} Priority
            </span>
          </div>
          
          <div className="space-y-4">
            {analysisResult.assessment && (
              <div>
                <h4 className="font-medium mb-2">Assessment</h4>
                <p className="text-sm text-neutral-700">{analysisResult.assessment}</p>
              </div>
            )}

            {analysisResult.recommendations && (
              <div>
                <h4 className="font-medium mb-2">Recommendations</h4>
                <ul className="text-sm text-neutral-600 space-y-1">
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-secondary-500 mt-1">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-primary-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="page-header">
          <h1 className="page-title">
            Welcome to MedAI Copilot
          </h1>
          <p className="page-subtitle">
            Your intelligent healthcare assistant powered by advanced AI technology
          </p>
        </div>

        {/* Main Modules */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {modules.map((module) => (
            <div key={module.id} className="feature-card">
              <div className={`feature-icon ${module.bgColor} ${module.textColor}`}>
                {module.icon}
              </div>
              <h3 className="feature-title">{module.title}</h3>
              <p className="feature-description">{module.description}</p>

              <button 
                className={`btn ${module.buttonColor} w-full mt-6`}
                onClick={() => {
                  setActiveModule(module.id);
                  setUploadedFile(null);
                  setAnalysisResult(null);
                  setError(null);
                }}
              >
                {module.id === 'triage' ? 'Start Chat' : 'Upload Image'}
              </button>
            </div>
          ))}
        </div>

        {/* Active Module Interface */}
        {activeModule && (
          <div className="card mb-8">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h2 className="card-title">
                  {modules.find(m => m.id === activeModule)?.title}
                </h2>
                <button 
                  onClick={() => {
                    setActiveModule(null);
                    setUploadedFile(null);
                    setAnalysisResult(null);
                    setError(null);
                  }}
                  className="btn btn-ghost btn-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {activeModule === 'triage' ? (
              /* Triage Chat Interface */
              <TriageInterface onSubmit={handleTriageSubmit} isLoading={isAnalyzing} />
            ) : (
              /* File Upload Interface */
              <div className="space-y-6">
                <div 
                  className={`border-2 border-dashed rounded-xl p-6 md:p-8 text-center bg-neutral-50 transition-all duration-300 cursor-pointer shadow-sm hover:shadow-md ${
                    dragOver 
                      ? 'border-primary-500 bg-primary-100 transform scale-[1.02] shadow-lg' 
                      : 'border-neutral-300 hover:border-primary-400 hover:bg-primary-50'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById('file-input').click()}
                >
                  <div className="flex flex-col items-center justify-center">
                    <div className={`mb-4 transition-colors duration-300 ${
                      dragOver ? 'text-primary-600' : 'text-neutral-400 hover:text-primary-500'
                    }`}>
                      <svg 
                        className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 mx-auto" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <h3 className="text-base sm:text-lg font-semibold text-neutral-700 mb-2 max-w-xs">
                      {uploadedFile ? uploadedFile.name : 'Drop your medical image here'}
                    </h3>
                    <p className="text-sm text-neutral-500 mb-3">
                      or click to browse files
                    </p>
                    <div className="text-xs sm:text-sm text-neutral-400 px-2">
                      Supported formats: {modules.find(m => m.id === activeModule)?.acceptedFiles}
                    </div>
                  </div>
                  <input 
                    id="file-input"
                    type="file" 
                    className="hidden"
                    accept={modules.find(m => m.id === activeModule)?.acceptedFiles}
                    onChange={handleFileUpload}
                  />
                </div>

                {uploadedFile && (
                  <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-secondary-100 text-secondary-600 rounded-lg flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-neutral-800">{uploadedFile.name}</p>
                        <p className="text-sm text-neutral-500">
                          {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button 
                        className="btn btn-primary"
                        onClick={handleAnalyze}
                        disabled={isAnalyzing}
                      >
                        {isAnalyzing ? (
                          <>
                            <div className="loading-spinner w-4 h-4" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            Analyze
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {error && (
                  <div className="bg-error-50 border border-error-200 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-error-100 text-error-600 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <p className="text-error-700">{error}</p>
                    </div>
                  </div>
                )}

                {/* Analysis Results */}
                {renderAnalysisResults()}
                
                {/* Analyze Another Image Button */}
                {analysisResult && (
                  <div className="mt-6 text-center">
                    <button 
                      className="btn btn-outline"
                      onClick={() => {
                        setUploadedFile(null);
                        setAnalysisResult(null);
                        setError(null);
                        // Keep activeModule to stay in the same analysis type
                      }}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                      </svg>
                      Analyze Another Image
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Triage Interface Component
const TriageInterface = ({ onSubmit, isLoading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSubmit(message);
      setMessage('');
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-neutral-50 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-info-100 text-info-600 rounded-full flex items-center justify-center text-sm font-semibold">
            AI
          </div>
          <div className="flex-1">
            <p className="text-sm text-neutral-700">
              Hello! I'm your virtual triage assistant. Please describe your symptoms, 
              and I'll help assess the urgency and provide guidance.
            </p>
          </div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input 
          type="text" 
          placeholder="Describe your symptoms..."
          className="input flex-1"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={isLoading || !message.trim()}
        >
          {isLoading ? (
            <>
              <div className="loading-spinner w-4 h-4" />
              Analyzing...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Send
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Dashboard;
