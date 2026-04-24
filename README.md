# Multi-Memory Agent with LangGraph

🎯 **Mục tiêu**: Xây dựng một Multi-Memory Agent (Tác tử AI có đa bộ nhớ) bằng framework LangGraph với 4 loại bộ nhớ khác nhau.

## 📋 Tổng quan

Dự án này triển khai một tác tử AI thông minh với hệ thống bộ nhớ phân cấp, bao gồm:
- **Short-term Memory**: Bộ nhớ ngắn hạn với quản lý token tự động
- **Long-term Memory**: Bộ nhớ dài hạn (Redis) cho sở thích người dùng
- **Episodic Memory**: Lưu trữ trải nghiệm qua JSON
- **Semantic Memory**: Truy xuất tri thức với ChromaDB (RAG)

## 🛠️ Kiến trúc

```
src/
├── memory/                  # 4 loại hệ thống lưu trữ
│   ├── short_term.py        # Xử lý buffer & token management
│   ├── long_term.py         # Redis cho user preferences
│   ├── episodic.py          # JSON cho past trajectories
│   └── semantic.py          # Chroma cho RAG / Domain knowledge
├── graph/                   # Luồng hoạt động LangGraph
│   ├── state.py             # TypedDict cho MemoryState
│   ├── nodes.py             # load_memory, agent_chat, save_memory
│   └── builder.py           # Compile đồ thị LangGraph
├── config.py                # Biến môi trường và cấu hình
├── main.py                  # Entry point chạy Agent
└── benchmark.py             # Script benchmark 10 test case
```

## 🚀 Cài đặt và Chạy

### 1. Clone repository
```bash
git clone <your-repo-url>
cd Lab17-Multi-Memory-Agent
```

### 2. Tạo môi trường ảo
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
```bash
# Copy file .env.example sang .env
cp .env.example .env

# Edit .env và thêm API keys của bạn
nano .env  # hoặc dùng editor khác
```

### 5. Khởi động services (bắt buộc)
```bash
# Khởi động Redis
docker run -d -p 6379:6379 redis:latest

# Hoặc cài Redis local
# Windows: dùng WSL hoặc Redis for Windows
# Linux: sudo apt-get install redis-server
# Mac: brew install redis
```

### 6. Tạo thư mục cần thiết
```bash
mkdir -p data logs
```

## 🏃‍♂️ Chạy dự án

### Chế độ tương tác (Interactive Mode)
```bash
cd src
python main.py
```

### Chạy Benchmark
```bash
cd src
python benchmark.py
```

## 📊 Benchmark và Đánh giá

### Chạy 10 test case tự động
```bash
python src/benchmark.py
```

Kết quả sẽ được lưu trong `benchmark_results.json` với các metrics:
- **Response Relevance**: Độ liên quan của câu trả lời
- **Context Utilization**: Mức độ tận dụng ngữ cảnh
- **Token Efficiency**: Hiệu suất sử dụng token
- **Memory Hit Rate**: Tỷ lệ sử dụng bộ nhớ

### Visualize kết quả
```python
import pandas as pd
import matplotlib.pyplot as plt

# Đọc kết quả benchmark
results = pd.read_json('benchmark_results.json')
# Visualize...
```

## 🔧 Cấu hình Token Management

### Token Budget Configuration
- **MAX_TOKENS**: 4000 tokens cho toàn bộ prompt
- **Priority Order**: Short-term > Long-term > Episodic > Semantic
- **Auto-trimming**: Tự động cắt khi vượt giới hạn

### Memory Limits
- **Short-term**: 1000 tokens
- **Long-term**: Unlimited (Redis)
- **Episodic**: JSON file storage
- **Semantic**: ChromaDB vector storage

## 🧪 Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

## 📝 4 Bước thực hành

### ✅ Bước 1: Implement 4 memory backends
- [x] ConversationBufferMemory (short-term)
- [x] Redis (long-term preferences)
- [x] JSON (episodic trajectories)
- [x] ChromaDB (semantic RAG)

### ✅ Bước 2: Build memory router
- [x] Smart routing based on user intent
- [x] Priority-based memory selection
- [x] Context-aware retrieval

### ✅ Bước 3: Context window management
- [x] Token counting với tiktoken (cl100k_base)
- [x] Priority-based eviction (4-level hierarchy)
- [x] Auto-trimming mechanism

### ✅ Bước 4: Benchmark
- [x] 10 multi-turn conversations
- [x] Performance metrics collection
- [x] Memory hit rate analysis

## 🐛 Troubleshooting

### Common Issues

1. **Redis connection failed**
   ```bash
   # Kiểm tra Redis đang chạy
   redis-cli ping
   # Expected response: PONG
   ```

2. **OpenAI API key error**
   ```bash
   # Kiểm tra .env file
   cat .env | grep OPENAI_API_KEY
   ```

3. **ChromaDB initialization error**
   ```bash
   # Xóa và tạo lại ChromaDB
   rm -rf chroma_db
   ```

4. **Token limit exceeded**
   - Kiểm tra `MAX_TOKENS` trong `src/graph/nodes.py`
   - Monitor token usage trong benchmark results

## 📈 Performance Metrics

### Expected Performance
- **Response Time**: < 2s cho single query
- **Token Efficiency**: > 80% utilization
- **Memory Hit Rate**: > 70% for relevant queries
- **Context Relevance**: > 85% accuracy

### Monitoring
```bash
# Xem logs
tail -f logs/agent.log

# Monitor token usage
python -c "from src.memory.short_term import ShortTermMemory; print(ShortTermMemory().get_buffer_info())"
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - xem file `LICENSE` để biết chi tiết.

## 📞 Support

- Issues: GitHub Issues
- Documentation: `docs/` folder
- Examples: `examples/` folder

---

**Note**: Đảm bảo tất cả services (Redis, ChromaDB) đang chạy trước khi khởi động agent.
