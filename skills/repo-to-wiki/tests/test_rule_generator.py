#!/usr/bin/env python3
"""
单元测试：RuleGenerator 核心功能测试
"""

import os
import sys
import tempfile
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_TO_WIKI_DIR = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_TO_WIKI_DIR, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from rule_generator import RuleGenerator


class TestRuleGenerator:
    """RuleGenerator 单元测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def java_scan_result(self):
        """Java 项目扫描结果"""
        return {
            'project_name': 'java-project',
            'tech_stack': {
                'language': 'Java',
                'framework': 'Spring Boot',
                'orm': 'MyBatis',
                'build_tool': 'Maven',
                'java_version': '21',
                'database': 'MySQL',
                'cache': 'Redis'
            },
            'commands': [
                {'command': 'mvn spring-boot:run', 'description': '开发运行'},
                {'command': 'mvn test', 'description': '测试'},
                {'command': 'mvn clean package', 'description': '构建'}
            ],
            'modules': ['controller', 'service', 'mapper', 'entity']
        }
    
    @pytest.fixture
    def python_scan_result(self):
        """Python 项目扫描结果"""
        return {
            'project_name': 'python-project',
            'tech_stack': {
                'language': 'Python',
                'framework': 'FastAPI',
                'orm': 'SQLAlchemy',
                'build_tool': 'pip',
                'python_version': '3.12',
                'database': 'PostgreSQL'
            },
            'commands': [
                {'command': 'uvicorn main:app --reload', 'description': '开发运行'},
                {'command': 'pytest', 'description': '测试'},
                {'command': 'pip install -r requirements.txt', 'description': '安装依赖'}
            ],
            'modules': ['api', 'services', 'models']
        }
    
    @pytest.fixture
    def js_scan_result(self):
        """JavaScript 项目扫描结果"""
        return {
            'project_name': 'js-project',
            'tech_stack': {
                'language': 'TypeScript',
                'framework': 'Next.js',
                'orm': 'Prisma',
                'build_tool': 'npm',
                'node_version': '22'
            },
            'commands': [
                {'command': 'npm run dev', 'description': '开发运行'},
                {'command': 'npm test', 'description': '测试'},
                {'command': 'npm run build', 'description': '构建'}
            ],
            'modules': ['pages', 'api', 'services', 'models']
        }
    
    @pytest.fixture
    def go_scan_result(self):
        """Go 项目扫描结果"""
        return {
            'project_name': 'go-project',
            'tech_stack': {
                'language': 'Go',
                'framework': 'Gin',
                'build_tool': 'Go Modules',
                'go_version': '1.22'
            },
            'commands': [
                {'command': 'go run main.go', 'description': '开发运行'},
                {'command': 'go test ./...', 'description': '测试'},
                {'command': 'go build', 'description': '构建'}
            ],
            'modules': ['handler', 'service', 'repository', 'model']
        }
    
    def test_init_with_valid_data(self, java_scan_result):
        """测试初始化"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        assert generator.project_path == '/path/to/project'
        assert generator.language == 'Java'
        assert generator.framework == 'Spring Boot'
    
    def test_get_backend_language_java(self, java_scan_result):
        """测试获取后端语言 - Java"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_backend_language()
        assert 'Java' in result
        assert '21' in result
    
    def test_get_backend_language_python(self, python_scan_result):
        """测试获取后端语言 - Python"""
        generator = RuleGenerator('/path/to/project', python_scan_result, {})
        result = generator._get_backend_language()
        assert 'Python' in result
        assert '3.12' in result
    
    def test_get_backend_language_js(self, js_scan_result):
        """测试获取后端语言 - TypeScript"""
        generator = RuleGenerator('/path/to/project', js_scan_result, {})
        result = generator._get_backend_language()
        assert 'Typescript' in result  # 注意：实际返回的是小写 's'
    
    def test_get_backend_language_go(self, go_scan_result):
        """测试获取后端语言 - Go"""
        generator = RuleGenerator('/path/to/project', go_scan_result, {})
        result = generator._get_backend_language()
        assert 'Go' in result
        assert '1.22' in result
    
    def test_get_command_by_desc(self, java_scan_result):
        """测试根据描述获取命令"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_command_by_desc(java_scan_result['commands'], '测试')
        assert result == 'mvn test'
    
    def test_get_command_by_desc_not_found(self, java_scan_result):
        """测试根据描述获取命令 - 未找到"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_command_by_desc(java_scan_result['commands'], '部署')
        assert result is None
    
    def test_get_tech_constraints_table_java(self, java_scan_result):
        """测试获取技术约束表 - Java"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_tech_constraints_table()
        assert 'Spring Context' in result
        assert 'Jackson' in result
    
    def test_get_tech_constraints_table_python(self, python_scan_result):
        """测试获取技术约束表 - Python"""
        generator = RuleGenerator('/path/to/project', python_scan_result, {})
        result = generator._get_tech_constraints_table()
        assert 'SQLAlchemy' in result
        assert 'requests' in result
    
    def test_get_tech_constraints_table_js(self, js_scan_result):
        """测试获取技术约束表 - JavaScript"""
        generator = RuleGenerator('/path/to/project', js_scan_result, {})
        result = generator._get_tech_constraints_table()
        assert 'Zustand' in result
        assert 'axios' in result
    
    def test_get_success_response_example_java(self, java_scan_result):
        """测试成功响应示例 - Java"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_success_response_example()
        assert 'AjaxResult.success' in result
    
    def test_get_success_response_example_python(self, python_scan_result):
        """测试成功响应示例 - Python"""
        generator = RuleGenerator('/path/to/project', python_scan_result, {})
        result = generator._get_success_response_example()
        assert 'code' in result
        assert 'data' in result
    
    def test_get_test_framework_java(self, java_scan_result):
        """测试获取测试框架 - Java"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_test_framework()
        assert 'JUnit' in result
        assert 'Mockito' in result
    
    def test_get_test_framework_python(self, python_scan_result):
        """测试获取测试框架 - Python"""
        generator = RuleGenerator('/path/to/project', python_scan_result, {})
        result = generator._get_test_framework()
        assert 'pytest' in result
    
    def test_get_test_framework_js(self, js_scan_result):
        """测试获取测试框架 - JavaScript"""
        generator = RuleGenerator('/path/to/project', js_scan_result, {})
        result = generator._get_test_framework()
        assert 'Jest' in result or 'Vitest' in result
    
    def test_get_test_framework_go(self, go_scan_result):
        """测试获取测试框架 - Go"""
        generator = RuleGenerator('/path/to/project', go_scan_result, {})
        result = generator._get_test_framework()
        assert 'Go testing' in result
    
    def test_get_test_file_location_java(self, java_scan_result):
        """测试获取测试文件位置 - Java"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        result = generator._get_test_file_location()
        assert 'src/test/java' in result
    
    def test_get_test_file_location_python(self, python_scan_result):
        """测试获取测试文件位置 - Python"""
        generator = RuleGenerator('/path/to/project', python_scan_result, {})
        result = generator._get_test_file_location()
        assert 'tests/' in result
    
    def test_generate_all_claude(self, temp_dir, java_scan_result):
        """测试生成所有规则文件 - Claude"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        generator.generate_all(temp_dir, tools=['claude'])
        
        assert os.path.exists(os.path.join(temp_dir, 'CLAUDE.md'))
        assert os.path.exists(os.path.join(temp_dir, '.claude'))
    
    def test_generate_all_agents(self, temp_dir, java_scan_result):
        """测试生成所有规则文件 - Agents"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        generator.generate_all(temp_dir, tools=['agents'])
        
        assert os.path.exists(os.path.join(temp_dir, 'AGENTS.md'))
    
    def test_generate_all_multiple_tools(self, temp_dir, java_scan_result):
        """测试生成所有规则文件 - 多个工具"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        generator.generate_all(temp_dir, tools=['claude', 'agents', 'cursor', 'copilot'])
        
        assert os.path.exists(os.path.join(temp_dir, 'CLAUDE.md'))
        assert os.path.exists(os.path.join(temp_dir, 'AGENTS.md'))
        assert os.path.exists(os.path.join(temp_dir, '.cursorrules'))
        assert os.path.exists(os.path.join(temp_dir, '.copilot-instructions.md'))
    
    def test_generate_agents_content(self, temp_dir, java_scan_result):
        """测试生成 AGENTS.md 内容"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        generator._generate_agents_md(temp_dir)
        
        agents_path = os.path.join(temp_dir, 'AGENTS.md')
        assert os.path.exists(agents_path)
        
        with open(agents_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'java-project' in content
            assert 'Spring Boot' in content
    
    def test_generate_claude_content(self, temp_dir, java_scan_result):
        """测试生成 CLAUDE.md 内容"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        generator._generate_claude_md(temp_dir)
        
        claude_path = os.path.join(temp_dir, 'CLAUDE.md')
        assert os.path.exists(claude_path)
        
        with open(claude_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'java-project' in content
    
    def test_build_agents_content(self, java_scan_result):
        """测试直接构建 AGENTS.md 内容"""
        generator = RuleGenerator('/path/to/project', java_scan_result, {})
        content = generator._build_agents_content()
        
        assert 'java-project' in content
        assert 'Spring Boot' in content
        assert '技术栈' in content
        assert '常用命令' in content
        assert '架构约束' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
