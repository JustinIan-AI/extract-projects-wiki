#!/usr/bin/env python3
"""
报告生成模块
生成双轨知识库文档（human + AI）
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ReportGenerator:
    def __init__(self, project_path, scan_result, knowledge):
        self.project_path = project_path
        self.scan_result = scan_result
        self.knowledge = knowledge

    def generate(self, output_dir):
        """生成报告"""
        try:
            logging.info(f"开始生成报告，输出目录: {output_dir}")

            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(os.path.join(output_dir, 'human'), exist_ok=True)
            os.makedirs(os.path.join(output_dir, 'ai'), exist_ok=True)

            # 生成给人看的文档
            self._generate_project_wiki(output_dir)
            self._generate_business_qa(output_dir)
            self._generate_architecture(output_dir)

            # 生成给 AI 看的文档
            self._generate_ai_docs(output_dir)

            logging.info("报告生成完成")
            return True

        except Exception as e:
            logging.error(f"报告生成过程中出错: {str(e)}")
            return False

    def _generate_project_wiki(self, output_dir):
        """生成项目综合手册"""
        content = f"# {self.scan_result.get('project_name', '项目')} - 项目 Wiki\n\n"

        # 项目概览
        content += "## 项目概览\n\n"
        content += f"| 属性 | 值 |\n|------|-----|\n"
        content += f"| **项目名称** | {self.scan_result.get('project_name', 'Unknown')} |\n"
        content += f"| **技术栈** | {self.scan_result.get('tech_stack', 'Unknown')} |\n"
        content += f"| **总文件数** | {self.scan_result.get('file_count', 0)} |\n"
        content += f"| **代码总行数** | {self.scan_result.get('total_lines', 0)} |\n"
        content += f"| **主要模块** | {len(self.scan_result.get('modules', []))} 个核心模块 |\n\n"

        # 系统架构图
        content += "## 系统架构图\n\n"
        content += self.knowledge.get('architecture_diagram', '') + "\n\n"

        # 模块结构
        content += "## 模块结构\n\n"
        content += self.knowledge.get('module_structure', '') + "\n\n"

        # 核心功能清单
        content += "## 核心功能清单\n\n"
        for feature in self.knowledge.get('business_logic', {}).get('features', []):
            content += f"- **{feature['name']}**：{feature['description']}\n"
        content += "\n"

        # 核心业务流程
        content += "## 核心业务流程\n\n"
        for process in self.knowledge.get('core_processes', [])[:5]:
            content += f"### {process.get('process', process.get('name', 'Unknown'))}\n"
            content += f"{process.get('description', '')}\n\n"
            if 'steps' in process:
                content += "**步骤**:\n"
                for step in process['steps']:
                    content += f"- {step}\n"
            content += "\n"

        # 专业术语表
        content += "## 专业术语表\n\n"
        content += "| 术语 | 说明 |\n|------|------|\n"
        for term in self.knowledge.get('terms', []):
            content += f"| {term['name']} | {term['description']} |\n"
        content += "\n"

        # 核心类清单
        content += "## 核心类清单\n\n"
        core_classes = self.knowledge.get('core_classes', {})

        content += "### Controller 层\n"
        content += "| 类名 | 功能 |\n|------|------|\n"
        for cls in core_classes.get('controllers', [])[:15]:
            content += f"| {cls['name']} | {cls['function']} |\n"
        content += "\n"

        content += "### Service 层\n"
        content += "| 类名 | 功能 |\n|------|------|\n"
        for cls in core_classes.get('services', [])[:10]:
            content += f"| {cls['name']} | {cls['function']} |\n"
        content += "\n"

        content += "### Mapper 层\n"
        content += "| 类名 | 功能 |\n|------|------|\n"
        for cls in core_classes.get('mappers', [])[:10]:
            content += f"| {cls['name']} | {cls['function']} |\n"
        content += "\n"

        # 类间调用链路
        content += "## 类间调用链路\n\n"
        for chain in self.knowledge.get('call_chains', [])[:3]:
            content += f"### {chain['name']}\n"
            content += f"```\n{chain['flow']}\n```\n\n"

        # 新手入门必问的业务问题清单
        content += "## 新手入门必问的业务问题清单\n\n"
        questions = self.knowledge.get('questions', {})

        content += "### 基础概念\n"
        for i, q in enumerate(questions.get('basic', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        content += "### 系统配置\n"
        for i, q in enumerate(questions.get('config', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        content += "### 功能开发\n"
        for i, q in enumerate(questions.get('development', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        content += "### 部署运维\n"
        for i, q in enumerate(questions.get('deployment', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        with open(os.path.join(output_dir, 'human', 'PROJECT_WIKI.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("PROJECT_WIKI.md 生成完成")

    def _generate_business_qa(self, output_dir):
        """生成业务问卷"""
        content = "# 业务问卷\n\n"
        content += "## 请回答以下问题以完善业务逻辑理解\n\n"

        questions = self.knowledge.get('questions', {})

        content += "### 基础概念\n"
        for i, q in enumerate(questions.get('basic', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        content += "### 系统配置\n"
        for i, q in enumerate(questions.get('config', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        content += "### 功能开发\n"
        for i, q in enumerate(questions.get('development', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        content += "### 部署运维\n"
        for i, q in enumerate(questions.get('deployment', []), 1):
            content += f"{i}. {q}\n"
        content += "\n"

        # 各功能模块追问
        content += "### 各功能模块追问\n\n"
        for feature in self.knowledge.get('business_logic', {}).get('features', []):
            content += f"#### {feature['name']}\n"
            content += "- 详细流程是怎样的？\n"
            content += "- 有哪些特殊规则？\n"
            content += "- 与其他功能的关系是什么？\n\n"

        with open(os.path.join(output_dir, 'human', 'BUSINESS_QA.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("BUSINESS_QA.md 生成完成")

    def _generate_architecture(self, output_dir):
        """生成架构文档"""
        content = "# 架构文档\n\n"

        # 架构层次
        content += "## 架构层次\n\n"
        content += self.knowledge.get('architecture_diagram', '') + "\n\n"

        # 模块依赖
        content += "## 模块依赖\n\n"
        content += self.knowledge.get('module_dependencies', '') + "\n\n"

        # 模块职责
        content += "## 模块职责\n\n"
        for module in self.knowledge.get('architecture', {}).get('modules', []):
            content += f"### {module['name']}\n"
            content += f"- **类型**: {module.get('type', 'Unknown')}\n"
            content += f"- **职责**: {module.get('responsibility', 'Unknown')}\n"
            content += f"- **关键包**: {module.get('key_packages', 'Unknown')}\n\n"

        # 安全架构
        content += "## 安全架构\n\n"
        content += "### 认证流程\n"
        content += "```\n"
        content += self.knowledge.get('auth_flow', '') + "\n"
        content += "```\n\n"

        content += "### 授权流程\n"
        content += "```\n"
        content += self.knowledge.get('authz_flow', '') + "\n"
        content += "```\n\n"

        content += "### 数据权限\n"
        content += "```\n"
        content += self.knowledge.get('data_scope_flow', '') + "\n"
        content += "```\n\n"

        with open(os.path.join(output_dir, 'human', 'ARCHITECTURE.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("ARCHITECTURE.md 生成完成")

    def _generate_ai_docs(self, output_dir):
        """生成 AI 知识库文档"""
        # L0: 技术约束
        self._generate_l0_profile(output_dir)

        # L1: 系统架构
        self._generate_l1_architecture(output_dir)

        # L2: 模块分析
        self._generate_l2_modules(output_dir)

        # L3: 业务逻辑
        self._generate_l3_business(output_dir)

        # AI 路由总控
        self._generate_index_json(output_dir)

    def _generate_l0_profile(self, output_dir):
        """生成 L0 技术约束"""
        content = "# 技术约束\n\n"

        content += "## 项目技术栈\n"
        tech_stack = self.scan_result.get('tech_stack', {})
        for key, value in tech_stack.items():
            content += f"- **{key}**: {value}\n"
        content += "\n"

        content += "## 代码规范\n"
        for rule in self.knowledge.get('coding_standards', []):
            content += f"- {rule}\n"
        content += "\n"

        content += "## 系统约束\n"
        for constraint in self.knowledge.get('system_constraints', []):
            content += f"- {constraint}\n"
        content += "\n"

        content += "## 安全约束\n"
        for constraint in self.knowledge.get('security_constraints', []):
            content += f"- {constraint}\n"
        content += "\n"

        content += "## 性能约束\n"
        for constraint in self.knowledge.get('performance_constraints', []):
            content += f"- {constraint}\n"
        content += "\n"

        with open(os.path.join(output_dir, 'ai', 'L0_profile.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("L0_profile.md 生成完成")

    def _generate_l1_architecture(self, output_dir):
        """生成 L1 系统架构"""
        content = "# 系统架构\n\n"

        content += "## 模块依赖关系\n\n"
        content += self.knowledge.get('module_dependencies', '') + "\n\n"

        content += "## 安全架构\n\n"
        content += "### 认证流程\n"
        content += "```\n" + self.knowledge.get('auth_flow', '') + "\n```\n\n"

        content += "### 授权流程\n"
        content += "```\n" + self.knowledge.get('authz_flow', '') + "\n```\n\n"

        content += "### 数据权限\n"
        content += "```\n" + self.knowledge.get('data_scope_flow', '') + "\n```\n\n"

        with open(os.path.join(output_dir, 'ai', 'L1_architecture.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("L1_architecture.md 生成完成")

    def _generate_l2_modules(self, output_dir):
        """生成 L2 模块分析"""
        content = "# 模块分析\n\n"
        content += "## 核心模块\n\n"

        for module in self.knowledge.get('architecture', {}).get('modules', []):
            content += f"### {module['name']}\n"
            content += f"- **层次**: {module.get('layer', 'Unknown')}\n"
            content += f"- **职责**: {module.get('responsibility', 'Unknown')}\n"

            if 'key_packages' in module:
                content += "- **关键包**:\n"
                for pkg in module['key_packages']:
                    content += f"  - `{pkg['path']}` - {pkg['description']}\n"

            if 'core_classes' in module:
                content += "- **核心类**:\n"
                for cls in module['core_classes']:
                    content += f"  - {cls['name']}: {cls['function']}\n"

            content += "\n"

        with open(os.path.join(output_dir, 'ai', 'L2_modules.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("L2_modules.md 生成完成")

    def _generate_l3_business(self, output_dir):
        """生成 L3 业务逻辑"""
        content = "# 业务逻辑\n\n"

        # 核心流程
        content += "## 核心流程\n\n"
        for process in self.knowledge.get('core_processes', []):
            content += f"### {process.get('process', process.get('name', 'Unknown'))}\n"
            content += f"- **模块**: {process.get('module', 'Unknown')}\n"
            content += "- **步骤**:\n"
            for step in process.get('steps', []):
                content += f"  {step}\n"
            content += "\n"

        # 业务规则
        content += "## 业务规则\n\n"
        for rule_category, rules in self.knowledge.get('business_rules', {}).items():
            content += f"### {rule_category}\n"
            for rule in rules:
                content += f"{rule}\n"
            content += "\n"

        # 业务实体关系
        content += "## 业务实体关系\n\n"
        content += "```\n" + self.knowledge.get('entity_relations', '') + "\n```\n\n"

        # 业务功能矩阵
        content += "## 业务功能矩阵\n\n"
        content += "| 功能模块 | 涉及模块 | 核心类 | 数据库表 |\n"
        content += "|---------|---------|--------|---------|\n"
        for row in self.knowledge.get('function_matrix', []):
            content += f"| {row['feature']} | {row['modules']} | {row['classes']} | {row['tables']} |\n"
        content += "\n"

        with open(os.path.join(output_dir, 'ai', 'L3_business.md'), 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info("L3_business.md 生成完成")

    def _generate_index_json(self, output_dir):
        """生成 AI 路由总控"""
        index_data = {
            'project': self.project_path,
            'project_name': self.scan_result.get('project_name', 'Unknown'),
            'description': self.scan_result.get('description', ''),
            'tech_stack': self.scan_result.get('tech_stack', {}),
            'modules': [m['name'] for m in self.knowledge.get('architecture', {}).get('modules', [])],
            'features': [f['name'] for f in self.knowledge.get('business_logic', {}).get('features', [])],
            'file_count': self.scan_result.get('file_count', 0),
            'total_lines': self.scan_result.get('total_lines', 0)
        }

        with open(os.path.join(output_dir, 'ai', '_index.json'), 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        logging.info("_index.json 生成完成")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        project_path = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = '/tmp/test_wiki'

    # 读取扫描结果
    scan_result_file = os.path.join(project_path, '.repo-to-wiki', 'scan_result.json')
    scan_result = {}
    if os.path.exists(scan_result_file):
        with open(scan_result_file, 'r', encoding='utf-8') as f:
            scan_result = json.load(f)

    # 读取知识提取结果
    knowledge_file = os.path.join(project_path, '.repo-to-wiki', 'knowledge.json')
    knowledge = {}
    if os.path.exists(knowledge_file):
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)

    generator = ReportGenerator(project_path, scan_result, knowledge)
    success = generator.generate(output_dir)
    if success:
        print(f"报告生成完成，输出目录: {output_dir}")
    else:
        print("报告生成失败")
