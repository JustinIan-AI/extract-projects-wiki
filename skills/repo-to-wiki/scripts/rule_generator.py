#!/usr/bin/env python3
"""
规则文件生成器
基于 legacy-rule-miner 方法论，生成 AI 编程规则文件
所有 fallback 默认值根据技术栈动态选择
"""

import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 获取技能根目录
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RuleGenerator:
    def __init__(self, project_path, scan_result, knowledge):
        self.project_path = project_path
        self.scan_result = scan_result
        self.knowledge = knowledge
        self.tech_stack = scan_result.get('tech_stack', {})
        self.language = self.tech_stack.get('language', '')
        self.framework = self.tech_stack.get('framework', '')
        self.build_tool = self.tech_stack.get('build_tool', '')

    def generate_all(self, output_dir, tools=None):
        if tools is None:
            tools = ['claude', 'agents']

        logging.info(f"开始生成规则文件，输出目录: {output_dir}")
        logging.info(f"技术栈: {self.tech_stack}")
        logging.info(f"目标工具: {', '.join(tools)}")

        os.makedirs(output_dir, exist_ok=True)

        if 'agents' in tools:
            self._generate_agents_md(output_dir)

        if 'claude' in tools:
            self._generate_claude_md(output_dir)
            self._generate_claude_rules(output_dir)
            self._generate_claude_local_md(output_dir)

        if 'cursor' in tools:
            self._generate_cursorrules(output_dir)

        if 'copilot' in tools:
            self._generate_copilot_instructions(output_dir)

        logging.info("规则文件生成完成")

    def _load_template(self, template_name):
        """从 assets/wiki 目录加载模板文件"""
        template_path = os.path.join(SKILL_DIR, 'assets', 'wiki', template_name)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def _generate_agents_md(self, output_dir):
        """使用模板生成 AGENTS.md"""
        template = self._load_template('AGENTS.md')
        if template:
            content = self._fill_agents_template(template)
        else:
            content = self._build_agents_content()
        
        filepath = os.path.join(output_dir, 'AGENTS.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info("AGENTS.md 生成完成")

    def _fill_agents_template(self, template):
        """填充 AGENTS.md 模板占位符"""
        project_name = self.scan_result.get('project_name', os.path.basename(self.project_path))
        date = datetime.now().strftime('%Y-%m-%d')
        
        lang = self.language.lower()
        
        # 后端技术栈
        backend_language = self._get_backend_language()
        backend_framework = self.framework or ('Spring Boot' if 'java' in lang else 
                                                'Django/Flask' if 'python' in lang else
                                                'Express/Next.js' if 'javascript' in lang or 'typescript' in lang else
                                                'Gin/Echo' if 'go' in lang else 'Unknown')
        orm = self.tech_stack.get('orm', ('MyBatis/JPA' if 'java' in lang else 
                                          'SQLAlchemy' if 'python' in lang else 
                                          'Prisma' if 'javascript' in lang or 'typescript' in lang else 
                                          ''))
        database = self.tech_stack.get('database', 'MySQL/PostgreSQL')
        cache = self.tech_stack.get('cache', 'Redis')
        
        # 前端技术栈（如有）
        frontend_framework = ''
        state_management = ''
        ui_library = ''
        build_tool = ''
        
        # 基础设施
        containerization = self.tech_stack.get('containerization', 'Docker')
        cicd = self.tech_stack.get('cicd', 'GitHub Actions')
        repo_structure = self.tech_stack.get('repo_structure', 'monorepo' if 'monorepo' in str(self.scan_result.get('modules', [])).lower() else 'multi-repo')
        
        # 常用命令
        commands = self._extract_commands()
        dev_command = self._get_command_by_desc(commands, '开发') or self._get_command_by_desc(commands, '运行') or ''
        test_command = self._get_command_by_desc(commands, '测试') or ''
        build_command = self._get_command_by_desc(commands, '构建') or ''
        lint_command = self._get_command_by_desc(commands, 'Lint') or ''
        format_command = self._get_command_by_desc(commands, '格式化') or ''
        db_command = self._get_command_by_desc(commands, '数据库') or ''
        dependency_command = self._get_command_by_desc(commands, '安装') or ''
        
        # 目录结构
        controller_dir = 'controller/' if 'java' in lang else 'routes/' if 'javascript' in lang or 'typescript' in lang else 'views/'
        service_dir = 'service/' if 'java' in lang else 'services/'
        repository_dir = 'mapper/' if 'mybatis' in self.tech_stack.get('orm', '').lower() else 'repository/' if 'java' in lang else 'models/'
        model_dir = 'entity/' if 'java' in lang else 'models/'
        middleware_dir = 'middleware/' if 'javascript' in lang or 'typescript' in lang else ''
        utils_dir = 'util/' if 'java' in lang else 'utils/'
        
        controller_name = 'Controller' if 'java' in lang else 'Route/Controller'
        service_name = 'Service' if 'java' in lang else 'Service'
        repository_name = 'Mapper' if 'mybatis' in self.tech_stack.get('orm', '').lower() else 'Repository'
        
        # 禁止改动区域
        prohibited_dirs = self._get_prohibited_dirs()
        
        # 技术选型约束表
        tech_constraints_table = self._get_tech_constraints_table()
        
        # 安全规则
        data_security_rules = '\n'.join([f"- {rule}" for rule in self._extract_security_rules()])
        input_validation_rules = "- 所有外部输入 MUST 经过 schema 校验\n- NEVER 直接拼接用户输入到 SQL/命令中"
        secret_management_rules = "- NEVER 硬编码密钥、密码、Access Token\n- 所有密钥必须从环境变量或配置中心读取"
        
        # API 设计规范
        success_response_example = self._get_success_response_example()
        error_response_example = self._get_error_response_example()
        path_naming_rules = f"- 统一使用 `/api/v1/` 前缀\n- 使用名词而非动词：`/users` 而非 `/getUsers`"
        error_handling_rules = "- 使用统一的错误码和错误格式\n- 业务异常使用 BusinessException"
        
        # 测试规范
        test_framework = self._get_test_framework()
        coverage_requirement = "核心业务逻辑 80%，工具函数 90%"
        test_file_location = self._get_test_file_location()
        
        # 经验教训
        lessons_learned = '\n'.join([f"- {pitfall}" for pitfall in self._extract_pitfalls()[:5]])
        
        # 私有依赖
        private_dependencies = "无"
        
        # 参考文档链接
        architecture_doc_link = "[wiki/ai/L1_architecture.md](./wiki/ai/L1_architecture.md)"
        api_doc_link = "[wiki/ai/L2_modules.md](./wiki/ai/L2_modules.md)"
        database_doc_link = "[wiki/ai/L3_business.md](./wiki/ai/L3_business.md)"
        deployment_doc_link = "#"

        replacements = {
            '{project_name}': project_name,
            '{date}': date,
            '{backend_language}': backend_language,
            '{backend_framework}': backend_framework,
            '{orm}': orm,
            '{database}': database,
            '{cache}': cache,
            '{frontend_framework}': frontend_framework,
            '{state_management}': state_management,
            '{ui_library}': ui_library,
            '{build_tool}': build_tool,
            '{containerization}': containerization,
            '{cicd}': cicd,
            '{repo_structure}': repo_structure,
            '{dev_command}': dev_command,
            '{test_command}': test_command,
            '{build_command}': build_command,
            '{lint_command}': lint_command,
            '{format_command}': format_command,
            '{db_command}': db_command,
            '{dependency_command}': dependency_command,
            '{controller_dir}': controller_dir,
            '{service_dir}': service_dir,
            '{repository_dir}': repository_dir,
            '{model_dir}': model_dir,
            '{middleware_dir}': middleware_dir,
            '{utils_dir}': utils_dir,
            '{prohibited_dirs}': prohibited_dirs,
            '{controller_name}': controller_name,
            '{service_name}': service_name,
            '{repository_name}': repository_name,
            '{tech_constraints_table}': tech_constraints_table,
            '{data_security_rules}': data_security_rules,
            '{input_validation_rules}': input_validation_rules,
            '{secret_management_rules}': secret_management_rules,
            '{success_response_example}': success_response_example,
            '{error_response_example}': error_response_example,
            '{path_naming_rules}': path_naming_rules,
            '{error_handling_rules}': error_handling_rules,
            '{test_framework}': test_framework,
            '{coverage_requirement}': coverage_requirement,
            '{test_file_location}': test_file_location,
            '{lessons_learned}': lessons_learned,
            '{private_dependencies}': private_dependencies,
            '{architecture_doc_link}': architecture_doc_link,
            '{api_doc_link}': api_doc_link,
            '{database_doc_link}': database_doc_link,
            '{deployment_doc_link}': deployment_doc_link,
        }

        content = template
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content

    def _get_backend_language(self):
        lang = self.language.lower()
        if 'java' in lang:
            return 'Java ' + self.tech_stack.get('java_version', '21')
        elif 'python' in lang:
            return 'Python ' + self.tech_stack.get('python_version', '3.12')
        elif 'javascript' in lang or 'typescript' in lang:
            return lang.capitalize() + ' ' + self.tech_stack.get('node_version', '22')
        elif 'go' in lang:
            return 'Go ' + self.tech_stack.get('go_version', '1.22')
        return self.language or 'Unknown'

    def _get_command_by_desc(self, commands, desc):
        for cmd in commands:
            if desc.lower() in cmd['description'].lower():
                return cmd['command']
        return None

    def _get_prohibited_dirs(self):
        return "无明确禁止改动的目录"

    def _get_tech_constraints_table(self):
        lang = self.language.lower()
        if 'java' in lang:
            return """| 状态管理 | Spring Context | - |
| HTTP 请求 | RestTemplate/WebClient | - |
| JSON 处理 | Jackson | Gson |"""
        elif 'python' in lang:
            return """| ORM | SQLAlchemy | 裸写 SQL |
| HTTP 请求 | requests | urllib |"""
        elif 'javascript' in lang or 'typescript' in lang:
            return """| 状态管理 | Zustand | Redux |
| HTTP 请求 | axios | 原生 fetch |
| 日期处理 | dayjs | moment.js（已废弃）|"""
        return "| - | - | - |"

    def _get_success_response_example(self):
        lang = self.language.lower()
        if 'java' in lang:
            return "return AjaxResult.success(data);"
        elif 'python' in lang:
            return "return {'code': 0, 'data': result, 'message': 'success'}"
        elif 'javascript' in lang or 'typescript' in lang:
            return "res.json({ code: 0, data: result, message: 'success' });"
        return "// 正确响应格式"

    def _get_error_response_example(self):
        lang = self.language.lower()
        if 'java' in lang:
            return "// return data directly;"
        elif 'python' in lang:
            return "# return result directly"
        elif 'javascript' in lang or 'typescript' in lang:
            return "// res.json(result);"
        return "// 错误响应格式"

    def _get_test_framework(self):
        lang = self.language.lower()
        if 'java' in lang:
            return 'JUnit 5 + Mockito'
        elif 'python' in lang:
            return 'pytest + pytest-mock'
        elif 'javascript' in lang or 'typescript' in lang:
            return 'Jest / Vitest'
        elif 'go' in lang:
            return 'Go testing + testify'
        return '根据项目配置'

    def _get_test_file_location(self):
        lang = self.language.lower()
        if 'java' in lang:
            return '与源文件同包，`src/test/java/`'
        elif 'python' in lang:
            return '`tests/` 目录'
        elif 'javascript' in lang or 'typescript' in lang:
            return '与源文件同目录或 `__tests__/` 目录'
        elif 'go' in lang:
            return '与源文件同目录'
        return '根据项目配置'

    def _build_agents_content(self):
        """备用：直接生成内容（当模板不存在时）"""
        project_name = self.scan_result.get('project_name', os.path.basename(self.project_path))

        content = f"""# AGENTS.md — {project_name} AI 协作规范

> 版本：v1.0 | 最后更新：{datetime.now().strftime('%Y-%m-%d')} | 自动生成

---

## 技术栈

### 后端
"""
        lang = self.language
        if 'java' in lang.lower():
            content += f"- 语言：Java\n"
            content += f"- 框架：{self.framework or 'Spring Boot'}\n"
            content += f"- ORM：{self.tech_stack.get('orm', 'MyBatis/JPA')}\n"
            content += f"- 构建工具：{self.build_tool or 'Maven'}\n"
            if self.tech_stack.get('auth'):
                content += f"- 认证：{self.tech_stack['auth']}\n"
            if self.tech_stack.get('cache'):
                content += f"- 缓存：{self.tech_stack['cache']}\n"
        elif 'python' in lang.lower():
            content += f"- 语言：Python\n"
            content += f"- 框架：{self.framework or 'Django/Flask'}\n"
            content += f"- 构建工具：{self.build_tool or 'pip'}\n"
        elif 'javascript' in lang.lower() or 'typescript' in lang.lower():
            content += f"- 语言：{lang}\n"
            content += f"- 框架：{self.framework or 'Express/Next.js'}\n"
            content += f"- 构建工具：{self.build_tool or 'npm'}\n"
            if self.tech_stack.get('orm'):
                content += f"- ORM：{self.tech_stack['orm']}\n"
        elif 'go' in lang.lower():
            content += f"- 语言：Go\n"
            content += f"- 框架：{self.framework or 'Gin/Echo'}\n"
            content += f"- 构建工具：{self.build_tool or 'Go Modules'}\n"
        else:
            content += f"- 语言：{lang or 'Unknown'}\n"
            if self.framework:
                content += f"- 框架：{self.framework}\n"

        content += "\n### 常用命令\n\n```bash\n"
        for cmd in self._extract_commands():
            content += f"# {cmd['description']}\n{cmd['command']}\n"
        content += "```\n\n"

        content += "## 目录结构\n\n```\n"
        content += self._extract_directory_structure()
        content += "```\n\n"

        content += "## 架构约束\n\n"
        for constraint in self._extract_layer_constraints():
            content += f"- {constraint}\n"
        content += "\n"

        content += "### 安全红线\n"
        for rule in self._extract_security_rules():
            content += f"- {rule}\n"
        content += "\n"

        content += "## 代码风格\n\n"
        for rule in self._extract_naming_rules():
            content += f"- {rule}\n"
        content += "\n"

        content += "## 已知陷阱\n\n"
        for pitfall in self._extract_pitfalls():
            content += f"- {pitfall}\n"
        content += "\n"

        content += "## 参考文档\n\n"
        content += "- 完整架构文档：[wiki/ai/L1_architecture.md](./wiki/ai/L1_architecture.md)\n"
        content += "- 模块详情：[wiki/ai/L2_modules.md](./wiki/ai/L2_modules.md)\n"
        content += "- 业务逻辑：[wiki/ai/L3_business.md](./wiki/ai/L3_business.md)\n\n"

        return content

    def _generate_claude_md(self, output_dir):
        """使用模板生成 CLAUDE.md"""
        template = self._load_template('CLAUDE.md')
        if template:
            content = self._fill_claude_template(template)
        else:
            content = self._build_claude_content()
        
        claude_dir = os.path.join(output_dir, '.claude')
        os.makedirs(claude_dir, exist_ok=True)
        filepath = os.path.join(output_dir, 'CLAUDE.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info("CLAUDE.md 生成完成")

    def _fill_claude_template(self, template):
        """填充 CLAUDE.md 模板占位符"""
        project_name = self.scan_result.get('project_name', os.path.basename(self.project_path))
        date = datetime.now().strftime('%Y-%m-%d')
        
        commands = self._extract_commands()
        lint_command = self._get_command_by_desc(commands, 'Lint') or 'npm run lint / ruff check .'
        test_command = self._get_command_by_desc(commands, '测试') or 'npm run test / pytest'
        
        tech_stack_str = '\n'.join([f"- **{key}**: {value}" for key, value in self.tech_stack.items()])
        architecture_decisions = "# 架构决策\n- 采用分层架构设计\n- 遵循单一职责原则"
        
        commands_str = '\n'.join([f"# {cmd['description']}\n{cmd['command']}" for cmd in commands])
        pitfalls_str = '\n'.join([f"- {pitfall}" for pitfall in self._extract_pitfalls()])

        replacements = {
            '{project_name}': project_name,
            '{date}': date,
            '{lint_command}': lint_command,
            '{test_command}': test_command,
            '{tech_stack}': tech_stack_str,
            '{architecture_decisions}': architecture_decisions,
            '{commands}': commands_str,
            '{pitfalls}': pitfalls_str,
        }

        content = template
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content

    def _build_claude_content(self):
        """备用：直接生成内容（当模板不存在时）"""
        project_name = self.scan_result.get('project_name', os.path.basename(self.project_path))

        content = f"""# CLAUDE.md — {project_name}

> 自动生成 | 版本：v1.0 | {datetime.now().strftime('%Y-%m-%d')}

## 概述

本项目使用 {self.language} + {self.framework} 技术栈。使用本规则文件确保 AI 助手的代码修改与项目现有风格和约束保持一致。

## 核心原则

1. **Copy-Paste First** — 新代码必须模仿最近的同类代码
2. **No Surprise** — 禁止引入项目从未使用过的模式
3. **Version Lock** — 禁止升级依赖版本，除非明确要求
4. **Gradual Improvement Only** — 只能做方法内的安全改进
5. **Pitfall Awareness** — 已知陷阱必须显式标注

---

@AGENTS.md

---

## Claude Code 专属配置

### 模块化规则导入
@.claude/rules/testing.md
@.claude/rules/api-design.md
@.claude/rules/architecture.md

### 技术栈（是什么）
"""
        for key, value in self.tech_stack.items():
            content += f"- **{key}**: {value}\n"

        content += "\n### 常用命令（怎么做）\n```bash\n"
        for cmd in self._extract_commands():
            content += f"# {cmd['description']}\n{cmd['command']}\n"
        content += "```\n\n"

        content += "### 已知陷阱\n"
        for pitfall in self._extract_pitfalls():
            content += f"- 🔒 {pitfall}\n"
        content += "\n"

        return content

    def _generate_claude_rules(self, output_dir):
        rules_dir = os.path.join(output_dir, '.claude', 'rules')
        os.makedirs(rules_dir, exist_ok=True)
        self._generate_testing_rules(rules_dir)
        self._generate_api_design_rules(rules_dir)
        self._generate_architecture_rules(rules_dir)
        logging.info(".claude/rules/ 目录生成完成")

    def _generate_testing_rules(self, rules_dir):
        lang = self.language.lower()
        if 'java' in lang:
            content = self._java_testing_rules()
        elif 'python' in lang:
            content = self._python_testing_rules()
        elif 'javascript' in lang or 'typescript' in lang:
            content = self._js_testing_rules()
        elif 'go' in lang:
            content = self._go_testing_rules()
        else:
            content = self._generic_testing_rules()

        with open(os.path.join(rules_dir, 'testing.md'), 'w', encoding='utf-8') as f:
            f.write(content)

    def _java_testing_rules(self):
        return """# 测试规范

## 测试框架
- 使用 JUnit 5 + Mockito
- 测试文件位置：`src/test/java/` 与源文件同包

## 命名规范
- 测试类：`XxxTest.java`
- 测试方法：`should_期望结果_when_条件`

## 编写要求
- MUST 为所有 Service 层公共方法编写测试
- MUST 为所有 API 端点编写集成测试（MockMvc）
- NEVER 在测试中连接真实数据库（使用 @MockBean 或 H2）

## 示例

```java
// ✅ 正确
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserMapper userMapper;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    void should_returnUser_when_getById() {
        when(userMapper.selectById(1L)).thenReturn(mockUser);
        User result = userService.getById(1L);
        assertThat(result).isNotNull();
    }
}

// ❌ 错误
@Test
void test() { assertTrue(true); }
```
"""

    def _python_testing_rules(self):
        return """# 测试规范

## 测试框架
- 使用 pytest + pytest-mock
- 测试文件位置：`tests/` 目录

## 命名规范
- 测试文件：`test_xxx.py`
- 测试函数：`test_期望结果_条件`

## 编写要求
- MUST 为所有 Service 层公共方法编写测试
- MUST 使用 fixture 管理测试数据
- NEVER 在测试中连接真实数据库（使用 mock）

## 示例

```python
# ✅ 正确
def test_get_user_by_id(user_service, mock_repo):
    mock_repo.get_by_id.return_value = mock_user
    result = user_service.get_by_id(1)
    assert result is not None

# ❌ 错误
def test(): assert True
```
"""

    def _js_testing_rules(self):
        return """# 测试规范

## 测试框架
- 使用 Jest / Vitest
- 测试文件位置：与源文件同目录或 `__tests__/` 目录

## 命名规范
- 测试文件：`[module].test.ts`
- 测试函数：`describe('模块名', () => { it('should xxx', ...) })`

## 编写要求
- MUST 为所有 Service 层公共方法编写测试
- MUST 为所有 API 端点编写集成测试
- NEVER 在测试中连接真实数据库（使用 mock）

## 示例

```typescript
// ✅ 正确
describe('UserService', () => {
  it('should return user by id', async () => {
    const mockRepo = jest.mocked(userRepository);
    mockRepo.findById.mockResolvedValue(mockUser);
    const result = await userService.getById(1);
    expect(result).toEqual(mockUser);
  });
});

// ❌ 错误
it('works', () => { expect(true).toBe(true); });
```
"""

    def _go_testing_rules(self):
        return """# 测试规范

## 测试框架
- 使用 Go 标准 testing 包 + testify
- 测试文件位置：与源文件同目录

## 命名规范
- 测试文件：`xxx_test.go`
- 测试函数：`TestXxx(t *testing.T)`

## 编写要求
- MUST 为所有导出函数编写测试
- MUST 使用 table-driven tests
- NEVER 在测试中连接真实数据库

## 示例

```go
// ✅ 正确
func TestGetUserByID(t *testing.T) {
    tests := []struct {
        name    string
        id      int64
        want    *User
        wantErr bool
    }{
        {"valid id", 1, &User{ID: 1}, false},
        {"invalid id", -1, nil, true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := service.GetByID(tt.id)
            if (err != nil) != tt.wantErr {
                t.Errorf("GetByID() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```
"""

    def _generic_testing_rules(self):
        return """# 测试规范

## 编写要求
- MUST 为核心业务逻辑编写测试
- MUST 覆盖正常、边界、异常场景
- NEVER 在测试中连接真实外部服务
"""

    def _generate_api_design_rules(self, rules_dir):
        lang = self.language.lower()
        if 'java' in lang:
            content = self._java_api_rules()
        elif 'python' in lang:
            content = self._python_api_rules()
        elif 'javascript' in lang or 'typescript' in lang:
            content = self._js_api_rules()
        else:
            content = self._generic_api_rules()

        with open(os.path.join(rules_dir, 'api-design.md'), 'w', encoding='utf-8') as f:
            f.write(content)

    def _java_api_rules(self):
        return """# API 设计规范

## URL 规范
- RESTful 风格：`/api/v1/{resource}`
- 使用名词而非动词：`/users` 而非 `/getUsers`

## Spring Boot 注解
- GET：`@GetMapping`
- POST：`@PostMapping`
- PUT：`@PutMapping`
- DELETE：`@DeleteMapping`

## 响应格式
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## 示例

```java
// ✅ 正确
@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    @GetMapping("/{id}")
    public AjaxResult getById(@PathVariable Long id) {
        return AjaxResult.success(userService.getById(id));
    }
}

// ❌ 错误
@GetMapping("/getUser")
public User getUser(@RequestParam Long id) { ... }
```
"""

    def _python_api_rules(self):
        return """# API 设计规范

## URL 规范
- RESTful 风格：`/api/v1/{resource}`

## 视图函数
- 使用 Django REST Framework 的 `@api_view` 或 FastAPI 的路由装饰器

## 响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

## 示例

```python
# ✅ 正确 (FastAPI)
@router.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_by_id(user_id)
    return {"code": 0, "data": user, "message": "success"}
```
"""

    def _js_api_rules(self):
        return """# API 设计规范

## URL 规范
- RESTful 风格：`/api/v1/{resource}`

## 路由定义
- Express：`router.get('/users/:id', ...)`
- NestJS：`@Get(':id')`

## 响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

## 示例

```typescript
// ✅ 正确
router.get('/api/v1/users/:id', async (req, res) => {
  const user = await userService.getById(req.params.id);
  res.json({ code: 0, data: user, message: 'success' });
});
```
"""

    def _generic_api_rules(self):
        return """# API 设计规范

## URL 规范
- RESTful 风格：`/api/v1/{resource}`
- 使用名词而非动词

## 响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```
"""

    def _generate_architecture_rules(self, rules_dir):
        lang = self.language.lower()
        if 'java' in lang:
            content = self._java_architecture_rules()
        elif 'python' in lang:
            content = self._python_architecture_rules()
        elif 'javascript' in lang or 'typescript' in lang:
            content = self._js_architecture_rules()
        else:
            content = self._generic_architecture_rules()

        with open(os.path.join(rules_dir, 'architecture.md'), 'w', encoding='utf-8') as f:
            f.write(content)

    def _java_architecture_rules(self):
        orm = self.tech_stack.get('orm', 'MyBatis')
        return f"""# 架构规范

## 分层架构

### Controller 层
- 位置：`src/main/java/.../controller/`
- 职责：参数校验、路由转发、返回格式化
- NEVER：禁止在此层编写业务逻辑

### Service 层
- 位置：`src/main/java/.../service/`
- 职责：业务逻辑处理
- NEVER：禁止直接操作数据库

### {orm} 层
- 位置：`src/main/java/.../mapper/` 或 `src/main/java/.../repository/`
- 职责：数据访问逻辑
- NEVER：禁止包含业务判断

## 依赖方向
```
Controller → Service → {orm}/Repository
```

## 新增代码位置
- 新增 API：在 Controller 层添加
- 新增业务逻辑：在 Service 层添加
- 新增数据访问：在 {orm} 层添加
"""

    def _python_architecture_rules(self):
        return """# 架构规范

## 分层架构

### View/API 层
- 职责：参数校验、路由转发、返回格式化
- NEVER：禁止在此层编写业务逻辑

### Service 层
- 职责：业务逻辑处理
- NEVER：禁止直接操作数据库

### Model/DAO 层
- 职责：数据访问逻辑
- NEVER：禁止包含业务判断

## 依赖方向
```
View/API → Service → Model/DAO
```
"""

    def _js_architecture_rules(self):
        return """# 架构规范

## 分层架构

### Route/Controller 层
- 职责：参数校验、路由转发、返回格式化
- NEVER：禁止在此层编写业务逻辑

### Service 层
- 职责：业务逻辑处理
- NEVER：禁止直接操作数据库

### Repository/DAO 层
- 职责：数据访问逻辑
- NEVER：禁止包含业务判断

## 依赖方向
```
Route/Controller → Service → Repository/DAO
```
"""

    def _generic_architecture_rules(self):
        return """# 架构规范

## 分层架构

### Presentation 层
- 职责：参数校验、路由转发、返回格式化
- NEVER：禁止在此层编写业务逻辑

### Business 层
- 职责：业务逻辑处理

### Data 层
- 职责：数据访问逻辑

## 依赖方向
```
Presentation → Business → Data
```
"""

    def _generate_claude_local_md(self, output_dir):
        project_name = self.scan_result.get('project_name', os.path.basename(self.project_path))
        content = f"""# CLAUDE.local.md

> 本文件为个人本地配置，不会提交到 Git

---

## 个人偏好

### 本地路径
- 项目根目录：`~/projects/{project_name}`

### 快捷命令
```bash
"""

        for cmd in self._extract_commands():
            content += f"# {cmd['description']}\nalias {cmd['description'].lower().replace(' ', '_')}=\"{cmd['command']}\"\n"

        content += "```\n"

        filepath = os.path.join(output_dir, 'CLAUDE.local.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info("CLAUDE.local.md 生成完成")

    def _generate_cursorrules(self, output_dir):
        project_name = os.path.basename(self.project_path)
        content = f"""# {project_name} — Cursor Rules

> 自动生成 | 版本：v1.0 | {datetime.now().strftime('%Y-%m-%d')}

## 技术栈

"""
        for key, value in self.tech_stack.items():
            content += f"- {key}: {value}\n"

        content += "\n## 核心规则\n\n### 必须遵循\n"
        for constraint in self._extract_layer_constraints():
            content += f"- {constraint}\n"

        content += "\n### 禁止事项\n"
        for pitfall in self._extract_pitfalls():
            content += f"- NEVER: {pitfall}\n"

        content += "\n## 命名规范\n"
        for rule in self._extract_naming_rules():
            content += f"- {rule}\n"

        filepath = os.path.join(output_dir, '.cursorrules')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(".cursorrules 生成完成")

    def _generate_copilot_instructions(self, output_dir):
        project_name = os.path.basename(self.project_path)
        content = f"""# {project_name} — GitHub Copilot Instructions

> 自动生成 | 版本：v1.0 | {datetime.now().strftime('%Y-%m-%d')}

## 项目概述

本项目使用以下技术栈：

"""
        for key, value in self.tech_stack.items():
            content += f"- **{key}**: {value}\n"

        content += "\n## 编码规则\n\n### 必须遵循\n"
        for constraint in self._extract_layer_constraints():
            content += f"- {constraint}\n"

        content += "\n### 禁止事项\n"
        for pitfall in self._extract_pitfalls():
            content += f"- Do not: {pitfall}\n"

        content += "\n## 快捷命令\n\n"
        for cmd in self._extract_commands():
            content += f"- **{cmd['description']}**: `{cmd['command']}`\n"

        filepath = os.path.join(output_dir, '.copilot-instructions.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(".copilot-instructions.md 生成完成")

    # ========== 辅助方法（全部基于 tech_stack 动态选择）==========

    def _extract_commands(self):
        if 'commands' in self.scan_result and self.scan_result['commands']:
            return self.scan_result['commands']

        lang = self.language.lower()
        if 'java' in lang:
            return [
                {'description': '构建', 'command': 'mvn clean package -DskipTests'},
                {'description': '测试', 'command': 'mvn test'},
                {'description': '运行', 'command': 'mvn spring-boot:run'},
            ]
        elif 'python' in lang:
            return [
                {'description': '安装', 'command': 'pip install -e .'},
                {'description': '测试', 'command': 'pytest'},
                {'description': 'Lint', 'command': 'ruff check .'},
            ]
        elif 'go' in lang:
            return [
                {'description': '构建', 'command': 'go build ./...'},
                {'description': '测试', 'command': 'go test ./...'},
                {'description': '运行', 'command': 'go run .'},
            ]
        elif 'javascript' in lang or 'typescript' in lang:
            return [
                {'description': '开发', 'command': 'npm run dev'},
                {'description': '测试', 'command': 'npm test'},
                {'description': '构建', 'command': 'npm run build'},
                {'description': 'Lint', 'command': 'npm run lint'},
            ]
        return [
            {'description': '构建', 'command': 'make'},
            {'description': '测试', 'command': 'make test'},
        ]

    def _extract_directory_structure(self):
        if 'modules' in self.scan_result:
            modules = self.scan_result['modules']
            structure = f"{os.path.basename(self.project_path)}/\n"
            for module in modules[:10]:
                structure += f"├── {module}/\n"
            if len(modules) > 10:
                structure += f"└── ... ({len(modules) - 10} more)\n"
            return structure
        return f"{os.path.basename(self.project_path)}/\n├── src/\n├── tests/\n└── docs/\n"

    def _extract_layer_constraints(self):
        constraints = self.knowledge.get('coding_standards', [])
        if constraints:
            return constraints

        lang = self.language.lower()
        framework = self.framework.lower()
        orm = self.tech_stack.get('orm', '').lower()
        if 'java' in lang:
            data_layer = 'Mapper' if 'mybatis' in orm else 'Repository'
            return [
                f"Controller 层 ONLY 负责参数校验和路由转发，业务逻辑 MUST 在 Service 层",
                f"Service 层 NEVER 直接操作数据库，MUST 通过 {data_layer} 层",
                f"{data_layer} 层 ONLY 包含数据访问逻辑，NEVER 包含业务判断",
            ]
        elif 'python' in lang:
            return [
                "View/API 层 ONLY 负责参数校验和路由转发，业务逻辑 MUST 在 Service 层",
                "Service 层 NEVER 直接操作数据库，MUST 通过 Model/DAO 层",
                "Model/DAO 层 ONLY 包含数据访问逻辑，NEVER 包含业务判断",
            ]
        elif 'javascript' in lang or 'typescript' in lang:
            return [
                "Route/Controller 层 ONLY 负责参数校验和路由转发，业务逻辑 MUST 在 Service 层",
                "Service 层 NEVER 直接操作数据库，MUST 通过 Repository 层",
                "Repository 层 ONLY 包含数据访问逻辑，NEVER 包含业务判断",
            ]
        return [
            "Presentation 层 ONLY 负责参数校验和路由转发",
            "Business 层 NEVER 直接操作数据库",
            "Data 层 ONLY 包含数据访问逻辑",
        ]

    def _extract_security_rules(self):
        rules = self.knowledge.get('security_constraints', [])
        if rules:
            return rules
        return [
            "所有数据库查询 MUST 按业务规则过滤",
            "NEVER 在日志中输出用户密码、token、手机号等敏感字段",
            "所有外部输入 MUST 经过校验",
        ]

    def _extract_naming_rules(self):
        rules = self.knowledge.get('naming_conventions', [])
        if rules:
            return rules

        lang = self.language.lower()
        if 'java' in lang:
            return [
                "类名：PascalCase（UserService）",
                "方法名：camelCase（getUserById）",
                "常量：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）",
                "包名：全小写（com.example.project）",
            ]
        elif 'python' in lang:
            return [
                "类名：PascalCase（UserService）",
                "函数/变量：snake_case（get_user_by_id）",
                "常量：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）",
            ]
        elif 'javascript' in lang or 'typescript' in lang:
            return [
                "类名：PascalCase（UserService）",
                "函数/变量：camelCase（getUserById）",
                "常量：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）",
                "文件名：kebab-case（user-service.ts）",
            ]
        return [
            "类名：PascalCase",
            "函数/变量：camelCase 或 snake_case",
            "常量：UPPER_SNAKE_CASE",
        ]

    def _extract_pitfalls(self):
        pitfalls = self.knowledge.get('pitfalls', [])
        if pitfalls:
            return pitfalls

        lang = self.language.lower()
        framework = self.framework.lower()
        if 'java' in lang:
            pitfalls = [
                "配置文件 NEVER 硬编码密码，使用环境变量或配置中心",
                "@Transactional 注解在同类方法调用时不生效（self-invocation）",
                "NEVER 在 Controller 层写超过 20 行的业务逻辑",
                "NEVER 在 main 分支直接提交，ALWAYS 走 PR 流程",
            ]
            if 'mybatis' in self.tech_stack.get('orm', '').lower():
                pitfalls.append("MyBatis XML mapper 中 NEVER 使用 ${} 拼接 SQL，ALWAYS 使用 #{}")
            return pitfalls
        elif 'python' in lang:
            return [
                "NEVER 使用 eval() 或 exec() 处理用户输入",
                "NEVER 在 settings.py 中硬编码密钥",
                "ALWAYS 使用参数化查询防止 SQL 注入",
            ]
        elif 'javascript' in lang or 'typescript' in lang:
            return [
                "NEVER 使用 `any` 类型，除非有明确注释",
                "NEVER 在 main 分支直接提交，ALWAYS 走 PR 流程",
                "异步操作 MUST 使用 async/await，禁止回调地狱",
            ]
        return [
            "NEVER 硬编码密钥、密码、敏感配置",
            "NEVER 裸写 SQL、拼接 SQL",
            "NEVER 在 main 分支直接提交",
        ]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        project_path = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = '/tmp/test_rules'

    scan_result_file = os.path.join(project_path, '.repo-to-wiki', 'scan_result.json')
    scan_result = {}
    if os.path.exists(scan_result_file):
        with open(scan_result_file, 'r', encoding='utf-8') as f:
            scan_result = json.load(f)

    knowledge_file = os.path.join(project_path, '.repo-to-wiki', 'knowledge.json')
    knowledge = {}
    if os.path.exists(knowledge_file):
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)

    generator = RuleGenerator(project_path, scan_result, knowledge)
    generator.generate_all(output_dir)
    print(f"规则文件生成完成，输出目录: {output_dir}")