import React, { useState, useEffect } from 'react';
import './SkinAnalysisResults.css'; // Reuse the same styles
import { generateRadiologyInsights, generateRadiologyResources, generateRadiologyKeywords } from '../utils/radiologyInsights';

const RadiologyAnalysisResults = ({ analysisResult, uploadedImage, isLoading }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [enhancedData, setEnhancedData] = useState({
    aiSummary: null,
    medicalResources: null,
    keywords: null
  });

  // Effect to generate immediate insights based on findings
  useEffect(() => {
    if (analysisResult && (analysisResult.findings || analysisResult.confidence_scores)) {
      console.log('Generating radiology insights for:', analysisResult);
      
      // Generate immediate insights based on the findings
      const immediateInsights = generateRadiologyInsights(
        analysisResult.findings || [],
        analysisResult.confidence_scores || {},
        analysisResult.urgency_level || 'ROUTINE'
      );
      
      const topFinding = getTopFinding(analysisResult.findings, analysisResult.confidence_scores);
      const immediateResources = generateRadiologyResources(topFinding);
      
      const immediateKeywords = generateRadiologyKeywords(
        topFinding,
        analysisResult.findings || [],
        analysisResult.recommendations || []
      );
      
      // Set the enhanced data immediately
      setEnhancedData({
        aiSummary: immediateInsights,
        medicalResources: immediateResources,
        keywords: immediateKeywords
      });
      
      console.log('Radiology insights generated:', immediateInsights);
    }
  }, [analysisResult]);

  // Helper function to get top finding
  const getTopFinding = (findings, confidenceScores) => {
    if (findings && findings.length > 0) {
      return findings[0];
    }
    
    if (confidenceScores && Object.keys(confidenceScores).length > 0) {
      const sortedFindings = Object.entries(confidenceScores)
        .filter(([_, score]) => score > 0.1)
        .sort(([_, a], [__, b]) => b - a);
      
      if (sortedFindings.length > 0) {
        return sortedFindings[0][0];
      }
    }
    
    return "No acute findings";
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="analysis-loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h3>Analyzing your chest X-ray...</h3>
          <p>Our AI is processing your chest X-ray and generating comprehensive insights.</p>
          
          <div className="progress-steps">
            <div className="progress-step">
              <span className="step-icon">🩻</span>
              <span className="step-text">X-ray Analysis</span>
            </div>
            <div className="progress-step">
              <span className="step-icon">🧠</span>
              <span className="step-text">Generating Insights</span>
            </div>
            <div className="progress-step">
              <span className="step-icon">📚</span>
              <span className="step-text">Fetching Resources</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show placeholder when no analysis result
  if (!analysisResult) {
    return (
      <div className="analysis-placeholder">
        <div className="placeholder-content">
          <div className="placeholder-icon">🩻</div>
          <h3>Upload a chest X-ray to get started</h3>
          <p>Our AI will analyze chest X-rays and provide detailed medical insights</p>
        </div>
      </div>
    );
  }

  // Helper functions
  const formatConfidence = (confidence) => {
    return `${Math.round(confidence * 100)}%`;
  };

  const getUrgencyColor = (urgencyLevel) => {
    const colors = {
      'ROUTINE': '#10B981',
      'FOLLOW-UP': '#F59E0B',
      'URGENT': '#EF4444',
      'EMERGENCY': '#DC2626'
    };
    return colors[urgencyLevel?.toUpperCase()] || '#6B7280';
  };

  const getUrgencyIcon = (urgencyLevel) => {
    const icons = {
      'ROUTINE': '🟢',
      'FOLLOW-UP': '🟡',
      'URGENT': '🔴',
      'EMERGENCY': '🚨'
    };
    return icons[urgencyLevel?.toUpperCase()] || '⚪';
  };

  const formatAnalysisTime = () => {
    return new Date().toLocaleString();
  };

  const topFinding = getTopFinding(analysisResult.findings, analysisResult.confidence_scores);
  const topConfidence = analysisResult.confidence_scores ? 
    Math.max(...Object.values(analysisResult.confidence_scores)) : 0.75;

  return (
    <div className="skin-analysis-results"> {/* Reuse skin analysis styles */}
      {/* Results Header */}
      <div className="results-header">
        <div className="result-summary">
          <h2>Radiology Analysis Results</h2>
          <div className="top-prediction">
            <span className="prediction-label">Primary Finding:</span>
            <span className="prediction-value">{topFinding}</span>
            <span className="confidence-badge">{formatConfidence(topConfidence)}</span>
          </div>
          <div className="risk-assessment">
            <span className="risk-icon">{getUrgencyIcon(analysisResult.urgency_level)}</span>
            <span className="risk-text">{(analysisResult.urgency_level || 'ROUTINE').toUpperCase()}</span>
          </div>
        </div>
        
        <div className="analysis-metadata">
          <div className="metadata-item">
            <span className="metadata-label">Analysis Time:</span>
            <span className="metadata-value">{formatAnalysisTime()}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Analyzed Image:</span>
            <span className="metadata-value">{uploadedImage?.name || 'Chest X-ray'}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Study Type:</span>
            <span className="metadata-value">Chest X-ray (PA/AP)</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'ai-insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai-insights')}
        >
          AI Insights
        </button>
        <button 
          className={`tab-button ${activeTab === 'resources' ? 'active' : ''}`}
          onClick={() => setActiveTab('resources')}
        >
          Learn More
        </button>
        <button 
          className={`tab-button ${activeTab === 'keywords' ? 'active' : ''}`}
          onClick={() => setActiveTab('keywords')}
        >
          Key Terms
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <RadiologyOverviewTab 
            analysisResult={analysisResult}
            uploadedImage={uploadedImage}
          />
        )}
        
        {activeTab === 'ai-insights' && (
          <RadiologyAIInsightsTab 
            aiSummary={enhancedData.aiSummary}
            isLoading={false}
          />
        )}
        
        {activeTab === 'resources' && (
          <RadiologyResourcesTab 
            medicalResources={enhancedData.medicalResources}
            condition={topFinding}
            isLoading={false}
          />
        )}
        
        {activeTab === 'keywords' && (
          <RadiologyKeywordsTab 
            keywords={enhancedData.keywords}
            condition={topFinding}
            isLoading={false}
          />
        )}
      </div>
    </div>
  );
};

// Radiology Overview Tab Component
const RadiologyOverviewTab = ({ analysisResult, uploadedImage }) => {
  if (!analysisResult) {
    return (
      <div className="overview-tab">
        <div className="loading-container">
          <p>Loading analysis results...</p>
        </div>
      </div>
    );
  }

  const formatConfidence = (confidence) => {
    return `${Math.round(confidence * 100)}%`;
  };

  const getUrgencyColor = (urgencyLevel) => {
    const colors = {
      'ROUTINE': '#10B981',
      'FOLLOW-UP': '#F59E0B',
      'URGENT': '#EF4444',
      'EMERGENCY': '#DC2626'
    };
    return colors[urgencyLevel?.toUpperCase()] || '#6B7280';
  };

  return (
    <div className="overview-tab">
      <div className="overview-grid">
        {/* Image and Findings */}
        <div className="overview-section">
          <h3>Imaging Results</h3>
          
          {uploadedImage && (
            <div className="analyzed-image">
              <img src={uploadedImage.preview} alt="Analyzed chest X-ray" />
            </div>
          )}
          
          <div className="prediction-results">
            <div className="top-prediction">
              <h4>Primary Finding</h4>
              <div className="prediction-item primary">
                <span className="condition-name">
                  {analysisResult.findings?.[0] || "No acute findings"}
                </span>
                <span className="confidence">
                  {analysisResult.confidence_scores ? 
                    formatConfidence(Math.max(...Object.values(analysisResult.confidence_scores))) : 
                    "75%"
                  }
                </span>
              </div>
            </div>
            
            <div className="all-predictions">
              <h4>All Findings</h4>
              <div className="predictions-list">
                {analysisResult.confidence_scores ? 
                  Object.entries(analysisResult.confidence_scores)
                    .filter(([_, score]) => score > 0.1)
                    .sort(([_, a], [__, b]) => b - a)
                    .slice(0, 6)
                    .map(([finding, confidence]) => (
                      <div key={finding} className="prediction-item">
                        <span className="condition-name">{finding}</span>
                        <div className="probability-bar">
                          <div 
                            className="probability-fill"
                            style={{ width: `${(confidence || 0) * 100}%` }}
                          ></div>
                          <span className="probability-text">{formatConfidence(confidence || 0)}</span>
                        </div>
                      </div>
                    )) :
                  (analysisResult.findings || ["No acute findings"]).map((finding, index) => (
                    <div key={index} className="prediction-item">
                      <span className="condition-name">{finding}</span>
                      <div className="probability-bar">
                        <div 
                          className="probability-fill"
                          style={{ width: "75%" }}
                        ></div>
                        <span className="probability-text">75%</span>
                      </div>
                    </div>
                  ))
                }
              </div>
            </div>
          </div>
        </div>

        {/* Clinical Summary and Recommendations */}
        <div className="overview-section">
          <h3>Clinical Assessment</h3>
          
          <div className="clinical-summary">
            <h4>Clinical Summary</h4>
            <p>{analysisResult.clinical_summary || `Analysis of chest X-ray shows ${analysisResult.findings?.[0] || "no acute findings"}.`}</p>
          </div>
          
          <div className="recommendations-section">
            <h4>Medical Recommendations</h4>
            <ul className="recommendations-list">
              {(analysisResult.recommendations || [
                "Clinical correlation recommended",
                "Follow-up as clinically indicated"
              ]).map((rec, index) => (
                <li key={index} className="recommendation-item">
                  <span className="rec-icon">💡</span>
                  <span className="rec-text">{rec}</span>
                </li>
              ))}
            </ul>
            
            <div className="urgency-assessment">
              <h4>Urgency Level</h4>
              <div 
                className="urgency-badge"
                style={{ 
                  backgroundColor: getUrgencyColor(analysisResult.urgency_level),
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  display: 'inline-block',
                  fontWeight: 'bold'
                }}
              >
                {(analysisResult.urgency_level || 'ROUTINE').toUpperCase()}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="analysis-id">
        <small>Analysis ID: {analysisResult.analysis_id || 'Unknown'}</small>
      </div>
    </div>
  );
};

// AI Insights Tab Component for Radiology
const RadiologyAIInsightsTab = ({ aiSummary, isLoading }) => {
  const hasSummary = aiSummary && (aiSummary.summary || aiSummary.explanation);
  
  if (!hasSummary) {
    return (
      <div className="ai-insights-tab">
        <div className="insight-section">
          <h3>
            <span className="section-icon">🧠</span>
            AI Radiology Summary
          </h3>
          <div className="insight-content">
            <div className="summary-text">
              Radiology insights are being processed. Please check back in a moment or refresh the page.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-insights-tab">
      {aiSummary.summary && (
        <div className="insight-section">
          <h3>
            <span className="section-icon">🩻</span>
            AI Radiology Summary
          </h3>
          <div className="insight-content">
            <div className="summary-text">
              {aiSummary.summary}
            </div>
            {aiSummary.generated_at && (
              <div className="generation-info">
                <small>Generated: {new Date(aiSummary.generated_at).toLocaleString()}</small>
              </div>
            )}
          </div>
        </div>
      )}
      
      {aiSummary.explanation && (
        <div className="insight-section">
          <h3>
            <span className="section-icon">📚</span>
            Clinical Explanation
          </h3>
          <div className="insight-content">
            <div className="explanation-text">
              {aiSummary.explanation}
            </div>
          </div>
        </div>
      )}
      
      {aiSummary.clinical_significance && (
        <div className="insight-section">
          <h3>
            <span className="section-icon">🏥</span>
            Clinical Significance
          </h3>
          <div className="insight-content">
            <div className="explanation-text">
              {aiSummary.clinical_significance}
            </div>
          </div>
        </div>
      )}
      
      {/* Show confidence and urgency interpretations if available */}
      {(aiSummary.confidence_interpretation || aiSummary.urgency_interpretation) && (
        <div className="insight-section">
          <h3>
            <span className="section-icon">📊</span>
            Analysis Interpretation
          </h3>
          <div className="insight-content">
            {aiSummary.confidence_interpretation && (
              <div className="interpretation-item">
                <h4>Confidence Level</h4>
                <p>{aiSummary.confidence_interpretation}</p>
              </div>
            )}
            {aiSummary.urgency_interpretation && (
              <div className="interpretation-item">
                <h4>Urgency Assessment</h4>
                <p>{aiSummary.urgency_interpretation}</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      <div className="disclaimer-section">
        <div className="disclaimer">
          <span className="disclaimer-icon">⚠️</span>
          <div className="disclaimer-text">
            <strong>Medical Disclaimer:</strong> This AI-generated radiology interpretation is for informational purposes only 
            and should not replace professional radiological interpretation or medical advice. Always consult with 
            qualified healthcare professionals and radiologists for definitive diagnosis.
          </div>
        </div>
      </div>
    </div>
  );
};

// Resources Tab Component for Radiology
const RadiologyResourcesTab = ({ medicalResources, condition, isLoading }) => {
  const hasResources = medicalResources && (
    (medicalResources.reference_images && medicalResources.reference_images.length > 0) ||
    (medicalResources.medical_articles && medicalResources.medical_articles.length > 0)
  );

  if (!hasResources) {
    return (
      <div className="resources-tab">
        <div className="resource-section">
          <h3>
            <span className="section-icon">📚</span>
            Medical Resources for {condition}
          </h3>
          <div className="resource-content">
            <p>Here are trusted medical resources about {condition}:</p>
            
            <div className="general-resources">
              <h4>Trusted Medical Sources:</h4>
              <div className="resource-links">
                <a href="https://www.radiologyinfo.org/en/info/chestrad" target="_blank" rel="noopener noreferrer">
                  RadiologyInfo.org - Chest X-ray Information
                </a>
                <a href="https://www.acr.org/Clinical-Resources" target="_blank" rel="noopener noreferrer">
                  American College of Radiology - Clinical Resources
                </a>
                <a href="https://www.lung.org/lung-health-diseases" target="_blank" rel="noopener noreferrer">
                  American Lung Association - Lung Health
                </a>
                <a href="https://www.heart.org/" target="_blank" rel="noopener noreferrer">
                  American Heart Association - Heart Health
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="resources-tab">
      {medicalResources.medical_articles && medicalResources.medical_articles.length > 0 && (
        <div className="resource-section">
          <h3>
            <span className="section-icon">📄</span>
            Medical Articles
          </h3>
          <div className="articles-list">
            {medicalResources.medical_articles.map((article, index) => (
              <div key={index} className="article-item">
                <div className="article-header">
                  <h4>
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      {article.title || `Medical Article ${index + 1}`}
                    </a>
                  </h4>
                  <div className="article-meta">
                    <span className="article-source">
                      Source: {article.source || 'Medical Database'}
                    </span>
                    {article.relevance_score && (
                      <span className="relevance-score">
                        Relevance: {(article.relevance_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
                <div className="article-snippet">
                  {article.snippet || `Medical information about ${condition}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {medicalResources.fetched_at && (
        <div className="fetch-info">
          <small>Resources updated: {new Date(medicalResources.fetched_at).toLocaleString()}</small>
        </div>
      )}
    </div>
  );
};

// Keywords Tab Component for Radiology
const RadiologyKeywordsTab = ({ keywords, condition, isLoading }) => {
  const hasKeywords = keywords && Object.keys(keywords).some(key => 
    key !== 'extracted_at' && Array.isArray(keywords[key]) && keywords[key].length > 0
  );

  if (!hasKeywords) {
    return (
      <div className="keywords-tab">
        <div className="keywords-header">
          <h3>
            <span className="section-icon">🏷️</span>
            Medical Keywords for {condition || 'Your Analysis'}
          </h3>
          <p>Key medical terms related to your radiology analysis</p>
        </div>
        
        <div className="keywords-grid">
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">🩻</span>
              Conditions
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">
                {condition?.toLowerCase() || 'chest x-ray finding'}
              </span>
              <span className="keyword-tag">chest x-ray</span>
              <span className="keyword-tag">radiology</span>
            </div>
          </div>
          
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">🔬</span>
              Procedures
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">chest x-ray</span>
              <span className="keyword-tag">radiological assessment</span>
              <span className="keyword-tag">imaging study</span>
            </div>
          </div>
          
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">💊</span>
              Treatments
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">medical evaluation</span>
              <span className="keyword-tag">clinical correlation</span>
              <span className="keyword-tag">follow-up care</span>
            </div>
          </div>
          
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">📋</span>
              General
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">pulmonary health</span>
              <span className="keyword-tag">cardiac health</span>
              <span className="keyword-tag">medical imaging</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="keywords-tab">
      <div className="keywords-header">
        <h3>
          <span className="section-icon">🏷️</span>
          Medical Keywords
        </h3>
        <p>Key medical terms extracted from your radiology analysis</p>
      </div>
      
      <div className="keywords-grid">
        {Object.entries(keywords).map(([category, terms]) => {
          if (category === 'extracted_at' || !Array.isArray(terms) || terms.length === 0) {
            return null;
          }
          
          const categoryIcons = {
            conditions: '🩻',
            symptoms: '🫁', 
            treatments: '💊',
            procedures: '🔬',
            general: '📋'
          };
          
          return (
            <div key={category} className="keyword-category">
              <h4 className="category-title">
                <span className="category-icon">{categoryIcons[category] || '📋'}</span>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </h4>
              <div className="keyword-tags">
                {terms.map((term, index) => (
                  <span key={index} className="keyword-tag">
                    {term}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
      
      {keywords.extracted_at && (
        <div className="extraction-info">
          <small>Keywords extracted: {new Date(keywords.extracted_at).toLocaleString()}</small>
        </div>
      )}
    </div>
  );
};

export default RadiologyAnalysisResults;
