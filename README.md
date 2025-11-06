# Qwen2.5-VL-7B API Server

Docker 기반 Qwen2.5-VL-7B 비전-언어 모델 API 서버

## 시스템 요구사항

- **GPU**: NVIDIA RTX 3060 (12GB VRAM) 이상
- **CUDA**: 12.0+
- **Docker**: 20.10+
- **nvidia-docker**: 설치 필요

## 빠른 시작

### 1. 환경 설정

```bash
# API 키 생성
python3 scripts/generate_api_key.py

# .env 파일 수정
cp .env.example .env
# VLLM_API_KEY를 생성된 키로 변경
```

### 2. 서버 실행

```bash
# Docker 이미지 빌드 및 서버 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서버 상태 확인
./scripts/health_check.sh
```

### 3. API 테스트

```bash
# 환경변수 설정
export VLLM_API_KEY="your-api-key-here"

# 테스트 실행
pip install openai
python test_client.py
```

## API 사용법

### OpenAI 호환 API

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key-here",
    base_url="http://localhost:8000/v1",
)

# 텍스트 채팅
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-7B-Instruct",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
)
print(response.choices[0].message.content)
```

### 이미지 포함 요청

```python
import base64

# 이미지 인코딩
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-7B-Instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    },
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)
```

### cURL 예제

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key-here" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": "What is AI?"
      }
    ],
    "max_tokens": 100
  }'
```

## 서버 관리

### 서버 시작/중지

```bash
# 시작
docker-compose up -d

# 중지
docker-compose down

# 재시작
docker-compose restart

# 로그 보기
docker-compose logs -f
```

### 볼륨 관리

모델과 로그는 `volumes/` 디렉토리에 저장됩니다:

```
volumes/
├── models/     # HuggingFace 모델 캐시 (~15GB)
└── logs/       # API 서버 로그
```

**백업:**
```bash
tar -czf qwen-vllm-backup-$(date +%Y%m%d).tar.gz volumes/
```

### GPU 모니터링

```bash
# GPU 사용률 확인
watch -n 1 nvidia-smi

# 컨테이너 리소스 사용량
docker stats qwen-vllm-api
```

## 설정 변경

### docker-compose.yml

```yaml
command: >
  vllm serve Qwen/Qwen2.5-VL-7B-Instruct
  --max-model-len 32768          # 컨텍스트 길이 (메모리에 따라 조정)
  --gpu-memory-utilization 0.90  # GPU 메모리 사용률
  --limit-mm-per-prompt '{"image":2,"video":0}'  # 이미지 개수 제한
```

### 성능 튜닝

**메모리 부족 시:**
- `--max-model-len`을 16384 또는 8192로 줄이기
- `--gpu-memory-utilization`을 0.85로 낮추기

**처리량 향상:**
- 배치 크기 조정은 vLLM이 자동으로 처리
- 이미지 개수 제한으로 메모리 관리

## 문제 해결

### 서버가 시작되지 않을 때

```bash
# 로그 확인
docker-compose logs

# 컨테이너 상태 확인
docker ps -a

# GPU 접근 확인
docker run --rm --gpus device=0 nvidia/cuda:12.0-base nvidia-smi
```

### OOM (Out of Memory) 에러

1. `--max-model-len` 값을 줄이기 (32768 → 16384)
2. `--gpu-memory-utilization` 값을 낮추기 (0.90 → 0.85)
3. 다른 GPU 프로세스 종료 확인

### API 키 인증 실패

- `.env` 파일의 `VLLM_API_KEY`가 올바른지 확인
- 클라이언트에서 동일한 API 키 사용 확인
- Authorization 헤더 형식: `Bearer your-api-key`

## API 엔드포인트

| 엔드포인트 | 설명 |
|-----------|------|
| `/v1/chat/completions` | 채팅 완성 (텍스트 및 이미지) |
| `/v1/completions` | 텍스트 완성 |
| `/v1/models` | 사용 가능한 모델 목록 |
| `/health` | 서버 상태 확인 |

## 보안 주의사항

1. **API 키 보안**
   - `.env` 파일을 git에 커밋하지 마세요
   - 강력한 API 키 사용 (`scripts/generate_api_key.py`)
   
2. **네트워크 보안**
   - 프로덕션 환경에서는 방화벽 설정
   - 필요시 HTTPS 프록시 추가 (Nginx 등)

3. **접근 제어**
   - 신뢰할 수 있는 IP만 허용
   - Rate limiting 고려

## 참고 문서

- [vLLM Documentation](https://docs.vllm.ai/)
- [Qwen2.5-VL Model Card](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 라이선스

이 프로젝트는 Qwen2.5-VL 모델의 라이선스를 따릅니다.
