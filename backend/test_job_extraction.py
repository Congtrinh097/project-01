#!/usr/bin/env python3
"""
Simple test script for job extraction functionality
Run this to test the job extraction API endpoint
"""

import requests
import json
import sys

def test_job_extraction():
    """Test the job extraction endpoint"""
    
    # Test URLs (you can replace these with actual job posting URLs)
    test_urls = [
        "https://example.com/job1",
        "https://example.com/job2"
    ]
    
    # API endpoint
    url = "http://localhost:8000/extract-jobs"
    
    # Request payload
    payload = {
        "urls": test_urls
    }
    
    try:
        print("Testing job extraction endpoint...")
        print(f"URLs: {test_urls}")
        
        # Make the request
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result['message']}")
            print(f"Jobs extracted: {result['count']}")
            
            # Check if jobs were saved to database
            if 'saved_job_ids' in result and result['saved_job_ids']:
                print(f"✅ Jobs saved to database with IDs: {result['saved_job_ids']}")
                print("ℹ️  Note: Summary and embedding fields are stored but not returned in API responses")
            else:
                print("⚠️  No job IDs returned - jobs may not have been saved to database")
            
            print("\nExtracted data:")
            print(json.dumps(result['extracted_data'], indent=2))
            
            # Check if tags are included in the response
            if result['extracted_data']:
                first_job = result['extracted_data'][0]
                if 'tags' in first_job:
                    print(f"\n✅ Tags found: {first_job['tags']}")
                else:
                    print("\n⚠️  No tags field found in extracted data")
                
                # Validate required fields
                required_fields = ['position', 'company', 'job_link', 'location', 'working_type', 'skills', 'responsibilities', 'requirements', 'benefits', 'company_size', 'why_join', 'posted', 'summary', 'tags']
                missing_fields = [field for field in required_fields if field not in first_job]
                if missing_fields:
                    print(f"\n⚠️  Missing fields: {missing_fields}")
                else:
                    print("\n✅ All required fields present")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health_check():
    """Test the health check endpoint"""
    
    url = "http://localhost:8000/extract-jobs/health"
    
    try:
        print("\nTesting health check endpoint...")
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed!")
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            print(f"Model: {result.get('model', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_jobs_endpoints():
    """Test the individual jobs endpoints"""
    
    try:
        print("\nTesting individual jobs endpoints...")
        
        # Test list jobs
        print("\n1. Testing GET /jobs...")
        response = requests.get("http://localhost:8000/jobs?limit=5")
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Found {len(jobs)} jobs")
            if jobs:
                print(f"First job: {jobs[0]['position']} at {jobs[0]['company']}")
        else:
            print(f"❌ Error listing jobs: {response.status_code}")
        
        # Test search jobs
        print("\n2. Testing GET /jobs/search...")
        response = requests.get("http://localhost:8000/jobs/search?q=engineer&limit=3")
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Found {len(jobs)} jobs matching 'engineer'")
        else:
            print(f"❌ Error searching jobs: {response.status_code}")
        
        # Test get specific job (if any jobs exist)
        print("\n3. Testing GET /jobs/{id}...")
        response = requests.get("http://localhost:8000/jobs")
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                job_id = jobs[0]['id']
                response = requests.get(f"http://localhost:8000/jobs/{job_id}")
                if response.status_code == 200:
                    job = response.json()
                    print(f"✅ Retrieved job: {job['position']} at {job['company']}")
                    print(f"   Tags: {job.get('tags', [])}")
                else:
                    print(f"❌ Error getting job {job_id}: {response.status_code}")
            else:
                print("⚠️  No jobs available to test individual job retrieval")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Job Extraction API Test")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test job extraction
    test_job_extraction()
    
    # Test individual jobs endpoints
    test_jobs_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
