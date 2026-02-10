# 导师评价系统 (Mentor Evaluation System)

一个基于真实学生评价的导师评价平台，采用 Apple 风格设计，帮助学生做出更明智的导师选择。

## 📊 项目概览

- **学校数量**: 189 所
- **导师数量**: 9,392 位
- **评价总数**: 17,910 条
- **评价维度**: 6 个维度（导师能力、经费情况、学生补助、师生关系、工作时间、毕业去向）

## ✨ 功能特性

### 已实现功能

1. **数据处理系统** 📁
   - 自动解析 XLS 文件
   - 智能提取评价维度
   - 情感分析评分系统
   - 生成结构化 JSON 数据

2. **学校列表页面** 🏫
   - 展示所有学校统计信息
   - 实时搜索功能
   - 多维度排序（按导师数、评分、名称）
   - Apple 风格卡片设计

3. **导师列表页面** 👨‍🏫
   - 按学校分组展示导师
   - 搜索导师姓名和院系
   - 多维度排序
   - 维度评分预览

4. **导师详情页面** 📈
   - 纯 JavaScript 实现的雷达图
   - 6 维度评分可视化
   - 完整学生评价展示
   - 智能选择建议
   - 评价过滤（全部/正面/负面）

5. **响应式设计** 📱
   - 完美适配桌面和移动设备
   - 流畅的动画效果
   - 优雅的交互体验

### 预留功能（未实现）

6. **匿名数据提交** 🔒
   - 数据模型已定义 ([data-submission.js](docs/js/data-submission.js:1))
   - 表单验证逻辑已完成
   - 等待后端集成
   - 详见代码中的 TODO 注释

## 🏗️ 项目结构

```
mentor_evaluations/
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Pages 自动部署
├── docs/                           # 前端网站目录
│   ├── index.html                  # 学校列表页面
│   ├── mentors.html               # 导师列表页面
│   ├── mentor-detail.html         # 导师详情页面
│   ├── css/
│   │   ├── styles.css             # 主样式表（Apple 风格）
│   │   ├── mentors.css            # 导师列表页样式
│   │   └── mentor-detail.css      # 导师详情页样式
│   ├── js/
│   │   ├── common.js              # 公共工具函数
│   │   ├── schools.js             # 学校页面逻辑
│   │   ├── mentors.js             # 导师列表逻辑
│   │   ├── mentor-detail.js       # 导师详情逻辑
│   │   ├── radar-chart.js         # 雷达图组件
│   │   └── data-submission.js     # 数据提交模块（预留）
│   └── data/
│       ├── metadata.json          # 元数据
│       ├── schools.json           # 学校列表
│       ├── mentors_by_school.json # 按学校分组的导师
│       └── mentors/               # 导师详情文件夹
│           └── {mentor-id}.json   # 9,392 个导师详情文件
├── analyze_data.py                # 数据分析脚本
├── data_processor.py              # 数据处理核心模块
├── generate_web_data.py           # Web 数据生成器
├── merged_data.csv                # 合并后的原始数据
├── mentor_metrics.json            # 导师评价指标
├── 导师信息.xls                    # 原始导师数据
└── 评价信息.xls                    # 原始评价数据
```

## 🚀 快速开始

### 1. 数据处理

```bash
# 安装依赖
pip3 install pandas xlrd openpyxl

# 分析数据
python3 analyze_data.py

# 处理数据并生成指标
python3 data_processor.py

# 生成 Web 数据文件
python3 generate_web_data.py
```

### 2. 本地预览

```bash
# 进入网站目录
cd docs

# 使用 Python 启动本地服务器
python3 -m http.server 8000

# 访问 http://localhost:8000
```

### 3. 部署到 GitHub Pages

1. 初始化 Git 仓库
```bash
git init
git add .
git commit -m "Initial commit: Mentor Evaluation System"
```

2. 创建 GitHub 仓库并推送
```bash
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
```

3. 在 GitHub 仓库设置中启用 GitHub Pages
   - Settings → Pages
   - Source: GitHub Actions
   - 工作流会自动部署 `docs` 目录

## 💻 技术栈

### 后端数据处理
- **Python 3.11**
- **Pandas**: 数据处理和分析
- **xlrd**: Excel 文件读取
- **正则表达式**: 维度提取
- **情感分析**: 自定义关键词分析

### 前端
- **纯 HTML5/CSS3/JavaScript**: 无框架依赖
- **原生 Canvas API**: 雷达图绘制
- **CSS Grid & Flexbox**: 响应式布局
- **ES6+**: 现代 JavaScript 特性
- **模块化设计**: 清晰的代码结构

### 部署
- **GitHub Pages**: 静态网站托管
- **GitHub Actions**: 自动化 CI/CD

## 🎨 设计特色

### Apple 风格设计系统

1. **颜色方案**
   - 主色调: #007AFF (iOS 蓝)
   - 背景: #F5F5F7 (浅灰)
   - 文字: #1d1d1f (深灰)
   - 渐变: 紫色系渐变

2. **排版**
   - 字体: San Francisco (-apple-system)
   - 大标题: 3rem, 700 weight
   - 负字间距优化

3. **交互**
   - 平滑过渡动画
   - Hover 状态提升
   - 微妙的阴影效果
   - 磨砂玻璃效果 (backdrop-filter)

4. **组件**
   - 圆角卡片 (12-18px)
   - 柔和阴影
   - 渐变背景
   - 优雅的加载状态

## 📐 评价维度说明

系统从评论中自动提取以下 6 个维度的评分（0-10 分）：

| 维度 | 说明 |
|------|------|
| 导师能力 | 科研能力、学术水平、指导能力 |
| 经费情况 | 科研经费充足程度 |
| 学生补助 | 每月补贴、工资发放情况 |
| 师生关系 | 导师对学生的态度和尊重程度 |
| 工作时间 | 工作强度、加班情况、休息时间 |
| 毕业去向 | 对学生职业发展的支持和关注 |

## 🔮 未来功能规划

### 匿名数据提交系统

已预留完整的代码模块 ([data-submission.js](docs/js/data-submission.js:1))，包含：

#### 数据模型
- `SchoolSubmission`: 学校提交
- `MentorSubmission`: 导师提交
- `EvaluationSubmission`: 评价提交

#### 表单验证
- 必填字段验证
- 评分范围验证 (0-10)
- 邮箱格式验证
- XSS 防护
- 垃圾内容检测

#### 待实现功能
1. **后端服务**
   - Node.js/Python API 服务器
   - 数据库集成 (MongoDB/PostgreSQL)
   - RESTful API 端点

2. **内容审核**
   - 提交审核队列
   - 垃圾信息过滤
   - 人工审核界面

3. **用户界面**
   - 提交表单页面
   - 成功/失败通知
   - 提交历史查看

4. **安全特性**
   - API 速率限制
   - CAPTCHA 集成
   - IP 黑名单
   - 内容过滤

5. **数据管理**
   - 自动数据聚合
   - 增量更新
   - 数据备份

## 📊 数据统计

通过运行 `python3 data_processor.py` 可以看到：

- 总导师数: 9,392 位
- 总学校数: 189 所
- 平均评分: 5.12/10
- Top 学校:
  1. 东南大学: 413 位导师
  2. 浙江大学: 398 位导师
  3. 北京航空航天大学: 325 位导师
  4. 西安交通大学: 315 位导师
  5. 天津大学: 284 位导师

## 🛠️ 模块说明

### 数据处理模块

#### [analyze_data.py](analyze_data.py:1)
分析原始 XLS 文件结构，输出统计信息。

#### [data_processor.py](data_processor.py:1)
核心数据处理模块，包含：
- `DimensionExtractor`: 维度提取器
  - 识别评价维度关键词
  - 提取维度内容
  - 情感分析评分
- `MentorDataProcessor`: 主处理器
  - 数据加载和合并
  - 评价处理和聚合
  - 指标计算
  - 文件导出

#### [generate_web_data.py](generate_web_data.py:1)
生成前端所需的优化数据文件：
- 学校列表（带统计）
- 按学校分组的导师列表
- 独立的导师详情文件
- 元数据

### 前端模块

#### [common.js](docs/js/common.js:1)
公共工具函数库：
- 数据获取和缓存
- 数字格式化
- URL 参数处理
- 错误处理
- 通用动画

#### [radar-chart.js](docs/js/radar-chart.js:1)
纯 JavaScript 雷达图组件：
- Canvas 绘制
- 响应式适配
- 高 DPI 支持
- 平滑动画

#### [data-submission.js](docs/js/data-submission.js:1)
数据提交模块（预留）：
- 数据模型定义
- 表单验证逻辑
- API 端点占位
- 安全检查函数

## 🔒 隐私和安全

- 所有评价数据已脱敏
- 不存储个人身份信息
- 前端纯静态页面，无后端追踪
- 预留的提交系统包含完整的安全验证

## 📝 许可证

本项目仅供学习和参考使用。数据来源于公开评价，请合理使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题或建议，请提交 GitHub Issue。

---

**注意**: 本系统中的评价数据仅供参考，建议结合多方信息综合判断。
