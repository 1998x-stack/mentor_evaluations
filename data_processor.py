#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Processor Module for Mentor Evaluation System
Handles data merging, dimension extraction, and metric calculation
"""

import pandas as pd
import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class DimensionExtractor:
    """Extract evaluation dimensions from comments"""

    # Define evaluation dimensions
    DIMENSIONS = {
        '导师能力': ['导师能力', '科研能力', '学术水平', '指导能力'],
        '经费情况': ['经费发放', '学术经费', '科研经费', '经费'],
        '学生补助': ['学生补助', '每月补贴', '补助', '补贴', '工资'],
        '师生关系': ['与学生关系', '师生关系', '对待学生'],
        '工作时间': ['工作时间', '加班', '休息'],
        '毕业去向': ['学生毕业去向', '毕业去向', '就业', '发展'],
    }

    # Sentiment keywords
    POSITIVE_KEYWORDS = [
        '好', '优秀', '不错', '负责', '和蔼', '尊重', '充足', '高',
        '认真', '耐心', '支持', '关心', '帮助', '友善'
    ]

    NEGATIVE_KEYWORDS = [
        '差', '不好', '糟糕', '压榨', '不尊重', '威胁', '延期', '不足',
        '低', '少', '无', '苛刻', '严苛', '畜生', '奴隶', '不管'
    ]

    def extract_dimensions(self, comment: str) -> Dict[str, str]:
        """Extract dimension mentions from a comment"""
        dimensions = {}

        for dim_key, keywords in self.DIMENSIONS.items():
            for keyword in keywords:
                if keyword in comment:
                    # Extract the content after the keyword
                    pattern = f"{keyword}[：:](.*?)(?:导师能力|经费|补助|关系|时间|去向|利益相关|$)"
                    match = re.search(pattern, comment)
                    if match:
                        content = match.group(1).strip()
                        dimensions[dim_key] = content
                        break

        return dimensions

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text
        Returns a score between 0-10 (0=very negative, 5=neutral, 10=very positive)
        """
        if not text or text == '不了解' or text == '不清楚':
            return 5.0  # Neutral for unknown

        positive_count = sum(1 for keyword in self.POSITIVE_KEYWORDS if keyword in text)
        negative_count = sum(1 for keyword in self.NEGATIVE_KEYWORDS if keyword in text)

        # Calculate base score
        if positive_count > negative_count:
            score = 6.0 + min(positive_count, 4) * 0.75
        elif negative_count > positive_count:
            score = 4.0 - min(negative_count, 4) * 0.75
        else:
            score = 5.0

        # Clamp between 0-10
        return max(0.0, min(10.0, score))


class MentorDataProcessor:
    """Main data processor for mentor evaluation system"""

    def __init__(self):
        self.extractor = DimensionExtractor()
        self.mentor_data = None
        self.evaluation_data = None
        self.merged_data = None

    def load_data(self, mentor_file: str, evaluation_file: str):
        """Load data from xls files"""
        print("📂 Loading data files...")
        self.mentor_data = pd.read_excel(mentor_file, engine='xlrd')
        self.evaluation_data = pd.read_excel(evaluation_file, engine='xlrd')

        # Clean NaN values immediately
        self.mentor_data = self.mentor_data.fillna('未知')
        self.evaluation_data = self.evaluation_data.fillna('未知')

        print(f"✓ Loaded {len(self.mentor_data)} mentors and {len(self.evaluation_data)} evaluations")

    def merge_data(self) -> pd.DataFrame:
        """Merge mentor info with evaluations"""
        print("\n🔄 Merging data...")

        # Merge on 编号
        merged = pd.merge(
            self.evaluation_data,
            self.mentor_data,
            on='编号',
            how='left'
        )

        self.merged_data = merged
        print(f"✓ Merged {len(merged)} records")

        return merged

    def process_evaluations(self) -> Dict:
        """Process all evaluations and calculate metrics for each mentor"""
        print("\n⚙️ Processing evaluations...")

        if self.merged_data is None:
            self.merge_data()

        mentor_metrics = defaultdict(lambda: {
            'name': '',
            'school': '',
            'department': '',
            'evaluations': [],
            'dimensions': defaultdict(list),
            'dimension_scores': {},
            'total_score': 0.0,
            'evaluation_count': 0
        })

        # Process each evaluation
        for idx, row in self.merged_data.iterrows():
            mentor_id = row['编号']
            comment = str(row['评价'])

            # Store basic info
            if not mentor_metrics[mentor_id]['name']:
                mentor_metrics[mentor_id]['name'] = row.get('姓名', '')
                mentor_metrics[mentor_id]['school'] = row.get('学校', '')
                mentor_metrics[mentor_id]['department'] = row.get('专业', '')

            # Extract dimensions
            dimensions = self.extractor.extract_dimensions(comment)

            # Store evaluation
            mentor_metrics[mentor_id]['evaluations'].append({
                'comment': comment,
                'dimensions': dimensions
            })
            mentor_metrics[mentor_id]['evaluation_count'] += 1

            # Collect dimension scores
            for dim_key, dim_content in dimensions.items():
                score = self.extractor.analyze_sentiment(dim_content)
                mentor_metrics[mentor_id]['dimensions'][dim_key].append(score)

        # Calculate average scores for each dimension
        for mentor_id, data in mentor_metrics.items():
            dimension_scores = {}
            total = 0.0
            count = 0

            for dim_key, scores in data['dimensions'].items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    dimension_scores[dim_key] = round(avg_score, 2)
                    total += avg_score
                    count += 1

            data['dimension_scores'] = dimension_scores
            data['total_score'] = round(total / count if count > 0 else 5.0, 2)

            # Clean up temporary dimensions list
            del data['dimensions']

        print(f"✓ Processed {len(mentor_metrics)} mentors")

        return dict(mentor_metrics)

    def export_to_csv(self, output_file: str = 'merged_data.csv'):
        """Export merged data to CSV"""
        if self.merged_data is None:
            self.merge_data()

        print(f"\n💾 Exporting to {output_file}...")
        self.merged_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ Exported {len(self.merged_data)} records")

    def export_mentor_metrics(self, output_file: str = 'mentor_metrics.json'):
        """Export calculated mentor metrics to JSON"""
        metrics = self.process_evaluations()

        print(f"\n💾 Exporting metrics to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"✓ Exported metrics for {len(metrics)} mentors")

        return metrics

    def generate_summary_stats(self) -> Dict:
        """Generate summary statistics"""
        metrics = self.process_evaluations()

        schools = defaultdict(int)
        total_scores = []
        dimension_counts = Counter()

        for data in metrics.values():
            if data['school']:
                schools[data['school']] += 1
            total_scores.append(data['total_score'])
            dimension_counts.update(data['dimension_scores'].keys())

        stats = {
            'total_mentors': len(metrics),
            'total_schools': len(schools),
            'top_schools': dict(sorted(schools.items(), key=lambda x: x[1], reverse=True)[:10]),
            'average_score': round(sum(total_scores) / len(total_scores), 2) if total_scores else 0,
            'dimension_coverage': dict(dimension_counts)
        }

        return stats


def main():
    """Main execution"""
    print("="*60)
    print("Mentor Evaluation Data Processor")
    print("="*60)

    # Initialize processor
    processor = MentorDataProcessor()

    # Load data
    processor.load_data('导师信息.xls', '评价信息.xls')

    # Merge and export CSV
    processor.export_to_csv('merged_data.csv')

    # Process evaluations and export metrics
    metrics = processor.export_mentor_metrics('mentor_metrics.json')

    # Generate and display summary statistics
    stats = processor.generate_summary_stats()

    print("\n" + "="*60)
    print("📊 Summary Statistics")
    print("="*60)
    print(f"Total Mentors with Evaluations: {stats['total_mentors']}")
    print(f"Total Schools: {stats['total_schools']}")
    print(f"Average Overall Score: {stats['average_score']}/10")
    print(f"\n🏆 Top 10 Schools by Mentor Count:")
    for i, (school, count) in enumerate(stats['top_schools'].items(), 1):
        print(f"  {i}. {school}: {count} mentors")

    print(f"\n📋 Dimension Coverage:")
    for dim, count in stats['dimension_coverage'].items():
        print(f"  {dim}: {count} mentors")

    print("\n" + "="*60)
    print("✅ Processing Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
