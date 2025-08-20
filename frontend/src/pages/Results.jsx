// Results page component
import React, { useState, useEffect } from 'react';
import Dashboard from '../components/Dashboard';

const Results = () => {
  const [savedResults, setSavedResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load saved results from localStorage or API
    loadSavedResults();
  }, []);

  const loadSavedResults = () => {
    try {
      // For now, load from localStorage
      // In production, this would be an API call
      const saved = localStorage.getItem('mediscan_results');
      if (saved) {
        setSavedResults(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading saved results:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveResult = (result) => {
    const newResult = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...result
    };

    const updated = [newResult, ...savedResults];
    setSavedResults(updated);
    localStorage.setItem('mediscan_results', JSON.stringify(updated));
  };

  const deleteResult = (id) => {
    const updated = savedResults.filter(result => result.id !== id);
    setSavedResults(updated);
    localStorage.setItem('mediscan_results', JSON.stringify(updated));
    
    if (selectedResult?.id === id) {
      setSelectedResult(null);
    }
  };

  const exportResults = () => {
    const dataStr = JSON.stringify(savedResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `mediscan_results_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
  };

  const getResultTypeIcon = (type) => {
    switch (type) {
      case 'skin': return '🔬';
      case 'radiology': return '🩻';
      case 'triage': return '🩺';
      default: return '📊';
    }
  };

  const getResultSummary = (result) => {
    if (result.analysisResults?.prediction) {
      return `${result.analysisResults.prediction} (${(result.analysisResults.confidence * 100).toFixed(1)}%)`;
    }
    if (result.triageResults?.urgency_level) {
      return `Urgency: ${result.triageResults.urgency_level}`;
    }
    return 'Analysis completed';
  };

  if (loading) {
    return (
      <div className="results-loading">
        <div className="loading-spinner"></div>
        <p>Loading your results...</p>
      </div>
    );
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <h1>📊 Your Analysis Results</h1>
        <p>View and manage your saved medical analysis results</p>
        
        <div className="results-actions">
          <button className="btn btn-primary" onClick={exportResults}>
            📥 Export All Results
          </button>
          <button className="btn btn-secondary" onClick={loadSavedResults}>
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="results-content">
        {savedResults.length === 0 ? (
          <div className="no-results">
            <div className="no-results-icon">📋</div>
            <h3>No Results Yet</h3>
            <p>
              You haven't completed any analyses yet. Visit the home page to 
              start with a virtual triage assessment or upload medical images 
              for analysis.
            </p>
            <button 
              className="btn btn-primary"
              onClick={() => window.location.href = '/'}
            >
              Start Analysis
            </button>
          </div>
        ) : (
          <div className="results-layout">
            <div className="results-sidebar">
              <h3>Saved Results ({savedResults.length})</h3>
              
              <div className="results-list">
                {savedResults.map((result) => (
                  <div
                    key={result.id}
                    className={`result-item ${selectedResult?.id === result.id ? 'active' : ''}`}
                    onClick={() => setSelectedResult(result)}
                  >
                    <div className="result-item-header">
                      <span className="result-icon">
                        {getResultTypeIcon(result.analysisType)}
                      </span>
                      <span className="result-date">
                        {new Date(result.timestamp).toLocaleDateString()}
                      </span>
                      <button
                        className="delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteResult(result.id);
                        }}
                      >
                        🗑️
                      </button>
                    </div>
                    
                    <div className="result-item-content">
                      <p className="result-type">
                        {result.analysisType?.toUpperCase() || 'ANALYSIS'}
                      </p>
                      <p className="result-summary">
                        {getResultSummary(result)}
                      </p>
                      <p className="result-time">
                        {new Date(result.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="results-main">
              {selectedResult ? (
                <div className="selected-result">
                  <div className="result-header">
                    <h2>
                      {getResultTypeIcon(selectedResult.analysisType)} 
                      Analysis from {new Date(selectedResult.timestamp).toLocaleString()}
                    </h2>
                    
                    <div className="result-actions">
                      <button className="btn btn-outline">
                        📄 Generate Report
                      </button>
                      <button className="btn btn-outline">
                        📧 Share with Doctor
                      </button>
                      <button className="btn btn-outline">
                        🖨️ Print
                      </button>
                    </div>
                  </div>

                  <Dashboard
                    analysisResults={selectedResult.analysisResults}
                    triageResults={selectedResult.triageResults}
                    analysisType={selectedResult.analysisType}
                  />
                </div>
              ) : (
                <div className="no-selection">
                  <div className="no-selection-icon">👈</div>
                  <h3>Select a Result</h3>
                  <p>
                    Choose a result from the sidebar to view detailed analysis 
                    and recommendations.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="results-stats">
        <h3>📈 Your Health Insights</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{savedResults.length}</div>
            <div className="stat-label">Total Analyses</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">
              {savedResults.filter(r => r.analysisType === 'skin').length}
            </div>
            <div className="stat-label">Skin Analyses</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">
              {savedResults.filter(r => r.analysisType === 'radiology').length}
            </div>
            <div className="stat-label">X-ray Analyses</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">
              {savedResults.filter(r => r.triageResults).length}
            </div>
            <div className="stat-label">Triage Assessments</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Results;
