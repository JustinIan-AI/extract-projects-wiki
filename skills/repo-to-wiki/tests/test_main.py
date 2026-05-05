#!/usr/bin/env python3
"""
单元测试：main.py 核心功能测试
"""

import os
import sys
import tempfile
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_TO_WIKI_DIR = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_TO_WIKI_DIR, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from main import resolve_input, phase0_input, phase1_scan, phase5_summary


class TestMain:
    """main.py 单元测试类"""
    
    @pytest.fixture
    def temp_project(self):
        """创建临时测试项目"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def valid_python_project(self, temp_project):
        """创建有效的 Python 测试项目"""
        with open(os.path.join(temp_project, 'pyproject.toml'), 'w') as f:
            f.write('[project]\nname = "test-project"\nversion = "1.0.0"\n')
        
        with open(os.path.join(temp_project, 'main.py'), 'w') as f:
            f.write('print("Hello")\n')
        
        return temp_project
    
    def test_resolve_input_local_path(self, temp_project):
        """测试 resolve_input - 本地路径"""
        path, fetcher = resolve_input(temp_project)
        assert path == os.path.abspath(temp_project)
        assert fetcher is None
    
    def test_resolve_input_invalid_path(self, temp_project):
        """测试 resolve_input - 无效路径"""
        invalid_path = os.path.join(temp_project, 'nonexistent')
        with pytest.raises(ValueError):
            resolve_input(invalid_path)
    
    def test_resolve_input_github_url(self):
        """测试 resolve_input - GitHub URL（验证格式）"""
        github_url = "https://github.com/example/test"
        # 这里不实际克隆，只测试 URL 检测
        from github_fetcher import is_github_url
        assert is_github_url(github_url) is True
    
    def test_phase0_input_local(self, valid_python_project):
        """测试 phase0_input - 本地项目"""
        local_path, fetcher = phase0_input(valid_python_project, None)
        assert local_path == os.path.abspath(valid_python_project)
        assert fetcher is None
    
    def test_phase1_scan_basic(self, valid_python_project):
        """测试 phase1_scan - 基础扫描"""
        scan_result = phase1_scan(valid_python_project, depth='quick', force=True)
        
        assert 'project_path' in scan_result
        assert 'project_name' in scan_result
        assert 'tech_stack' in scan_result
        assert 'file_count' in scan_result
        assert scan_result['file_count'] >= 1
    
    def test_phase5_summary_empty(self, temp_project):
        """测试 phase5_summary - 空目录"""
        files = phase5_summary(temp_project)
        assert len(files) == 0
    
    def test_phase5_summary_with_files(self, temp_project):
        """测试 phase5_summary - 有文件"""
        with open(os.path.join(temp_project, 'file1.txt'), 'w') as f:
            f.write('content1')
        
        with open(os.path.join(temp_project, 'file2.txt'), 'w') as f:
            f.write('content2')
        
        files = phase5_summary(temp_project)
        assert len(files) == 2
        
        paths = [f['path'] for f in files]
        assert 'file1.txt' in paths
        assert 'file2.txt' in paths
    
    def test_phase5_summary_with_subdirs(self, temp_project):
        """测试 phase5_summary - 包含子目录"""
        os.makedirs(os.path.join(temp_project, 'subdir'), exist_ok=True)
        
        with open(os.path.join(temp_project, 'root.txt'), 'w') as f:
            f.write('root')
        
        with open(os.path.join(temp_project, 'subdir', 'nested.txt'), 'w') as f:
            f.write('nested')
        
        files = phase5_summary(temp_project)
        assert len(files) == 2
        
        paths = [f['path'] for f in files]
        assert 'root.txt' in paths
        assert 'subdir/nested.txt' in paths
    
    def test_scan_result_contains_tech_stack(self, valid_python_project):
        """测试扫描结果包含技术栈信息"""
        scan_result = phase1_scan(valid_python_project, depth='quick', force=True)
        
        tech_stack = scan_result.get('tech_stack', {})
        assert 'language' in tech_stack
        assert tech_stack['language'] == 'Python'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
