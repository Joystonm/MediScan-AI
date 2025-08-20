// Results + risk display dashboard component
import React, { useState } from 'react';
import SkinAnalysisResults from './SkinAnalysisResults';

const Dashboard = ({ analysisResults, triageResults, analysisType, uploadedImage }) => {
  const [activeSection, setActiveSection] = useState('analysis');

  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return '#28a745';
      case 'moderate': return '#ffc107';
      case 'high': return '#dc3545';
      case 'emergency': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getUrgencyColor = (urgencyLevel) => {
    switch (urgencyLevel?.toLowerCase()) {
      case 'routine': return '#28a745';
      case 'urgent': return '#ffc107';
      case 'emergency': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const renderSkinAnalysisResults = () => {
    return (
      <SkinAnalysisResults 
        analysisResult={analysisResults} 
        uploadedImage={uploadedImage}
      />
    );
  };

  const renderRadiologyResults = () => {
    if (!analysisResults) return null;

    return (
      <div className="analysis-section">
        <h3>🩻 Radiology Analysis Results</h3>
        
        <div className="result-cards">
          <div className="result-card primary">
            <h4>Findings</h4>
            <ul className="findings-list">
              {analysisResults.findings?.map((finding, index) => (
                <li key={index}>{finding}</li>
              ))}
            </ul>
          </div>

          <div className="result-card urgency">
            <h4>Urgency Level</h4>
            <div 
              className="urgency-indicator"
              style={{ backgroundColor: getUrgencyColor(analysisResults.urgency_level) }}
            >
              {analysisResults.urgency_level?.toUpperCase()}
            </div>
          </div>
        </div>

        <div className="confidence-scores">
          <h4>Pathology Confidence Scores</h4>
          <div className="scores-grid">
            {Object.entries(analysisResults.confidence_scores || {})
              .filter(([_, score]) => score > 0.1)
              .sort(([_, a], [__, b]) => b - a)
              .slice(0, 6)
              .map(([pathology, score]) => (
                <div key={pathology} className="score-item">
                  <span className="pathology-name">{pathology}</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill"
                      style={{ width: `${score * 100}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{(score * 100).toFixed(1)}%</span>
                </div>
              ))}
          </div>
        </div>

        <div className="recommendations">
          <h4>📋 Recommendations</h4>
          <ul>
            {analysisResults.recommendations?.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  const renderTriageResults = () => {
    if (!triageResults) return null;

    return (
      <div className="triage-section">
        <h3>🩺 Triage Assessment</h3>
        
        <div className="result-cards">
          <div className="result-card urgency">
            <h4>Urgency Level</h4>
            <div 
              className="urgency-indicator"
              style={{ backgroundColor: getUrgencyColor(triageResults.urgency_level) }}
            >
              {triageResults.urgency_level?.toUpperCase()}
            </div>
          </div>
        </div>

        <div className="triage-details">
          <div className="detail-section">
            <h4>🔍 Possible Conditions</h4>
            <ul>
              {triageResults.possible_conditions?.map((condition, index) => (
                <li key={index}>{condition}</li>
              ))}
            </ul>
          </div>

          <div className="detail-section">
            <h4>💡 Recommendations</h4>
            <ul>
              {triageResults.recommendations?.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>

          <div className="detail-section">
            <h4>📝 Next Steps</h4>
            <ul>
              {triageResults.next_steps?.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  };

  const renderEmergencyAlert = () => {
    const isEmergency = 
      analysisResults?.urgency_level === 'emergency' ||
      triageResults?.urgency_level === 'emergency' ||
      analysisResults?.risk_level === 'high';

    if (!isEmergency) return null;

    return (
      <div className="emergency-alert">
        <div className="alert-content">
          <h3>⚠️ URGENT MEDICAL ATTENTION REQUIRED</h3>
          <p>
            Based on the analysis, immediate medical evaluation is recommended. 
            Please contact your healthcare provider or visit the nearest emergency room.
          </p>
          <div className="emergency-actions">
            <button className="btn btn-emergency">Call 911</button>
            <button className="btn btn-urgent">Find Nearest Hospital</button>
          </div>
        </div>
      </div>
    );
  };

  if (!analysisResults && !triageResults) {
    return (
      <div className="dashboard-empty">
        <div className="empty-content">
          <div className="empty-icon">📊</div>
          <h3>Welcome to MediScan-AI Dashboard</h3>
          <p>Upload an image or complete a triage assessment to see AI-powered medical analysis results.</p>
          <div className="empty-actions">
            <button className="btn btn-primary" onClick={() => setActiveSection('upload')}>
              Start Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {renderEmergencyAlert()}
      
      {/* Enhanced Analysis Results */}
      <div className="dashboard-content">
        {analysisType === 'skin' && renderSkinAnalysisResults()}
        {analysisType === 'radiology' && renderRadiologyResults()}
        {renderTriageResults()}
      </div>

      {/* Action Footer */}
      <div className="dashboard-footer">
        <div className="disclaimer">
          <div className="disclaimer-content">
            <h4>⚠️ Important Medical Disclaimer</h4>
            <p>
              This AI analysis is for informational and educational purposes only. It should not replace 
              professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare 
              providers for medical concerns. In case of emergency, call emergency services immediately.
            </p>
          </div>
        </div>

        <div className="actions">
          <button className="btn btn-primary">
            <span>💾</span> Save Results
          </button>
          <button className="btn btn-secondary">
            <span>👨‍⚕️</span> Share with Doctor
          </button>
          <button className="btn btn-outline">
            <span>🖨️</span> Generate Report
          </button>
          <button className="btn btn-outline">
            <span>🔄</span> New Analysis
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
