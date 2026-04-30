#!/usr/bin/env python3
"""
知识提取模块
负责从代码中提取业务逻辑和架构信息，基于实际代码分析而非硬编码
"""

import os
import json
import re
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class KnowledgeExtractor:
    def __init__(self, project_path, scan_result):
        self.project_path = project_path
        self.scan_result = scan_result
        self.tech_stack = scan_result.get('tech_stack', {})
        self.language = self.tech_stack.get('language', '')

    def extract(self):
        try:
            logging.info("开始提取知识")
            logging.info(f"技术栈: {self.tech_stack}")

            knowledge = {
                'architecture': {
                    'layers': [],
                    'modules': [],
                    'dependencies': []
                },
                'business_logic': {
                    'features': [],
                    'processes': [],
                    'rules': []
                },
                'core_processes': [],
                'core_classes': {
                    'controllers': [],
                    'services': [],
                    'mappers': [],
                    'repositories': [],
                    'models': []
                },
                'call_chains': [],
                'terms': [],
                'questions': {
                    'basic': [],
                    'config': [],
                    'development': [],
                    'deployment': []
                },
                'coding_standards': [],
                'security_constraints': [],
                'naming_conventions': [],
                'pitfalls': []
            }

            self._extract_architecture(knowledge)
            self._extract_business_logic(knowledge)
            self._extract_core_classes(knowledge)
            self._extract_core_processes(knowledge)
            self._extract_call_chains(knowledge)
            self._extract_constraints(knowledge)
            self._generate_questions(knowledge)

            logging.info("知识提取完成")
            logging.info(f"提取到 {len(knowledge['core_processes'])} 个核心流程")
            logging.info(f"提取到 {len(knowledge['business_logic']['features'])} 个业务功能")
            logging.info(f"提取到 {len(knowledge['core_classes']['controllers'])} 个 Controller")

            try:
                knowledge_file = os.path.join(self.project_path, '.repo-to-wiki', 'knowledge.json')
                os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
                with open(knowledge_file, 'w', encoding='utf-8') as f:
                    json.dump(knowledge, f, indent=2, ensure_ascii=False)
                logging.info(f"知识提取结果已保存: {knowledge_file}")
            except Exception as e:
                logging.warning(f"知识提取结果保存失败: {str(e)}")

            return knowledge

        except Exception as e:
            logging.error(f"知识提取过程中出错: {str(e)}")
            return None

    def _extract_architecture(self, knowledge):
        modules = self.scan_result.get('modules', [])
        language = self.language.lower()

        if 'java' in language or 'kotlin' in language:
            knowledge['architecture']['layers'] = ['controller', 'service', 'mapper/repository', 'entity/model']
            self._extract_java_architecture(knowledge, modules)
        elif 'python' in language:
            knowledge['architecture']['layers'] = ['view/api', 'service', 'model/dao']
            self._extract_python_architecture(knowledge, modules)
        elif 'javascript' in language or 'typescript' in language:
            knowledge['architecture']['layers'] = ['route/controller', 'service', 'repository/dao', 'model']
            self._extract_js_architecture(knowledge, modules)
        elif 'go' in language:
            knowledge['architecture']['layers'] = ['handler', 'service', 'repository', 'model']
            self._extract_go_architecture(knowledge, modules)
        else:
            knowledge['architecture']['layers'] = ['presentation', 'business', 'data']
            for module in modules[:10]:
                knowledge['architecture']['modules'].append({
                    'name': module,
                    'layer': 'business',
                    'responsibility': f'{module} 模块'
                })

    def _extract_java_architecture(self, knowledge, modules):
        for module in modules:
            module_dir = os.path.join(self.project_path, module)
            if not os.path.isdir(module_dir):
                continue

            src_dir = os.path.join(module_dir, 'src', 'main', 'java')
            if not os.path.exists(src_dir):
                src_dir = module_dir

            responsibility = self._infer_module_responsibility(module, src_dir, 'java')
            knowledge['architecture']['modules'].append({
                'name': module,
                'layer': self._infer_layer(module),
                'responsibility': responsibility
            })

    def _extract_python_architecture(self, knowledge, modules):
        for module in modules:
            module_dir = os.path.join(self.project_path, module)
            if not os.path.isdir(module_dir):
                continue
            responsibility = self._infer_module_responsibility(module, module_dir, 'python')
            knowledge['architecture']['modules'].append({
                'name': module,
                'layer': self._infer_layer(module),
                'responsibility': responsibility
            })

    def _extract_js_architecture(self, knowledge, modules):
        for module in modules:
            module_dir = os.path.join(self.project_path, module)
            if not os.path.isdir(module_dir):
                continue
            responsibility = self._infer_module_responsibility(module, module_dir, 'js')
            knowledge['architecture']['modules'].append({
                'name': module,
                'layer': self._infer_layer(module),
                'responsibility': responsibility
            })

    def _extract_go_architecture(self, knowledge, modules):
        for module in modules:
            module_dir = os.path.join(self.project_path, module)
            if not os.path.isdir(module_dir):
                continue
            responsibility = self._infer_module_responsibility(module, module_dir, 'go')
            knowledge['architecture']['modules'].append({
                'name': module,
                'layer': self._infer_layer(module),
                'responsibility': responsibility
            })

    def _infer_layer(self, module_name):
        name = module_name.lower()
        if any(k in name for k in ['web', 'api', 'controller', 'admin', 'ui', 'view', 'page', 'app']):
            return 'presentation'
        elif any(k in name for k in ['service', 'business', 'logic', 'core', 'domain']):
            return 'business'
        elif any(k in name for k in ['dao', 'mapper', 'repository', 'data', 'model', 'entity', 'db']):
            return 'data'
        elif any(k in name for k in ['common', 'util', 'config', 'framework']):
            return 'infrastructure'
        elif any(k in name for k in ['test', 'spec']):
            return 'test'
        return 'business'

    def _infer_module_responsibility(self, module_name, src_dir, lang):
        name = module_name.lower()
        name_map = {
            'user': '用户管理：注册、登录、权限、个人信息',
            'admin': '管理后台：系统配置、用户管理、数据维护',
            'system': '系统管理：配置、字典、日志、监控',
            'order': '订单管理：创建、支付、状态流转',
            'product': '产品管理：商品信息、库存、分类',
            'payment': '支付管理：支付渠道、退款、对账',
            'auth': '认证授权：登录、权限、令牌管理',
            'common': '公共模块：工具类、常量、异常定义',
            'framework': '框架核心：基础配置、拦截器、过滤器',
            'generator': '代码生成：模板、生成策略、输出',
            'quartz': '定时任务：调度、执行、监控',
            'config': '配置管理：系统参数、环境配置',
        }
        for key, desc in name_map.items():
            if key in name:
                return desc

        controller_count = 0
        service_count = 0
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                fl = f.lower()
                if 'controller' in fl:
                    controller_count += 1
                elif 'service' in fl:
                    service_count += 1
        if controller_count > 0:
            return f'{module_name} 模块（含 {controller_count} 个 Controller、{service_count} 个 Service）'
        elif service_count > 0:
            return f'{module_name} 模块（含 {service_count} 个 Service）'
        return f'{module_name} 模块'

    def _extract_business_logic(self, knowledge):
        language = self.language.lower()

        if 'java' in language or 'kotlin' in language:
            self._extract_java_business(knowledge)
        elif 'python' in language:
            self._extract_python_business(knowledge)
        elif 'javascript' in language or 'typescript' in language:
            self._extract_js_business(knowledge)
        else:
            self._extract_generic_business(knowledge)

    def _extract_java_business(self, knowledge):
        controller_pattern = re.compile(r'@(RestController|Controller)')
        request_mapping = re.compile(r'@(?:Request|Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']')
        service_pattern = re.compile(r'@Service')
        class_pattern = re.compile(r'public\s+(?:class|interface)\s+(\w+)')

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'target', 'build', '.idea']]
            for file in files:
                if not file.endswith('.java'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                rel_path = os.path.relpath(file_path, self.project_path)
                module = rel_path.split(os.sep)[0] if os.sep in rel_path else ''

                if controller_pattern.search(content):
                    class_match = class_pattern.search(content)
                    class_name = class_match.group(1) if class_match else file.replace('.java', '')
                    endpoints = request_mapping.findall(content)
                    if endpoints:
                        feature_name = class_name.replace('Controller', '').replace('Controller', '')
                        knowledge['business_logic']['features'].append({
                            'name': f'{module} - {feature_name}',
                            'description': f'API 端点: {", ".join(endpoints[:5])}',
                            'module': module,
                            'endpoints': endpoints
                        })

    def _extract_python_business(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']]
            for file in files:
                if not file.endswith('.py'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                rel_path = os.path.relpath(file_path, self.project_path)
                module = rel_path.split(os.sep)[0] if os.sep in rel_path else ''

                if 'views' in file.lower() or 'api' in file.lower() or 'router' in file.lower():
                    route_patterns = re.findall(r'@(?:app|router)\.(?:route|get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']', content)
                    if not route_patterns:
                        route_patterns = re.findall(r'(?:path|url)\s*=\s*["\']([^"\']+)["\']', content)
                    if route_patterns:
                        feature_name = file.replace('.py', '').replace('_', ' ').title()
                        knowledge['business_logic']['features'].append({
                            'name': f'{module} - {feature_name}',
                            'description': f'API 端点: {", ".join(route_patterns[:5])}',
                            'module': module
                        })

    def _extract_js_business(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'dist', 'build', '.next']]
            for file in files:
                if not file.endswith(('.ts', '.js', '.tsx', '.jsx')):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                rel_path = os.path.relpath(file_path, self.project_path)
                module = rel_path.split(os.sep)[0] if os.sep in rel_path else ''

                route_patterns = re.findall(r'(?:router|app)\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
                if route_patterns:
                    feature_name = file.replace('.ts', '').replace('.js', '').replace('.tsx', '').replace('.jsx', '')
                    knowledge['business_logic']['features'].append({
                        'name': f'{module} - {feature_name}',
                        'description': f'API 端点: {", ".join(route_patterns[:5])}',
                        'module': module
                    })

    def _extract_generic_business(self, knowledge):
        for module in self.scan_result.get('modules', []):
            knowledge['business_logic']['features'].append({
                'name': f'{module} - 业务模块',
                'description': f'{module} 相关业务功能（LOW_CONFIDENCE - 未能自动提取详细信息）',
                'module': module
            })

    def _extract_core_classes(self, knowledge):
        language = self.language.lower()

        if 'java' in language or 'kotlin' in language:
            self._extract_java_core_classes(knowledge)
        elif 'python' in language:
            self._extract_python_core_classes(knowledge)
        elif 'javascript' in language or 'typescript' in language:
            self._extract_js_core_classes(knowledge)

    def _extract_java_core_classes(self, knowledge):
        class_pattern = re.compile(r'public\s+(?:class|interface)\s+(\w+)')
        controller_pattern = re.compile(r'@(RestController|Controller)')
        service_pattern = re.compile(r'@Service')
        mapper_pattern = re.compile(r'@(Mapper|Repository)')

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'target', 'build', '.idea']]
            for file in files:
                if not file.endswith('.java'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                class_match = class_pattern.search(content)
                if not class_match:
                    continue
                class_name = class_match.group(1)

                if controller_pattern.search(content):
                    endpoints = re.findall(r'@(?:Request|Get|Post|Put|Delete)Mapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']', content)
                    knowledge['core_classes']['controllers'].append({
                        'name': class_name,
                        'function': f'API: {", ".join(endpoints[:3])}' if endpoints else class_name
                    })
                elif service_pattern.search(content):
                    methods = re.findall(r'public\s+\w+\s+(\w+)\s*\(', content)
                    knowledge['core_classes']['services'].append({
                        'name': class_name,
                        'function': f'方法: {", ".join(methods[:3])}' if methods else class_name
                    })
                elif mapper_pattern.search(content):
                    knowledge['core_classes']['mappers'].append({
                        'name': class_name,
                        'function': class_name
                    })

    def _extract_python_core_classes(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv']]
            for file in files:
                if not file.endswith('.py'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                class_names = re.findall(r'class\s+(\w+)', content)
                for cn in class_names:
                    if 'view' in cn.lower() or 'api' in cn.lower():
                        knowledge['core_classes']['controllers'].append({'name': cn, 'function': cn})
                    elif 'service' in cn.lower():
                        knowledge['core_classes']['services'].append({'name': cn, 'function': cn})
                    elif 'model' in cn.lower() or 'entity' in cn.lower():
                        knowledge['core_classes']['models'].append({'name': cn, 'function': cn})

    def _extract_js_core_classes(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'dist', 'build']]
            for file in files:
                if not file.endswith(('.ts', '.js', '.tsx', '.jsx')):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                if 'controller' in file.lower():
                    name = file.replace('.ts', '').replace('.js', '')
                    knowledge['core_classes']['controllers'].append({'name': name, 'function': name})
                elif 'service' in file.lower():
                    name = file.replace('.ts', '').replace('.js', '')
                    knowledge['core_classes']['services'].append({'name': name, 'function': name})
                elif 'repository' in file.lower() or 'dao' in file.lower():
                    name = file.replace('.ts', '').replace('.js', '')
                    knowledge['core_classes']['repositories'].append({'name': name, 'function': name})

    def _extract_core_processes(self, knowledge):
        language = self.language.lower()

        if 'java' in language or 'kotlin' in language:
            self._extract_java_core_processes(knowledge)
        elif 'python' in language:
            self._extract_python_core_processes(knowledge)
        elif 'javascript' in language or 'typescript' in language:
            self._extract_js_core_processes(knowledge)

        if not knowledge['core_processes']:
            logging.warning("未能自动提取核心业务流程，标注 LOW_CONFIDENCE")
            for feature in knowledge['business_logic']['features'][:3]:
                knowledge['core_processes'].append({
                    'module': feature.get('module', 'unknown'),
                    'process': feature['name'],
                    'description': feature['description'],
                    'steps': ['LOW_CONFIDENCE - 需要人工补充详细步骤'],
                    'confidence': 'low'
                })

    def _extract_java_core_processes(self, knowledge):
        controller_pattern = re.compile(r'@(RestController|Controller)')
        method_pattern = re.compile(r'@(?:Post|Put)Mapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']')
        method_name_pattern = re.compile(r'public\s+\w+\s+(\w+)\s*\(')

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'target', 'build', '.idea']]
            for file in files:
                if not file.endswith('.java'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                if not controller_pattern.search(content):
                    continue

                rel_path = os.path.relpath(file_path, self.project_path)
                module = rel_path.split(os.sep)[0] if os.sep in rel_path else ''

                class_name = file.replace('.java', '')
                post_endpoints = method_pattern.findall(content)
                service_calls = re.findall(r'(\w+Service)\.\w+', content)

                if post_endpoints or service_calls:
                    process_name = class_name.replace('Controller', '')
                    steps = []
                    for svc in service_calls[:3]:
                        steps.append(f'调用 {svc} 处理业务逻辑')
                    for ep in post_endpoints[:2]:
                        steps.append(f'处理 POST 请求: {ep}')
                    if not steps:
                        steps = ['接收请求', '调用 Service 处理', '返回结果']

                    knowledge['core_processes'].append({
                        'module': module,
                        'process': process_name,
                        'description': f'{process_name} 相关业务流程',
                        'steps': steps,
                        'confidence': 'medium'
                    })

    def _extract_python_core_processes(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv']]
            for file in files:
                if not file.endswith('.py'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                if 'views' not in file.lower() and 'api' not in file.lower():
                    continue

                rel_path = os.path.relpath(file_path, self.project_path)
                module = rel_path.split(os.sep)[0] if os.sep in rel_path else ''

                functions = re.findall(r'def\s+(\w+)\s*\(', content)
                post_funcs = [f for f in functions if any(k in f.lower() for k in ['create', 'post', 'add', 'save', 'update', 'delete'])]

                if post_funcs:
                    process_name = file.replace('.py', '').replace('_', ' ').title()
                    knowledge['core_processes'].append({
                        'module': module,
                        'process': process_name,
                        'description': f'{process_name} 相关业务流程',
                        'steps': [f'执行 {func}' for func in post_funcs[:5]],
                        'confidence': 'medium'
                    })

    def _extract_js_core_processes(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'dist', 'build']]
            for file in files:
                if not file.endswith(('.ts', '.js')):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                if 'controller' not in file.lower() and 'service' not in file.lower():
                    continue

                rel_path = os.path.relpath(file_path, self.project_path)
                module = rel_path.split(os.sep)[0] if os.sep in rel_path else ''

                functions = re.findall(r'(?:async\s+)?(?:function\s+)?(\w+)\s*\(', content)
                if functions:
                    process_name = file.replace('.ts', '').replace('.js', '')
                    knowledge['core_processes'].append({
                        'module': module,
                        'process': process_name,
                        'description': f'{process_name} 相关业务流程',
                        'steps': [f'执行 {func}' for func in functions[:5]],
                        'confidence': 'medium'
                    })

    def _extract_call_chains(self, knowledge):
        language = self.language.lower()

        if 'java' in language or 'kotlin' in language:
            self._extract_java_call_chains(knowledge)

        if not knowledge['call_chains']:
            for process in knowledge['core_processes'][:2]:
                knowledge['call_chains'].append({
                    'name': process['process'],
                    'flow': ' → '.join(process.get('steps', [])),
                    'confidence': 'low'
                })

    def _extract_java_call_chains(self, knowledge):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'target', 'build', '.idea']]
            for file in files:
                if not file.endswith('.java'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue

                if '@Controller' not in content and '@RestController' not in content:
                    continue

                class_name = file.replace('.java', '')
                service_calls = re.findall(r'(\w+Service)\.\w+', content)
                if service_calls:
                    chain = [f'{class_name} (Controller)']
                    for svc in service_calls[:3]:
                        chain.append(f'{svc} (Service)')
                    knowledge['call_chains'].append({
                        'name': f'{class_name} 调用链',
                        'flow': ' → '.join(chain),
                        'confidence': 'medium'
                    })

    def _extract_constraints(self, knowledge):
        language = self.language.lower()
        framework = self.tech_stack.get('framework', '').lower()

        if 'java' in language:
            knowledge['naming_conventions'] = [
                '类名：PascalCase（UserService）',
                '方法名：camelCase（getUserById）',
                '常量：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）',
                '包名：全小写（com.example.project）',
            ]
            if 'spring' in framework:
                knowledge['coding_standards'] = [
                    'Controller 只做参数校验和路由转发',
                    'Service 层处理业务逻辑',
                    'Repository/Mapper 层只做数据访问',
                    '使用 @Autowired 或构造器注入',
                ]
                knowledge['security_constraints'] = [
                    '所有接口必须有权限控制',
                    '禁止在日志中输出敏感信息',
                    'SQL 必须使用参数化查询',
                ]
                knowledge['pitfalls'] = [
                    'Spring Boot 配置文件不要硬编码密码',
                    '@Transactional 注解在同类方法调用时不生效',
                    '避免在 Controller 层写业务逻辑',
                ]
        elif 'python' in language:
            knowledge['naming_conventions'] = [
                '类名：PascalCase（UserService）',
                '函数/变量：snake_case（get_user_by_id）',
                '常量：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）',
            ]
            knowledge['coding_standards'] = [
                '遵循 PEP 8 编码规范',
                '使用类型注解',
                '异常统一捕获处理',
            ]
        elif 'javascript' in language or 'typescript' in language:
            knowledge['naming_conventions'] = [
                '类名：PascalCase（UserService）',
                '函数/变量：camelCase（getUserById）',
                '常量：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）',
                '文件名：kebab-case（user-service.ts）',
            ]
            knowledge['coding_standards'] = [
                '使用 ESLint + Prettier',
                '优先使用 const/let，禁止 var',
                '异步操作使用 async/await',
            ]

    def _generate_questions(self, knowledge):
        features = knowledge['business_logic']['features']
        modules = [m['name'] for m in knowledge['architecture']['modules']]

        knowledge['questions']['basic'] = [
            f'项目包含哪些核心模块？({", ".join(modules[:5])})',
            f'项目的技术栈是什么？({self.tech_stack.get("language", "Unknown")} + {self.tech_stack.get("framework", "Unknown")})',
            '项目的入口文件在哪里？',
            '项目的认证/授权方式是什么？',
        ]
        knowledge['questions']['config'] = [
            '数据库连接配置在哪里？',
            '缓存配置如何设置？',
            '日志级别如何调整？',
            '环境变量如何管理？',
        ]
        knowledge['questions']['development'] = [
            '如何新增一个 API 端点？',
            '如何新增一个业务服务？',
            '如何新增一个数据访问方法？',
            '如何编写单元测试？',
        ]
        knowledge['questions']['deployment'] = [
            '如何构建生产版本？',
            '如何部署到服务器？',
            '如何进行数据库迁移？',
            '如何监控应用运行状态？',
        ]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    scan_result_file = os.path.join(project_path, '.repo-to-wiki', 'scan_result.json')
    if os.path.exists(scan_result_file):
        with open(scan_result_file, 'r', encoding='utf-8') as f:
            scan_result = json.load(f)
    else:
        scan_result = {
            'project_path': project_path,
            'file_count': 0,
            'modules': [],
            'tech_stack': {}
        }

    extractor = KnowledgeExtractor(project_path, scan_result)
    knowledge = extractor.extract()
    if knowledge:
        print(json.dumps(knowledge, indent=2, ensure_ascii=False))
    else:
        print("知识提取失败")
