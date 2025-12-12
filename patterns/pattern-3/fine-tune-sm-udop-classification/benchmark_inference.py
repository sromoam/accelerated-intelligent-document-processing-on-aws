#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Benchmark SageMaker inference endpoint latency for UDOP document classification.
Tests with real documents and generates a performance report.
"""

import argparse
import boto3
import json
import time
import numpy as np
from datetime import datetime
import os
import sagemaker


class InferenceBenchmark:
    def __init__(self, endpoint_name, region="us-east-1"):
        self.endpoint_name = endpoint_name
        # Increase timeout for first request (model download)
        from botocore.config import Config
        config = Config(
            read_timeout=600,  # 10 minutes for first request
            connect_timeout=60
        )
        self.runtime = boto3.client('sagemaker-runtime', region_name=region, config=config)
        self.s3 = boto3.client('s3', region_name=region)
        
    def invoke_endpoint(self, payload, timeout=60):
        """Invoke endpoint and measure latency"""
        start_time = time.time()
        
        # Use correct prompt for trained model
        if payload.get('prompt') is None:
            payload['prompt'] = "Document Classification on RVLCDIP."
        
        try:
            response = self.runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            
            latency = time.time() - start_time
            result = json.loads(response['Body'].read().decode())
            
            return {
                'success': True,
                'latency': latency,
                'prediction': result.get('prediction'),
                'error': None
            }
        except Exception as e:
            latency = time.time() - start_time
            return {
                'success': False,
                'latency': latency,
                'prediction': None,
                'error': str(e)
            }
    
    def get_test_samples_from_s3(self, data_bucket, data_prefix, num_samples=10):
        """Get test samples from S3"""
        print(f"Loading test samples from s3://{data_bucket}/{data_prefix}/...")
        
        # Try test folder first, then validation
        for folder in ['test', 'validation']:
            response = self.s3.list_objects_v2(
                Bucket=data_bucket,
                Prefix=f"{data_prefix}/{folder}/",
                MaxKeys=num_samples * 2
            )
            
            samples = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith('.json') and 'textract' in key:
                    base_name = key.replace('_textract.json', '')
                    image_key = base_name + '.png'
                    
                    try:
                        self.s3.head_object(Bucket=data_bucket, Key=image_key)
                        samples.append({
                            'image': f"s3://{data_bucket}/{image_key}",
                            'textract': f"s3://{data_bucket}/{key}"
                        })
                        
                        if len(samples) >= num_samples:
                            break
                    except:
                        continue
            
            if samples:
                print(f"Found {len(samples)} samples in {folder} folder")
                return samples
        
        print(f"Found 0 test samples")
        return []
    
    def get_test_samples_from_local(self, data_dir, num_samples=10):
        """Get test samples from local directory"""
        import glob
        print(f"Loading test samples from local directory: {data_dir}")
        
        samples = []
        # Try validation folder first, then training
        for folder in ['validation', 'training']:
            textract_pattern = os.path.join(data_dir, folder, 'textract', '*.json')
            textract_files = glob.glob(textract_pattern)
            
            for textract_file in textract_files[:num_samples]:
                # Get corresponding image
                base_name = os.path.basename(textract_file).replace('.json', '')
                image_file = os.path.join(data_dir, folder, 'images', f'{base_name}.png')
                
                if os.path.exists(image_file):
                    samples.append({
                        'image_local': image_file,
                        'textract_local': textract_file
                    })
                    
                    if len(samples) >= num_samples:
                        break
            
            if samples:
                print(f"Found {len(samples)} samples in {folder} folder")
                return samples
        
        print(f"Found 0 test samples")
        return []
    
    def run_warmup(self, test_sample, num_warmup=3):
        """Run warmup requests"""
        print(f"\nRunning {num_warmup} warmup requests...")
        warmup_latencies = []
        
        for i in range(num_warmup):
            payload = {
                'input_image': test_sample['image'],
                'input_textract': test_sample['textract'],
                'prompt': None,
                'debug': False
            }
            
            result = self.invoke_endpoint(payload)
            warmup_latencies.append(result['latency'])
            
            status = "✓" if result['success'] else "✗"
            print(f"  Warmup {i+1}: {result['latency']:.2f}s {status}")
            
            if not result['success']:
                print(f"    Error: {result['error']}")
        
        return warmup_latencies
    
    def run_benchmark(self, test_samples, iterations_per_sample=5):
        """Run benchmark across multiple samples"""
        print(f"\nRunning benchmark with {len(test_samples)} samples, {iterations_per_sample} iterations each...")
        
        all_results = []
        
        for sample_idx, sample in enumerate(test_samples):
            print(f"\nSample {sample_idx + 1}/{len(test_samples)}")
            
            for iter_idx in range(iterations_per_sample):
                payload = {
                    'input_image': sample['image'],
                    'input_textract': sample['textract'],
                    'prompt': None,
                    'debug': False
                }
                
                result = self.invoke_endpoint(payload)
                result['sample_idx'] = sample_idx
                result['iteration'] = iter_idx
                all_results.append(result)
                
                status = "✓" if result['success'] else "✗"
                print(f"  Iteration {iter_idx + 1}: {result['latency']:.2f}s {status}")
                
                if not result['success']:
                    print(f"    Error: {result['error']}")
                
                # Small delay between requests
                time.sleep(0.5)
        
        return all_results
    
    def generate_report(self, warmup_results, benchmark_results, output_file=None):
        """Generate performance report"""
        successful_results = [r for r in benchmark_results if r['success']]
        failed_results = [r for r in benchmark_results if not r['success']]
        
        if not successful_results:
            print("\n❌ All requests failed!")
            return
        
        latencies = [r['latency'] for r in successful_results]
        
        report = {
            'endpoint_name': self.endpoint_name,
            'timestamp': datetime.now().isoformat(),
            'warmup': {
                'num_requests': len(warmup_results),
                'latencies': warmup_results,
                'avg_latency': np.mean(warmup_results),
                'max_latency': np.max(warmup_results)
            },
            'benchmark': {
                'total_requests': len(benchmark_results),
                'successful_requests': len(successful_results),
                'failed_requests': len(failed_results),
                'success_rate': len(successful_results) / len(benchmark_results) * 100
            },
            'latency_stats': {
                'mean': np.mean(latencies),
                'median': np.median(latencies),
                'std': np.std(latencies),
                'min': np.min(latencies),
                'max': np.max(latencies),
                'p50': np.percentile(latencies, 50),
                'p95': np.percentile(latencies, 95),
                'p99': np.percentile(latencies, 99)
            },
            'throughput': {
                'requests_per_second': 1.0 / np.mean(latencies)
            }
        }
        
        # Print report
        print("\n" + "="*70)
        print("INFERENCE BENCHMARK REPORT")
        print("="*70)
        print(f"\nEndpoint: {self.endpoint_name}")
        print(f"Timestamp: {report['timestamp']}")
        
        print(f"\n--- Warmup Phase ---")
        print(f"Requests: {report['warmup']['num_requests']}")
        print(f"Average latency: {report['warmup']['avg_latency']:.3f}s")
        print(f"Max latency: {report['warmup']['max_latency']:.3f}s")
        
        print(f"\n--- Benchmark Results ---")
        print(f"Total requests: {report['benchmark']['total_requests']}")
        print(f"Successful: {report['benchmark']['successful_requests']}")
        print(f"Failed: {report['benchmark']['failed_requests']}")
        print(f"Success rate: {report['benchmark']['success_rate']:.1f}%")
        
        print(f"\n--- Latency Statistics (seconds) ---")
        print(f"Mean:   {report['latency_stats']['mean']:.3f}s")
        print(f"Median: {report['latency_stats']['median']:.3f}s")
        print(f"Std:    {report['latency_stats']['std']:.3f}s")
        print(f"Min:    {report['latency_stats']['min']:.3f}s")
        print(f"Max:    {report['latency_stats']['max']:.3f}s")
        print(f"P50:    {report['latency_stats']['p50']:.3f}s")
        print(f"P95:    {report['latency_stats']['p95']:.3f}s")
        print(f"P99:    {report['latency_stats']['p99']:.3f}s")
        
        print(f"\n--- Throughput ---")
        print(f"Requests/second: {report['throughput']['requests_per_second']:.2f}")
        
        print("\n" + "="*70)
        
        # Save to file
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark UDOP inference endpoint"
    )
    parser.add_argument(
        "--endpoint-name",
        type=str,
        required=True,
        help="SageMaker endpoint name"
    )
    parser.add_argument(
        "--data-bucket",
        type=str,
        default="idp-evaluation-datasets",
        help="S3 bucket with test data (ignored if --local-data is used)"
    )
    parser.add_argument(
        "--data-prefix",
        type=str,
        default="datasets/udop-rvl_cdip",
        help="S3 prefix for test data (ignored if --local-data is used)"
    )
    parser.add_argument(
        "--local-data",
        type=str,
        default=None,
        help="Local data directory (e.g., data/udop_rvlcdip)"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=5,
        help="Number of test samples to use"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Iterations per sample"
    )
    parser.add_argument(
        "--num-warmup",
        type=int,
        default=3,
        help="Number of warmup requests"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for report (JSON)"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region"
    )
    
    args = parser.parse_args()
    
    # Set default output filename if not provided
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmark_report_{args.endpoint_name}_{timestamp}.json"
    
    print("="*70)
    print("UDOP INFERENCE BENCHMARK")
    print("="*70)
    print(f"Endpoint: {args.endpoint_name}")
    print(f"Region: {args.region}")
    print(f"Test samples: {args.num_samples}")
    print(f"Iterations per sample: {args.iterations}")
    print(f"Warmup requests: {args.num_warmup}")
    
    # Initialize benchmark
    benchmark = InferenceBenchmark(args.endpoint_name, args.region)
    
    # Get test samples
    if args.local_data:
        test_samples = benchmark.get_test_samples_from_local(
            args.local_data,
            args.num_samples
        )
        # Upload samples to S3 for endpoint access
        if test_samples:
            print("\nUploading test samples to S3 for endpoint access...")
            uploaded_samples = []
            
            # Get SageMaker session with region
            boto_session = boto3.Session(region_name=args.region)
            sm_session = sagemaker.Session(boto_session=boto_session)
            bucket = sm_session.default_bucket()
            prefix = f"benchmark-temp/{args.endpoint_name}"
            
            for idx, sample in enumerate(test_samples):
                
                # Upload image
                image_key = f"{prefix}/image_{idx}.png"
                benchmark.s3.upload_file(sample['image_local'], bucket, image_key)
                
                # Upload textract
                textract_key = f"{prefix}/textract_{idx}.json"
                benchmark.s3.upload_file(sample['textract_local'], bucket, textract_key)
                
                uploaded_samples.append({
                    'image': f"s3://{bucket}/{image_key}",
                    'textract': f"s3://{bucket}/{textract_key}"
                })
                print(f"  Uploaded sample {idx+1}/{len(test_samples)}")
            
            test_samples = uploaded_samples
    else:
        test_samples = benchmark.get_test_samples_from_s3(
            args.data_bucket,
            args.data_prefix,
            args.num_samples
        )
    
    if not test_samples:
        print("❌ No test samples found!")
        return
    
    # Run warmup
    warmup_latencies = benchmark.run_warmup(test_samples[0], args.num_warmup)
    
    # Run benchmark
    results = benchmark.run_benchmark(test_samples, args.iterations)
    
    # Generate report
    report = benchmark.generate_report(warmup_latencies, results, args.output)


if __name__ == "__main__":
    main()
