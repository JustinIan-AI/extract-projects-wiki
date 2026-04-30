#!/usr/bin/env python3
"""
repo-to-wiki 统一入口
编排全流程：输入处理 → 扫描 → 知识提取 → Wiki 生成 → 规则生成
"""

import os
import sys
import json
import argparse
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPTS_DIR)

sys.path.insert(0, SCRIPTS_DIR)

from github_fetcher import GitHubFetcher, is_github_url
from scan_engine import ScanEngine
from knowledge_extractor import KnowledgeExtractor
from report_generator import ReportGenerator
from rule_generator import RuleGenerator


def resolve_input(input_path):
    if is_github_url(input_path):
        logging.info(f"检测到 GitHub URL: {input_path}")
        fetcher = GitHubFetcher()
        local_path = fetcher.clone_repo(input_path)
        return local_path, fetcher
    elif os.path.isdir(input_path):
        logging.info(f"检测到本地路径: {input_path}")
        return os.path.abspath(input_path), None
    else:
        raise ValueError(f"无效的输入路径: {input_path}")


def phase0_input(input_path, output_dir):
    logging.info("=" * 60)
    logging.info("Phase 0: 输入处理")
    logging.info("=" * 60)

    local_path, fetcher = resolve_input(input_path)
    logging.info(f"项目路径: {local_path}")
    logging.info(f"输出目录: {output_dir}")

    return local_path, fetcher


def phase1_scan(local_path, depth='standard', force=False):
    logging.info("=" * 60)
    logging.info("Phase 1: 项目扫描")
    logging.info("=" * 60)

    engine = ScanEngine(local_path, depth=depth, force=force)
    scan_result = engine.scan()

    tech_stack = scan_result.get('tech_stack', {})
    logging.info(f"技术栈: {tech_stack}")
    logging.info(f"文件统计: {scan_result.get('file_stats', {})}")

    return scan_result


def phase2_extract(local_path, scan_result):
    logging.info("=" * 60)
    logging.info("Phase 2: 知识提取")
    logging.info("=" * 60)

    extractor = KnowledgeExtractor(local_path, scan_result)
    knowledge = extractor.extract()

    features_count = len(knowledge.get('business_logic', {}).get('features', []))
    processes_count = len(knowledge.get('core_processes', []))
    logging.info(f"业务功能: {features_count} 个")
    logging.info(f"核心流程: {processes_count} 个")

    return knowledge


def phase3_wiki(local_path, scan_result, knowledge, output_dir):
    logging.info("=" * 60)
    logging.info("Phase 3: Wiki 生成")
    logging.info("=" * 60)

    wiki_dir = os.path.join(output_dir, 'wiki')
    generator = ReportGenerator(local_path, scan_result, knowledge)
    generator.generate(wiki_dir)

    logging.info(f"Wiki 文档已生成到: {wiki_dir}")


def phase4_rules(local_path, scan_result, knowledge, output_dir, tools=None):
    logging.info("=" * 60)
    logging.info("Phase 4: 规则文件生成")
    logging.info("=" * 60)

    generator = RuleGenerator(local_path, scan_result, knowledge)
    generator.generate_all(output_dir, tools=tools)

    logging.info(f"规则文件已生成到: {output_dir}")


def phase5_summary(output_dir):
    logging.info("=" * 60)
    logging.info("Phase 5: 生成摘要")
    logging.info("=" * 60)

    generated_files = []
    for root, dirs, files in os.walk(output_dir):
        for f in files:
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, output_dir)
            size = os.path.getsize(filepath)
            generated_files.append({'path': relpath, 'size': size})

    logging.info(f"共生成 {len(generated_files)} 个文件:")
    for f in generated_files:
        size_str = f"{f['size']}B" if f['size'] < 1024 else f"{f['size'] / 1024:.1f}KB"
        logging.info(f"  {f['path']} ({size_str})")

    return generated_files


def run(input_path, output_dir=None, depth='standard', force=False,
        wiki_only=False, rules_only=False, tools=None):
    start_time = time.time()

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(input_path)
                                  if os.path.isdir(input_path)
                                  else os.getcwd(), 'docs')

    os.makedirs(output_dir, exist_ok=True)

    fetcher = None
    try:
        local_path, fetcher = phase0_input(input_path, output_dir)
        scan_result = phase1_scan(local_path, depth=depth, force=force)
        knowledge = phase2_extract(local_path, scan_result)

        if not rules_only:
            phase3_wiki(local_path, scan_result, knowledge, output_dir)

        if not wiki_only:
            phase4_rules(local_path, scan_result, knowledge, output_dir, tools=tools)

        generated_files = phase5_summary(output_dir)

        elapsed = time.time() - start_time
        logging.info(f"全流程完成，耗时 {elapsed:.1f}s，共生成 {len(generated_files)} 个文件")

        return {
            'output_dir': output_dir,
            'files': generated_files,
            'elapsed': elapsed,
            'tech_stack': scan_result.get('tech_stack', {}),
        }

    finally:
        if fetcher:
            fetcher.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description='repo-to-wiki: 分析代码仓库，生成双轨知识库和 AI 编程规则文件'
    )
    parser.add_argument('input', help='本地项目路径或 GitHub URL')
    parser.add_argument('-o', '--output', default=None, help='输出目录（默认: 项目目录/docs）')
    parser.add_argument('-d', '--depth', choices=['quick', 'standard', 'deep'],
                        default='standard', help='扫描深度（默认: standard）')
    parser.add_argument('-f', '--force', action='store_true', help='强制重新扫描，忽略缓存')
    parser.add_argument('--wiki-only', action='store_true', help='只生成 Wiki 文档')
    parser.add_argument('--rules-only', action='store_true', help='只生成规则文件')
    parser.add_argument('--tools', default=None,
                        help='目标工具，逗号分隔（claude,agents,cursor,copilot）')

    args = parser.parse_args()

    tools = None
    if args.tools:
        tools = [t.strip() for t in args.tools.split(',')]

    result = run(
        input_path=args.input,
        output_dir=args.output,
        depth=args.depth,
        force=args.force,
        wiki_only=args.wiki_only,
        rules_only=args.rules_only,
        tools=tools,
    )

    print(f"\n✅ 完成！输出目录: {result['output_dir']}")
    print(f"   技术栈: {result['tech_stack']}")
    print(f"   生成文件: {len(result['files'])} 个")
    print(f"   耗时: {result['elapsed']:.1f}s")


if __name__ == '__main__':
    main()
