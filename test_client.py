#!/usr/bin/env python3
"""
Simple test client for the Bulk Document Conversion Service
"""
import requests
import time
import zipfile
import os
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

def create_test_zip():
    """Create a test ZIP file with sample DOCX files"""
    # This is a placeholder - in a real test, you would create actual DOCX files
    # For now, we'll create a simple text file to demonstrate the API
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test file (in real scenario, this would be a DOCX)
    test_file = test_dir / "test_document.txt"
    test_file.write_text("This is a test document for conversion.")
    
    # Create ZIP file
    zip_path = "test_documents.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(test_file, "test_document.txt")
    
    return zip_path

def test_api():
    """Test the API endpoints"""
    print("Testing Bulk Document Conversion Service API")
    print("=" * 50)
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"   Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Health check failed: {e}")
        return
    
    # Create test ZIP file
    print("\n2. Creating test ZIP file...")
    zip_path = create_test_zip()
    print(f"   Created: {zip_path}")
    
    # Submit job
    print("\n3. Submitting conversion job...")
    try:
        with open(zip_path, 'rb') as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/jobs",
                files={'file': f}
            )
        
        if response.status_code == 202:
            job_data = response.json()
            job_id = job_data['job_id']
            print(f"   Job submitted successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   File count: {job_data['file_count']}")
        else:
            print(f"   Job submission failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   Job submission error: {e}")
        return
    
    # Monitor job status
    print("\n4. Monitoring job status...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE_URL}/api/v1/jobs/{job_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   Attempt {attempt + 1}: Status = {status_data['status']}")
                
                if status_data['status'] in ['COMPLETED', 'FAILED']:
                    print(f"   Final status: {status_data['status']}")
                    
                    # Show file details
                    print("   File details:")
                    for file_info in status_data['files']:
                        print(f"     - {file_info['filename']}: {file_info['status']}")
                        if file_info.get('error_message'):
                            print(f"       Error: {file_info['error_message']}")
                    
                    # Try to download if completed
                    if status_data['status'] == 'COMPLETED' and status_data.get('download_url'):
                        print("\n5. Downloading results...")
                        download_response = requests.get(f"{API_BASE_URL}/api/v1/jobs/{job_id}/download")
                        if download_response.status_code == 200:
                            output_file = f"converted_files_{job_id}.zip"
                            with open(output_file, 'wb') as f:
                                f.write(download_response.content)
                            print(f"   Downloaded: {output_file}")
                        else:
                            print(f"   Download failed: {download_response.status_code}")
                    
                    break
                else:
                    time.sleep(2)
                    attempt += 1
            else:
                print(f"   Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"   Status check error: {e}")
            break
    
    if attempt >= max_attempts:
        print("   Timeout waiting for job completion")
    
    # Cleanup
    print("\n6. Cleaning up...")
    try:
        os.remove(zip_path)
        print(f"   Removed: {zip_path}")
    except:
        pass
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_api()
