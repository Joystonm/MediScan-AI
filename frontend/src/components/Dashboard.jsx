// Results + risk display dashboard component
import React from 'react';

const Dashboard = ({ analysisResults, triageResults, analysisType }) => {
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
    if (!analysisResults) return null;

    return (
      <div className="analysis-section">
        <h3>🔬 Skin Lesion Analysis Results</h3>
        
        <div className="result-cards">
          <div className="result-card primary">
            <h4>Diagnosis</h4>
            <p className="diagnosis">{analysisResults.prediction}</p>
            <div className="confidence-bar">
              <div 
                className="confidence-fill"
                style={{ width: `${analysisResults.confidence * 100}%` }}
              ></div>
            </div>
            <p className="confidence-text">
              Confidence: {(analysisResults.confidence * 100).toFixed(1)}%
            </p>
          </div>

          <div className="result-card risk">
            <h4>Risk Level</h4>
            <div 
              className="risk-indicator"
              style={{ backgroundColor: getRiskColor(analysisResults.risk_level) }}
            >
              {analysisResults.risk_level?.toUpperCase()}
            </div>
          </div>
        </div>

        <div className="lesion-characteristics">
          <h4>Lesion Characteristics</h4>
          <div className="characteristics-grid">
            {Object.entries(analysisResults.lesion_characteristics || {}).map(([key, value]) => (
              <div key={key} className="characteristic-item">
                <span className="characteristic-label">
                  {key.replace('_', ' ').toUpperCase()}:
                </span>
                <span className="characteristic-value">{value}</span>
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
        <h3>No Results Available</h3>
        <p>Upload an image or complete a triage assessment to see results here.</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {renderEmergencyAlert()}
      
      <div className="dashboard-header">
        <h2>📊 Analysis Dashboard</h2>
        <p className="analysis-timestamp">
          Analysis completed: {new Date().toLocaleString()}
        </p>
      </div>

      <div className="dashboard-content">
        {analysisType === 'skin' && renderSkinAnalysisResults()}
        {analysisType === 'radiology' && renderRadiologyResults()}
        {renderTriageResults()}
      </div>

      <div className="dashboard-footer">
        <div className="disclaimer">
          <h4>⚠️ Important Disclaimer</h4>
          <p>
            This analysis is for informational purposes only and should not replace 
            professional medical advice, diagnosis, or treatment. Always consult with 
            a qualified healthcare provider for medical concerns.
          </p>
        </div>

        <div className="actions">
          <button className="btn btn-primary">Save Results</button>
          <button className="btn btn-secondary">Share with Doctor</button>
          <button className="btn btn-outline">Print Report</button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
