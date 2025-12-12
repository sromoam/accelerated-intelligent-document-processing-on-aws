#!/usr/bin/env python3
"""
Advanced benchmarking with concurrent load testing and accuracy scoring
"""

import argparse
import boto3
import json
import time
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.config import Config
import sagemaker
from pathlib import Path
import os
import glob
import random


class AdvancedBenchmark:
    def __init__(self, endpoint_name, region="us-west-2"):
        self.endpoint_name = endpoint_name
        config = Config(read_timeout=600, connect_timeout=60)
        self.runtime = boto3.client('sagemaker-runtime', region_name=region, config=config)
        self.s3 = boto3.client('s3', region_name=region)
        self.region = region
        
    def load_validation_data(self, data_dir, max_samples=None):
        """Load validation data with labels"""
        
        print(f"Loading validation data from {data_dir}...")
        
        # Load metadata for labels
        metadata_path = Path(data_dir) / "validation" / "metadata.json"
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        label_map = metadata.get('label_map', {})
        
        # Get all samples
        textract_files = glob.glob(f"{data_dir}/validation/textract/*.json")
        
        if max_samples:
            textract_files = textract_files[:max_samples]
        
        samples = []
        for textract_file in textract_files:
            base_name = Path(textract_file).stem
            image_file = f"{data_dir}/validation/images/{base_name}.png"
            label_file = f"{data_dir}/validation/labels/{base_name}.json"
            
            if os.path.exists(image_file) and os.path.exists(label_file):
                with open(label_file) as f:
                    label_data = json.load(f)
                    label_name = label_data.get('label', '').lower()
                
                samples.append({
                    'image_local': image_file,
                    'textract_local': textract_file,
                    'label': label_name
                })
        
        print(f"Loaded {len(samples)} samples with labels")
        return samples
    
    def upload_samples_to_s3(self, samples):
        """Upload samples to S3 for endpoint access"""
        print("\nUploading samples to S3...")
        
        boto_session = boto3.Session(region_name=self.region)
        sm_session = sagemaker.Session(boto_session=boto_session)
        bucket = sm_session.default_bucket()
        prefix = f"benchmark-advanced/{self.endpoint_name}"
        
        uploaded_samples = []
        for idx, sample in enumerate(samples):
            image_key = f"{prefix}/image_{idx}.png"
            textract_key = f"{prefix}/textract_{idx}.json"
            
            self.s3.upload_file(sample['image_local'], bucket, image_key)
            self.s3.upload_file(sample['textract_local'], bucket, textract_key)
            
            uploaded_samples.append({
                'image': f"s3://{bucket}/{image_key}",
                'textract': f"s3://{bucket}/{textract_key}",
                'label': sample['label']
            })
            
            if (idx + 1) % 50 == 0:
                print(f"  Uploaded {idx + 1}/{len(samples)}")
        
        print(f"✓ Uploaded {len(uploaded_samples)} samples")
        return uploaded_samples
    
    def invoke_single(self, sample):
        """Invoke endpoint for a single sample"""
        payload = {
            'input_image': sample['image'],
            'input_textract': sample['textract'],
            'prompt': "Document Classification on RVLCDIP.",
            'debug': False
        }
        
        start = time.time()
        try:
            response = self.runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            latency = time.time() - start
            result = json.loads(response['Body'].read().decode())
            prediction = result.get('prediction', '').strip().lower()
            
            return {
                'success': True,
                'latency': latency,
                'prediction': prediction,
                'label': sample['label'].lower(),
                'correct': prediction == sample['label'].lower(),
                'error': None
            }
        except Exception as e:
            latency = time.time() - start
            return {
                'success': False,
                'latency': latency,
                'prediction': None,
                'label': sample['label'].lower(),
                'correct': False,
                'error': str(e)
            }
    
    def run_concurrent_test(self, samples, concurrency=10):
        """Run concurrent load test"""
        print(f"\nRunning concurrent test with {concurrency} threads...")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.invoke_single, sample) for sample in samples]
            
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)
                
                # Print progress
                status = "✓" if result['success'] else "✗"
                if not result['success']:
                    print(f"  Request {i+1}: {status} Error: {result['error']}")
                elif (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    print(f"  Completed {i + 1}/{len(samples)} ({rate:.1f} req/s)")
        
        total_time = time.time() - start_time
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        print(f"\n✓ Completed: {successful}/{len(results)} successful")
        
        return results, total_time
    
    def calculate_accuracy(self, results):
        """Calculate accuracy metrics"""
        successful = [r for r in results if r['success']]
        
        if not successful:
            return None
        
        correct = sum(1 for r in successful if r['correct'])
        total = len(successful)
        accuracy = correct / total
        
        # Per-class accuracy
        by_label = {}
        for r in successful:
            label = r['label']
            if label not in by_label:
                by_label[label] = {'correct': 0, 'total': 0}
            by_label[label]['total'] += 1
            if r['correct']:
                by_label[label]['correct'] += 1
        
        per_class = {
            label: stats['correct'] / stats['total']
            for label, stats in by_label.items()
        }
        
        return {
            'overall_accuracy': accuracy,
            'correct': correct,
            'total': total,
            'per_class_accuracy': per_class
        }
    
    def generate_report(self, test_results, output_file=None):
        """Generate comprehensive report"""
        report = {
            'endpoint_name': self.endpoint_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        print("\n" + "="*70)
        print("ADVANCED BENCHMARK REPORT")
        print("="*70)
        print(f"\nEndpoint: {self.endpoint_name}")
        print(f"Timestamp: {report['timestamp']}")
        
        for test_name, data in test_results.items():
            results = data['results']
            total_time = data.get('total_time')
            concurrency = data.get('concurrency', 1)
            
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            if not successful:
                continue
            
            latencies = [r['latency'] for r in successful]
            
            # Calculate metrics
            metrics = {
                'concurrency': concurrency,
                'total_requests': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) * 100,
                'total_time': total_time,
                'throughput': len(successful) / total_time if total_time else None,
                'latency': {
                    'mean': np.mean(latencies),
                    'median': np.median(latencies),
                    'std': np.std(latencies),
                    'min': np.min(latencies),
                    'max': np.max(latencies),
                    'p50': np.percentile(latencies, 50),
                    'p95': np.percentile(latencies, 95),
                    'p99': np.percentile(latencies, 99)
                }
            }
            
            # Add accuracy if available
            accuracy = self.calculate_accuracy(results)
            if accuracy:
                metrics['accuracy'] = accuracy
            
            report['tests'][test_name] = metrics
            
            # Print section
            print(f"\n--- {test_name.upper()} ---")
            print(f"Concurrency: {concurrency}")
            print(f"Total requests: {metrics['total_requests']}")
            print(f"Successful: {metrics['successful']}")
            print(f"Failed: {metrics['failed']}")
            print(f"Success rate: {metrics['success_rate']:.1f}%")
            
            if total_time:
                print(f"Total time: {total_time:.2f}s")
                print(f"Throughput: {metrics['throughput']:.2f} req/s")
            
            print(f"\nLatency:")
            print(f"  Mean: {metrics['latency']['mean']:.3f}s")
            print(f"  Median: {metrics['latency']['median']:.3f}s")
            print(f"  P95: {metrics['latency']['p95']:.3f}s")
            print(f"  Min/Max: {metrics['latency']['min']:.3f}s / {metrics['latency']['max']:.3f}s")
            
            if accuracy:
                print(f"\nAccuracy:")
                print(f"  Overall: {accuracy['overall_accuracy']*100:.1f}% ({accuracy['correct']}/{accuracy['total']})")
                print(f"  Per-class accuracy: {len(accuracy['per_class_accuracy'])} classes")
        
        print("\n" + "="*70)
        
        # Save report
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Advanced inference benchmarking with concurrency and accuracy"
    )
    parser.add_argument("--endpoint-name", required=True)
    parser.add_argument("--data-dir", default="data/udop_rvlcdip")
    parser.add_argument("--region", default="us-west-2")
    parser.add_argument("--output", default="advanced_benchmark_report.json")
    
    # Test modes
    parser.add_argument("--sequential", action="store_true", help="Run sequential test")
    parser.add_argument("--concurrent", action="store_true", help="Run concurrent tests")
    parser.add_argument("--throughput", action="store_true", help="Run throughput test (1000 docs)")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Test parameters
    parser.add_argument("--num-samples", type=int, default=25, help="Samples for sequential test")
    parser.add_argument("--concurrency-levels", type=int, nargs='+', default=[1, 5, 10, 20], 
                       help="Concurrency levels to test")
    parser.add_argument("--throughput-samples", type=int, default=1000, help="Samples for throughput test")
    parser.add_argument("--throughput-concurrency", type=int, default=10, help="Concurrency for throughput test")
    
    args = parser.parse_args()
    
    # Default to all tests if none specified
    if not (args.sequential or args.concurrent or args.throughput or args.all):
        args.all = True
    
    if args.all:
        args.sequential = args.concurrent = args.throughput = True
    
    print("="*70)
    print("ADVANCED INFERENCE BENCHMARK")
    print("="*70)
    print(f"Endpoint: {args.endpoint_name}")
    print(f"Region: {args.region}")
    
    benchmark = AdvancedBenchmark(args.endpoint_name, args.region)
    
    # Load validation data
    max_samples = max(args.num_samples, args.throughput_samples) if args.throughput else args.num_samples
    samples = benchmark.load_validation_data(args.data_dir, max_samples)
    
    if not samples:
        print("No samples found!")
        return 1
    
    # Upload to S3
    samples = benchmark.upload_samples_to_s3(samples)
    
    test_results = {}
    
    # Sequential test
    if args.sequential:
        print(f"\n{'='*70}")
        print("SEQUENTIAL TEST")
        print(f"{'='*70}")
        test_samples = samples[:args.num_samples]
        results, total_time = benchmark.run_concurrent_test(test_samples, concurrency=1)
        test_results['sequential'] = {
            'results': results,
            'total_time': total_time,
            'concurrency': 1
        }
    
    # Concurrent tests
    if args.concurrent:
        for concurrency in args.concurrency_levels:
            if concurrency == 1:
                continue  # Already done in sequential
            
            print(f"\n{'='*70}")
            print(f"CONCURRENT TEST (concurrency={concurrency})")
            print(f"{'='*70}")
            
            test_samples = samples[:args.num_samples]
            results, total_time = benchmark.run_concurrent_test(test_samples, concurrency)
            test_results[f'concurrent_{concurrency}'] = {
                'results': results,
                'total_time': total_time,
                'concurrency': concurrency
            }
    
    # Throughput test
    if args.throughput:
        print(f"\n{'='*70}")
        print(f"THROUGHPUT TEST ({args.throughput_samples} documents)")
        print(f"{'='*70}")
        
        # Randomly sample with replacement
        throughput_samples = random.choices(samples, k=args.throughput_samples)
        
        results, total_time = benchmark.run_concurrent_test(
            throughput_samples,
            concurrency=args.throughput_concurrency
        )
        
        test_results['throughput'] = {
            'results': results,
            'total_time': total_time,
            'concurrency': args.throughput_concurrency
        }
        
        print(f"\n✓ Processed {len(results)} documents in {total_time:.2f}s")
        print(f"  Throughput: {len(results)/total_time:.2f} docs/second")
    
    # Generate report
    report = benchmark.generate_report(test_results, args.output)
    
    return 0


if __name__ == "__main__":
    import sys
    import os
    sys.exit(main())
