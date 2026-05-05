#!/usr/bin/env python3
"""
单元测试：KnowledgeExtractor 核心功能测试
"""

import os
import sys
import tempfile
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_TO_WIKI_DIR = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_TO_WIKI_DIR, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from knowledge_extractor import KnowledgeExtractor


class TestKnowledgeExtractor:
    """KnowledgeExtractor 单元测试类"""
    
    @pytest.fixture
    def temp_project(self):
        """创建临时测试项目"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def java_project(self, temp_project):
        """创建 Java 测试项目结构"""
        os.makedirs(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'controller'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'service'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'mapper'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'entity'), exist_ok=True)
        
        with open(os.path.join(temp_project, 'pom.xml'), 'w') as f:
            f.write('<project><groupId>com.example</groupId><artifactId>test-project</artifactId></project>')
        
        with open(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'controller', 'UserController.java'), 'w') as f:
            f.write('package com.example.controller;\npublic class UserController {}\n')
        
        with open(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'service', 'UserService.java'), 'w') as f:
            f.write('package com.example.service;\npublic class UserService {}\n')
        
        return temp_project
    
    @pytest.fixture
    def python_project(self, temp_project):
        """创建 Python 测试项目结构"""
        os.makedirs(os.path.join(temp_project, 'app', 'api'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'app', 'services'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'app', 'models'), exist_ok=True)
        
        with open(os.path.join(temp_project, 'pyproject.toml'), 'w') as f:
            f.write('[project]\nname = "test-project"\n')
        
        with open(os.path.join(temp_project, 'app', 'api', 'users.py'), 'w') as f:
            f.write('from fastapi import APIRouter\nrouter = APIRouter()\n')
        
        with open(os.path.join(temp_project, 'app', 'services', 'user_service.py'), 'w') as f:
            f.write('class UserService:\n    pass\n')
        
        return temp_project
    
    @pytest.fixture
    def java_scan_result(self):
        """Java 项目扫描结果"""
        return {
            'project_name': 'java-test',
            'tech_stack': {
                'language': 'Java',
                'framework': 'Spring Boot',
                'orm': 'MyBatis',
                'build_tool': 'Maven'
            },
            'modules': ['controller', 'service', 'mapper', 'entity'],
            'file_count': 10,
            'file_types': {'java': 8, 'xml': 2},
            'core_classes': [
                {'name': 'UserController', 'type': 'controller', 'path': 'controller/UserController.java'},
                {'name': 'OrderController', 'type': 'controller', 'path': 'controller/OrderController.java'},
                {'name': 'UserService', 'type': 'service', 'path': 'service/UserService.java'},
                {'name': 'OrderService', 'type': 'service', 'path': 'service/OrderService.java'},
                {'name': 'UserMapper', 'type': 'mapper', 'path': 'mapper/UserMapper.java'},
                {'name': 'UserEntity', 'type': 'entity', 'path': 'entity/UserEntity.java'}
            ]
        }
    
    @pytest.fixture
    def python_scan_result(self):
        """Python 项目扫描结果"""
        return {
            'project_name': 'python-test',
            'tech_stack': {
                'language': 'Python',
                'framework': 'FastAPI',
                'orm': 'SQLAlchemy',
                'build_tool': 'pip'
            },
            'modules': ['api', 'services', 'models'],
            'file_count': 8,
            'file_types': {'py': 6, 'toml': 2},
            'core_classes': [
                {'name': 'UserRouter', 'type': 'router', 'path': 'api/users.py'},
                {'name': 'UserService', 'type': 'service', 'path': 'services/user_service.py'},
                {'name': 'UserModel', 'type': 'model', 'path': 'models/user.py'}
            ]
        }
    
    def test_init(self, java_scan_result):
        """测试初始化"""
        extractor = KnowledgeExtractor('/path/to/project', java_scan_result)
        assert extractor.project_path == '/path/to/project'
        assert extractor.language == 'Java'
    
    def test_extract_basic_structure(self, java_project, java_scan_result):
        """测试知识提取基本结构"""
        extractor = KnowledgeExtractor(java_project, java_scan_result)
        knowledge = extractor.extract()
        
        assert knowledge is not None
        assert 'architecture' in knowledge
        assert 'business_logic' in knowledge
        assert 'core_classes' in knowledge
        assert 'core_processes' in knowledge
        assert 'questions' in knowledge
    
    def test_extract_architecture_java(self, java_project, java_scan_result):
        """测试 Java 架构提取"""
        extractor = KnowledgeExtractor(java_project, java_scan_result)
        knowledge = extractor.extract()
        
        layers = knowledge['architecture']['layers']
        assert 'controller' in layers
        assert 'service' in layers
        assert 'mapper/repository' in layers
    
    def test_extract_architecture_python(self, python_project, python_scan_result):
        """测试 Python 架构提取"""
        extractor = KnowledgeExtractor(python_project, python_scan_result)
        knowledge = extractor.extract()
        
        layers = knowledge['architecture']['layers']
        assert 'view/api' in layers
        assert 'service' in layers
        assert 'model/dao' in layers
    
    def test_extract_core_classes(self, java_project, java_scan_result):
        """测试核心类提取"""
        extractor = KnowledgeExtractor(java_project, java_scan_result)
        knowledge = extractor.extract()
        
        core_classes = knowledge['core_classes']
        assert len(core_classes['controllers']) >= 0
        assert len(core_classes['services']) >= 0
        assert len(core_classes['mappers']) >= 0
    
    def test_extract_questions(self, java_project, java_scan_result):
        """测试问题生成"""
        extractor = KnowledgeExtractor(java_project, java_scan_result)
        knowledge = extractor.extract()
        
        questions = knowledge['questions']
        assert 'basic' in questions
        assert 'config' in questions
        assert 'development' in questions
        assert 'deployment' in questions
    
    def test_extract_empty_project(self, temp_project):
        """测试空项目提取"""
        scan_result = {
            'project_name': 'empty-project',
            'tech_stack': {'language': 'Python'},
            'modules': [],
            'file_count': 0,
            'file_types': {},
            'core_classes': []
        }
        
        extractor = KnowledgeExtractor(temp_project, scan_result)
        knowledge = extractor.extract()
        
        assert knowledge is not None
        assert len(knowledge['core_classes']['controllers']) == 0
    
    def test_extract_python(self, python_project, python_scan_result):
        """测试 Python 项目知识提取"""
        extractor = KnowledgeExtractor(python_project, python_scan_result)
        knowledge = extractor.extract()
        
        assert knowledge is not None
        # 验证技术栈信息被正确提取
        assert 'Python' in str(knowledge)
        assert 'FastAPI' in str(knowledge)
    
    def test_knowledge_structure_integrity(self, java_project, java_scan_result):
        """测试知识结构完整性"""
        extractor = KnowledgeExtractor(java_project, java_scan_result)
        knowledge = extractor.extract()
        
        # 验证所有必要字段存在
        required_fields = [
            'architecture', 'business_logic', 'core_processes', 
            'core_classes', 'call_chains', 'terms', 'questions',
            'coding_standards', 'security_constraints', 'naming_conventions', 'pitfalls'
        ]
        
        for field in required_fields:
            assert field in knowledge, f"缺失字段: {field}"
        
        # 验证 core_classes 结构
        assert 'controllers' in knowledge['core_classes']
        assert 'services' in knowledge['core_classes']
        assert 'mappers' in knowledge['core_classes']
        assert 'repositories' in knowledge['core_classes']
        assert 'models' in knowledge['core_classes']
        
        # 验证 questions 结构
        assert 'basic' in knowledge['questions']
        assert 'config' in knowledge['questions']
        assert 'development' in knowledge['questions']
        assert 'deployment' in knowledge['questions']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
