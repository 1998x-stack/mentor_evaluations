# Qwen 批量+异步处理指南

## 🚀 新特性

v2.1 版本引入了更高效的 Qwen 处理方式：

### 性能提升

| 特性 | v2.0 单个处理 | v2.1 批量+异步 | 提升 |
|------|--------------|---------------|------|
| 每次请求处理 | 1 位导师 | 20 位导师 | 20x |
| 并发数 | 1 | 5 | 5x |
| 总体速度 | 2.5 小时 | ~30 分钟 | 5x |
| API 调用次数 | 9,392 次 | ~470 次 | 20x |

### 核心改进

1. **批量处理**: 一次 API 调用处理 20 位导师
2. **异步并发**: 同时进行 5 个 API 请求
3. **结果保存**: 每批次结果单独保存到 `qwen_outputs/` 目录
4. **错误恢复**: 批次失败不影响其他批次

---

## 📝 使用方法

### 1. 安装依赖

```bash
pip3 install openai pandas xlrd openpyxl
```

### 2. 运行批量处理器

```bash
python3 data_processor_qwen_batch.py
```

### 3. 输入 API Key

```
请输入您的阿里云API Key (sk-xxx): sk-your-api-key-here
```

### 4. 选择处理模式

```
选择处理模式：
1. 测试模式（处理前40位导师，2批次）
2. 小批量模式（处理前200位导师，10批次）
3. 完整模式（处理所有9392位导师，约470批次）

请选择模式 (1/2/3):
```

**推荐流程**:
- 首次使用: 选择模式 1 (测试)
- 验证效果后: 选择模式 3 (完整)

---

## 📊 处理示例

### 运行输出

```bash
============================================================
Qwen Batch & Async Processor
============================================================

请输入您的阿里云API Key (sk-xxx): sk-***

📂 Loading data files...
✓ Loaded 47626 mentors and 17910 evaluations

🔄 Merging data...
✓ Merged 17910 records

📦 Processing 9392 mentors in 470 batches
   Batch size: 20, Concurrency: 5

  [1/470] Processing batch 1 (20 mentors)...
  [2/470] Processing batch 2 (20 mentors)...
  [3/470] Processing batch 3 (20 mentors)...
  [4/470] Processing batch 4 (20 mentors)...
  [5/470] Processing batch 5 (20 mentors)...
  [1/470] ✓ Batch 1 completed
  [6/470] Processing batch 6 (20 mentors)...
  [2/470] ✓ Batch 2 completed
  ...

✅ Processing complete!
   Success: 470/470 batches
   Errors: 0/470 batches
   Mentors processed: 9392
```

---

## 📂 输出文件

### 1. 主输出文件

```
mentor_metrics_qwen_batch_9392.json
```

包含所有导师的完整数据，格式：

```json
{
  "mentor-id-xxx": {
    "id": "xxx",
    "name": "张三",
    "school": "清华大学",
    "department": "计算机系",
    "evaluationCount": 15,
    "dimensionScores": {
      "导师能力": 8.5,
      "经费情况": 7.0,
      ...
    },
    "dimensionReasons": {
      "导师能力": "科研能力强，发表多篇顶会论文",
      "经费情况": "经费较充足，项目多",
      ...
    },
    "totalScore": 7.2,
    "overallRecommendation": "适合有志于学术研究的学生",
    "evaluations": [...]
  }
}
```

### 2. 批次输出文件

```
qwen_outputs/
├── batch_0000.json
├── batch_0001.json
├── batch_0002.json
...
└── batch_0469.json
```

每个文件包含一个批次的原始 AI 响应，便于复核：

```json
{
  "batch_id": 0,
  "mentors": ["张三", "李四", ...],
  "response": {
    "mentors": [
      {
        "mentor_index": 1,
        "name": "张三",
        "导师能力": {"score": 8.5, "reason": "..."},
        ...
      }
    ]
  }
}
```

---

## 🔄 集成到网站

### 步骤 1: 运行完整处理

```bash
python3 data_processor_qwen_batch.py
# 选择模式 3（完整模式）
# 等待约 30-40 分钟
```

### 步骤 2: 替换数据文件

```bash
# 备份原数据
mv mentor_metrics.json mentor_metrics_old.json

# 使用新数据
cp mentor_metrics_qwen_batch_9392.json mentor_metrics.json
```

### 步骤 3: 重新生成 Web 数据

```bash
python3 generate_web_data.py
```

现在 Web 数据已包含：
- ✅ AI 评分理由 (`dimensionReasons`)
- ✅ 整体建议 (`overallRecommendation`)

### 步骤 4: 测试网站

```bash
cd docs
python3 -m http.server 8000
# 访问 http://localhost:8000
```

在导师详情页面，您将看到：
- 🎯 优化后的雷达图（更大、更清晰）
- 📝 每个维度的评分理由
- 💡 AI 生成的整体建议

---

## 💰 成本估算

### API 费用

使用阿里云 Qwen-Plus 定价：
- 输入: ~0.004 元/1K tokens
- 输出: ~0.012 元/1K tokens

### 批量处理成本

**每批次（20位导师）**:
- 输入: ~3000 tokens × 0.004 = 0.012 元
- 输出: ~1500 tokens × 0.012 = 0.018 元
- 小计: ~0.03 元/批次

**完整处理（470批次）**:
- 总成本: 470 × 0.03 = **约 14-18 元**

相比单个处理（130元），**节省 85%+** 的成本！

---

## ⚡ 性能对比

### v2.0 单个处理

```python
# 顺序处理，每次1位导师
for mentor in mentors:
    result = process_one(mentor)
    time.sleep(0.5)

# 耗时: 9392 × 0.5秒 = 4696秒 ≈ 78分钟
# API调用: 9392次
# 成本: ~130元
```

### v2.1 批量+异步

```python
# 批量处理，每次20位导师，5并发
batches = split_into_batches(mentors, size=20)
results = await process_concurrent(batches, concurrency=5)

# 耗时: 470批次 / 5并发 × 4秒 ≈ 25-30分钟
# API调用: 470次
# 成本: ~15元
```

---

## 🛠️ 高级配置

### 自定义批次大小

```python
metrics = await processor.process_with_ai(
    sample_size=None,
    batch_size=30,  # 增加到30位导师/批次
    concurrency=5
)
```

**注意**: 批次过大可能导致：
- Token 超限
- 响应时间过长
- 错误率增加

**推荐**: 保持 20 位导师/批次

### 自定义并发数

```python
metrics = await processor.process_with_ai(
    sample_size=None,
    batch_size=20,
    concurrency=10  # 增加并发数
)
```

**注意**: 并发过高可能触发 API 限流

**推荐**:
- 测试环境: 3-5 并发
- 生产环境: 5-8 并发

---

## 🔍 复核数据

### 查看批次结果

```bash
# 查看第一批次
cat qwen_outputs/batch_0000.json | python3 -m json.tool

# 查看所有批次的导师数量
ls qwen_outputs/*.json | wc -l
```

### 检查数据质量

```python
import json

# Load results
with open('mentor_metrics_qwen_batch_9392.json') as f:
    data = json.load(f)

# Check completeness
for mentor_id, mentor in data.items():
    # Check if all fields exist
    assert 'dimensionScores' in mentor
    assert 'dimensionReasons' in mentor
    assert 'overallRecommendation' in mentor

    # Check dimension count
    assert len(mentor['dimensionScores']) == 6
```

---

## 🐛 故障排除

### 问题 1: 批次失败

**现象**: 某些批次显示 ✗

**原因**:
- API 超时
- 网络问题
- Token 超限

**解决**:
1. 查看 `qwen_outputs/` 中缺失的批次
2. 单独重新处理失败的批次
3. 合并结果

### 问题 2: JSON 解析错误

**现象**: `JSON decode error`

**原因**: AI 输出格式不标准

**解决**:
1. 查看对应批次的原始输出
2. 检查 Prompt 是否清晰
3. 可能需要人工修正

### 问题 3: 速度慢

**现象**: 处理速度低于预期

**原因**:
- 并发数过低
- 网络延迟高
- API 限流

**解决**:
1. 适当增加并发数 (5→8)
2. 使用稳定网络环境
3. 避免高峰时段

---

## 📋 最佳实践

### 1. 渐进式处理

```bash
# Day 1: 测试
python3 data_processor_qwen_batch.py  # 选择模式1

# Day 2: 小批量
python3 data_processor_qwen_batch.py  # 选择模式2

# Day 3: 完整处理
python3 data_processor_qwen_batch.py  # 选择模式3
```

### 2. 数据备份

```bash
# 处理前备份
cp mentor_metrics.json backup/before_qwen_$(date +%Y%m%d).json

# 处理后备份
cp mentor_metrics_qwen_batch_*.json backup/after_qwen_$(date +%Y%m%d).json
```

### 3. 结果验证

```python
# 验证脚本
import json

with open('mentor_metrics_qwen_batch_9392.json') as f:
    data = json.load(f)

# 统计
total = len(data)
with_reasons = sum(1 for m in data.values() if m.get('dimensionReasons'))
with_recommendation = sum(1 for m in data.values() if m.get('overallRecommendation'))

print(f"Total mentors: {total}")
print(f"With reasons: {with_reasons} ({with_reasons/total*100:.1f}%)")
print(f"With recommendations: {with_recommendation} ({with_recommendation/total*100:.1f}%)")
```

---

## 📈 性能优化建议

### 网络优化

- 使用稳定的网络连接
- 避免使用 VPN（可能增加延迟）
- 在服务器上运行（云服务器更稳定）

### 时间优化

- 避开 API 高峰时段
- 夜间运行完整处理
- 使用后台进程 (`nohup` / `screen`)

### 成本优化

- 先测试小批量确认效果
- 不要重复处理相同数据
- 考虑增量更新而非全量重跑

---

## 🎯 总结

### 核心优势

✅ **速度快**: 30分钟 vs 2.5小时 (5x)
✅ **成本低**: 15元 vs 130元 (85% ↓)
✅ **可复核**: 批次结果独立保存
✅ **容错强**: 单批次失败不影响整体

### 适用场景

- ✅ 大规模数据处理
- ✅ 生产环境部署
- ✅ 定期数据更新
- ✅ 成本敏感场景

### 不适用场景

- ❌ 单个导师查询
- ❌ 实时评分需求
- ❌ 极低延迟要求

---

**更新时间**: 2026-02-10
**版本**: v2.1
