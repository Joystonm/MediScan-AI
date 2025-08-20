import React, { useState, useEffect } from 'react';
import './SkinAnalysisResults.css';
import { generateImmediateInsights, generateImmediateResources, generateImmediateKeywords } from '../utils/immediateInsights';

const SkinAnalysisResults = ({ analysisResult, uploadedImage, isLoading }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [enhancedData, setEnhancedData] = useState({
    aiSummary: null,
    medicalResources: null,
    keywords: null
  });

  // Effect to generate immediate insights based on top prediction
  useEffect(() => {
    if (analysisResult && analysisResult.top_prediction) {
      console.log('Generating immediate insights for:', analysisResult.top_prediction);
      
      // Generate immediate insights based on the top prediction
      const immediateInsights = generateImmediateInsights(
        analysisResult.top_prediction,
        analysisResult.confidence || 0.5,
        analysisResult.risk_level || 'MEDIUM'
      );
      
      const immediateResources = generateImmediateResources(analysisResult.top_prediction);
      
      const immediateKeywords = generateImmediateKeywords(
        analysisResult.top_prediction,
        analysisResult.recommendations || []
      );
      
      // Set the enhanced data immediately
      setEnhancedData({
        aiSummary: immediateInsights,
        medicalResources: immediateResources,
        keywords: immediateKeywords
      });
      
      console.log('Immediate insights generated:', immediateInsights);
    }
  }, [analysisResult]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="analysis-loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h3>Analyzing your image...</h3>
          <p>Our AI is processing your skin lesion image and generating comprehensive insights.</p>
          
          <div className="progress-steps">
            <div className="progress-step">
              <span className="step-icon">🔬</span>
              <span className="step-text">AI Analysis</span>
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
          <div className="placeholder-icon">🔬</div>
          <h3>Upload an image to get started</h3>
          <p>Our AI will analyze skin lesions and provide detailed medical insights</p>
        </div>
      </div>
    );
  }

  // Helper functions
  const formatConfidence = (confidence) => {
    return `${Math.round(confidence * 100)}%`;
  };

  const getRiskLevelColor = (riskLevel) => {
    const colors = {
      'LOW': '#10B981',
      'MEDIUM': '#F59E0B', 
      'HIGH': '#EF4444',
      'CRITICAL': '#DC2626'
    };
    return colors[riskLevel?.toUpperCase()] || '#6B7280';
  };

  const getRiskLevelIcon = (riskLevel) => {
    const icons = {
      'LOW': '🟢',
      'MEDIUM': '🟡',
      'HIGH': '🔴', 
      'CRITICAL': '🚨'
    };
    return icons[riskLevel?.toUpperCase()] || '⚪';
  };

  const formatAnalysisTime = () => {
    return new Date().toLocaleString();
  };

  return (
    <div className="skin-analysis-results">
      {/* Results Header */}
      <div className="results-header">
        <div className="result-summary">
          <h2>Analysis Results</h2>
          <div className="top-prediction">
            <span className="prediction-label">Top Prediction:</span>
            <span className="prediction-value">{analysisResult.top_prediction || 'Unknown'}</span>
            <span className="confidence-badge">{formatConfidence(analysisResult.confidence || 0)}</span>
          </div>
          <div className="risk-assessment">
            <span className="risk-icon">{getRiskLevelIcon(analysisResult.risk_level)}</span>
            <span className="risk-text">{(analysisResult.risk_level || 'UNKNOWN').toUpperCase()} Risk</span>
          </div>
        </div>
        
        <div className="analysis-metadata">
          <div className="metadata-item">
            <span className="metadata-label">Analysis Time:</span>
            <span className="metadata-value">{formatAnalysisTime()}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Analyzed Image:</span>
            <span className="metadata-value">{uploadedImage?.name || 'Unknown'}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Dimensions:</span>
            <span className="metadata-value">
              {uploadedImage?.file ? `${uploadedImage.file.width || 'N/A'}x${uploadedImage.file.height || 'N/A'}` : 'N/A'}
            </span>
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
          <OverviewTab 
            analysisResult={analysisResult}
            uploadedImage={uploadedImage}
          />
        )}
        
        {activeTab === 'ai-insights' && (
          <AIInsightsTab 
            aiSummary={enhancedData.aiSummary || analysisResult.ai_summary}
            isLoading={false}
          />
        )}
        
        {activeTab === 'resources' && (
          <ResourcesTab 
            medicalResources={enhancedData.medicalResources || analysisResult.medical_resources}
            condition={analysisResult.top_prediction}
            isLoading={false}
          />
        )}
        
        {activeTab === 'keywords' && (
          <KeywordsTab 
            keywords={enhancedData.keywords || analysisResult.keywords}
            condition={analysisResult.top_prediction}
            isLoading={false}
          />
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ analysisResult, uploadedImage }) => {
  // Safety check for analysisResult
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

  const getRiskLevelColor = (riskLevel) => {
    const colors = {
      'LOW': '#10B981',
      'MEDIUM': '#F59E0B', 
      'HIGH': '#EF4444',
      'CRITICAL': '#DC2626'
    };
    return colors[riskLevel?.toUpperCase()] || '#6B7280';
  };

  const getRiskLevelIcon = (riskLevel) => {
    const icons = {
      'LOW': '🟢',
      'MEDIUM': '🟡',
      'HIGH': '🔴', 
      'CRITICAL': '🚨'
    };
    return icons[riskLevel?.toUpperCase()] || '⚪';
  };

  return (
    <div className="overview-tab">
      <div className="overview-grid">
        {/* Image and Predictions */}
        <div className="overview-section">
          <h3>Analysis Results</h3>
          
          {uploadedImage && (
            <div className="analyzed-image">
              <img src={uploadedImage.preview} alt="Analyzed lesion" />
              {analysisResult.visual_overlay?.overlay_image_url && (
                <div className="overlay-toggle">
                  <button className="btn btn-secondary btn-sm">
                    Show AI Overlay
                  </button>
                </div>
              )}
            </div>
          )}
          
          <div className="prediction-results">
            <div className="top-prediction">
              <h4>Top Prediction</h4>
              <div className="prediction-item primary">
                <span className="condition-name">{analysisResult.top_prediction || 'Unknown'}</span>
                <span className="confidence">{formatConfidence(analysisResult.confidence || 0)}</span>
              </div>
            </div>
            
            <div className="all-predictions">
              <h4>All Predictions</h4>
              <div className="predictions-list">
                {Object.entries(analysisResult.predictions || {})
                  .sort(([,a], [,b]) => b - a)
                  .map(([condition, probability]) => (
                    <div key={condition} className="prediction-item">
                      <span className="condition-name">{condition}</span>
                      <div className="probability-bar">
                        <div 
                          className="probability-fill"
                          style={{ width: `${(probability || 0) * 100}%` }}
                        ></div>
                        <span className="probability-text">{formatConfidence(probability || 0)}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="overview-section">
          <h3>Medical Recommendations</h3>
          
          {/* Recommendations section only - ABCDE removed */}
          
          <div className="recommendations-section">
            <h4>Medical Recommendations</h4>
            <ul className="recommendations-list">
              {(analysisResult.recommendations || []).map((rec, index) => (
                <li key={index} className="recommendation-item">
                  <span className="rec-icon">💡</span>
                  <span className="rec-text">{rec}</span>
                </li>
              ))}
            </ul>
            
            <h4>Next Steps</h4>
            <ul className="next-steps-list">
              {(analysisResult.next_steps || []).map((step, index) => (
                <li key={index} className="next-step-item">
                  <span className="step-number">{index + 1}</span>
                  <span className="step-text">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      
      <div className="analysis-id">
        <small>Analysis ID: {analysisResult.analysis_id || 'Unknown'}</small>
      </div>
    </div>
  );
};

// AI Insights Tab Component
const AIInsightsTab = ({ aiSummary, isLoading }) => {
  // Always show content if we have any data, ignore loading state
  const hasSummary = aiSummary && (aiSummary.summary || aiSummary.explanation);
  
  if (!hasSummary) {
    // Show a simple message instead of loading
    return (
      <div className="ai-insights-tab">
        <div className="insight-section">
          <h3>
            <span className="section-icon">🧠</span>
            AI Medical Summary
          </h3>
          <div className="insight-content">
            <div className="summary-text">
              AI insights are being processed. Please check back in a moment or refresh the page.
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
            <span className="section-icon">🧠</span>
            AI Medical Summary
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
            Condition Explanation
          </h3>
          <div className="insight-content">
            <div className="explanation-text">
              {aiSummary.explanation}
            </div>
          </div>
        </div>
      )}
      
      {/* Show confidence and risk interpretations if available */}
      {(aiSummary.confidence_interpretation || aiSummary.risk_interpretation) && (
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
            {aiSummary.risk_interpretation && (
              <div className="interpretation-item">
                <h4>Risk Assessment</h4>
                <p>{aiSummary.risk_interpretation}</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      <div className="disclaimer-section">
        <div className="disclaimer">
          <span className="disclaimer-icon">⚠️</span>
          <div className="disclaimer-text">
            <strong>Medical Disclaimer:</strong> This AI-generated content is for informational purposes only 
            and should not replace professional medical advice, diagnosis, or treatment. Always consult with 
            qualified healthcare professionals for medical concerns.
          </div>
        </div>
      </div>
    </div>
  );
};

// Resources Tab Component
const ResourcesTab = ({ medicalResources, condition, isLoading }) => {
  const hasResources = medicalResources && (
    (medicalResources.reference_images && medicalResources.reference_images.length > 0) ||
    (medicalResources.medical_articles && medicalResources.medical_articles.length > 0)
  );

  if (!hasResources) {
    // Show simple message with useful links instead of loading
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
                <a href="https://www.aad.org/public/diseases/skin-cancer" target="_blank" rel="noopener noreferrer">
                  American Academy of Dermatology - Skin Cancer Information
                </a>
                <a href="https://www.mayoclinic.org/diseases-conditions/skin-cancer/symptoms-causes/syc-20377605" target="_blank" rel="noopener noreferrer">
                  Mayo Clinic - Skin Cancer Overview
                </a>
                <a href="https://www.skincancer.org/" target="_blank" rel="noopener noreferrer">
                  Skin Cancer Foundation
                </a>
                <a href="https://dermnetnz.org/" target="_blank" rel="noopener noreferrer">
                  DermNet NZ - Dermatology Resource
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
      {medicalResources.reference_images && medicalResources.reference_images.length > 0 && (
        <div className="resource-section">
          <h3>
            <span className="section-icon">🖼️</span>
            Reference Images
          </h3>
          <div className="images-grid">
            {medicalResources.reference_images.map((image, index) => (
              <div key={index} className="reference-image">
                <div className="image-container">
                  <img 
                    src={image.url} 
                    alt={image.title || `Reference image ${index + 1}`}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div className="image-placeholder" style={{ display: 'none' }}>
                    <span>Image unavailable</span>
                  </div>
                </div>
                <div className="image-info">
                  <h4>{image.title || `Reference Image ${index + 1}`}</h4>
                  <p>{image.description || `Clinical reference for ${condition}`}</p>
                  <small>Source: {image.source || 'Medical Database'}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
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

// Keywords Tab Component
const KeywordsTab = ({ keywords, condition, isLoading }) => {
  const hasKeywords = keywords && Object.keys(keywords).some(key => 
    key !== 'extracted_at' && Array.isArray(keywords[key]) && keywords[key].length > 0
  );

  if (!hasKeywords) {
    // Show basic keywords instead of loading
    return (
      <div className="keywords-tab">
        <div className="keywords-header">
          <h3>
            <span className="section-icon">🏷️</span>
            Medical Keywords for {condition || 'Your Analysis'}
          </h3>
          <p>Key medical terms related to your analysis</p>
        </div>
        
        <div className="keywords-grid">
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">🏥</span>
              Conditions
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">
                {condition?.toLowerCase() || 'skin condition'}
              </span>
              <span className="keyword-tag">skin lesion</span>
              <span className="keyword-tag">dermatology</span>
            </div>
          </div>
          
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">🩺</span>
              Procedures
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">clinical examination</span>
              <span className="keyword-tag">dermatological consultation</span>
              <span className="keyword-tag">medical evaluation</span>
            </div>
          </div>
          
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">💊</span>
              Treatments
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">professional assessment</span>
              <span className="keyword-tag">medical monitoring</span>
              <span className="keyword-tag">preventive care</span>
            </div>
          </div>
          
          <div className="keyword-category">
            <h4 className="category-title">
              <span className="category-icon">📋</span>
              General
            </h4>
            <div className="keyword-tags">
              <span className="keyword-tag">skin health</span>
              <span className="keyword-tag">medical diagnosis</span>
              <span className="keyword-tag">healthcare</span>
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
        <p>Key medical terms extracted from your analysis results</p>
      </div>
      
      <div className="keywords-grid">
        {Object.entries(keywords).map(([category, terms]) => {
          if (category === 'extracted_at' || !Array.isArray(terms) || terms.length === 0) {
            return null;
          }
          
          const categoryIcons = {
            conditions: '🏥',
            symptoms: '🩺', 
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

export default SkinAnalysisResults;
