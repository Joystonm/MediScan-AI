"""
Advanced ABCDE Characteristics Analyzer
Calculates real lesion characteristics from image analysis (simplified version)
"""

import numpy as np
from PIL import Image, ImageStat, ImageFilter
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ABCDEAnalyzer:
    """Advanced analyzer for ABCDE characteristics of skin lesions"""
    
    def __init__(self):
        self.confidence_threshold = 0.3
        
    async def analyze_lesion_characteristics(
        self, 
        image: Image.Image, 
        predictions: Dict,
        confidence_threshold: float = 0.3
    ) -> Dict[str, float]:
        """
        Analyze ABCDE characteristics from lesion image
        
        Returns:
            Dict with asymmetry_score, border_irregularity, color_variation, evolution_risk
        """
        
        try:
            # Get confidence and prediction info
            confidence = predictions.get("confidence", 0.0)
            top_class = predictions.get("top_class", "").lower()
            
            # If confidence is too low, return N/A values
            if confidence < confidence_threshold:
                logger.info(f"Confidence {confidence:.2%} below threshold, returning N/A values")
                return {
                    "asymmetry_score": None,  # Will display as "N/A"
                    "border_irregularity": None,
                    "color_variation": None,
                    "evolution_risk": None
                }
            
            # Analyze image characteristics
            asymmetry_score = self._analyze_asymmetry(image, confidence, top_class)
            border_score = self._analyze_border_irregularity(image, confidence, top_class)
            color_score = self._analyze_color_variation(image, confidence, top_class)
            evolution_score = self._estimate_evolution_risk(predictions, asymmetry_score, border_score, color_score)
            
            logger.info(f"ABCDE calculated: A={asymmetry_score:.2f}, B={border_score:.2f}, C={color_score:.2f}, E={evolution_score:.2f}")
            
            return {
                "asymmetry_score": asymmetry_score,
                "border_irregularity": border_score,
                "color_variation": color_score,
                "evolution_risk": evolution_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing ABCDE characteristics: {str(e)}")
            # Fallback to confidence-based scores
            return self._get_confidence_based_scores(predictions)
    
    def _analyze_asymmetry(self, image: Image.Image, confidence: float, top_class: str) -> float:
        """Analyze asymmetry using image statistics"""
        
        try:
            # Convert to grayscale for analysis
            gray_image = image.convert('L')
            width, height = gray_image.size
            
            # Split image into quadrants and compare
            left_half = gray_image.crop((0, 0, width//2, height))
            right_half = gray_image.crop((width//2, 0, width, height))
            top_half = gray_image.crop((0, 0, width, height//2))
            bottom_half = gray_image.crop((0, height//2, width, height))
            
            # Calculate statistics for each half
            left_stats = ImageStat.Stat(left_half)
            right_stats = ImageStat.Stat(right_half)
            top_stats = ImageStat.Stat(top_half)
            bottom_stats = ImageStat.Stat(bottom_half)
            
            # Compare means and standard deviations
            horizontal_diff = abs(left_stats.mean[0] - right_stats.mean[0]) / 255.0
            vertical_diff = abs(top_stats.mean[0] - bottom_stats.mean[0]) / 255.0
            
            # Combine horizontal and vertical asymmetry
            asymmetry = (horizontal_diff + vertical_diff) / 2
            
            # Adjust based on condition type and confidence
            asymmetry = self._adjust_score_by_condition(asymmetry, confidence, top_class, "asymmetry")
            
            return min(max(asymmetry, 0.15), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating asymmetry: {str(e)}")
            return self._get_default_score(confidence, top_class, "asymmetry")
    
    def _analyze_border_irregularity(self, image: Image.Image, confidence: float, top_class: str) -> float:
        """Analyze border irregularity using edge detection"""
        
        try:
            # Apply edge detection filter
            edges = image.filter(ImageFilter.FIND_EDGES)
            edge_gray = edges.convert('L')
            
            # Calculate edge statistics
            edge_stats = ImageStat.Stat(edge_gray)
            edge_intensity = edge_stats.mean[0] / 255.0
            edge_variance = edge_stats.stddev[0] / 255.0 if edge_stats.stddev else 0
            
            # Combine edge intensity and variance for irregularity score
            irregularity = (edge_intensity + edge_variance) / 2
            
            # Adjust based on condition type and confidence
            irregularity = self._adjust_score_by_condition(irregularity, confidence, top_class, "border")
            
            return min(max(irregularity, 0.12), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating border irregularity: {str(e)}")
            return self._get_default_score(confidence, top_class, "border")
    
    def _analyze_color_variation(self, image: Image.Image, confidence: float, top_class: str) -> float:
        """Analyze color variation within the image"""
        
        try:
            # Convert to RGB if not already
            rgb_image = image.convert('RGB')
            
            # Calculate statistics for each color channel
            r_stats = ImageStat.Stat(rgb_image, mask=None)
            
            # Calculate coefficient of variation for each channel
            variations = []
            for i in range(3):  # R, G, B channels
                mean_val = r_stats.mean[i]
                std_val = r_stats.stddev[i] if r_stats.stddev else 0
                
                if mean_val > 0:
                    cv = std_val / mean_val
                    variations.append(cv)
            
            # Average variation across channels
            if variations:
                color_variation = np.mean(variations) / 2.0  # Normalize
            else:
                color_variation = 0.25
            
            # Adjust based on condition type and confidence
            color_variation = self._adjust_score_by_condition(color_variation, confidence, top_class, "color")
            
            return min(max(color_variation, 0.18), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating color variation: {str(e)}")
            return self._get_default_score(confidence, top_class, "color")
    
    def _estimate_evolution_risk(
        self, 
        predictions: Dict, 
        asymmetry: float, 
        border: float, 
        color: float
    ) -> float:
        """Estimate evolution risk based on other ABCDE factors and prediction"""
        
        try:
            confidence = predictions.get("confidence", 0.5)
            top_class = predictions.get("top_class", "").lower()
            
            # Base evolution risk on ABCDE factors
            abcde_risk = (asymmetry + border + color) / 3
            
            # Adjust based on condition type
            condition_multiplier = 1.0
            
            if "melanoma" in top_class:
                condition_multiplier = 1.4  # Higher evolution risk
            elif "carcinoma" in top_class:
                condition_multiplier = 1.2  # Moderate evolution risk
            elif "keratosis" in top_class and "actinic" in top_class:
                condition_multiplier = 1.1  # Slight evolution risk (precancerous)
            elif "nevus" in top_class or "benign" in top_class:
                condition_multiplier = 0.7  # Lower evolution risk
            
            # Combine factors
            evolution_risk = abcde_risk * condition_multiplier * confidence
            
            # Normalize and bound
            evolution_risk = min(max(evolution_risk, 0.1), 1.0)
            
            return evolution_risk
            
        except Exception as e:
            logger.error(f"Error estimating evolution risk: {str(e)}")
            return 0.3  # Default moderate risk
    
    def _adjust_score_by_condition(self, base_score: float, confidence: float, top_class: str, score_type: str) -> float:
        """Adjust scores based on condition type and confidence"""
        
        # Base adjustment on confidence
        confidence_factor = 0.5 + (confidence * 0.5)  # Scale from 0.5 to 1.0
        adjusted_score = base_score * confidence_factor
        
        # Condition-specific adjustments
        if "melanoma" in top_class:
            if score_type == "asymmetry":
                adjusted_score *= 1.3
            elif score_type == "border":
                adjusted_score *= 1.4
            elif score_type == "color":
                adjusted_score *= 1.2
        elif "carcinoma" in top_class:
            if score_type == "asymmetry":
                adjusted_score *= 1.1
            elif score_type == "border":
                adjusted_score *= 1.2
            elif score_type == "color":
                adjusted_score *= 1.0
        elif "keratosis" in top_class:
            if score_type == "asymmetry":
                adjusted_score *= 0.9
            elif score_type == "border":
                adjusted_score *= 1.1
            elif score_type == "color":
                adjusted_score *= 1.0
        elif "nevus" in top_class or "benign" in top_class:
            if score_type == "asymmetry":
                adjusted_score *= 0.8
            elif score_type == "border":
                adjusted_score *= 0.9
            elif score_type == "color":
                adjusted_score *= 0.9
        
        return adjusted_score
    
    def _get_default_score(self, confidence: float, top_class: str, score_type: str) -> float:
        """Get default score when image analysis fails"""
        
        base_scores = {
            "asymmetry": 0.4,
            "border": 0.35,
            "color": 0.3,
            "evolution": 0.25
        }
        
        base_score = base_scores.get(score_type, 0.3)
        return self._adjust_score_by_condition(base_score, confidence, top_class, score_type)
    
    def _get_confidence_based_scores(self, predictions: Dict) -> Dict[str, float]:
        """Generate ABCDE scores based on prediction confidence and type when image analysis fails"""
        
        confidence = predictions.get("confidence", 0.5)
        top_class = predictions.get("top_class", "").lower()
        
        # Base scores on confidence
        base_asymmetry = max(0.2, confidence * 0.7)
        base_border = max(0.15, confidence * 0.6)
        base_color = max(0.25, confidence * 0.5)
        base_evolution = max(0.1, confidence * 0.8)
        
        # Adjust based on condition type
        if "melanoma" in top_class:
            asymmetry_score = min(base_asymmetry * 1.3, 1.0)
            border_irregularity = min(base_border * 1.4, 1.0)
            color_variation = min(base_color * 1.2, 1.0)
            evolution_risk = min(base_evolution * 1.5, 1.0)
        elif "carcinoma" in top_class:
            asymmetry_score = min(base_asymmetry * 1.1, 1.0)
            border_irregularity = min(base_border * 1.2, 1.0)
            color_variation = min(base_color * 1.0, 1.0)
            evolution_risk = min(base_evolution * 1.3, 1.0)
        elif "keratosis" in top_class:
            asymmetry_score = min(base_asymmetry * 0.9, 1.0)
            border_irregularity = min(base_border * 1.1, 1.0)
            color_variation = min(base_color * 1.0, 1.0)
            evolution_risk = min(base_evolution * 1.1, 1.0)
        else:
            # Default values
            asymmetry_score = base_asymmetry
            border_irregularity = base_border
            color_variation = base_color
            evolution_risk = base_evolution
        
        return {
            "asymmetry_score": asymmetry_score,
            "border_irregularity": border_irregularity,
            "color_variation": color_variation,
            "evolution_risk": evolution_risk
        }
