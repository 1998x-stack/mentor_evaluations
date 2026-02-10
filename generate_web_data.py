#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate web-ready data files for GitHub Pages
Organizes mentor data by school and creates optimized JSON files
"""

import json
from collections import defaultdict
from typing import Dict, List
import os


def generate_school_data(mentor_metrics: Dict) -> List[Dict]:
    """Generate school list with statistics"""
    school_stats = defaultdict(lambda: {
        'mentor_count': 0,
        'total_evaluations': 0,
        'avg_score': [],
        'departments': set()
    })

    for mentor_id, data in mentor_metrics.items():
        school = str(data.get('school', '未知'))
        # Clean various forms of NaN/None
        if not school or school in ['nan', 'NaN', 'None', '', 'null', '未知']:
            school = '未知学校'

        school_stats[school]['mentor_count'] += 1
        school_stats[school]['total_evaluations'] += data.get('evaluation_count', 0)
        school_stats[school]['avg_score'].append(data.get('total_score', 5.0))

        dept = str(data.get('department', '未知'))
        if dept and dept not in ['nan', 'NaN', 'None', '', 'null', '未知']:
            school_stats[school]['departments'].add(dept)

    # Convert to list format
    schools = []
    for school_name, stats in school_stats.items():
        avg_score = sum(stats['avg_score']) / len(stats['avg_score']) if stats['avg_score'] else 5.0

        schools.append({
            'name': school_name,
            'mentorCount': stats['mentor_count'],
            'evaluationCount': stats['total_evaluations'],
            'averageScore': round(avg_score, 2),
            'departmentCount': len(stats['departments'])
        })

    # Sort by mentor count
    schools.sort(key=lambda x: x['mentorCount'], reverse=True)

    return schools


def generate_mentor_list_by_school(mentor_metrics: Dict) -> Dict[str, List]:
    """Generate mentor lists organized by school"""
    mentors_by_school = defaultdict(list)

    for mentor_id, data in mentor_metrics.items():
        school = str(data.get('school', '未知'))
        if not school or school in ['nan', 'NaN', 'None', '', 'null', '未知']:
            school = '未知学校'

        name = str(data.get('name', '未知'))
        if not name or name in ['nan', 'NaN', 'None', '', 'null']:
            name = '未知导师'

        dept = str(data.get('department', '未知'))
        if not dept or dept in ['nan', 'NaN', 'None', '', 'null']:
            dept = '未知院系'

        # Support both old format (evaluation_count) and new format (evaluationCount)
        eval_count = data.get('evaluationCount', data.get('evaluation_count', 0))
        total_score = data.get('totalScore', data.get('total_score', 5.0))
        dim_scores = data.get('dimensionScores', data.get('dimension_scores', {}))

        mentor_summary = {
            'id': mentor_id,
            'name': name,
            'department': dept,
            'evaluationCount': eval_count,
            'totalScore': total_score,
            'dimensionScores': dim_scores
        }

        mentors_by_school[school].append(mentor_summary)

    # Sort mentors within each school by evaluation count
    for school in mentors_by_school:
        mentors_by_school[school].sort(
            key=lambda x: x['evaluationCount'],
            reverse=True
        )

    return dict(mentors_by_school)


def generate_mentor_details(mentor_metrics: Dict, output_dir: str):
    """Generate individual mentor detail files"""
    details_dir = os.path.join(output_dir, 'mentors')
    os.makedirs(details_dir, exist_ok=True)

    count = 0
    for mentor_id, data in mentor_metrics.items():
        # Clean all string fields
        name = str(data.get('name', '未知'))
        if not name or name in ['nan', 'NaN', 'None', '', 'null']:
            name = '未知导师'

        school = str(data.get('school', '未知'))
        if not school or school in ['nan', 'NaN', 'None', '', 'null']:
            school = '未知学校'

        dept = str(data.get('department', '未知'))
        if not dept or dept in ['nan', 'NaN', 'None', '', 'null']:
            dept = '未知院系'

        # Support both old and new format
        eval_count = data.get('evaluationCount', data.get('evaluation_count', 0))
        total_score = data.get('totalScore', data.get('total_score', 5.0))
        dim_scores = data.get('dimensionScores', data.get('dimension_scores', {}))
        dim_reasons = data.get('dimensionReasons', data.get('dimension_reasons', {}))
        overall_rec = data.get('overallRecommendation', data.get('overall_recommendation', ''))

        detail = {
            'id': mentor_id,
            'name': name,
            'school': school,
            'department': dept,
            'evaluationCount': eval_count,
            'totalScore': total_score,
            'dimensionScores': dim_scores,
            'dimensionReasons': dim_reasons,  # Add reasons
            'overallRecommendation': overall_rec,  # Add AI recommendation
            'evaluations': [
                {
                    'comment': eval_data['comment'],
                    'dimensions': eval_data.get('dimensions', {})
                }
                for eval_data in data.get('evaluations', [])
            ]
        }

        # Save individual file
        file_path = os.path.join(details_dir, f"{mentor_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(detail, f, ensure_ascii=False, indent=2)

        count += 1
        if count % 1000 == 0:
            print(f"  Generated {count} mentor detail files...")

    print(f"✓ Generated {count} mentor detail files")


def main():
    print("="*60)
    print("Web Data Generator for Mentor Evaluation System")
    print("="*60)

    # Load mentor metrics
    print("\n📂 Loading mentor metrics...")
    with open('mentor_metrics.json', 'r', encoding='utf-8') as f:
        mentor_metrics = json.load(f)
    print(f"✓ Loaded {len(mentor_metrics)} mentors")

    # Create output directory
    output_dir = 'docs/data'
    os.makedirs(output_dir, exist_ok=True)

    # Generate school list
    print("\n🏫 Generating school list...")
    schools = generate_school_data(mentor_metrics)
    with open(os.path.join(output_dir, 'schools.json'), 'w', encoding='utf-8') as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)
    print(f"✓ Generated data for {len(schools)} schools")

    # Generate mentor lists by school
    print("\n👨‍🏫 Generating mentor lists by school...")
    mentors_by_school = generate_mentor_list_by_school(mentor_metrics)
    with open(os.path.join(output_dir, 'mentors_by_school.json'), 'w', encoding='utf-8') as f:
        json.dump(mentors_by_school, f, ensure_ascii=False, indent=2)
    print(f"✓ Generated mentor lists for {len(mentors_by_school)} schools")

    # Generate individual mentor detail files
    print("\n📄 Generating individual mentor detail files...")
    generate_mentor_details(mentor_metrics, output_dir)

    # Generate metadata
    print("\n📊 Generating metadata...")
    metadata = {
        'generatedAt': '2026-02-10',
        'totalMentors': len(mentor_metrics),
        'totalSchools': len(schools),
        'totalEvaluations': sum(school['evaluationCount'] for school in schools),
        'dimensions': [
            '导师能力',
            '经费情况',
            '学生补助',
            '师生关系',
            '工作时间',
            '毕业去向'
        ]
    }
    with open(os.path.join(output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("✓ Generated metadata")

    print("\n" + "="*60)
    print("✅ Web Data Generation Complete!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - docs/data/schools.json ({len(schools)} schools)")
    print(f"  - docs/data/mentors_by_school.json")
    print(f"  - docs/data/mentors/*.json ({len(mentor_metrics)} files)")
    print(f"  - docs/data/metadata.json")


if __name__ == "__main__":
    main()
