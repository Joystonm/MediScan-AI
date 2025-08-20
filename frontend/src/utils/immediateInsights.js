/**
 * Immediate AI Insights Generator
 * Generates prediction-based insights instantly without waiting for backend APIs
 */

export const generateImmediateInsights = (topPrediction, confidence, riskLevel) => {
  const predictionLower = topPrediction.toLowerCase();
  
  // Condition-specific insights
  const insights = {
    "basal cell carcinoma": {
      summary: `Basal Cell Carcinoma detected with ${Math.round(confidence * 100)}% confidence. This is the most common form of skin cancer that grows slowly and rarely spreads to other parts of the body. While it's considered ${riskLevel?.toLowerCase() || 'moderate'} risk, early treatment prevents complications and ensures the best cosmetic outcome. BCC typically appears as a pearly or waxy bump, a flat flesh-colored lesion, or a bleeding sore that heals and returns.`,
      explanation: `Basal Cell Carcinoma (BCC) develops in the basal cells of the skin's outer layer, typically in sun-exposed areas. It's the most frequently occurring form of all cancers, with over 4 million cases diagnosed in the U.S. each year. BCC rarely metastasizes (spreads) but can cause significant local damage if left untreated. The good news is that when detected early, BCC has a cure rate of over 95% with appropriate treatment.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "squamous cell carcinoma": {
      summary: `Squamous Cell Carcinoma identified with ${Math.round(confidence * 100)}% confidence. This is the second most common type of skin cancer that can be more aggressive than basal cell carcinoma. The ${riskLevel?.toLowerCase() || 'moderate'} risk assessment indicates the need for prompt medical evaluation and treatment. SCC can spread to other parts of the body if left untreated, making early detection crucial.`,
      explanation: `Squamous Cell Carcinoma (SCC) arises from squamous cells in the skin's upper layers. It often appears as a firm, red nodule or a flat lesion with a scaly, crusted surface. SCC is more likely to spread than basal cell carcinoma, particularly in high-risk locations like the lips, ears, or genitals. With early detection and treatment, the cure rate is excellent, typically over 90%.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "melanoma": {
      summary: `Melanoma detected with ${Math.round(confidence * 100)}% confidence. This is the most serious type of skin cancer that can spread rapidly if not treated early. The ${riskLevel?.toLowerCase() || 'high'} risk classification emphasizes the critical importance of immediate professional medical evaluation. Early-stage melanoma has excellent survival rates, but delayed treatment can be life-threatening.`,
      explanation: `Melanoma develops in melanocytes, the cells that produce melanin (skin pigment). It can appear anywhere on the body and may develop from an existing mole or appear as a new, unusual growth. Melanoma is responsible for the majority of skin cancer deaths, but when caught early (Stage 0 or I), the 5-year survival rate exceeds 95%. The ABCDE rule (Asymmetry, Border, Color, Diameter, Evolution) helps identify suspicious lesions.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "actinic keratosis": {
      summary: `Actinic Keratosis identified with ${Math.round(confidence * 100)}% confidence. This is a precancerous condition caused by sun damage that has the potential to develop into squamous cell carcinoma. The ${riskLevel?.toLowerCase() || 'low'} risk indicates the importance of monitoring and potential treatment to prevent progression to cancer.`,
      explanation: `Actinic Keratosis (AK) appears as rough, scaly patches on sun-exposed areas of the skin, particularly the face, scalp, ears, neck, hands, and forearms. While AK itself is not cancer, it's considered precancerous because 5-10% of cases can progress to squamous cell carcinoma. Treatment options include topical medications, cryotherapy, and photodynamic therapy.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "seborrheic keratosis": {
      summary: `Seborrheic Keratosis detected with ${Math.round(confidence * 100)}% confidence. This is a common, benign (non-cancerous) skin growth that typically appears as people age. The ${riskLevel?.toLowerCase() || 'low'} risk assessment reflects its generally harmless nature, though professional evaluation confirms the diagnosis and rules out other conditions.`,
      explanation: `Seborrheic Keratosis appears as waxy, scaly, or slightly raised growths that can range in color from light tan to black. These growths are very common in people over 50 and are sometimes called 'wisdom spots.' They're completely benign but can sometimes be confused with melanoma or other skin cancers, making professional evaluation important for accurate diagnosis.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "benign keratosis": {
      summary: `Benign Keratosis detected with ${Math.round(confidence * 100)}% confidence. This represents a non-cancerous skin growth that poses minimal health risk. The ${riskLevel?.toLowerCase() || 'low'} risk assessment indicates routine monitoring is typically sufficient, though any changes in appearance should be evaluated by a healthcare professional.`,
      explanation: `Benign keratoses are common, non-cancerous skin growths that include seborrheic keratoses and other harmless lesions. They typically develop with age and sun exposure but don't pose cancer risk. While generally harmless, they can sometimes be cosmetically bothersome or confused with other skin conditions, making professional evaluation valuable for peace of mind.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "melanocytic nevus": {
      summary: `Melanocytic Nevus (mole) identified with ${Math.round(confidence * 100)}% confidence. This appears to be a common skin growth that is typically benign. The ${riskLevel?.toLowerCase() || 'low'} risk assessment suggests routine monitoring, as most moles remain harmless throughout life, though changes should be evaluated professionally.`,
      explanation: `A melanocytic nevus is a common type of skin growth, often called a mole, composed of melanocytes (pigment-producing cells). Most people have 10-40 moles, and they're usually harmless. However, changes in size, shape, color, or texture should be evaluated by a healthcare professional, as these could indicate the need for closer monitoring or removal.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "vascular lesion": {
      summary: `Vascular Lesion detected with ${Math.round(confidence * 100)}% confidence. This indicates a growth involving blood vessels in the skin, which are typically benign. The ${riskLevel?.toLowerCase() || 'low'} risk assessment reflects that most vascular lesions are harmless, though professional evaluation can determine the specific type and any treatment needs.`,
      explanation: `Vascular lesions include various growths involving blood vessels, such as cherry angiomas, spider veins, or hemangiomas. Most are benign and cosmetic in nature. Some may be present from birth, while others develop with age. While generally harmless, rapid changes or bleeding should be evaluated by a healthcare professional.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    },
    
    "dermatofibroma": {
      summary: `Dermatofibroma detected with ${Math.round(confidence * 100)}% confidence. This is a common, benign skin growth composed of fibrous tissue. The ${riskLevel?.toLowerCase() || 'low'} risk assessment indicates it's typically harmless, though professional evaluation can confirm the diagnosis and discuss removal options if desired.`,
      explanation: `Dermatofibromas are small, firm nodules that commonly appear on the legs and arms. They're composed of fibrous tissue and are completely benign. They often develop after minor skin injuries like insect bites or splinters. While harmless, they can be removed for cosmetic reasons or if they become irritated by clothing or shaving.`,
      confidence_interpretation: interpretConfidence(confidence),
      risk_interpretation: interpretRisk(riskLevel)
    }
  };
  
  // Find matching insight
  for (const [condition, insight] of Object.entries(insights)) {
    if (predictionLower.includes(condition)) {
      return {
        ...insight,
        generated_at: new Date().toISOString()
      };
    }
  }
  
  // Default insight for unknown conditions
  return {
    summary: `${topPrediction} detected with ${Math.round(confidence * 100)}% confidence. This skin condition requires professional medical evaluation for accurate diagnosis and appropriate treatment planning. The ${riskLevel?.toLowerCase() || 'moderate'} risk assessment guides the urgency of follow-up care.`,
    explanation: `Professional dermatological evaluation is recommended for ${topPrediction}. A qualified healthcare provider can perform a thorough examination, potentially including dermoscopy or biopsy if needed, to confirm the diagnosis and recommend the most appropriate treatment approach.`,
    confidence_interpretation: interpretConfidence(confidence),
    risk_interpretation: interpretRisk(riskLevel),
    generated_at: new Date().toISOString()
  };
};

function interpretConfidence(confidence) {
  if (confidence >= 0.8) {
    return `High confidence (${Math.round(confidence * 100)}%) indicates strong certainty in the AI assessment based on clear diagnostic features visible in the image.`;
  } else if (confidence >= 0.6) {
    return `Good confidence (${Math.round(confidence * 100)}%) shows reasonable certainty in the assessment, with professional confirmation recommended for definitive diagnosis.`;
  } else if (confidence >= 0.4) {
    return `Moderate confidence (${Math.round(confidence * 100)}%) suggests some uncertainty in the assessment, making professional medical evaluation particularly important.`;
  } else {
    return `Low confidence (${Math.round(confidence * 100)}%) indicates significant uncertainty in the assessment, requiring professional medical evaluation for accurate diagnosis.`;
  }
}

function interpretRisk(riskLevel) {
  const interpretations = {
    "HIGH": "High risk indicates features that may suggest a serious condition requiring immediate medical attention and prompt treatment.",
    "MEDIUM": "Medium risk indicates features that warrant professional evaluation within a reasonable timeframe to ensure proper diagnosis and care.",
    "LOW": "Low risk indicates features that appear benign but should still be monitored regularly and evaluated if any changes occur.",
    "CRITICAL": "Critical risk indicates features requiring emergency medical evaluation due to potentially serious implications."
  };
  return interpretations[riskLevel?.toUpperCase()] || "Professional medical evaluation is recommended to determine the appropriate level of care and monitoring needed.";
}

export const generateImmediateResources = (topPrediction) => {
  const predictionLower = topPrediction.toLowerCase();
  
  const baseResources = [
    {
      title: `Understanding ${topPrediction}: Medical Overview`,
      url: "https://www.mayoclinic.org/diseases-conditions/skin-cancer",
      source: "Mayo Clinic",
      snippet: `Comprehensive medical information about ${topPrediction} including symptoms, diagnosis, and treatment options from Mayo Clinic's expert medical team.`,
      relevance_score: 0.95
    },
    {
      title: "Dermatology Guidelines and Best Practices",
      url: "https://www.aad.org/public/diseases/skin-cancer",
      source: "American Academy of Dermatology",
      snippet: `Professional guidelines for ${topPrediction} diagnosis, treatment, and patient care from the leading dermatology organization.`,
      relevance_score: 0.90
    },
    {
      title: "When to See a Dermatologist",
      url: "https://www.aad.org/public/everyday-care/when-to-see-dermatologist",
      source: "American Academy of Dermatology",
      snippet: "Guidelines for when to seek professional dermatological care and evaluation for skin concerns.",
      relevance_score: 0.85
    }
  ];
  
  // Add condition-specific resources
  if (predictionLower.includes('carcinoma') || predictionLower.includes('melanoma')) {
    baseResources.push({
      title: "Skin Cancer Prevention and Early Detection",
      url: "https://www.skincancer.org/early-detection",
      source: "Skin Cancer Foundation",
      snippet: "Evidence-based information on preventing skin cancer and recognizing early warning signs for better outcomes.",
      relevance_score: 0.88
    });
  }
  
  return {
    reference_images: [],
    medical_articles: baseResources,
    fetched_at: new Date().toISOString()
  };
};

export const generateImmediateKeywords = (topPrediction, recommendations = []) => {
  const predictionLower = topPrediction.toLowerCase();
  
  // Base keywords
  let keywords = {
    conditions: [predictionLower, "skin lesion", "dermatology"],
    symptoms: ["skin growth", "lesion", "skin change"],
    treatments: ["medical evaluation", "dermatological consultation"],
    procedures: ["clinical examination", "dermoscopy", "professional assessment"],
    general: ["skin health", "medical diagnosis", "healthcare", "prevention"]
  };
  
  // Add condition-specific keywords
  if (predictionLower.includes('carcinoma')) {
    keywords.conditions.push("skin cancer", "carcinoma");
    keywords.treatments.push("surgical excision", "mohs surgery", "radiation therapy");
    keywords.procedures.push("biopsy", "histopathology", "staging");
  }
  
  if (predictionLower.includes('melanoma')) {
    keywords.conditions.push("melanoma", "malignant melanoma");
    keywords.treatments.push("immunotherapy", "targeted therapy", "surgical excision");
    keywords.procedures.push("sentinel lymph node biopsy", "staging", "genetic testing");
    keywords.symptoms.push("ABCDE criteria", "asymmetry", "irregular borders");
  }
  
  if (predictionLower.includes('keratosis')) {
    keywords.conditions.push("keratosis", "precancerous lesion");
    keywords.treatments.push("cryotherapy", "topical therapy", "monitoring");
    keywords.symptoms.push("scaly patch", "rough texture", "sun damage");
  }
  
  if (predictionLower.includes('benign') || predictionLower.includes('nevus')) {
    keywords.conditions.push("benign lesion", "mole");
    keywords.treatments.push("monitoring", "routine surveillance");
    keywords.general.push("benign condition", "non-cancerous");
  }
  
  // Extract keywords from recommendations
  recommendations.forEach(rec => {
    const recLower = rec.toLowerCase();
    if (recLower.includes('dermatologist')) {
      keywords.procedures.push("dermatological consultation");
    }
    if (recLower.includes('biopsy')) {
      keywords.procedures.push("tissue biopsy");
    }
    if (recLower.includes('monitor')) {
      keywords.treatments.push("clinical monitoring");
    }
    if (recLower.includes('sunscreen')) {
      keywords.general.push("sun protection", "UV protection");
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
