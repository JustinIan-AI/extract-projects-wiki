#!/usr/bin/env python3
"""
Code-Explorer Subagent 核心模块
负责多文件/跨目录/模式化代码探查
"""

import os
import json
import logging
import re
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CodeExplorer:
    def __init__(self, project_path, depth='standard'):
        self.project_path = project_path
        self.depth = depth
        self.exploration_results = {
            'structure_snapshot': {},
            'candidate_index': [],
            'code_snippets': {},
            'dependency_graph': {},
            'code_patterns': {},
            'exploration_scope': {},
            'exploration_suggestions': []
        }
    
    def explore(self):
        """执行完整的代码探索流程"""
        logging.info(f"开始探索项目: {self.project_path}")
        
        # 1. 任务解析与范围界定
        self._define_exploration_scope()
        
        # 2. 仓库结构全景扫描
        self._scan_repository_structure()
        
        # 3. 批量模式化检索
        self._batch_pattern_search()
        
        # 4. 定向精读与片段提取
        self._extract_code_snippets()
        
        # 5. 关联链路溯源
        self._trace_dependencies()
        
        # 6. 信息聚合与降噪
        self._aggregate_and_clean()
        
        # 7. 结论收敛与边界标注
        self._finalize_results()
        
        logging.info("代码探索完成")
        return self.exploration_results
    
    def _define_exploration_scope(self):
        """界定探索范围"""
        logging.info("界定探索范围")
        self.exploration_scope = {
            'included_dirs': [],
            'excluded_dirs': ['.git', 'node_modules', '__pycache__', 'target', 'build', 'dist'],
            'included_extensions': ['.java', '.js', '.ts', '.vue', '.html', '.css', '.json', '.yml', '.xml'],
            'search_patterns': [
                r'public.*class',
                r'public.*interface',
                r'public.*function',
                r'@Controller',
                r'@Service',
                r'@Repository',
                r'@Entity',
                r'main\s*\(',
                r'public\s+static\s+void\s+main'
            ]
        }
        
        # 识别项目类型并调整范围
        if os.path.exists(os.path.join(self.project_path, 'pom.xml')):
            logging.info("识别到 Maven 项目")
            self.exploration_scope['included_dirs'].extend(['src/main/java', 'src/main/resources'])
        elif os.path.exists(os.path.join(self.project_path, 'package.json')):
            logging.info("识别到 Node.js 项目")
            self.exploration_scope['included_dirs'].extend(['src', 'public'])
    
    def _scan_repository_structure(self):
        """扫描仓库结构"""
        logging.info("扫描仓库结构")
        
        structure = {
            'root': self.project_path,
            'directories': {},
            'key_files': [],
            'module_summary': []
        }
        
        # 递归遍历目录
        for root, dirs, files in os.walk(self.project_path):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in self.exploration_scope['excluded_dirs']]
            
            # 相对路径
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path == '.':
                rel_path = ''
            
            # 收集关键文件
            for file in files:
                if any(file.endswith(ext) for ext in self.exploration_scope['included_extensions']):
                    file_path = os.path.join(rel_path, file) if rel_path else file
                    structure['key_files'].append(file_path)
                    
                    # 识别项目入口文件
                    if file in ['pom.xml', 'package.json', 'application.yml', 'Application.java', 'main.js']:
                        structure['key_files'].append({'path': file_path, 'type': 'entry'})
        
        # 生成模块摘要
        modules = set()
        for file_path in structure['key_files']:
            if isinstance(file_path, dict):
                path = file_path['path']
            else:
                path = file_path
            
            parts = path.split('/')
            if len(parts) > 0 and parts[0]:
                modules.add(parts[0])
        
        for module in sorted(modules):
            structure['module_summary'].append({
                'name': module,
                'file_count': sum(1 for f in structure['key_files'] if isinstance(f, str) and f.startswith(module + '/'))
            })
        
        self.exploration_results['structure_snapshot'] = structure
    
    def _batch_pattern_search(self):
        """批量模式化检索"""
        logging.info("批量模式化检索")
        
        candidate_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in self.exploration_scope['excluded_dirs']]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.exploration_scope['included_extensions']):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_path)
                    
                    # 读取文件内容并搜索模式
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        matches = []
                        for pattern in self.exploration_scope['search_patterns']:
                            pattern_matches = re.findall(pattern, content, re.MULTILINE)
                            if pattern_matches:
                                matches.extend(pattern_matches[:3])  # 限制匹配数量
                        
                        if matches:
                            candidate_files.append({
                                'path': rel_path,
                                'matches': matches[:5],  # 限制匹配数量
                                'match_count': len(matches)
                            })
                    except Exception as e:
                        logging.warning(f"读取文件失败: {file_path}, {str(e)}")
        
        # 按匹配数量排序
        candidate_files.sort(key=lambda x: x['match_count'], reverse=True)
        self.exploration_results['candidate_index'] = candidate_files[:50]  # 限制候选文件数量
    
    def _extract_code_snippets(self):
        """提取代码片段"""
        logging.info("提取代码片段")
        
        snippets = {}
        
        # 处理候选文件
        for candidate in self.exploration_results['candidate_index'][:20]:  # 限制处理文件数量
            file_path = os.path.join(self.project_path, candidate['path'])
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # 提取类和函数定义
                class_snippets = []
                function_snippets = []
                
                for i, line in enumerate(lines):
                    if re.search(r'public.*class|public.*interface', line):
                        # 提取类定义及其上下文
                        start = max(0, i-2)
                        end = min(len(lines), i+5)
                        class_snippets.append({
                            'type': 'class',
                            'content': ''.join(lines[start:end]),
                            'line': i+1
                        })
                    elif re.search(r'public.*function|public.*void|public.*\(.*\)', line):
                        # 提取函数定义及其上下文
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        function_snippets.append({
                            'type': 'function',
                            'content': ''.join(lines[start:end]),
                            'line': i+1
                        })
                
                if class_snippets or function_snippets:
                    snippets[candidate['path']] = {
                        'classes': class_snippets[:3],  # 限制数量
                        'functions': function_snippets[:5]  # 限制数量
                    }
            except Exception as e:
                logging.warning(f"提取代码片段失败: {file_path}, {str(e)}")
        
        self.exploration_results['code_snippets'] = snippets
    
    def _trace_dependencies(self):
        """追踪依赖关系"""
        logging.info("追踪依赖关系")
        
        dependencies = {
            'imports': defaultdict(list),
            'calls': defaultdict(list),
            'module_dependencies': defaultdict(set)
        }
        
        # 处理候选文件
        for candidate in self.exploration_results['candidate_index'][:30]:  # 限制处理文件数量
            file_path = os.path.join(self.project_path, candidate['path'])
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取导入语句
                if candidate['path'].endswith('.java'):
                    import_matches = re.findall(r'import\s+([\w\.]+);', content)
                    for imp in import_matches:
                        dependencies['imports'][candidate['path']].append(imp)
                elif candidate['path'].endswith('.js') or candidate['path'].endswith('.ts'):
                    import_matches = re.findall(r'import\s+.*from\s+[\'"]([^\'"]+)\'"', content)
                    for imp in import_matches:
                        dependencies['imports'][candidate['path']].append(imp)
                
                # 提取模块依赖
                module = candidate['path'].split('/')[0]
                for imp in dependencies['imports'][candidate['path']]:
                    # 简单识别模块依赖
                    if '.' in imp:
                        parts = imp.split('.')
                        if parts[0] in ['com', 'org', 'io'] and len(parts) > 2:
                            dep_module = parts[2]
                            dependencies['module_dependencies'][module].add(dep_module)
            except Exception as e:
                logging.warning(f"追踪依赖失败: {file_path}, {str(e)}")
        
        # 转换为普通字典
        dependencies['module_dependencies'] = {k: list(v) for k, v in dependencies['module_dependencies'].items()}
        self.exploration_results['dependency_graph'] = dependencies
    
    def _aggregate_and_clean(self):
        """信息聚合与降噪"""
        logging.info("信息聚合与降噪")
        
        # 清理重复信息
        seen_files = set()
        cleaned_candidates = []
        for candidate in self.exploration_results['candidate_index']:
            if candidate['path'] not in seen_files:
                seen_files.add(candidate['path'])
                cleaned_candidates.append(candidate)
        self.exploration_results['candidate_index'] = cleaned_candidates
        
        # 识别代码模式
        patterns = {
            'coding_style': [],
            'common_patterns': [],
            'util_classes': []
        }
        
        # 简单识别代码模式
        for file_path, snippets in self.exploration_results['code_snippets'].items():
            # 检查编码风格
            if file_path.endswith('.java'):
                patterns['coding_style'].append('Java 标准编码风格')
            elif file_path.endswith('.js') or file_path.endswith('.ts'):
                patterns['coding_style'].append('JavaScript/TypeScript 编码风格')
            
            # 检查工具类
            if 'util' in file_path.lower() or 'helper' in file_path.lower():
                patterns['util_classes'].append(file_path)
        
        # 去重
        patterns['coding_style'] = list(set(patterns['coding_style']))
        patterns['util_classes'] = list(set(patterns['util_classes']))
        
        self.exploration_results['code_patterns'] = patterns
    
    def _finalize_results(self):
        """最终ize结果"""
        logging.info("最终ize结果")
        
        # 探索范围说明
        scope = {
            'explored_directories': [],
            'excluded_directories': self.exploration_scope['excluded_dirs'],
            'explored_file_types': self.exploration_scope['included_extensions'],
            'limitations': [
                '仅处理前 50 个候选文件',
                '代码片段提取限制数量',
                '依赖分析基于静态导入语句'
            ]
        }
        
        # 收集已探索目录
        for candidate in self.exploration_results['candidate_index']:
            parts = candidate['path'].split('/')
            if len(parts) > 1:
                dir_path = parts[0]
                if dir_path not in scope['explored_directories']:
                    scope['explored_directories'].append(dir_path)
        
        self.exploration_results['exploration_scope'] = scope
        
        # 后续探索建议
        suggestions = [
            '深入分析核心业务模块的实现细节',
            '检查数据库访问层的设计与实现',
            '分析前端与后端的交互接口',
            '评估项目的测试覆盖情况',
            '检查项目的安全配置与最佳实践'
        ]
        
        self.exploration_results['exploration_suggestions'] = suggestions

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    explorer = CodeExplorer(project_path)
    results = explorer.explore()
    
    # 保存结果
    output_file = os.path.join(project_path, '.repo-to-wiki', 'exploration_results.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logging.info(f"探索结果已保存: {output_file}")
