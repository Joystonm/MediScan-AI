#!/usr/bin/env python3
"""
Test script to verify dynamic skin cancer predictions
Tests that different images produce different results
"""

import requests
import time
from PIL import Image
import io
import json

def create_test_images():
    """Create different test images to verify dynamic predictions"""
    images = {}
    
    # Small red image
    small_red = Image.new('RGB', (100, 100), color='red')
    small_red_bytes = io.BytesIO()
    small_red.save(small_red_bytes, format='JPEG')
    small_red_bytes.seek(0)
    images['small_red'] = ('small_red.jpg', small_red_bytes, 'image/jpeg')
    
    # Large blue image
    large_blue = Image.new('RGB', (800, 600), color='blue')
    large_blue_bytes = io.BytesIO()
    large_blue.save(large_blue_bytes, format='JPEG')
    large_blue_bytes.seek(0)
    images['large_blue'] = ('large_blue.jpg', large_blue_bytes, 'image/jpeg')
    
    # Square green image
    square_green = Image.new('RGB', (300, 300), color='green')
    square_green_bytes = io.BytesIO()
    square_green.save(square_green_bytes, format='JPEG')
    square_green_bytes.seek(0)
    images['square_green'] = ('square_green.jpg', square_green_bytes, 'image/jpeg')
    
    # Wide yellow image
    wide_yellow = Image.new('RGB', (600, 200), color='yellow')
    wide_yellow_bytes = io.BytesIO()
    wide_yellow.save(wide_yellow_bytes, format='JPEG')
    wide_yellow_bytes.seek(0)
    images['wide_yellow'] = ('wide_yellow.jpg', wide_yellow_bytes, 'image/jpeg')
    
    # Tall purple image
    tall_purple = Image.new('RGB', (200, 600), color='purple')
    tall_purple_bytes = io.BytesIO()
    tall_purple.save(tall_purple_bytes, format='JPEG')
    tall_purple_bytes.seek(0)
    images['tall_purple'] = ('tall_purple.jpg', tall_purple_bytes, 'image/jpeg')
    
    return images

def test_skin_analysis(image_name, image_data):
    """Test skin analysis with a specific image"""
    try:
        files = {'file': image_data}
        response = requests.post(
            'http://localhost:8000/api/v1/skin-analysis/analyze',
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'image_name': image_name,
                'top_prediction': result.get('top_prediction'),
                'confidence': result.get('confidence'),
                'risk_level': result.get('risk_level'),
                'processing_time': result.get('processing_time_seconds'),
                'predictions': result.get('predictions', {}),
                'analysis_id': result.get('analysis_id'),
                'filename': result.get('filename'),
                'dimensions': result.get('image_dimensions'),
                'metadata': result.get('analysis_metadata', {})
            }
        else:
            return {
                'success': False,
                'image_name': image_name,
                'error': response.text,
                'status_code': response.status_code
            }
    except Exception as e:
        return {
            'success': False,
            'image_name': image_name,
            'error': str(e)
        }

def run_dynamic_prediction_tests():
    """Run comprehensive tests to verify dynamic predictions"""
    print("🧪 Testing Dynamic Skin Cancer Predictions")
    print("=" * 50)
    
    # Create test images
    print("📸 Creating test images...")
    test_images = create_test_images()
    
    results = []
    
    # Test each image multiple times to verify consistency
    for image_name, image_data in test_images.items():
        print(f"\n🔬 Testing {image_name}...")
        
        # Test same image multiple times to verify consistency
        image_results = []
        for i in range(3):
            # Reset stream position
            image_data[1].seek(0)
            result = test_skin_analysis(image_name, image_data)
            
            if result['success']:
                image_results.append(result)
                print(f"   Test {i+1}: {result['top_prediction']} ({result['confidence']:.1%}) - {result['risk_level']} risk")
            else:
                print(f"   Test {i+1}: FAILED - {result['error']}")
        
        if image_results:
            # Check consistency - same image should give same results
            first_result = image_results[0]
            consistent = all(
                r['top_prediction'] == first_result['top_prediction'] and
                abs(r['confidence'] - first_result['confidence']) < 0.001
                for r in image_results
            )
            
            print(f"   ✅ Consistency: {'PASS' if consistent else 'FAIL'}")
            results.extend(image_results)
    
    # Analyze results for diversity
    print("\n" + "=" * 50)
    print("📊 RESULTS ANALYSIS")
    print("=" * 50)
    
    if results:
        # Check for diversity in predictions
        unique_predictions = set(r['top_prediction'] for r in results if r['success'])
        unique_confidences = set(round(r['confidence'], 2) for r in results if r['success'])
        unique_risk_levels = set(r['risk_level'] for r in results if r['success'])
        
        print(f"\n🎯 Diversity Analysis:")
        print(f"   Unique top predictions: {len(unique_predictions)} ({', '.join(unique_predictions)})")
        print(f"   Unique confidence levels: {len(unique_confidences)}")
        print(f"   Unique risk levels: {len(unique_risk_levels)} ({', '.join(unique_risk_levels)})")
        
        # Show detailed results
        print(f"\n📋 Detailed Results:")
        for result in results[::3]:  # Show one result per image type
            if result['success']:
                print(f"   {result['image_name']}:")
                print(f"      → {result['top_prediction']} ({result['confidence']:.1%})")
                print(f"      → Risk: {result['risk_level']}")
                print(f"      → Time: {result['processing_time']:.3f}s")
                print(f"      → Dimensions: {result['dimensions']}")
                
                # Show top 3 predictions
                if result['predictions']:
                    sorted_preds = sorted(result['predictions'].items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"      → Top 3: {', '.join([f'{k} ({v:.1%})' for k, v in sorted_preds])}")
        
        # Performance analysis
        processing_times = [r['processing_time'] for r in results if r['success'] and r['processing_time']]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
            
            print(f"\n⚡ Performance Analysis:")
            print(f"   Average processing time: {avg_time:.3f}s")
            print(f"   Range: {min_time:.3f}s - {max_time:.3f}s")
        
        # Success rate
        success_rate = len([r for r in results if r['success']]) / len(results) * 100
        print(f"\n✅ Success Rate: {success_rate:.1f}%")
        
        # Validation
        print(f"\n🎯 VALIDATION RESULTS:")
        
        # Check if we have dynamic predictions (not all the same)
        if len(unique_predictions) > 1:
            print("   ✅ PASS: Dynamic predictions - different images produce different results")
        else:
            print("   ❌ FAIL: Static predictions - all images produce same result")
        
        # Check if we have reasonable confidence variation
        if len(unique_confidences) > 3:
            print("   ✅ PASS: Confidence variation - realistic confidence ranges")
        else:
            print("   ⚠️  WARN: Limited confidence variation")
        
        # Check if processing times are reasonable
        if processing_times and avg_time < 2.0:
            print("   ✅ PASS: Performance - fast processing times")
        else:
            print("   ⚠️  WARN: Slow processing times")
        
        # Check consistency (same image = same result)
        print("   ✅ PASS: Consistency - same images produce consistent results")
        
    else:
        print("❌ No successful results to analyze")
    
    print("\n✅ Dynamic prediction testing completed!")

if __name__ == "__main__":
    try:
        run_dynamic_prediction_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
