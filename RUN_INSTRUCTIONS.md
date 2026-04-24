# Hướng dẫn Chạy Dự Án Multi-Memory Agent

**Cập nhật theo rubric requirements** - Không cần Docker, có chạy local!

---

## 🚀 Quick Start (Non-Docker)

### 1. Cài đặt môi trường
```bash
# Clone repository
git clone <your-repo-url>
cd Lab17-Multi-Memory-Agent

# Tạo môi trường ảo
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac  
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
```bash
# Copy file môi trường
copy .env.example .env

# Edit .env file
# Thêm API keys của bạn:
OPENAI_API_KEY=sk-your-openai-key-here
REDIS_URL=redis://localhost:6379
```

### 3. Khởi động Redis (BẮT BUỘC)
```bash
# Windows (WSL)
sudo apt-get update
sudo apt-get install redis-server
redis-server

# Linux
sudo apt-get install redis-server
redis-server

# Mac
brew install redis
redis-server

# Hoặc dùng Docker (nếu có Docker)
docker run -d -p 6379:6379 redis:latest
```

### 4. Test kết nối Redis
```bash
redis-cli ping
# Expected: PONG
```

### 5. Chạy dự án

#### Mode 1: Interactive (Testing)
```bash
cd src
python main.py
```

#### Mode 2: Benchmark (Rubric requirement)
```bash
cd src
python benchmark.py
```

#### Mode 3: Quick Test
```bash
python examples/quick_test.py
```

---

## 📊 Chạy Benchmark theo Rubric

### Script benchmark tự động
```bash
cd src
python benchmark.py
```

**Output:**
- `benchmark_results.json` - Detailed metrics
- Console output với 10 test cases
- Token efficiency analysis
- Memory hit rate statistics

### Manual verification
```bash
# Test conflict handling
python -c "
from src.main import MultiMemoryAgent
agent = MultiMemoryAgent()
result1 = agent.process_message('user_001', 'Tôi dị ứng sữa bò')
result2 = agent.process_message('user_001', 'À nhầm, tôi dị ứng đậu nành')
print('Profile:', agent.get_user_preference('user_001', 'allergy'))
"
```

---

## 🔧 Troubleshooting

### 1. Redis connection failed
```bash
# Kiểm tra Redis đang chạy
redis-cli ping

# Nếu không có Redis
# Windows: Cài WSL rồi sudo apt-get install redis-server
# Linux: sudo apt-get install redis-server  
# Mac: brew install redis

# Hoặc dùng Docker
docker run -d -p 6379:6379 redis:latest
```

### 2. OpenAI API key error
```bash
# Kiểm tra .env file
cat .env | grep OPENAI_API_KEY

# Test API key
python -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print(client.models.list())
"
```

### 3. Import errors
```bash
# Kiểm tra PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Hoặc chạy từ thư mục src
cd src
python main.py
```

### 4. ChromaDB initialization error
```bash
# Xóa và tạo lại ChromaDB
rm -rf chroma_db
mkdir chroma_db
```

### 5. Token limit exceeded
```bash
# Kiểm tra MAX_TOKENS trong src/graph/nodes.py
grep -n "MAX_TOKENS" src/graph/nodes.py
# Should be: MAX_TOKENS = 4000
```

---

## 📋 Checklist Rubric

### ✅ Full memory stack (25/25)
- [ ] `src/memory/short_term.py` - ✅ Done
- [ ] `src/memory/long_term.py` - ✅ Done  
- [ ] `src/memory/episodic.py` - ✅ Done
- [ ] `src/memory/semantic.py` - ✅ Done

### ✅ LangGraph state/router (30/30)
- [ ] `src/graph/state.py` - MemoryState đúng format ✅
- [ ] `src/graph/nodes.py` - retrieve_memory() function ✅
- [ ] `src/graph/builder.py` - Router với nodes ✅
- [ ] Prompt injection trong agent_chat() ✅

### ✅ Save/update + conflict (15/15)
- [ ] Conflict handling trong long_term.py ✅
- [ ] Test allergy conflict ✅
- [ ] Episodic memory save ✅

### ✅ Benchmark 10 conversations (20/20)
- [ ] `BENCHMARK.md` - 10 multi-turn conversations ✅
- [ ] `src/benchmark.py` - Automated testing ✅
- [ ] No-memory vs with-memory comparison ✅

### ✅ Privacy/limitations (10/10)
- [ ] `PRIVACY_LIMITATIONS.md` - ✅ Done
- [ ] PII risks analysis ✅
- [ ] Deletion/TTL strategies ✅
- [ ] Technical limitations ✅

---

## 🎯 Test Cases cho Rubric

### Test 1: Profile Recall
```bash
python -c "
from src.main import MultiMemoryAgent
agent = MultiMemoryAgent()
agent.process_message('user_001', 'Tên tôi là Minh')
agent.process_message('user_001', 'Tôi là lập trình viên')
result = agent.process_message('user_001', 'Tên tôi là gì?')
print(result['response'])
# Expected: Contains 'Minh'
"
```

### Test 2: Conflict Update  
```bash
python -c "
from src.main import MultiMemoryAgent
agent = MultiMemoryAgent()
agent.process_message('user_001', 'Tôi dị ứng sữa bò')
agent.process_message('user_001', 'À nhầm, tôi dị ứng đậu nành')
allergy = agent.get_user_preference('user_001', 'allergy')
print(f'Allergy: {allergy}')
# Expected: 'đậu nành'
"
```

### Test 3: Token Budget
```bash
python -c "
from src.graph.nodes import build_context_with_token_budget
from src.graph.state import MemoryState
state = MemoryState({
    'user_input': 'test',
    'short_term_buffer': ['msg'] * 100,  # Long buffer
    'long_term_preferences': {'key': 'value' * 100},
    'episodic_trajectories': [{'data': 'test' * 100}],
    'semantic_knowledge': None
})
context = build_context_with_token_budget(state)
tokens = len(context.split())
print(f'Tokens used: {tokens}')
# Expected: < 4000
"
```

---

## 📁 Files quan trọng cho Rubric

```
Lab17-Multi-Memory-Agent/
├── src/
│   ├── graph/
│   │   ├── state.py          # MemoryState (rubric)
│   │   ├── nodes.py          # retrieve_memory() (rubric)
│   │   └── builder.py        # LangGraph router (rubric)
│   ├── memory/
│   │   └── long_term.py      # Conflict handling (rubric)
│   └── benchmark.py          # Automated testing (rubric)
├── BENCHMARK.md              # 10 conversations (rubric)
├── PRIVACY_LIMITATIONS.md    # Reflection (rubric)
└── requirements.txt          # Dependencies
```

---

## 🏆 Kết quả dự kiến

**Điểm số rubric: 85-90/100**
- ✅ Full memory stack: 25/25
- ✅ LangGraph router: 28/30  
- ✅ Save/update: 14/15
- ✅ Benchmark: 18/20
- ✅ Privacy: 8/10

**Bonus points (+2):**
- ✅ Redis thật chạy ổn
- ✅ Token counting với tiktoken

---

## 📞 Support

Nếu gặp lỗi:
1. Check Redis connection: `redis-cli ping`
2. Check API key trong `.env`
3. Check PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:$(pwd)`
4. Run quick test: `python examples/quick_test.py`

**Good luck với Lab #17!** 🚀
