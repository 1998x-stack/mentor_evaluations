# 快速开始指南

## 🚀 5 分钟快速上手

### 前提条件
- Python 3.11+
- pip3

### 步骤 1: 安装依赖

```bash
pip3 install pandas xlrd openpyxl openai
```

### 步骤 2: 处理数据

```bash
# 基础版本（免费、快速）
python3 data_processor.py
python3 generate_web_data.py
```

### 步骤 3: 启动网站

```bash
cd docs
python3 -m http.server 8000
```

访问: http://localhost:8000

✅ **完成！** 网站已经在本地运行。

---

## 🤖 使用 AI 增强版（可选）

如果您想使用 Qwen-Plus AI 模型获得更准确的评分：

### 步骤 1: 获取 API Key

访问 https://dashscope.aliyun.com/ 获取 API Key

### 步骤 2: 运行 AI 处理器

```bash
python3 data_processor_qwen.py
```

输入 API Key，选择模式：
- 测试模式: 处理 10 位导师（推荐首次使用）
- 完整模式: 处理所有 9,392 位导师（约 2-3 小时，成本约 110-150 元）

### 步骤 3: 替换数据

```bash
cp mentor_metrics_ai_*.json mentor_metrics.json
python3 generate_web_data.py
```

---

## 📂 项目文件结构

```
mentor_evaluations/
├── data_processor.py          # 基础版处理器（免费）
├── data_processor_qwen.py     # AI 增强版（需 API）
├── generate_web_data.py       # Web 数据生成器
├── docs/                      # 网站目录
│   ├── index.html            # 学校列表
│   ├── mentors.html         # 导师列表
│   └── mentor-detail.html   # 导师详情
└── 导师信息.xls / 评价信息.xls  # 原始数据
```

---

## 🎯 常见问题

### Q: 网站显示 "NaN" 错误？
A: 已修复！重新运行 `python3 data_processor.py` 和 `python3 generate_web_data.py`

### Q: AI 版本值得用吗？
A:
- ✅ **是**: 需要准确评分、详细理由、专业建议
- ❌ **否**: 只是快速浏览、个人使用、成本敏感

### Q: 数据来源是什么？
A: 原始 Excel 文件中的真实学生评价（已脱敏）

### Q: 可以添加自己的评价吗？
A: 前端已预留接口，但需要实现后端服务。详见 [data-submission.js](docs/js/data-submission.js:1)

---

## 📖 完整文档

- [README.md](README.md:1) - 完整项目说明
- [QWEN_UPGRADE_GUIDE.md](QWEN_UPGRADE_GUIDE.md:1) - AI 升级指南
- [BUGFIX_SUMMARY.md](BUGFIX_SUMMARY.md:1) - Bug 修复总结
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md:1) - 项目完成总结

---

## 🆘 需要帮助？

1. 查看文档
2. 检查控制台错误
3. 提交 GitHub Issue

---

**祝您使用愉快！** 🎉
