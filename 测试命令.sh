#!/bin/bash
# 导师评价系统测试脚本

echo "================================"
echo "导师评价系统 v2.1 - 测试脚本"
echo "================================"
echo ""

# 1. 检查Python环境
echo "1. 检查Python环境..."
python3 --version || { echo "❌ Python3 未安装"; exit 1; }
echo "✓ Python环境正常"
echo ""

# 2. 检查依赖
echo "2. 检查依赖..."
python3 -c "import pandas, xlrd, openai" 2>/dev/null && echo "✓ 所有依赖已安装" || {
    echo "⚠️  缺少依赖，正在安装..."
    pip3 install pandas xlrd openpyxl openai
}
echo ""

# 3. 检查数据文件
echo "3. 检查数据文件..."
if [ -f "导师信息.xls" ] && [ -f "评价信息.xls" ]; then
    echo "✓ 原始数据文件存在"
else
    echo "❌ 缺少原始数据文件"
    exit 1
fi
echo ""

# 4. 运行规则处理器
echo "4. 运行规则处理器（快速测试）..."
python3 data_processor.py || { echo "❌ 规则处理失败"; exit 1; }
echo "✓ 规则处理完成"
echo ""

# 5. 生成Web数据
echo "5. 生成Web数据..."
python3 generate_web_data.py || { echo "❌ Web数据生成失败"; exit 1; }
echo "✓ Web数据生成完成"
echo ""

# 6. 验证输出文件
echo "6. 验证输出文件..."
files=(
    "mentor_metrics.json"
    "docs/data/schools.json"
    "docs/data/mentors_by_school.json"
    "docs/data/metadata.json"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ❌ $file 缺失"
        exit 1
    fi
done
echo ""

# 7. 验证JSON格式
echo "7. 验证JSON格式..."
python3 -c "
import json
try:
    with open('docs/data/schools.json') as f:
        json.load(f)
    print('✓ schools.json 有效')
    
    with open('docs/data/mentors_by_school.json') as f:
        json.load(f)
    print('✓ mentors_by_school.json 有效')
    
    with open('mentor_metrics.json') as f:
        data = json.load(f)
    print(f'✓ mentor_metrics.json 有效 ({len(data)} 位导师)')
except Exception as e:
    print(f'❌ JSON 验证失败: {e}')
    exit(1)
"
echo ""

# 8. 测试雷达图JS
echo "8. 检查前端文件..."
frontend_files=(
    "docs/index.html"
    "docs/mentors.html"
    "docs/mentor-detail.html"
    "docs/js/radar-chart.js"
    "docs/js/mentor-detail.js"
    "docs/css/mentor-detail.css"
)

for file in "${frontend_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ❌ $file 缺失"
    fi
done
echo ""

# 9. 完成
echo "================================"
echo "✅ 所有测试通过！"
echo "================================"
echo ""
echo "启动网站："
echo "  cd docs"
echo "  python3 -m http.server 8000"
echo ""
echo "然后访问: http://localhost:8000"
echo ""

