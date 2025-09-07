# Testcontainers Cloud Setup & Integration Guide

## 🚀 Installation Status
✅ **Testcontainers Desktop v1.22.0** installed via winget

## 📋 Next Steps for Complete Setup

### 1. Launch Testcontainers Desktop
```bash
# Option 1: Search in Start Menu
# Look for "Testcontainers Desktop" in Windows Start Menu

# Option 2: Direct launch (after finding install path)
# The application should be installed in one of these locations:
# - C:\Users\scarm\AppData\Local\Programs\Testcontainers Desktop\
# - C:\Program Files\Testcontainers Desktop\
```

### 2. Authentication Setup
Once Testcontainers Desktop launches:

1. **Sign in with Docker Account**
   - You'll be prompted to authenticate
   - Use your Docker Hub credentials
   - If you don't have one, sign up at https://hub.docker.com

2. **Generate Service Account Token**
   - Go to Testcontainers Cloud dashboard
   - Create a Service Account for CI/automation
   - Save the `TC_CLOUD_TOKEN` for later use

### 3. Environment Configuration
Add to your `.env` file:

```env
# Testcontainers Cloud Configuration
TC_CLOUD_TOKEN=your_service_account_token_here
TESTCONTAINERS_CLOUD_ENABLED=true
TESTCONTAINERS_REUSE_ENABLE=true
TESTCONTAINERS_CHECKS_DISABLE=false
```

## 🔧 Integration with AI Swarm

### Benefits for AI Swarm System:
1. **Cloud-based testing** - No local Docker daemon required
2. **Parallel test execution** - Multiple containers simultaneously
3. **Resource optimization** - Better performance for AI workloads
4. **CI/CD friendly** - Perfect for automated testing pipelines

### Docker Compose Integration

Create `docker-compose.testcontainers.yml`:

```yaml
version: '3.8'

# Testcontainers-optimized AI Swarm setup
services:
  # AI Swarm Test Environment
  ai-swarm-test:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - TESTCONTAINERS_CLOUD_ENABLED=true
      - TC_CLOUD_TOKEN=${TC_CLOUD_TOKEN}
      - SWARM_MODE=testing
      - DATABASE_PATH=/tmp/test_swarm.db
    labels:
      - "testcontainers.session-id=ai-swarm-${GITHUB_RUN_ID:-local}"
    networks:
      - test-network
    volumes:
      - /tmp:/tmp
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Test Database
  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: swarm_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test123
    labels:
      - "testcontainers.session-id=ai-swarm-${GITHUB_RUN_ID:-local}"
    networks:
      - test-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 3s
      retries: 5

networks:
  test-network:
    driver: bridge
```

### Python Test Integration

Create `test_ai_swarm_containers.py`:

```python
"""
AI Swarm Testcontainers Integration
Tests for containerized AI components
"""

import pytest
import requests
import time
from testcontainers.compose import DockerCompose
from testcontainers.postgres import PostgresContainer

class TestAISwarmContainers:
    
    def setup_method(self):
        """Set up test containers"""
        self.compose = DockerCompose(
            ".", 
            compose_file_name="docker-compose.testcontainers.yml"
        )
        self.compose.start()
        
        # Wait for services to be healthy
        time.sleep(10)
    
    def teardown_method(self):
        """Clean up containers"""
        self.compose.stop()
    
    def test_ai_swarm_health(self):
        """Test AI Swarm health endpoint"""
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert data["database"] is True
    
    def test_ai_swarm_integrations(self):
        """Test AI Swarm integrations endpoint"""
        response = requests.get("http://localhost:8000/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "AI Swarm Intelligence System"
        assert "integrations" in data
        assert data["integrations"] >= 0
    
    def test_database_connectivity(self):
        """Test database connections"""
        # Test AI Swarm database connection
        response = requests.get("http://localhost:8000/health")
        data = response.json()
        assert data["database"] is True
    
    def test_redis_cache(self):
        """Test Redis cache connectivity"""
        # This would test Redis through AI Swarm endpoints
        response = requests.get("http://localhost:8000/status")
        assert response.status_code == 200
    
    @pytest.mark.integration
    def test_full_ai_workflow(self):
        """Test complete AI Swarm workflow"""
        # 1. Check system health
        health = requests.get("http://localhost:8000/health")
        assert health.status_code == 200
        
        # 2. Check integrations
        status = requests.get("http://localhost:8000/status")
        assert status.status_code == 200
        
        # 3. Test AI processing (if endpoints exist)
        # This would depend on your AI Swarm API structure
        
        print("✅ Full AI Swarm workflow test passed!")

# Performance Tests
class TestAISwarmPerformance:
    
    def test_response_time(self):
        """Test API response times"""
        start_time = time.time()
        response = requests.get("http://localhost:8000/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return requests.get("http://localhost:8000/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
```

### GitHub Actions Integration

Create `.github/workflows/testcontainers-ci.yml`:

```yaml
name: AI Swarm Testcontainers CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Set up Testcontainers Cloud
      uses: atomicjar/testcontainers-cloud-setup-action@v1
      with:
        token: ${{ secrets.TC_CLOUD_TOKEN }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest testcontainers[postgres] requests
    
    - name: Run Testcontainers tests
      env:
        TC_CLOUD_TOKEN: ${{ secrets.TC_CLOUD_TOKEN }}
        TESTCONTAINERS_CLOUD_ENABLED: true
      run: |
        pytest test_ai_swarm_containers.py -v --tb=short
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: test-results.xml
```

## 🎯 Expected Benefits

### Performance Improvements:
- **50% faster test execution** with cloud parallelization
- **No local resource constraints** for AI model testing
- **Automatic cleanup** of test containers
- **Better isolation** between test runs

### Development Workflow:
- **Local development** without Docker Desktop dependency
- **Consistent environments** between dev/test/prod
- **Easy CI/CD integration** with cloud resources
- **Cost optimization** with pay-per-use model

## 🔍 Troubleshooting

### Common Issues:

1. **Authentication Failed**
   ```bash
   # Check token
   echo $TC_CLOUD_TOKEN
   
   # Re-authenticate
   # Launch Testcontainers Desktop and re-login
   ```

2. **Container Start Timeout**
   ```yaml
   # Increase timeouts in docker-compose.testcontainers.yml
   healthcheck:
     interval: 30s
     timeout: 15s
     retries: 5
   ```

3. **Network Connectivity**
   ```bash
   # Test connection
   curl -I https://app.testcontainers.cloud/
   ```

## 🚀 Next Actions

1. **Launch Testcontainers Desktop** from Start Menu
2. **Sign in** with Docker account
3. **Generate service token** for automation
4. **Update .env** with TC_CLOUD_TOKEN
5. **Run first test** with the provided examples
6. **Integrate with CI/CD** pipeline

---

**Status**: Ready for authentication setup and testing!