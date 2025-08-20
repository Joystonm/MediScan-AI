#!/usr/bin/env python3
"""
Performance test script for optimized MediScan-AI backend
Tests analysis speed and model loading efficiency
"""

import requests
import time
import statistics
from PIL import Image
import io
import concurrent.futures
import threading

# Create test images of different sizes
def create_test_images():
    """Create test images for performance testing"""
    images = {}
    
    # Small image (224x224)
    small_img = Image.new('RGB', (224, 224), color='red')
    small_bytes = io.BytesIO()
    small_img.save(small_bytes, format='JPEG')
    small_bytes.seek(0)
    images['small'] = small_bytes
    
    # Medium image (512x512)
    medium_img = Image.new('RGB', (512, 512), color='green')
    medium_bytes = io.BytesIO()
    medium_img.save(medium_bytes, format='JPEG')
    medium_bytes.seek(0)
    images['medium'] = medium_bytes
    
    # Large image (1024x1024)
    large_img = Image.new('RGB', (1024, 1024), color='blue')
    large_bytes = io.BytesIO()
    large_img.save(large_bytes, format='JPEG')
    large_bytes.seek(0)
    images['large'] = large_bytes
    
    return images

def test_single_analysis(endpoint, image_data, image_name):
    """Test single analysis performance"""
    start_time = time.time()
    
    try:
        files = {'file': (f'test_{image_name}.jpg', image_data, 'image/jpeg')}
        response = requests.post(endpoint, files=files, timeout=30)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            server_time = result.get('processing_time_seconds', 0)
            return {
                'success': True,
                'total_time': total_time,
                'server_time': server_time,
                'network_time': total_time - server_time,
                'image_size': image_name,
                'response_size': len(response.content)
            }
        else:
            return {
                'success': False,
                'error': response.text,
                'total_time': total_time,
                'image_size': image_name
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'total_time': time.time() - start_time,
            'image_size': image_name
        }

def test_concurrent_analysis(endpoint, image_data, num_concurrent=3):
    """Test concurrent analysis performance"""
    print(f"\n🔄 Testing {num_concurrent} concurrent requests...")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        for i in range(num_concurrent):
            image_data.seek(0)  # Reset stream position
            future = executor.submit(test_single_analysis, endpoint, image_data, f'concurrent_{i}')
            futures.append(future)
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
    
    total_time = time.time() - start_time
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        avg_server_time = statistics.mean([r['server_time'] for r in successful_results])
        avg_total_time = statistics.mean([r['total_time'] for r in successful_results])
        
        print(f"✅ Concurrent test completed:")
        print(f"   Total wall time: {total_time:.3f}s")
        print(f"   Average server time: {avg_server_time:.3f}s")
        print(f"   Average total time: {avg_total_time:.3f}s")
        print(f"   Successful requests: {len(successful_results)}/{num_concurrent}")
        
        return {
            'wall_time': total_time,
            'avg_server_time': avg_server_time,
            'avg_total_time': avg_total_time,
            'success_rate': len(successful_results) / num_concurrent
        }
    else:
        print(f"❌ All concurrent requests failed")
        return None

def test_model_warmup():
    """Test model warmup time"""
    print("\n🔥 Testing model warmup...")
    
    # Test system status endpoint
    start_time = time.time()
    try:
        response = requests.get('http://localhost:8000/api/v1/system/status', timeout=10)
        warmup_time = time.time() - start_time
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System status check: {warmup_time:.3f}s")
            print(f"   Models loaded: {status.get('models', {}).get('models_loaded', [])}")
            print(f"   GPU available: {status.get('models', {}).get('gpu_available', False)}")
            return warmup_time
        else:
            print(f"❌ System status failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ System status error: {e}")
        return None

def run_performance_tests():
    """Run comprehensive performance tests"""
    print("🚀 MediScan-AI Performance Test Suite")
    print("=" * 50)
    
    # Test model warmup
    warmup_time = test_model_warmup()
    
    # Create test images
    print("\n📸 Creating test images...")
    test_images = create_test_images()
    
    # Test endpoints
    endpoints = {
        'skin': 'http://localhost:8000/api/v1/skin-analysis/analyze',
        'radiology': 'http://localhost:8000/api/v1/radiology/analyze?scan_type=chest_xray'
    }
    
    results = {}
    
    for endpoint_name, endpoint_url in endpoints.items():
        print(f"\n🧪 Testing {endpoint_name.upper()} Analysis")
        print("-" * 30)
        
        endpoint_results = {}
        
        # Test different image sizes
        for size_name, image_data in test_images.items():
            print(f"\n📏 Testing {size_name} image ({image_data.getvalue().__len__()} bytes)...")
            
            # Run multiple tests for average
            times = []
            server_times = []
            
            for i in range(3):
                image_data.seek(0)  # Reset stream position
                result = test_single_analysis(endpoint_url, image_data, f'{size_name}_{i}')
                
                if result['success']:
                    times.append(result['total_time'])
                    server_times.append(result['server_time'])
                    print(f"   Test {i+1}: {result['total_time']:.3f}s (server: {result['server_time']:.3f}s)")
                else:
                    print(f"   Test {i+1}: FAILED - {result['error']}")
            
            if times:
                avg_time = statistics.mean(times)
                avg_server_time = statistics.mean(server_times)
                min_time = min(times)
                max_time = max(times)
                
                endpoint_results[size_name] = {
                    'avg_total_time': avg_time,
                    'avg_server_time': avg_server_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'tests_run': len(times)
                }
                
                print(f"   📊 Average: {avg_time:.3f}s (server: {avg_server_time:.3f}s)")
                print(f"   📊 Range: {min_time:.3f}s - {max_time:.3f}s")
        
        # Test concurrent requests
        test_images['medium'].seek(0)
        concurrent_result = test_concurrent_analysis(endpoint_url, test_images['medium'])
        if concurrent_result:
            endpoint_results['concurrent'] = concurrent_result
        
        results[endpoint_name] = endpoint_results
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    if warmup_time:
        print(f"🔥 Model warmup time: {warmup_time:.3f}s")
    
    for endpoint_name, endpoint_results in results.items():
        print(f"\n🎯 {endpoint_name.upper()} Analysis:")
        
        for size_name, size_results in endpoint_results.items():
            if size_name == 'concurrent':
                print(f"   Concurrent (3 requests): {size_results['avg_server_time']:.3f}s avg")
            else:
                print(f"   {size_name.capitalize()} image: {size_results['avg_server_time']:.3f}s avg")
    
    # Performance targets
    print("\n🎯 PERFORMANCE TARGETS:")
    print("   ✅ Target: < 3 seconds per analysis")
    print("   ✅ Target: < 5 seconds for large images")
    print("   ✅ Target: Concurrent processing support")
    
    # Check if targets are met
    all_fast = True
    for endpoint_name, endpoint_results in results.items():
        for size_name, size_results in endpoint_results.items():
            if size_name != 'concurrent':
                avg_time = size_results['avg_server_time']
                target = 5.0 if size_name == 'large' else 3.0
                
                if avg_time > target:
                    print(f"   ⚠️  {endpoint_name} {size_name} exceeds target: {avg_time:.3f}s > {target}s")
                    all_fast = False
    
    if all_fast:
        print("   🎉 All performance targets met!")
    
    print("\n✅ Performance testing completed!")

if __name__ == "__main__":
    try:
        run_performance_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Performance testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
