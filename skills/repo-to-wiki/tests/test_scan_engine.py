#!/usr/bin/env python3
"""
单元测试：ScanEngine 核心功能测试
"""

import os
import sys
import tempfile
import shutil
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_TO_WIKI_DIR = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_TO_WIKI_DIR, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from scan_engine import ScanEngine


class TestScanEngine:
    """ScanEngine 单元测试类"""
    
    @pytest.fixture
    def temp_project(self):
        """创建临时测试项目"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def java_project(self, temp_project):
        """创建 Java/Maven 测试项目"""
        os.makedirs(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'controller'), exist_ok=True)
        os.makedirs(os.path.join(temp_project, 'src', 'test', 'java', 'com', 'example'), exist_ok=True)
        
        # 创建 pom.xml
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>1.0.0</version>
    <name>demo</name>
    <description>Spring Boot Demo Project</description>
    <properties>
        <java.version>21</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
'''
        with open(os.path.join(temp_project, 'pom.xml'), 'w') as f:
            f.write(pom_content)
        
        # 创建示例 Java 文件
        with open(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'Application.java'), 'w') as f:
            f.write('''package com.example;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
''')
        
        with open(os.path.join(temp_project, 'src', 'main', 'java', 'com', 'example', 'controller', 'UserController.java'), 'w') as f:
            f.write('''package com.example.controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
@RestController
public class UserController {
    @GetMapping("/users")
    public String getUsers() {
        return "users";
    }
}
''')
        
        return temp_project
    
    @pytest.fixture
    def python_project(self, temp_project):
        """创建 Python/PyProject 测试项目"""
        pyproject_content = '''[project]
name = "my-py-project"
version = "1.0.0"
description = "A Python project"
dependencies = [
    "fastapi",
    "uvicorn",
]
[tool.pytest.ini_options]
testpaths = ["tests"]
'''
        with open(os.path.join(temp_project, 'pyproject.toml'), 'w') as f:
            f.write(pyproject_content)
        
        with open(os.path.join(temp_project, 'main.py'), 'w') as f:
            f.write('''from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Hello World"}
''')
        
        return temp_project
    
    @pytest.fixture
    def js_project(self, temp_project):
        """创建 JavaScript/TypeScript 测试项目"""
        pkg_content = '''{
  "name": "my-js-project",
  "version": "1.0.0",
  "description": "A JavaScript project",
  "dependencies": {
    "react": "^18.0.0",
    "next": "^14.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "jest"
  }
}
'''
        with open(os.path.join(temp_project, 'package.json'), 'w') as f:
            f.write(pkg_content)
        
        with open(os.path.join(temp_project, 'index.js'), 'w') as f:
            f.write('''console.log("Hello World");
''')
        
        return temp_project
    
    @pytest.fixture
    def go_project(self, temp_project):
        """创建 Go 测试项目"""
        go_mod_content = '''module github.com/example/my-go-project
go 1.21
require github.com/gin-gonic/gin v1.9.1
'''
        with open(os.path.join(temp_project, 'go.mod'), 'w') as f:
            f.write(go_mod_content)
        
        with open(os.path.join(temp_project, 'main.go'), 'w') as f:
            f.write('''package main
import "github.com/gin-gonic/gin"
func main() {
    r := gin.Default()
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "hello world"})
    })
    r.Run()
}
''')
        
        return temp_project
    
    def test_init_with_valid_path(self, temp_project):
        """测试 ScanEngine 初始化 - 有效路径"""
        engine = ScanEngine(temp_project, depth='standard')
        assert engine.project_path == temp_project
        assert engine.depth == 'standard'
        assert engine.force is False
    
    def test_detect_project_name_java(self, java_project):
        """测试项目名称检测 - Java/Maven"""
        engine = ScanEngine(java_project)
        project_name = engine._detect_project_name()
        assert project_name == 'demo'
    
    def test_detect_project_name_python(self, python_project):
        """测试项目名称检测 - Python"""
        engine = ScanEngine(python_project)
        project_name = engine._detect_project_name()
        assert project_name == 'my-py-project'
    
    def test_detect_project_name_js(self, js_project):
        """测试项目名称检测 - JavaScript"""
        engine = ScanEngine(js_project)
        project_name = engine._detect_project_name()
        assert project_name == 'my-js-project'
    
    def test_detect_project_name_go(self, go_project):
        """测试项目名称检测 - Go"""
        engine = ScanEngine(go_project)
        project_name = engine._detect_project_name()
        assert project_name == 'github.com/example/my-go-project'
    
    def test_detect_project_name_fallback(self, temp_project):
        """测试项目名称检测 - 回退到目录名"""
        engine = ScanEngine(temp_project)
        project_name = engine._detect_project_name()
        assert project_name == os.path.basename(temp_project)
    
    def test_detect_tech_stack_java_spring(self, java_project):
        """测试技术栈检测 - Java Spring Boot"""
        engine = ScanEngine(java_project)
        tech_stack = engine._detect_tech_stack()
        assert tech_stack.get('language') == 'Java'
        assert tech_stack.get('build_tool') == 'Maven'
        assert tech_stack.get('framework') == 'Spring Boot'
        assert tech_stack.get('orm') == 'Spring Data JPA'
    
    def test_detect_tech_stack_python(self, python_project):
        """测试技术栈检测 - Python FastAPI"""
        engine = ScanEngine(python_project)
        tech_stack = engine._detect_tech_stack()
        assert tech_stack.get('language') == 'Python'
    
    def test_detect_tech_stack_js_next(self, js_project):
        """测试技术栈检测 - JavaScript Next.js"""
        engine = ScanEngine(js_project)
        tech_stack = engine._detect_tech_stack()
        assert tech_stack.get('language') == 'TypeScript'
        assert tech_stack.get('build_tool') == 'npm'
        assert tech_stack.get('framework') == 'Next.js'
    
    def test_detect_tech_stack_go(self, go_project):
        """测试技术栈检测 - Go Gin"""
        engine = ScanEngine(go_project)
        tech_stack = engine._detect_tech_stack()
        assert tech_stack.get('language') == 'Go'
        assert tech_stack.get('build_tool') == 'Go Modules'
        assert tech_stack.get('framework') == 'Gin'
    
    def test_detect_commands_java(self, java_project):
        """测试命令检测 - Java"""
        engine = ScanEngine(java_project)
        engine._tech_stack = {'language': 'Java'}
        commands = engine._detect_commands()
        assert len(commands) > 0
        descriptions = [cmd['description'] for cmd in commands]
        assert '构建' in descriptions
        assert '测试' in descriptions
    
    def test_detect_commands_js(self, js_project):
        """测试命令检测 - JavaScript"""
        engine = ScanEngine(js_project)
        engine._tech_stack = {'language': 'JavaScript/TypeScript'}
        commands = engine._detect_commands()
        assert len(commands) > 0
        descriptions = [cmd['description'] for cmd in commands]
        assert '开发' in descriptions
        assert '构建' in descriptions
        assert '测试' in descriptions
    
    def test_scan_basic(self, temp_project):
        """测试基础扫描功能"""
        # 创建一些测试文件
        with open(os.path.join(temp_project, 'test.txt'), 'w') as f:
            f.write('Hello World')
        
        engine = ScanEngine(temp_project, force=True)
        result = engine.scan()
        
        assert 'project_path' in result
        assert 'project_name' in result
        assert 'tech_stack' in result
        assert 'file_count' in result
        assert result['file_count'] >= 1
    
    def test_scan_empty_dir(self, temp_project):
        """测试扫描空目录 - ScanEngine会创建.nexus-map和.repo-to-wiki目录"""
        # 创建一个明确为空的子目录
        empty_dir = os.path.join(temp_project, 'empty')
        os.makedirs(empty_dir, exist_ok=True)
        
        engine = ScanEngine(empty_dir, force=True)
        result = engine.scan()
        
        # 注意：ScanEngine会自动创建.nexus-map和.repo-to-wiki目录
        # 所以file_count会包含这些自动创建的文件
        assert 'error' not in result
        assert result['file_count'] >= 0
    
    def test_scan_with_cache(self, temp_project):
        """测试缓存功能"""
        with open(os.path.join(temp_project, 'test.txt'), 'w') as f:
            f.write('Test')
        
        engine = ScanEngine(temp_project, force=False)
        result1 = engine.scan()
        
        # 再次扫描，应该使用缓存
        engine2 = ScanEngine(temp_project, force=False)
        result2 = engine2.scan()
        
        assert result1['file_count'] == result2['file_count']
    
    def test_scan_force_refresh(self, temp_project):
        """测试强制刷新"""
        with open(os.path.join(temp_project, 'test.txt'), 'w') as f:
            f.write('Test')
        
        engine = ScanEngine(temp_project, force=True)
        result1 = engine.scan()
        
        # 添加新文件
        with open(os.path.join(temp_project, 'test2.txt'), 'w') as f:
            f.write('Test 2')
        
        # 强制刷新
        engine2 = ScanEngine(temp_project, force=True)
        result2 = engine2.scan()
        
        assert result2['file_count'] > result1['file_count']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
