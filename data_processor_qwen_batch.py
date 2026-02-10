#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Qwen Data Processor with Batch & Async Processing
- Batch: 20 mentors per request
- Async: 5 concurrent requests
- Output: Individual JSON files for review
"""

import pandas as pd
import json
import asyncio
import time
from collections import defaultdict
from typing import Dict, List
from openai import AsyncOpenAI
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class QwenBatchProcessor:
    """Batch & Async Qwen-Plus processor"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
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

    def create_batch_prompt(self, mentors_batch: List[Dict]) -> str:
        """
        Create prompt for batch of mentors

        Args:
            mentors_batch: List of mentor dicts with name, school, comments

        Returns:
            Formatted prompt string
        """

        mentors_text = ""
        for idx, mentor in enumerate(mentors_batch, 1):
            comments = "\n".join([f"  - {c}" for c in mentor['comments'][:10]])
            mentors_text += f"""
【导师 {idx}】
姓名：{mentor['name']}
学校：{mentor['school']}
院系：{mentor['department']}
评价数：{len(mentor['comments'])}
学生评价：
{comments}

"""

        prompt = f"""你是一个专业的研究生导师评价分析专家。请分析以下{len(mentors_batch)}位导师的评价，从研究生选导师的角度，给出客观的评价。

{mentors_text}

**任务要求：**
对于每一位导师，从以下6个维度进行评分（0-10分）：
1. 导师能力（科研能力、学术水平、指导能力）
2. 经费情况（科研经费充足程度）
3. 学生补助（每月补贴、工资发放情况）
4. 师生关系（导师对学生的态度和尊重程度）
5. 工作时间（工作强度、加班情况、休息时间，分数越高代表工作时间越合理）
6. 毕业去向（对学生职业发展的支持和关注）

**评分标准：**
- 没有提及的维度：5分（中立）
- 明确正面：6-10分
- 明确负面：0-4分

**输出格式（严格按照以下JSON格式）：**
{{
  "mentors": [
    {{
      "mentor_index": 1,
      "name": "导师姓名",
      "导师能力": {{"score": 分数, "reason": "评分理由（不超过30字）"}},
      "经费情况": {{"score": 分数, "reason": "评分理由"}},
      "学生补助": {{"score": 分数, "reason": "评分理由"}},
      "师生关系": {{"score": 分数, "reason": "评分理由"}},
      "工作时间": {{"score": 分数, "reason": "评分理由"}},
      "毕业去向": {{"score": 分数, "reason": "评分理由"}},
      "overall_recommendation": "整体建议（不超过50字）"
    }},
    ...
  ]
}}

请只输出JSON，不要包含任何其他文字。确保输出{len(mentors_batch)}位导师的评分。"""

        return prompt

    async def process_batch_async(
        self,
        mentors_batch: List[Dict],
        batch_id: int
    ) -> Dict:
        """
        Process a batch of mentors asynchronously

        Args:
            mentors_batch: List of mentor dicts
            batch_id: Batch identifier

        Returns:
            Dictionary with results for all mentors in batch
        """

        prompt = self.create_batch_prompt(mentors_batch)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的研究生导师评价专家。必须严格按照JSON格式输出，输出的导师数量必须与输入一致。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000  # Increased for batch processing
            )

            result_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # Save raw response for review
            output_dir = Path("qwen_outputs")
            output_dir.mkdir(exist_ok=True)

            with open(output_dir / f"batch_{batch_id:04d}.json", 'w', encoding='utf-8') as f:
                json.dump({
                    'batch_id': batch_id,
                    'mentors': [m['name'] for m in mentors_batch],
                    'response': result
                }, f, ensure_ascii=False, indent=2)

            return {'batch_id': batch_id, 'result': result, 'success': True}

        except Exception as e:
            print(f"  ✗ Batch {batch_id} error: {e}")
            return {
                'batch_id': batch_id,
                'error': str(e),
                'success': False,
                'mentors': [m['name'] for m in mentors_batch]
            }

    async def process_all_batches(
        self,
        all_mentors: List[Dict],
        batch_size: int = 20,
        concurrency: int = 5
    ) -> Dict:
        """
        Process all mentors in batches with controlled concurrency

        Args:
            all_mentors: List of all mentor dicts
            batch_size: Number of mentors per batch (default: 20)
            concurrency: Number of concurrent requests (default: 5)

        Returns:
            Dictionary with all mentor metrics
        """

        # Split into batches
        batches = []
        for i in range(0, len(all_mentors), batch_size):
            batch = all_mentors[i:i + batch_size]
            batches.append((i // batch_size, batch))

        total_batches = len(batches)
        print(f"\n📦 Processing {len(all_mentors)} mentors in {total_batches} batches")
        print(f"   Batch size: {batch_size}, Concurrency: {concurrency}\n")

        # Process batches with concurrency limit
        results = []
        semaphore = asyncio.Semaphore(concurrency)

        async def process_with_semaphore(batch_id, batch):
            async with semaphore:
                print(f"  [{batch_id+1}/{total_batches}] Processing batch {batch_id+1} ({len(batch)} mentors)...")
                result = await self.process_batch_async(batch, batch_id)
                print(f"  [{batch_id+1}/{total_batches}] {'✓' if result['success'] else '✗'} Batch {batch_id+1} completed")
                return result

        # Execute all batches
        results = await asyncio.gather(*[
            process_with_semaphore(batch_id, batch)
            for batch_id, batch in batches
        ])

        # Aggregate results
        mentor_metrics = {}
        success_count = 0
        error_count = 0

        for batch_result in results:
            if batch_result['success']:
                success_count += 1
                batch_id = batch_result['batch_id']
                batch_mentors = batches[batch_id][1]

                # Map results back to mentors
                for mentor_result in batch_result['result'].get('mentors', []):
                    mentor_idx = mentor_result.get('mentor_index', 0) - 1
                    if 0 <= mentor_idx < len(batch_mentors):
                        mentor_data = batch_mentors[mentor_idx]
                        mentor_id = mentor_data['id']

                        # Extract scores and reasons
                        dimension_scores = {}
                        dimension_reasons = {}

                        for dim in self.dimensions:
                            if dim in mentor_result:
                                dimension_scores[dim] = float(mentor_result[dim].get('score', 5.0))
                                dimension_reasons[dim] = mentor_result[dim].get('reason', '')

                        # Calculate overall score
                        scores = list(dimension_scores.values())
                        total_score = sum(scores) / len(scores) if scores else 5.0

                        mentor_metrics[mentor_id] = {
                            'id': mentor_id,
                            'name': mentor_data['name'],
                            'school': mentor_data['school'],
                            'department': mentor_data['department'],
                            'evaluationCount': len(mentor_data['comments']),
                            'dimensionScores': dimension_scores,
                            'dimensionReasons': dimension_reasons,
                            'totalScore': round(total_score, 2),
                            'overallRecommendation': mentor_result.get('overall_recommendation', ''),
                            'evaluations': [{'comment': c, 'dimensions': {}} for c in mentor_data['comments']]
                        }
            else:
                error_count += 1

        print(f"\n✅ Processing complete!")
        print(f"   Success: {success_count}/{total_batches} batches")
        print(f"   Errors: {error_count}/{total_batches} batches")
        print(f"   Mentors processed: {len(mentor_metrics)}")

        return mentor_metrics


class EnhancedMentorDataProcessor:
    """Enhanced data processor with batch + async AI"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.processor = QwenBatchProcessor(api_key)
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

    def prepare_mentors_data(self, sample_size: int = None) -> List[Dict]:
        """Prepare mentor data for processing"""
        if self.merged_data is None:
            self.merge_data()

        # Group evaluations by mentor
        mentor_evaluations = defaultdict(lambda: {
            'id': '',
            'name': '',
            'school': '',
            'department': '',
            'comments': []
        })

        for idx, row in self.merged_data.iterrows():
            mentor_id = row['编号']
            comment = str(row['评价'])

            if not mentor_evaluations[mentor_id]['id']:
                mentor_evaluations[mentor_id]['id'] = mentor_id
                mentor_evaluations[mentor_id]['name'] = str(row.get('姓名', '未知'))
                mentor_evaluations[mentor_id]['school'] = str(row.get('学校', '未知'))
                mentor_evaluations[mentor_id]['department'] = str(row.get('专业', '未知'))

            mentor_evaluations[mentor_id]['comments'].append(comment)

        mentors_list = list(mentor_evaluations.values())

        if sample_size:
            mentors_list = mentors_list[:sample_size]

        return mentors_list

    async def process_with_ai(
        self,
        sample_size: int = None,
        batch_size: int = 20,
        concurrency: int = 5
    ) -> Dict:
        """Process evaluations with AI"""
        mentors_list = self.prepare_mentors_data(sample_size)

        metrics = await self.processor.process_all_batches(
            mentors_list,
            batch_size=batch_size,
            concurrency=concurrency
        )

        return metrics

    def export_metrics(self, metrics: Dict, output_file: str = 'mentor_metrics_qwen_batch.json'):
        """Export metrics to JSON"""
        print(f"\n💾 Exporting to {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        print(f"✓ Exported {len(metrics)} mentor metrics")


async def main():
    """Main execution"""
    print("=" * 60)
    print("Qwen Batch & Async Processor")
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

    # Process with AI
    print("\n" + "=" * 60)
    print("选择处理模式：")
    print("1. 测试模式（处理前40位导师，2批次）")
    print("2. 小批量模式（处理前200位导师，10批次）")
    print("3. 完整模式（处理所有9392位导师，约470批次）")
    print("=" * 60)

    mode = input("请选择模式 (1/2/3): ").strip()

    sample_size = {
        '1': 40,
        '2': 200,
        '3': None
    }.get(mode, 40)

    if sample_size:
        print(f"\n将处理前 {sample_size} 位导师...")
    else:
        print(f"\n将处理所有导师（约需 1-1.5 小时）...")
        confirm = input("确认继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("已取消")
            return

    start_time = time.time()

    # Process evaluations
    metrics = await processor.process_with_ai(
        sample_size=sample_size,
        batch_size=20,
        concurrency=5
    )

    elapsed = time.time() - start_time

    # Export results
    output_file = f'mentor_metrics_qwen_batch_{len(metrics)}.json'
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
    print(f"\n生成的文件:")
    print(f"  - {output_file}")
    print(f"  - qwen_outputs/batch_*.json ({len(metrics) // 20 + 1} files)")
    print(f"\n处理的导师数: {len(metrics)}")
    print(f"耗时: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
    print(f"平均每位导师: {elapsed/len(metrics):.2f} 秒")


if __name__ == "__main__":
    asyncio.run(main())
