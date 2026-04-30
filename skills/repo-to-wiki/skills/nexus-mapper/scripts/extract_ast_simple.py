#!/usr/bin/env python3
"""
简化版 AST 提取器 - 使用独立的语言包（避免网络下载）
"""

import os
import sys
import json
from pathlib import Path
from tree_sitter import Language, Parser
from tree_sitter_python import language as python_lang
from tree_sitter_javascript import language as js_lang

# 语言映射
LANGUAGE_MAP = {
    '.py': ('python', python_lang),
    '.js': ('javascript', js_lang),
}

def get_language_for_file(filepath):
    """根据文件扩展名获取语言"""
    ext = Path(filepath).suffix.lower()
    if ext in LANGUAGE_MAP:
        lang_name, lang_func = LANGUAGE_MAP[ext]
        try:
            return Language(lang_func())
        except Exception as e:
            print(f"Warning: Failed to load language for {ext}: {e}", file=sys.stderr)
            return None
    return None

def parse_file(filepath, repo_path):
    """解析单个文件"""
    language = get_language_for_file(filepath)
    if not language:
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Failed to read {filepath}: {e}", file=sys.stderr)
        return None
    
    lines = content.count('\n') + 1
    
    parser = Parser(language)
    try:
        tree = parser.parse(bytes(content, 'utf-8'))
        root_node = tree.root_node
        
        # 提取模块/类/函数节点
        nodes = []
        edges = []
        
        rel_path = os.path.relpath(filepath, repo_path)
        module_id = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '').replace('.js', '')
        
        # 添加模块节点
        module_node = {
            "id": module_id,
            "type": "Module",
            "label": Path(filepath).stem,
            "path": rel_path,
            "lines": lines,
            "lang": language.name if hasattr(language, 'name') else 'unknown'
        }
        nodes.append(module_node)
        
        # 使用递归遍历提取类和函数
        def traverse_node(node, parent_id=None):
            """递归遍历节点"""
            if node.type == 'class_definition' and language.name == 'python':
                # 查找类名
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = content[child.start_byte:child.end_byte]
                        class_id = f"{module_id}.{class_name}"
                        nodes.append({
                            "id": class_id,
                            "type": "Class",
                            "label": class_name,
                            "path": rel_path,
                            "parent": parent_id or module_id,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1
                        })
                        edges.append({
                            "source": parent_id or module_id,
                            "target": class_id,
                            "type": "contains"
                        })
                        # 继续遍历类内部
                        for subchild in node.children:
                            traverse_node(subchild, class_id)
                        return
                        
            elif node.type == 'function_definition' and language.name == 'python':
                # 查找函数名
                for child in node.children:
                    if child.type == 'identifier':
                        func_name = content[child.start_byte:child.end_byte]
                        func_id = f"{parent_id or module_id}.{func_name}"
                        nodes.append({
                            "id": func_id,
                            "type": "Function",
                            "label": func_name,
                            "path": rel_path,
                            "parent": parent_id or module_id,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1
                        })
                        edges.append({
                            "source": parent_id or module_id,
                            "target": func_id,
                            "type": "contains"
                        })
                        return
            
            # 递归遍历子节点
            for child in node.children:
                traverse_node(child, parent_id)
        
        # 开始遍历
        traverse_node(root_node)
        
        return {"nodes": nodes, "edges": edges}
        
    except Exception as e:
        print(f"Warning: Failed to parse {filepath}: {e}", file=sys.stderr)
        return {"nodes": [{"id": module_id, "type": "Module", "label": Path(filepath).stem, "path": rel_path, "lines": lines, "lang": language.name if hasattr(language, 'name') else 'unknown'}], "edges": []}

def scan_repository(repo_path, exclude_dirs=None):
    """扫描仓库中的所有支持文件"""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '.nexus-map', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.pytest_cache', '.mypy_cache'}
    
    all_nodes = []
    all_edges = []
    file_tree = []
    language_stats = {}
    total_lines = 0
    
    for root, dirs, files in os.walk(repo_path):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, repo_path)
            file_tree.append(rel_path)
            
            # 检查是否是支持的语言
            ext = Path(file).suffix.lower()
            if ext not in LANGUAGE_MAP:
                continue
            
            result = parse_file(filepath, repo_path)
            if result:
                all_nodes.extend(result["nodes"])
                all_edges.extend(result["edges"])
                
                # 统计
                lang_name = LANGUAGE_MAP[ext][0]
                language_stats[lang_name] = language_stats.get(lang_name, 0) + 1
                
                # 计算行数
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
    
    return {
        "nodes": all_nodes,
        "edges": all_edges,
        "file_tree": file_tree,
        "language_stats": language_stats,
        "total_lines": total_lines
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_ast_simple.py <repo_path>", file=sys.stderr)
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    print(f"Scanning repository: {repo_path}", file=sys.stderr)
    result = scan_repository(repo_path)
    
    # 构建输出
    output = {
        "languages": list(result["language_stats"].keys()),
        "stats": {
            "total_files": len(result["file_tree"]),
            "total_lines": result["total_lines"],
            "parse_errors": 0,
            "truncated": False,
            "truncated_nodes": 0,
            "supported_file_counts": result["language_stats"],
            "languages_with_structural_queries": list(result["language_stats"].keys()),
            "languages_with_custom_queries": [],
            "module_only_file_counts": {},
            "known_unsupported_file_counts": {},
            "configured_but_unavailable_file_counts": {},
            "custom_language_config_paths": []
        },
        "warnings": [
            "Using simplified AST extractor (standalone language packages)"
        ],
        "nodes": result["nodes"],
        "edges": result["edges"]
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
