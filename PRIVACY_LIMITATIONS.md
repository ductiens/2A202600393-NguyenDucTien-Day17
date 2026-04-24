# Privacy & Limitations Reflection

**Yêu cầu rubric:** Nhận diện rủi ro PII/privacy, memory nhạy cảm nhất, deletion/TTL/consent, limitation kỹ thuật.

---

## 1. Rủi ro PII/Privacy

### Rủi ro cao nhất:
- **Long-term memory (Redis)** lưu trữ user profile vĩnh viễn
- **Episodic memory** ghi lại toàn bộ conversation history
- **PII data**: tên, email, số điện thoại, địa chỉ, medical info

### Ví dụ rủi ro:
```python
# Nguy cơ: lưu thông tin nhạy cảm
user_profile = {
    "name": "Nguyễn Văn A",
    "email": "a.nguyen@email.com", 
    "phone": "0912345678",
    "allergy": "dị ứng đậu nành",  # Medical info
    "address": "123 ABC Street"
}
```

### Mitigation strategies:
- **Data minimization**: Chỉ lưu thông tin cần thiết
- **Encryption**: Mã hóa PII trong Redis
- **Access control**: Giới hạn quyền truy cập memory
- **Audit logging**: Log mọi access đến PII

---

## 2. Memory nào nhạy cảm nhất?

**1. Long-term Memory (Nhạy cảm nhất)**
- Lưu trữ vĩnh viễn user preferences
- Chứa PII, medical info, financial data
- Khó xóa, khó update

**2. Episodic Memory (Rất nhạy cảm)**
- Ghi lại toàn bộ conversation
- Có thể leak private discussions
- Dữ liệu tập trung, dễ trích xuất

**3. Semantic Memory (Trung bình)**
- Chỉ lưu domain knowledge
- Ít PII, nhưng có thể leak business info

**4. Short-term Memory (Ít nhạy cảm nhất)**
- Tự động expire
- Buffer size giới hạn
- Không lưu trữ vĩnh viễn

---

## 3. Deletion, TTL, Consent

### Current implementation gaps:
```python
# ❌ Thiếu TTL trong Redis
r.hset(f"user:{user_id}", key, value)  # Vĩnh viễn

# ❌ Thiếu deletion mechanism
# ❌ Thiêm consent management
# ❌ Thiêu data retention policy
```

### Proposed improvements:

#### 1. TTL Implementation
```python
def set_preference_with_ttl(self, user_id: str, key: str, value: Any, ttl_seconds: int = 86400):
    """Set preference with TTL (24 hours default)"""
    if not self.client:
        return False
    
    try:
        self.client.hset(f"user:{user_id}", key, str(value))
        self.client.expire(f"user:{user_id}", ttl_seconds)  # Auto-expire
        return True
    except Exception as e:
        print(f"Failed to set preference with TTL: {e}")
        return False
```

#### 2. Right to Deletion (GDPR)
```python
def delete_user_data(self, user_id: str):
    """Delete all user data (GDPR right to be forgotten)"""
    try:
        # Delete from Redis
        self.client.delete(f"user:{user_id}")
        
        # Delete from episodic memory
        self.episodic.clear_trajectories(user_id)
        
        # Delete from semantic memory
        self.semantic.delete_user_vectors(user_id)
        
        return True
    except Exception as e:
        print(f"Failed to delete user data: {e}")
        return False
```

#### 3. Consent Management
```python
def set_consent(self, user_id: str, consent_type: str, granted: bool):
    """Manage user consent for data processing"""
    consent_data = {
        "granted": granted,
        "timestamp": datetime.now().isoformat(),
        "purpose": consent_type
    }
    return self.set_preference(user_id, f"consent_{consent_type}", consent_data)
```

---

## 4. Limitations Kỹ thuật

### 4.1 Scalability Issues
- **Redis single point failure**: Nếu Redis down, mất toàn bộ long-term memory
- **ChromaDB memory usage**: Vector database consumes significant RAM
- **Token counting overhead**: tiktoken adds latency to each request

### 4.2 Memory Consistency
- **Race conditions**: Concurrent updates có thể gây data inconsistency
- **Eventual consistency**: Memory sync giữa backends có delay
- **Conflict resolution**: Hiện tại chỉ đơn giản overwrite

### 4.3 Performance Bottlenecks
```python
# ❌ Sequential memory loading
def retrieve_memory(state):
    short_term = ShortTermMemory()    # 10ms
    long_term = LongTermMemory()      # 50ms (Redis)
    episodic = EpisodicMemory()       # 20ms (file I/O)
    semantic = SemanticMemory()       # 100ms (vector search)
    # Total: 180ms per request
```

### 4.4 Security Vulnerabilities
- **Redis injection**: Nếu không sanitize input
- **Path traversal**: Episodic file access
- **Vector poisoning**: Semantic memory corruption

---

## 5. Risk Mitigation Strategies

### 5.1 Privacy by Design
```python
class PrivacyAwareMemory:
    def __init__(self):
        self.pii_fields = ["email", "phone", "ssn", "credit_card"]
        self.sensitive_categories = ["medical", "financial", "political"]
    
    def sanitize_input(self, data: dict) -> dict:
        """Remove or encrypt PII before storage"""
        sanitized = data.copy()
        for field in self.pii_fields:
            if field in sanitized:
                sanitized[field] = self.encrypt(sanitized[field])
        return sanitized
```

### 5.2 Rate Limiting
```python
def check_memory_access_rate(self, user_id: str) -> bool:
    """Prevent memory scraping attacks"""
    key = f"rate_limit:{user_id}"
    current = self.redis.get(key) or 0
    if int(current) > 100:  # 100 requests/hour
        return False
    self.redis.incr(key)
    self.redis.expire(key, 3600)
    return True
```

### 5.3 Memory Validation
```python
def validate_memory_content(self, content: str) -> bool:
    """Check for malicious content"""
    malicious_patterns = [
        r"<script.*?>.*?</script>",  # XSS
        r"DROP TABLE",               # SQL injection
        r"__import__.*?os"          # Code injection
    ]
    return not any(re.search(pattern, content) for pattern in malicious_patterns)
```

---

## 6. Recommendations

### 6.1 Immediate Actions
1. **Add TTL** cho tất cả memory types
2. **Implement deletion** mechanism  
3. **Add consent management** system
4. **Encrypt PII** trong Redis

### 6.2 Medium-term Improvements
1. **Distributed caching** để tránh single point failure
2. **Async memory loading** để cải thiện performance
3. **Memory validation** để prevent injection attacks
4. **Audit trails** cho compliance

### 6.3 Long-term Architecture
1. **Memory hierarchy** với automatic tiering
2. **Privacy-preserving ML** cho semantic search
3. **Federated learning** để không centralize PII
4. **Zero-knowledge proofs** cho privacy verification

---

## 7. Compliance Checklist

### GDPR Compliance
- ✅ Right to access data
- ✅ Right to rectification  
- ❌ Right to erasure (cần implement)
- ❌ Data portability (cần implement)
- ❌ Privacy by design (partial)

### Security Best Practices
- ✅ Input validation
- ✅ Error handling
- ❌ Encryption at rest
- ❌ Access control
- ❌ Audit trails

---

## 8. Testing Strategy

### Privacy Testing
```python
def test_pii_protection():
    """Test PII handling in memory"""
    user_input = "My name is John Doe, email john@example.com, phone 555-0123"
    
    # Should not store raw PII
    agent.process_message("user_001", user_input)
    
    # Check if PII is encrypted/anonymized
    stored_data = agent.get_user_profile("user_001")
    assert "john@example.com" not in str(stored_data)
    assert "555-0123" not in str(stored_data)
```

### Security Testing  
```python
def test_memory_injection():
    """Test for injection attacks"""
    malicious_input = "DROP TABLE users; --"
    
    # Should not break the system
    result = agent.process_message("user_001", malicious_input)
    assert result["success"] == True
    assert "DROP TABLE" not in result["response"]
```

---

**Kết luận:** System hiện tại có risks về privacy và limitations về scalability. Cần implement TTL, deletion mechanism, và security measures để production-ready.
