"""
Batch OCR for all images in a folder using Qwen2.5-VL API
With detailed logging and error handling
"""

import base64
import requests
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

# 설정
API_KEY = "vllm-hTmPPPUqHk81s95gimRWHpoEDKdUNnN4"
API_URL = "http://175.209.208.168:7777/v1/chat/completions"
IMAGE_FOLDER = r"C:\Users\User\Pictures\sh"
OUTPUT_FILE = "logs.txt"
ERROR_LOG_FILE = "error_logs.txt"

# 지원하는 이미지 확장자
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}


def log_message(message, level="INFO"):
    """콘솔과 에러 로그에 메시지 출력"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    
    if level in ["ERROR", "WARNING"]:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")


def test_api_connection():
    """API 서버 연결 테스트"""
    log_message("Testing API connection...")
    try:
        # 모델 목록 조회로 연결 테스트
        test_url = API_URL.replace("/v1/chat/completions", "/v1/models")
        response = requests.get(
            test_url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=10
        )
        
        if response.status_code == 200:
            log_message(f"✓ API server is reachable: {test_url}")
            log_message(f"  Response: {response.json()}")
            return True
        else:
            log_message(f"✗ API server returned status code: {response.status_code}", "ERROR")
            log_message(f"  Response: {response.text}", "ERROR")
            return False
            
    except requests.exceptions.ConnectionError as e:
        log_message(f"✗ Cannot connect to API server: {API_URL}", "ERROR")
        log_message(f"  Error: {str(e)}", "ERROR")
        log_message(f"  Check if the server is running and the IP/port are correct", "ERROR")
        return False
    except Exception as e:
        log_message(f"✗ Connection test failed: {str(e)}", "ERROR")
        log_message(f"  Traceback: {traceback.format_exc()}", "ERROR")
        return False


def encode_image(image_path):
    """이미지를 base64로 인코딩"""
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
            log_message(f"  Image size: {len(image_data)} bytes")
            return base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        log_message(f"  Failed to encode image: {str(e)}", "ERROR")
        raise


def ocr_image(image_path, image_name):
    """단일 이미지 OCR 처리"""
    log_message(f"Processing: {image_name}")
    
    try:
        # 이미지 파일 존재 확인
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        log_message(f"  Encoding image...")
        image_base64 = encode_image(image_path)
        log_message(f"  Base64 length: {len(image_base64)} characters")
        
        # API 요청 데이터
        request_data = {
            "model": "Qwen/Qwen2.5-VL-7B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "이 이미지의 모든 텍스트를 정확하게 추출해주세요. OCR 결과만 출력해주세요."
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        log_message(f"  Sending API request...")
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=request_data,
            timeout=120  # 2분 타임아웃
        )
        
        log_message(f"  API response status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            log_message(f"  {error_msg}", "ERROR")
            return f"ERROR: {error_msg}"
        
        result = response.json()
        log_message(f"  Response received: {len(str(result))} characters")
        
        # OCR 결과 추출
        if "choices" in result and len(result["choices"]) > 0:
            ocr_text = result["choices"][0]["message"]["content"]
            log_message(f"  ✓ Success - OCR text length: {len(ocr_text)} characters")
            return ocr_text
        else:
            error_msg = f"Unexpected response format: {result}"
            log_message(f"  {error_msg}", "ERROR")
            return f"ERROR: {error_msg}"
        
    except requests.exceptions.Timeout as e:
        error_msg = f"Request timeout after 120 seconds"
        log_message(f"  {error_msg}", "ERROR")
        return f"ERROR: {error_msg}"
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        log_message(f"  {error_msg}", "ERROR")
        log_message(f"  Traceback: {traceback.format_exc()}", "ERROR")
        return f"ERROR: {error_msg}"
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_message(f"  {error_msg}", "ERROR")
        log_message(f"  Traceback: {traceback.format_exc()}", "ERROR")
        return f"ERROR: {error_msg}"


def main():
    """메인 실행 함수"""
    log_message("="*80)
    log_message("Batch OCR Processing Started")
    log_message("="*80)
    log_message(f"Python version: {sys.version}")
    log_message(f"API URL: {API_URL}")
    log_message(f"API KEY: {API_KEY[:10]}... (hidden)")
    log_message(f"Image Folder: {IMAGE_FOLDER}")
    log_message(f"Output File: {OUTPUT_FILE}")
    log_message(f"Error Log File: {ERROR_LOG_FILE}")
    log_message("="*80)
    
    # 에러 로그 파일 초기화
    with open(ERROR_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Error Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    
    # API 연결 테스트
    if not test_api_connection():
        log_message("API connection test failed. Exiting.", "ERROR")
        input("Press Enter to exit...")
        return
    
    log_message("")
    
    # 이미지 폴더 확인
    image_folder = Path(IMAGE_FOLDER)
    
    if not image_folder.exists():
        log_message(f"Error: Folder does not exist: {IMAGE_FOLDER}", "ERROR")
        input("Press Enter to exit...")
        return
    
    log_message(f"Folder exists: {IMAGE_FOLDER}")
    
    # 이미지 파일 목록 가져오기
    try:
        all_files = list(image_folder.iterdir())
        log_message(f"Total files in folder: {len(all_files)}")
        
        image_files = [
            f for f in all_files
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]
        
        log_message(f"Image files found: {len(image_files)}")
        for img in image_files:
            log_message(f"  - {img.name}")
        
    except Exception as e:
        log_message(f"Error reading folder: {str(e)}", "ERROR")
        log_message(f"Traceback: {traceback.format_exc()}", "ERROR")
        input("Press Enter to exit...")
        return
    
    if not image_files:
        log_message(f"No image files found in {IMAGE_FOLDER}", "WARNING")
        input("Press Enter to exit...")
        return
    
    log_message("")
    log_message(f"Starting OCR processing for {len(image_files)} image(s)...")
    log_message("")
    
    # 로그 파일 열기
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as log_file:
            # 헤더 작성
            log_file.write("="*80 + "\n")
            log_file.write(f"Batch OCR Results\n")
            log_file.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Total Images: {len(image_files)}\n")
            log_file.write("="*80 + "\n\n")
            
            # 각 이미지 처리
            success_count = 0
            for idx, image_file in enumerate(image_files, 1):
                image_name = image_file.name
                
                log_message("")
                log_message(f"[{idx}/{len(image_files)}] Processing: {image_name}")
                
                # 로그 파일에 구분자 작성
                log_file.write("\n" + "-"*80 + "\n")
                log_file.write(f"[{idx}/{len(image_files)}] File: {image_name}\n")
                log_file.write(f"Path: {str(image_file)}\n")
                log_file.write(f"Size: {image_file.stat().st_size} bytes\n")
                log_file.write("-"*80 + "\n")
                
                # OCR 처리
                ocr_result = ocr_image(str(image_file), image_name)
                
                # 결과 저장
                log_file.write(ocr_result + "\n")
                log_file.flush()  # 즉시 파일에 쓰기
                
                if not ocr_result.startswith("ERROR"):
                    success_count += 1
            
            # 푸터 작성
            log_file.write("\n" + "="*80 + "\n")
            log_file.write(f"Processing Complete\n")
            log_file.write(f"Success: {success_count}/{len(image_files)}\n")
            log_file.write(f"Failed: {len(image_files) - success_count}/{len(image_files)}\n")
            log_file.write("="*80 + "\n")
        
        log_message("")
        log_message("="*80)
        log_message(f"✓ All processing complete!")
        log_message(f"✓ Results saved to: {OUTPUT_FILE}")
        log_message(f"✓ Error logs saved to: {ERROR_LOG_FILE}")
        log_message(f"✓ Success: {success_count}/{len(image_files)}")
        log_message(f"✓ Failed: {len(image_files) - success_count}/{len(image_files)}")
        log_message("="*80)
        
    except Exception as e:
        log_message(f"Error writing output file: {str(e)}", "ERROR")
        log_message(f"Traceback: {traceback.format_exc()}", "ERROR")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("\n\nProcess interrupted by user", "WARNING")
        input("Press Enter to exit...")
    except Exception as e:
        log_message(f"\n\nUnexpected error in main: {str(e)}", "ERROR")
        log_message(f"Traceback: {traceback.format_exc()}", "ERROR")
        input("Press Enter to exit...")