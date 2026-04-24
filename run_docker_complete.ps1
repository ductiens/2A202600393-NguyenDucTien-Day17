# Complete Docker Setup Script for Multi-Memory Agent
# Run this script from PowerShell

Write-Host "🐳 Multi-Memory Agent Docker Setup" -ForegroundColor Green

# Step 1: Clean existing containers
Write-Host "Step 1: Cleaning existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null
docker rmi lab17-multi-memory-agent-app 2>$null
docker system prune -f

# Step 2: Create .env file
Write-Host "Step 2: Creating .env file..." -ForegroundColor Yellow
echo "OPENAI_API_KEY=sk-test-key-for-demo-purposes" > .env
REDIS_URL=redis://redis:6379
CHROMA_PERSIST_DIR=/app/chroma_db
EPISODIC_STORAGE_PATH=/app/data/episodic_memory.json
SHORT_TERM_BUFFER_SIZE=1000
MAX_CONVERSATION_HISTORY=50
SEMANTIC_SEARCH_RESULTS=5
LOG_LEVEL=INFO
LOG_FILE=/app/logs/agent.log
"@ | Out-File -FilePath ".env" -Encoding utf8

# Step 3: Build and start containers
Write-Host "Step 3: Building and starting containers..." -ForegroundColor Yellow
docker-compose up -d --build

# Step 4: Wait for containers to be ready
Write-Host "Step 4: Waiting for containers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 5: Check container status
Write-Host "Step 5: Checking container status..." -ForegroundColor Yellow
docker-compose ps

# Step 6: Test connections
Write-Host "Step 6: Testing connections..." -ForegroundColor Yellow
try {
    $redis_test = docker-compose exec -T app python -c "import redis; r=redis.Redis(host='redis', port=6379); print('Redis OK' if r.ping() else 'Redis Failed')"
    Write-Host $redis_test -ForegroundColor Green
} catch {
    Write-Host "Redis connection failed" -ForegroundColor Red
}

# Step 7: Run benchmark
Write-Host "Step 7: Running benchmark..." -ForegroundColor Yellow
docker-compose exec app python src/benchmark.py

# Step 8: Copy results
Write-Host "Step 8: Copying results..." -ForegroundColor Yellow
docker cp multi-memory-agent:/app/benchmark_results.json ./ 2>$null
docker cp multi-memory-agent:/app/data/ ./data/ 2>$null
docker cp multi-memory-agent:/app/logs/ ./logs/ 2>$null

# Step 9: Show results
Write-Host "Step 9: Benchmark Results:" -ForegroundColor Green
if (Test-Path "benchmark_results.json") {
    Get-Content "benchmark_results.json" | Select-String "success_rate"
} else {
    Write-Host "Benchmark results not found" -ForegroundColor Red
}

Write-Host "✅ Docker setup complete!" -ForegroundColor Green
Write-Host "To run interactive mode: docker-compose exec app python src/main.py" -ForegroundColor Cyan
