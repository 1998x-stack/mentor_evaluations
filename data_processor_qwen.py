#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Data Processor with Qwen-Plus AI Model
Uses AI to extract more accurate evaluation dimensions
"""

import pandas as pd
import json
import math
from collections import defaultdict
from typing import Dict, List
import warnings
import time
from openai import OpenAI

warnings.filterwarnings('ignore')


class QwenDimensionExtractor:
    """AI-powered dimension extractor using Qwen-Plus model"""

    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen-plus"

        # Evaluation dimensions
        self.dimensions = [
            "导师能力",
            "经费情况",
            "学生补助",
            "师生关系",
            "工作时间",
            "毕业去向"
        ]

    def extract_dimensions_with_ai(
        self,
        mentor_name: str,
        school_name: str,
        comments: List[str]
    ) -> Dict:
        """
        Use Qwen-Plus to extract evaluation dimensions from comments

        Args:
            mentor_name: Name of the mentor
            school_name: Name of the school
            comments: List of evaluation comments

        Returns:
            Dictionary with dimension scores and analysis
        """

        # Combine all comments for this mentor
        all_comments = "\n\n---\n\n".join(comments[:10])  # Limit to 10 comments to avoid token limit

        prompt = f"""你是一个专业的研究生导师评价分析专家。请分析以下评论，从研究生选导师的角度，给出客观的评价。

**导师信息：**
- 姓名：{mentor_name}
- 学校：{school_name}

**学生评价：**
{all_comments}

**任务要求：**
请根据以上评价，从以下6个维度进行评分（0-10分，其中0分最差，10分最好）：

1. 导师能力（科研能力、学术水平、指导能力）
2. 经费情况（科研经费充足程度）
3. 学生补助（每月补贴、工资发放情况）
4. 师生关系（导师对学生的态度和尊重程度）
5. 工作时间（工作强度、加班情况、休息时间，分数越高代表工作时间越合理）
6. 毕业去向（对学生职业发展的支持和关注）

**评分标准：**
- 如果评论中没有提及某个维度，该维度评分为5分（中立）
- 如果评论中该维度被明确提及且为正面，评分6-10分
- 如果评论中该维度被明确提及且为负面，评分0-4分

**输出格式（必须严格按照以下JSON格式）：**
{{
  "导师能力": {{
    "score": 评分数字,
    "reason": "评分理由（简短，不超过30字）"
  }},
  "经费情况": {{
    "score": 评分数字,
    "reason": "评分理由"
  }},
  "学生补助": {{
    "score": 评分数字,
    "reason": "评分理由"
  }},
  "师生关系": {{
    "score": 评分数字,
    "reason": "评分理由"
  }},
  "工作时间": {{
    "score": 评分数字,
    "reason": "评分理由"
  }},
  "毕业去向": {{
    "score": 评分数字,
    "reason": "评分理由"
  }},
  "overall_recommendation": "整体建议（简短，不超过50字）"
}}

请只输出JSON，不要包含任何其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的研究生导师评价分析专家。请严格按照JSON格式输出结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            return result

        except Exception as e:
            print(f"  ⚠️ Error processing {mentor_name}: {e}")
            # Return default scores if AI fails
            return {
                dim: {"score": 5.0, "reason": "数据处理异常"}
                for dim in self.dimensions
            }


class EnhancedMentorDataProcessor:
    """Enhanced data processor with AI-powered analysis"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.extractor = QwenDimensionExtractor(api_key)
        self.mentor_data = None
        self.evaluation_data = None
        self.merged_data = None

    def load_data(self, mentor_file: str, evaluation_file: str):
        """Load data from xls files"""
        print("📂 Loading data files...")
        self.mentor_data = pd.read_excel(mentor_file, engine='xlrd')
        self.evaluation_data = pd.read_excel(evaluation_file, engine='xlrd')

        # Clean NaN values
        self.mentor_data = self.mentor_data.fillna('未知')
        self.evaluation_data = self.evaluation_data.fillna('未知')

        print(f"✓ Loaded {len(self.mentor_data)} mentors and {len(self.evaluation_data)} evaluations")

    def merge_data(self) -> pd.DataFrame:
        """Merge mentor info with evaluations"""
        print("\n🔄 Merging data...")

        merged = pd.merge(
            self.evaluation_data,
            self.mentor_data,
            on='编号',
            how='left'
        )

        self.merged_data = merged
        print(f"✓ Merged {len(merged)} records")

        return merged

    def process_evaluations_with_ai(
        self,
        sample_size: int = None,
        delay: float = 0.5
    ) -> Dict:
        """
        Process evaluations using AI model

        Args:
            sample_size: Number of mentors to process (None for all)
            delay: Delay between API calls in seconds

        Returns:
            Dictionary with mentor metrics
        """
        print("\n⚙️ Processing evaluations with Qwen-Plus AI...")

        if self.merged_data is None:
            self.merge_data()

        # Group evaluations by mentor
        mentor_evaluations = defaultdict(lambda: {
            'name': '',
            'school': '',
            'department': '',
            'comments': []
        })

        for idx, row in self.merged_data.iterrows():
            mentor_id = row['编号']
            comment = str(row['评价'])

            if not mentor_evaluations[mentor_id]['name']:
                mentor_evaluations[mentor_id]['name'] = str(row.get('姓名', '未知'))
                mentor_evaluations[mentor_id]['school'] = str(row.get('学校', '未知'))
                mentor_evaluations[mentor_id]['department'] = str(row.get('专业', '未知'))

            mentor_evaluations[mentor_id]['comments'].append(comment)

        # Process with AI
        mentor_metrics = {}
        mentor_list = list(mentor_evaluations.items())

        # Limit sample size if specified
        if sample_size:
            mentor_list = mentor_list[:sample_size]

        total = len(mentor_list)
        print(f"Processing {total} mentors with AI model...")

        for i, (mentor_id, data) in enumerate(mentor_list, 1):
            print(f"  [{i}/{total}] Processing {data['name']} ({data['school']})...", end=' ')

            try:
                ai_result = self.extractor.extract_dimensions_with_ai(
                    mentor_name=data['name'],
                    school_name=data['school'],
                    comments=data['comments']
                )

                # Extract scores and reasons
                dimension_scores = {}
                dimension_reasons = {}

                for dim in self.extractor.dimensions:
                    if dim in ai_result:
                        dimension_scores[dim] = float(ai_result[dim].get('score', 5.0))
                        dimension_reasons[dim] = ai_result[dim].get('reason', '')

                # Calculate overall score
                scores = list(dimension_scores.values())
                total_score = sum(scores) / len(scores) if scores else 5.0

                mentor_metrics[mentor_id] = {
                    'id': mentor_id,
                    'name': data['name'],
                    'school': data['school'],
                    'department': data['department'],
                    'evaluationCount': len(data['comments']),
                    'dimensionScores': dimension_scores,
                    'dimensionReasons': dimension_reasons,
                    'totalScore': round(total_score, 2),
                    'overallRecommendation': ai_result.get('overall_recommendation', ''),
                    'evaluations': [{'comment': c, 'dimensions': {}} for c in data['comments']]
                }

                print(f"✓ (Score: {total_score:.1f})")

                # Rate limiting
                time.sleep(delay)

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        print(f"\n✓ Successfully processed {len(mentor_metrics)} mentors")

        return mentor_metrics

    def export_metrics(self, metrics: Dict, output_file: str = 'mentor_metrics_ai.json'):
        """Export metrics to JSON"""
        print(f"\n💾 Exporting to {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        print(f"✓ Exported {len(metrics)} mentor metrics")


def main():
    """Main execution"""
    print("=" * 60)
    print("Enhanced Mentor Evaluation Data Processor")
    print("Powered by Qwen-Plus AI Model")
    print("=" * 60)

    # API Key
    api_key = input("\n请输入您的阿里云API Key (sk-xxx): ").strip()

    if not api_key or not api_key.startswith('sk-'):
        print("❌ Invalid API key!")
        return

    # Initialize processor
    processor = EnhancedMentorDataProcessor(api_key)

    # Load data
    processor.load_data('导师信息.xls', '评价信息.xls')

    # Process with AI (sample first)
    print("\n" + "=" * 60)
    print("选择处理模式：")
    print("1. 测试模式（处理前10位导师）")
    print("2. 小批量模式（处理前100位导师）")
    print("3. 完整模式（处理所有9392位导师，需要较长时间）")
    print("=" * 60)

    mode = input("请选择模式 (1/2/3): ").strip()

    sample_size = {
        '1': 10,
        '2': 100,
        '3': None
    }.get(mode, 10)

    if sample_size:
        print(f"\n将处理前 {sample_size} 位导师...")
    else:
        print(f"\n将处理所有导师（约需 2-3 小时）...")
        confirm = input("确认继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("已取消")
            return

    # Process evaluations
    metrics = processor.process_evaluations_with_ai(
        sample_size=sample_size,
        delay=0.5  # 0.5 second delay between requests
    )

    # Export results
    output_file = f'mentor_metrics_ai_{len(metrics)}.json'
    processor.export_metrics(metrics, output_file)

    # Show sample results
    print("\n" + "=" * 60)
    print("📊 Sample Results")
    print("=" * 60)

    sample_mentors = list(metrics.values())[:3]
    for mentor in sample_mentors:
        print(f"\n导师：{mentor['name']} ({mentor['school']})")
        print(f"综合评分：{mentor['totalScore']}/10")
        print(f"维度评分：")
        for dim, score in mentor['dimensionScores'].items():
            reason = mentor['dimensionReasons'].get(dim, '')
            print(f"  - {dim}: {score}/10 ({reason})")
        print(f"建议：{mentor.get('overallRecommendation', 'N/A')}")

    print("\n" + "=" * 60)
    print("✅ Processing Complete!")
    print("=" * 60)
    print(f"\n生成的文件: {output_file}")
    print(f"处理的导师数: {len(metrics)}")


if __name__ == "__main__":
    main()
