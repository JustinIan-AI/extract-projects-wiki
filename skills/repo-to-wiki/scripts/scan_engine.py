#!/usr/bin/env python3
"""
核心扫描引擎
负责项目的跨栈扫描、文件分类和技术栈检测
"""

import os
import json
import logging
import hashlib
import re
import xml.etree.ElementTree as ET
import concurrent.futures
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ScanEngine:
    def __init__(self, project_path, depth='standard', force=False):
        self.project_path = project_path
        self.depth = depth
        self.force = force
        self.file_types = {
            'java': ['.java', '.class', '.jar'],
            'kotlin': ['.kt', '.kts'],
            'python': ['.py', '.pyi'],
            'c_cpp': ['.c', '.cpp', '.h', '.hpp'],
            'go': ['.go'],
            'rust': ['.rs'],
            'web': ['.js', '.ts', '.vue', '.html', '.css', '.scss'],
            'ios': ['.swift', '.m', '.h'],
            'build': ['.gradle', '.maven', '.npm', '.yarn', '.git'],
            'config': ['.json', '.yaml', '.yml', '.xml', '.properties', '.toml']
        }
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.repo-to-wiki', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self):
        path_hash = hashlib.md5(self.project_path.encode()).hexdigest()
        try:
            mtime = str(max(os.path.getmtime(os.path.join(root, file))
                            for root, dirs, files in os.walk(self.project_path)
                            for file in files if not root.split(os.sep)[-1].startswith('.')))
        except (ValueError, OSError):
            mtime = str(datetime.now().timestamp())
        return f"{path_hash}_{self.depth}_{hashlib.md5(mtime.encode()).hexdigest()}"

    def _load_from_cache(self):
        cache_key = self._get_cache_key()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    logging.info(f"从缓存加载扫描结果: {cache_file}")
                    return json.load(f)
            except Exception as e:
                logging.warning(f"缓存加载失败: {str(e)}")
        return None

    def _save_to_cache(self, result):
        cache_key = self._get_cache_key()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logging.info(f"扫描结果已缓存: {cache_file}")
        except Exception as e:
            logging.warning(f"缓存保存失败: {str(e)}")
        try:
            latest_file = os.path.join(self.project_path, '.repo-to-wiki', 'scan_result.json')
            os.makedirs(os.path.dirname(latest_file), exist_ok=True)
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logging.info(f"最新扫描结果已保存: {latest_file}")
        except Exception as e:
            logging.warning(f"项目目录保存失败: {str(e)}")

    def _detect_project_name(self):
        if os.path.exists(os.path.join(self.project_path, 'pom.xml')):
            try:
                tree = ET.parse(os.path.join(self.project_path, 'pom.xml'))
                root = tree.getroot()
                ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
                artifact_id = root.find('m:artifactId', ns)
                if artifact_id is not None and artifact_id.text:
                    return artifact_id.text.strip()
                name = root.find('m:name', ns)
                if name is not None and name.text:
                    return name.text.strip()
            except Exception:
                pass
        if os.path.exists(os.path.join(self.project_path, 'package.json')):
            try:
                with open(os.path.join(self.project_path, 'package.json'), 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                if pkg.get('name'):
                    return pkg['name'].strip()
            except Exception:
                pass
        if os.path.exists(os.path.join(self.project_path, 'pyproject.toml')):
            try:
                with open(os.path.join(self.project_path, 'pyproject.toml'), 'r', encoding='utf-8') as f:
                    content = f.read()
                match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1).strip()
            except Exception:
                pass
        if os.path.exists(os.path.join(self.project_path, 'Cargo.toml')):
            try:
                with open(os.path.join(self.project_path, 'Cargo.toml'), 'r', encoding='utf-8') as f:
                    content = f.read()
                match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1).strip()
            except Exception:
                pass
        if os.path.exists(os.path.join(self.project_path, 'go.mod')):
            try:
                with open(os.path.join(self.project_path, 'go.mod'), 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                if first_line.startswith('module '):
                    return first_line.replace('module ', '').strip()
            except Exception:
                pass
        return os.path.basename(self.project_path)

    def _detect_tech_stack(self):
        stack = {}
        root = self.project_path

        # Java / Maven
        pom_path = os.path.join(root, 'pom.xml')
        if os.path.exists(pom_path):
            stack['language'] = 'Java'
            stack['build_tool'] = 'Maven'
            try:
                tree = ET.parse(pom_path)
                xml_root = tree.getroot()
                ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
                parent = xml_root.find('m:parent', ns)
                if parent is not None:
                    group_id = parent.find('m:groupId', ns)
                    artifact_id = parent.find('m:artifactId', ns)
                    version = parent.find('m:version', ns)
                    if artifact_id is not None and 'spring-boot' in (artifact_id.text or ''):
                        stack['framework'] = 'Spring Boot'
                        if version is not None:
                            stack['spring_boot_version'] = version.text.strip()
                for dep in xml_root.findall('.//m:dependency', ns):
                    aid = dep.find('m:artifactId', ns)
                    if aid is not None:
                        aid_text = aid.text or ''
                        if 'mybatis' in aid_text:
                            stack['orm'] = 'MyBatis'
                        elif 'mybatis-plus' in aid_text:
                            stack['orm'] = 'MyBatis-Plus'
                        elif 'jpa' in aid_text or 'spring-data-jpa' in aid_text:
                            stack['orm'] = 'Spring Data JPA'
                        if 'shiro' in aid_text:
                            stack['auth'] = 'Apache Shiro'
                        elif 'spring-security' in aid_text:
                            stack['auth'] = 'Spring Security'
                        if 'thymeleaf' in aid_text:
                            stack['template_engine'] = 'Thymeleaf'
                        if 'druid' in aid_text:
                            stack['connection_pool'] = 'Druid'
                        if 'redis' in aid_text:
                            stack['cache'] = 'Redis'
            except Exception as e:
                logging.warning(f"pom.xml 解析失败: {str(e)}")

        # Gradle (Java/Kotlin/Android)
        gradle_path = os.path.join(root, 'build.gradle')
        gradle_kts_path = os.path.join(root, 'build.gradle.kts')
        if os.path.exists(gradle_path) or os.path.exists(gradle_kts_path):
            if 'language' not in stack:
                stack['language'] = 'Java/Kotlin'
            stack['build_tool'] = 'Gradle'
            gf = gradle_path if os.path.exists(gradle_path) else gradle_kts_path
            try:
                with open(gf, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'org.springframework' in content:
                    stack['framework'] = 'Spring Boot'
                if 'com.android.application' in content:
                    stack['platform'] = 'Android'
                if 'org.jetbrains.kotlin' in content:
                    stack['language'] = 'Kotlin'
            except Exception:
                pass

        # Node.js / npm / yarn
        pkg_path = os.path.join(root, 'package.json')
        if os.path.exists(pkg_path):
            if 'language' not in stack:
                stack['language'] = 'JavaScript/TypeScript'
            try:
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'next' in deps:
                    stack['framework'] = 'Next.js'
                elif 'nuxt' in deps:
                    stack['framework'] = 'Nuxt.js'
                elif 'react' in deps:
                    stack['framework'] = 'React'
                elif 'vue' in deps:
                    stack['framework'] = 'Vue.js'
                elif 'express' in deps:
                    stack['framework'] = 'Express'
                elif 'koa' in deps:
                    stack['framework'] = 'Koa'
                elif 'nestjs' in deps or '@nestjs/core' in deps:
                    stack['framework'] = 'NestJS'
                if 'typescript' in deps:
                    stack['language'] = 'TypeScript'
                if 'yarn.lock' in os.listdir(root):
                    stack['build_tool'] = 'Yarn'
                elif 'pnpm-lock.yaml' in os.listdir(root):
                    stack['build_tool'] = 'pnpm'
                else:
                    stack['build_tool'] = 'npm'
                if 'tailwindcss' in deps:
                    stack['css_framework'] = 'Tailwind CSS'
                if 'prisma' in deps:
                    stack['orm'] = 'Prisma'
                elif 'typeorm' in deps:
                    stack['orm'] = 'TypeORM'
                elif 'mongoose' in deps:
                    stack['orm'] = 'Mongoose'
            except Exception:
                pass

        # Python
        pyproject_path = os.path.join(root, 'pyproject.toml')
        requirements_path = os.path.join(root, 'requirements.txt')
        setup_py_path = os.path.join(root, 'setup.py')
        if os.path.exists(pyproject_path) or os.path.exists(requirements_path) or os.path.exists(setup_py_path):
            if 'language' not in stack:
                stack['language'] = 'Python'
            try:
                if os.path.exists(pyproject_path):
                    with open(pyproject_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if 'django' in content.lower():
                        stack['framework'] = 'Django'
                    elif 'flask' in content.lower():
                        stack['framework'] = 'Flask'
                    elif 'fastapi' in content.lower():
                        stack['framework'] = 'FastAPI'
                    if 'poetry' in content.lower():
                        stack['build_tool'] = 'Poetry'
                elif os.path.exists(requirements_path):
                    with open(requirements_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if 'django' in content.lower():
                        stack['framework'] = 'Django'
                    elif 'flask' in content.lower():
                        stack['framework'] = 'Flask'
                    elif 'fastapi' in content.lower():
                        stack['framework'] = 'FastAPI'
                    stack['build_tool'] = 'pip'
            except Exception:
                pass

        # Go
        go_mod_path = os.path.join(root, 'go.mod')
        if os.path.exists(go_mod_path):
            stack['language'] = 'Go'
            stack['build_tool'] = 'Go Modules'
            try:
                with open(go_mod_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'gin-gonic' in content:
                    stack['framework'] = 'Gin'
                elif 'echo' in content:
                    stack['framework'] = 'Echo'
                elif 'fiber' in content:
                    stack['framework'] = 'Fiber'
            except Exception:
                pass

        # Rust
        cargo_path = os.path.join(root, 'Cargo.toml')
        if os.path.exists(cargo_path):
            stack['language'] = 'Rust'
            stack['build_tool'] = 'Cargo'
            try:
                with open(cargo_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'actix-web' in content:
                    stack['framework'] = 'Actix Web'
                elif 'axum' in content:
                    stack['framework'] = 'Axum'
                elif 'rocket' in content:
                    stack['framework'] = 'Rocket'
            except Exception:
                pass

        # 多模块项目检测
        if os.path.exists(pom_path):
            try:
                tree = ET.parse(pom_path)
                xml_root = tree.getroot()
                ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
                modules = xml_root.findall('m:modules/m:module', ns)
                if modules:
                    stack['project_type'] = 'Maven Multi-Module'
                    stack['module_count'] = len(modules)
            except Exception:
                pass

        return stack

    def _detect_commands(self):
        commands = []
        root = self.project_path
        stack = getattr(self, '_tech_stack', {})

        if os.path.exists(os.path.join(root, 'pom.xml')):
            commands.append({'description': '构建', 'command': 'mvn clean package -DskipTests'})
            commands.append({'description': '测试', 'command': 'mvn test'})
            commands.append({'description': '运行', 'command': 'mvn spring-boot:run'})
            if os.path.exists(os.path.join(root, 'mvnw')):
                commands.append({'description': '构建(Wrapper)', 'command': './mvnw clean package -DskipTests'})
        elif os.path.exists(os.path.join(root, 'build.gradle')) or os.path.exists(os.path.join(root, 'build.gradle.kts')):
            commands.append({'description': '构建', 'command': './gradlew build'})
            commands.append({'description': '测试', 'command': './gradlew test'})
            commands.append({'description': '运行', 'command': './gradlew bootRun'})
        elif os.path.exists(os.path.join(root, 'package.json')):
            try:
                with open(os.path.join(root, 'package.json'), 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                scripts = pkg.get('scripts', {})
                if 'dev' in scripts:
                    commands.append({'description': '开发', 'command': 'npm run dev'})
                if 'start' in scripts:
                    commands.append({'description': '运行', 'command': 'npm start'})
                if 'test' in scripts:
                    commands.append({'description': '测试', 'command': 'npm test'})
                if 'build' in scripts:
                    commands.append({'description': '构建', 'command': 'npm run build'})
                if 'lint' in scripts:
                    commands.append({'description': 'Lint', 'command': 'npm run lint'})
            except Exception:
                pass
        elif os.path.exists(os.path.join(root, 'pyproject.toml')):
            commands.append({'description': '安装', 'command': 'pip install -e .'})
            commands.append({'description': '测试', 'command': 'pytest'})
            commands.append({'description': 'Lint', 'command': 'ruff check .'})
        elif os.path.exists(os.path.join(root, 'go.mod')):
            commands.append({'description': '构建', 'command': 'go build ./...'})
            commands.append({'description': '测试', 'command': 'go test ./...'})
            commands.append({'description': '运行', 'command': 'go run .'})
        elif os.path.exists(os.path.join(root, 'Cargo.toml')):
            commands.append({'description': '构建', 'command': 'cargo build'})
            commands.append({'description': '测试', 'command': 'cargo test'})
            commands.append({'description': '运行', 'command': 'cargo run'})

        if not commands:
            commands.append({'description': '构建', 'command': 'make'})
            commands.append({'description': '测试', 'command': 'make test'})

        return commands

    def _scan_file(self, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()
        file_type = 'other'
        for key, extensions in self.file_types.items():
            if file_ext in extensions:
                file_type = key
                break
        return {
            'path': file_path,
            'type': file_type,
            'size': os.path.getsize(file_path),
            'mtime': os.path.getmtime(file_path)
        }

    def scan(self):
        if not self.force:
            cached_result = self._load_from_cache()
            if cached_result:
                return cached_result

        try:
            logging.info(f"开始扫描项目: {self.project_path}")
            logging.info(f"分析深度: {self.depth}")

            project_name = self._detect_project_name()
            tech_stack = self._detect_tech_stack()
            self._tech_stack = tech_stack
            commands = self._detect_commands()

            nexus_scripts_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'skills', 'nexus-mapper', 'scripts'
            )
            ast_output = os.path.join(self.project_path, '.nexus-map', 'raw', 'ast_nodes.json')
            file_tree_output = os.path.join(self.project_path, '.nexus-map', 'raw', 'file_tree.txt')
            os.makedirs(os.path.dirname(ast_output), exist_ok=True)

            import subprocess
            extract_ast_script = os.path.join(nexus_scripts_dir, 'extract_ast.py')
            if os.path.exists(extract_ast_script):
                cmd = [
                    'python3', extract_ast_script,
                    self.project_path,
                    '--file-tree-out', file_tree_output,
                    '--max-nodes', '10000'
                ]
                logging.info(f"执行 AST 提取: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    with open(ast_output, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    logging.info("AST 提取完成")
                else:
                    logging.warning(f"AST 提取失败: {result.stderr}")

            result = {
                'project_path': self.project_path,
                'project_name': project_name,
                'tech_stack': tech_stack,
                'commands': commands,
                'depth': self.depth,
                'file_count': 0,
                'total_lines': 0,
                'file_types': {},
                'modules': [],
                'scan_time': datetime.now().isoformat(),
                'nexus_ast_file': ast_output if os.path.exists(ast_output) else None
            }

            if os.path.exists(ast_output):
                try:
                    with open(ast_output, 'r', encoding='utf-8') as f:
                        ast_data = json.load(f)
                    if isinstance(ast_data, list):
                        for node in ast_data:
                            if 'file' in node:
                                file_path = node['file']
                                file_ext = os.path.splitext(file_path)[1].lower()
                                file_type = 'other'
                                for key, extensions in self.file_types.items():
                                    if file_ext in extensions:
                                        file_type = key
                                        break
                                if file_type not in result['file_types']:
                                    result['file_types'][file_type] = 0
                                result['file_types'][file_type] += 1
                                rel_path = os.path.relpath(file_path, self.project_path)
                                parts = rel_path.split(os.sep)
                                if len(parts) > 1:
                                    result['modules'].append(parts[0])
                            if 'lines' in node:
                                result['total_lines'] += node.get('lines', 0)
                        result['modules'] = list(set(result['modules']))
                        result['file_count'] = len(ast_data)
                except Exception as e:
                    logging.warning(f"AST 数据解析失败: {str(e)}")

            if result['file_count'] == 0:
                files_to_scan = []
                total_lines = 0
                for root, dirs, files in os.walk(self.project_path):
                    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'build', 'dist', 'target', '__pycache__']]
                    for file in files:
                        file_path = os.path.join(root, file)
                        files_to_scan.append(file_path)

                file_results = []
                max_workers = min(32, (os.cpu_count() or 1) * 2)
                logging.info(f"使用 {max_workers} 个线程进行并行扫描")

                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_file = {executor.submit(self._scan_file, file_path): file_path
                                      for file_path in files_to_scan}
                    for future in concurrent.futures.as_completed(future_to_file):
                        try:
                            file_result = future.result()
                            file_results.append(file_result)
                        except Exception as e:
                            logging.error(f"扫描文件失败: {future_to_file[future]} - {str(e)}")

                result['file_count'] = len(file_results)
                for file_result in file_results:
                    file_type = file_result['type']
                    if file_type not in result['file_types']:
                        result['file_types'][file_type] = 0
                    result['file_types'][file_type] += 1
                    try:
                        with open(file_result['path'], 'r', encoding='utf-8', errors='ignore') as f:
                            total_lines += sum(1 for _ in f)
                    except Exception:
                        pass

                modules = set()
                for file_result in file_results:
                    rel_path = os.path.relpath(file_result['path'], self.project_path)
                    parts = rel_path.split(os.sep)
                    if len(parts) > 1:
                        modules.add(parts[0])
                result['modules'] = list(modules)
                result['total_lines'] = total_lines

            logging.info(f"扫描完成，共发现 {result['file_count']} 个文件")
            logging.info(f"技术栈: {tech_stack}")
            logging.info(f"项目名称: {project_name}")

            self._save_to_cache(result)
            return result

        except Exception as e:
            logging.error(f"扫描过程中出错: {str(e)}")
            return {
                'project_path': self.project_path,
                'depth': self.depth,
                'error': str(e),
                'scan_time': datetime.now().isoformat()
            }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='扫描代码库')
    parser.add_argument('project_path', help='项目路径')
    parser.add_argument('--depth', default='standard',
                        choices=['fast', 'standard', 'deep', 'full'], help='分析深度')
    parser.add_argument('--force', action='store_true', help='强制重新扫描，忽略缓存')

    args = parser.parse_args()

    scanner = ScanEngine(args.project_path, args.depth, args.force)
    result = scanner.scan()
    print(json.dumps(result, indent=2, ensure_ascii=False))
