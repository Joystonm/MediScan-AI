/**
 * Radiology Immediate Insights Generator
 * Generates prediction-based insights for chest X-ray analysis
 */

export const generateRadiologyInsights = (findings, confidenceScores, urgencyLevel) => {
  // Get the top finding
  const topFinding = getTopFinding(findings, confidenceScores);
  const topConfidence = getTopConfidence(confidenceScores);
  
  // Generate condition-specific insights
  const insights = getConditionInsights(topFinding, topConfidence, urgencyLevel);
  
  return {
    ...insights,
    generated_at: new Date().toISOString()
  };
};

function getTopFinding(findings, confidenceScores) {
  if (!findings || findings.length === 0) {
    // Get top finding from confidence scores
    if (confidenceScores && Object.keys(confidenceScores).length > 0) {
      const sortedFindings = Object.entries(confidenceScores)
        .filter(([_, score]) => score > 0.1)
        .sort(([_, a], [__, b]) => b - a);
      
      if (sortedFindings.length > 0) {
        return sortedFindings[0][0];
      }
    }
    return "No acute findings";
  }
  return findings[0];
}

function getTopConfidence(confidenceScores) {
  if (!confidenceScores || Object.keys(confidenceScores).length === 0) {
    return 0.75; // Default confidence
  }
  
  const scores = Object.values(confidenceScores);
  return Math.max(...scores);
}

function getConditionInsights(finding, confidence, urgencyLevel) {
  const findingLower = finding.toLowerCase();
  const confidencePercent = Math.round(confidence * 100);
  
  // Condition-specific insights
  const conditionInsights = {
    "no acute findings": {
      summary: `No acute findings detected with ${confidencePercent}% confidence. This indicates that no immediate life-threatening conditions are visible on the chest X-ray. The ${urgencyLevel?.toLowerCase() || 'routine'} urgency level suggests standard follow-up care is appropriate. This is a reassuring finding that suggests the lungs, heart, and chest structures appear within normal limits for acute pathology.`,
      explanation: `"No acute findings" means that the radiologist or AI system did not identify any immediate, urgent medical conditions that require emergency treatment. This includes no signs of pneumonia, pneumothorax (collapsed lung), significant heart enlargement, or other critical abnormalities. However, this doesn't rule out chronic conditions or subtle changes that may require clinical correlation.`,
      clinical_significance: `This result suggests that if you're experiencing symptoms, they may be due to conditions not visible on chest X-ray, or may require additional imaging or clinical evaluation. Your healthcare provider may recommend follow-up based on your symptoms and clinical presentation.`
    },
    
    "pneumonia": {
      summary: `Pneumonia detected with ${confidencePercent}% confidence. This indicates an infection or inflammation in the lung tissue that appears as areas of increased density (consolidation or infiltrates) on the X-ray. The ${urgencyLevel?.toLowerCase() || 'urgent'} urgency level reflects the need for prompt medical attention and likely antibiotic treatment.`,
      explanation: `Pneumonia appears on chest X-rays as areas of increased whiteness (opacity) in the lung fields, representing fluid, pus, or inflammatory cells filling the air spaces. This can be caused by bacteria, viruses, fungi, or other organisms. The pattern and location can help determine the type and severity of pneumonia.`,
      clinical_significance: `Pneumonia typically requires antibiotic treatment for bacterial causes, supportive care for viral pneumonia, and close monitoring for complications. Early treatment generally leads to good outcomes, especially in otherwise healthy individuals.`
    },
    
    "pneumothorax": {
      summary: `Pneumothorax detected with ${confidencePercent}% confidence. This indicates the presence of air in the pleural space (between the lung and chest wall), causing partial or complete lung collapse. The ${urgencyLevel?.toLowerCase() || 'urgent'} urgency level reflects the potential need for immediate medical intervention.`,
      explanation: `Pneumothorax appears on chest X-rays as an area where the lung edge is visible, separated from the chest wall by a dark (air-filled) space. This can occur spontaneously, especially in tall, thin individuals, or result from trauma, medical procedures, or underlying lung disease.`,
      clinical_significance: `Small pneumothoraces may resolve on their own with observation, while larger ones often require chest tube insertion to re-expand the lung. Tension pneumothorax is a medical emergency requiring immediate decompression.`
    },
    
    "cardiomegaly": {
      summary: `Cardiomegaly (enlarged heart) detected with ${confidencePercent}% confidence. This indicates that the heart appears larger than normal on the chest X-ray, which may suggest various cardiac conditions. The ${urgencyLevel?.toLowerCase() || 'routine'} urgency level typically indicates this is a chronic finding requiring cardiology evaluation.`,
      explanation: `Cardiomegaly is diagnosed when the heart's width is greater than 50% of the chest width on a properly positioned chest X-ray. This can result from various conditions including heart failure, valve disease, high blood pressure, or cardiomyopathy. The enlargement may involve specific chambers or the entire heart.`,
      clinical_significance: `Cardiomegaly often requires further evaluation with echocardiogram, ECG, and cardiology consultation to determine the underlying cause and appropriate treatment. Management depends on the specific cardiac condition identified.`
    },
    
    "pleural effusion": {
      summary: `Pleural effusion detected with ${confidencePercent}% confidence. This indicates fluid accumulation in the pleural space (between the lung and chest wall), which appears as increased density at the lung bases. The ${urgencyLevel?.toLowerCase() || 'moderate'} urgency level suggests evaluation to determine the cause and need for drainage.`,
      explanation: `Pleural effusion appears on chest X-rays as blunting of the costophrenic angles or layering fluid density, especially visible on upright films. This can result from heart failure, infection, malignancy, kidney disease, or other conditions causing fluid accumulation.`,
      clinical_significance: `Treatment depends on the underlying cause and amount of fluid. Small effusions may be monitored, while larger ones may require thoracentesis (fluid drainage) for both diagnostic and therapeutic purposes.`
    },
    
    "atelectasis": {
      summary: `Atelectasis detected with ${confidencePercent}% confidence. This indicates partial or complete collapse of lung tissue, appearing as areas of increased density with volume loss. The ${urgencyLevel?.toLowerCase() || 'routine'} urgency level suggests this may be a chronic or slowly developing condition.`,
      explanation: `Atelectasis occurs when air spaces in the lung collapse, often due to blockage of airways, compression from outside the lung, or loss of surfactant. It appears as areas of increased whiteness with signs of volume loss such as shifted structures or elevated diaphragm.`,
      clinical_significance: `Treatment depends on the cause and may include chest physiotherapy, bronchoscopy to remove blockages, or treatment of underlying conditions. Post-operative atelectasis is common and often resolves with deep breathing exercises.`
    },
    
    "consolidation": {
      summary: `Consolidation detected with ${confidencePercent}% confidence. This indicates areas where the air spaces in the lungs are filled with fluid, pus, blood, or cells, creating dense areas on the X-ray. The ${urgencyLevel?.toLowerCase() || 'urgent'} urgency level suggests need for prompt evaluation and treatment.`,
      explanation: `Consolidation appears as areas of increased density (whiteness) in the lung fields where normal air-filled spaces are replaced by fluid or cellular material. This is commonly seen in pneumonia but can also occur with pulmonary edema, hemorrhage, or malignancy.`,
      clinical_significance: `The underlying cause determines treatment approach. Infectious consolidation typically requires antibiotics, while other causes may need specific targeted therapy. Clinical correlation with symptoms and laboratory tests is essential.`
    },
    
    "nodule": {
      summary: `Pulmonary nodule detected with ${confidencePercent}% confidence. This indicates a small, round opacity in the lung that requires further evaluation to determine its nature. The ${urgencyLevel?.toLowerCase() || 'routine'} urgency level suggests systematic follow-up rather than emergency intervention.`,
      explanation: `Pulmonary nodules appear as round or oval-shaped densities in the lung fields. They can be benign (such as granulomas from old infections) or malignant (lung cancer). Size, shape, growth rate, and patient risk factors help determine the likelihood of malignancy.`,
      clinical_significance: `Management depends on nodule size, characteristics, and patient risk factors. Small nodules may be monitored with serial imaging, while larger or suspicious nodules may require CT scan, PET scan, or biopsy for definitive diagnosis.`
    }
  };
  
  // Find matching condition
  for (const [condition, insights] of Object.entries(conditionInsights)) {
    if (findingLower.includes(condition) || condition.includes(findingLower)) {
      return {
        ...insights,
        confidence_interpretation: interpretRadiologyConfidence(confidence),
        urgency_interpretation: interpretUrgencyLevel(urgencyLevel)
      };
    }
  }
  
  // Default insights for unknown findings
  return {
    summary: `${finding} detected with ${confidencePercent}% confidence. This radiological finding requires professional medical interpretation for accurate diagnosis and appropriate clinical management. The ${urgencyLevel?.toLowerCase() || 'routine'} urgency level guides the timing of follow-up care.`,
    explanation: `Professional radiological interpretation is recommended for ${finding}. A qualified radiologist or healthcare provider can correlate this finding with your clinical symptoms, medical history, and other diagnostic tests to provide accurate diagnosis and treatment recommendations.`,
    clinical_significance: `The significance of this finding depends on clinical context, patient symptoms, and correlation with other diagnostic information. Your healthcare provider will determine the appropriate next steps based on the complete clinical picture.`,
    confidence_interpretation: interpretRadiologyConfidence(confidence),
    urgency_interpretation: interpretUrgencyLevel(urgencyLevel)
  };
}

function interpretRadiologyConfidence(confidence) {
  if (confidence >= 0.9) {
    return `Very high confidence (${Math.round(confidence * 100)}%) indicates strong certainty in the radiological assessment based on clear imaging features.`;
  } else if (confidence >= 0.7) {
    return `High confidence (${Math.round(confidence * 100)}%) shows good certainty in the assessment, with findings clearly visible on the imaging study.`;
  } else if (confidence >= 0.5) {
    return `Moderate confidence (${Math.round(confidence * 100)}%) suggests reasonable certainty, though additional imaging or clinical correlation may be helpful.`;
  } else {
    return `Lower confidence (${Math.round(confidence * 100)}%) indicates some uncertainty in the assessment, making professional radiological review particularly important.`;
  }
}

function interpretUrgencyLevel(urgencyLevel) {
  const interpretations = {
    "EMERGENCY": "Emergency urgency indicates findings that may be life-threatening and require immediate medical attention and intervention.",
    "URGENT": "Urgent urgency indicates findings that require prompt medical evaluation and treatment, typically within hours to days.",
    "ROUTINE": "Routine urgency indicates findings that can be addressed through standard medical follow-up and do not require emergency intervention.",
    "FOLLOW-UP": "Follow-up urgency indicates findings that require monitoring or additional evaluation but are not immediately concerning."
  };
  return interpretations[urgencyLevel?.toUpperCase()] || "Professional medical evaluation will determine the appropriate urgency and timing of follow-up care.";
}

export const generateRadiologyResources = (finding) => {
  const findingLower = finding.toLowerCase();
  
  const baseResources = [
    {
      title: `Understanding ${finding}: Radiology Overview`,
      url: "https://www.radiologyinfo.org/en/info/chestrad",
      source: "RadiologyInfo.org",
      snippet: `Comprehensive information about ${finding} and chest X-ray interpretation from the Radiological Society of North America.`,
      relevance_score: 0.95
    },
    {
      title: "Chest X-ray Interpretation Guidelines",
      url: "https://www.acr.org/Clinical-Resources",
      source: "American College of Radiology",
      snippet: `Professional guidelines for chest X-ray interpretation and ${finding} evaluation from leading radiology experts.`,
      relevance_score: 0.90
    },
    {
      title: "When to Seek Medical Care for Chest Symptoms",
      url: "https://www.lung.org/lung-health-diseases",
      source: "American Lung Association",
      snippet: "Guidelines for when to seek medical attention for chest symptoms and respiratory concerns.",
      relevance_score: 0.85
    }
  ];
  
  // Add condition-specific resources
  if (findingLower.includes('pneumonia')) {
    baseResources.push({
      title: "Pneumonia: Diagnosis and Treatment",
      url: "https://www.lung.org/lung-health-diseases/lung-disease-lookup/pneumonia",
      source: "American Lung Association",
      snippet: "Comprehensive information about pneumonia diagnosis, treatment, and recovery from respiratory health experts.",
      relevance_score: 0.92
    });
  }
  
  if (findingLower.includes('cardiomegaly') || findingLower.includes('heart')) {
    baseResources.push({
      title: "Heart Enlargement: Causes and Treatment",
      url: "https://www.heart.org/en/health-topics/cardiomyopathy",
      source: "American Heart Association",
      snippet: "Information about heart enlargement, its causes, and treatment options from cardiac health specialists.",
      relevance_score: 0.88
    });
  }
  
  return {
    reference_images: [],
    medical_articles: baseResources,
    fetched_at: new Date().toISOString()
  };
};

export const generateRadiologyKeywords = (finding, findings = [], recommendations = []) => {
  const findingLower = finding.toLowerCase();
  
  // Base keywords
  let keywords = {
    conditions: [findingLower, "chest x-ray", "radiology"],
    symptoms: ["chest symptoms", "respiratory symptoms"],
    treatments: ["medical evaluation", "radiological consultation"],
    procedures: ["chest x-ray", "imaging study", "radiological assessment"],
    general: ["pulmonary health", "cardiac health", "medical imaging", "diagnostic radiology"]
  };
  
  // Add condition-specific keywords
  if (findingLower.includes('pneumonia')) {
    keywords.conditions.push("pneumonia", "lung infection", "pulmonary infection");
    keywords.treatments.push("antibiotic therapy", "respiratory support");
    keywords.procedures.push("sputum culture", "blood tests");
    keywords.symptoms.push("cough", "fever", "shortness of breath");
  }
  
  if (findingLower.includes('pneumothorax')) {
    keywords.conditions.push("pneumothorax", "collapsed lung", "pleural air");
    keywords.treatments.push("chest tube", "needle decompression", "observation");
    keywords.procedures.push("thoracostomy", "pleural drainage");
    keywords.symptoms.push("chest pain", "sudden breathlessness");
  }
  
  if (findingLower.includes('cardiomegaly')) {
    keywords.conditions.push("cardiomegaly", "enlarged heart", "cardiac enlargement");
    keywords.treatments.push("cardiac medication", "heart failure treatment");
    keywords.procedures.push("echocardiogram", "ECG", "cardiac catheterization");
    keywords.symptoms.push("shortness of breath", "fatigue", "chest discomfort");
  }
  
  if (findingLower.includes('effusion')) {
    keywords.conditions.push("pleural effusion", "fluid accumulation", "pleural fluid");
    keywords.treatments.push("thoracentesis", "diuretics", "underlying cause treatment");
    keywords.procedures.push("pleural tap", "chest ultrasound");
    keywords.symptoms.push("shortness of breath", "chest heaviness");
  }
  
  if (findingLower.includes('no acute') || findingLower.includes('normal')) {
    keywords.conditions.push("normal chest x-ray", "no acute pathology");
    keywords.treatments.push("routine follow-up", "clinical correlation");
    keywords.general.push("reassuring findings", "normal imaging");
  }
  
  // Extract keywords from findings and recommendations
  [...findings, ...recommendations].forEach(item => {
    const itemLower = item.toLowerCase();
    if (itemLower.includes('follow-up')) {
      keywords.treatments.push("clinical follow-up");
    }
    if (itemLower.includes('correlation')) {
      keywords.procedures.push("clinical correlation");
    }
    if (itemLower.includes('ct') || itemLower.includes('computed tomography')) {
      keywords.procedures.push("CT scan", "computed tomography");
    }
  });
  
  // Remove duplicates
  Object.keys(keywords).forEach(category => {
    keywords[category] = [...new Set(keywords[category])];
  });
  
  return {
    ...keywords,
    extracted_at: new Date().toISOString()
  };
};
