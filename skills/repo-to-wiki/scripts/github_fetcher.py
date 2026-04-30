#!/usr/bin/env python3
"""
GitHub 链接处理模块
支持克隆 GitHub 仓库到本地临时目录
"""

import os
import re
import logging
import tempfile
import shutil
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class GitHubFetcher:
    def __init__(self):
        self.temp_dir = None
        self.clone_dir = None

    def parse_github_url(self, url):
        """
        解析 GitHub URL，支持多种格式：
        - https://github.com/username/repo
        - https://github.com/username/repo/tree/branch/path
        - https://github.com/username/repo/pull/123
        - git@github.com:username/repo.git
        """
        parsed = urlparse(url)

        # SSH 格式
        if url.startswith('git@'):
            match = re.match(r'git@github\.com:([^/]+)/(.+?)(?:\.git)?$', url)
            if match:
                return {
                    'owner': match.group(1),
                    'repo': match.group(2).replace('.git', ''),
                    'branch': 'main',
                    'subpath': ''
                }

        # HTTPS/HTTP 格式
        if 'github.com' in parsed.netloc:
            parts = parsed.path.strip('/').split('/')

            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace('.git', '')

                # 检查是否有 tree/branch/path
                branch = 'main'
                subpath = ''

                if len(parts) > 2:
                    if parts[2] == 'tree':
                        branch = parts[3] if len(parts) > 3 else 'main'
                        subpath = '/'.join(parts[4:]) if len(parts) > 4 else ''
                    elif parts[2] == 'pull':
                        # PR 链接，克隆整个仓库
                        branch = 'main'
                        subpath = ''
                    elif len(parts) > 2:
                        subpath = '/'.join(parts[2:])

                return {
                    'owner': owner,
                    'repo': repo,
                    'branch': branch,
                    'subpath': subpath
                }

        return None

    def clone_repo(self, url, branch=None, depth=1):
        """
        克隆 GitHub 仓库到临时目录

        Args:
            url: GitHub 仓库 URL
            branch: 指定分支，默认为 main
            depth: 克隆深度，1 表示浅克隆

        Returns:
            克隆后的本地目录路径
        """
        import subprocess

        parsed = self.parse_github_url(url)
        if not parsed:
            logging.error(f"无法解析 GitHub URL: {url}")
            return None

        owner = parsed['owner']
        repo = parsed['repo']
        target_branch = branch or parsed['branch']
        subpath = parsed['subpath']

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix='repo-to-wiki-')
        self.clone_dir = os.path.join(self.temp_dir, repo)

        logging.info(f"正在克隆仓库: {owner}/{repo} (分支: {target_branch})")
        logging.info(f"临时目录: {self.clone_dir}")

        try:
            # 构建 git clone 命令
            clone_url = f"https://github.com/{owner}/{repo}.git"
            cmd = ['git', 'clone', '--depth', str(depth)]

            if target_branch:
                cmd.extend(['--branch', target_branch])

            cmd.extend([clone_url, self.clone_dir])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logging.error(f"克隆失败: {result.stderr}")

                # 如果浅克隆失败，尝试完整克隆
                if depth > 1:
                    return None

                logging.info("尝试完整克隆...")
                cmd = ['git', 'clone', clone_url, self.clone_dir]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    logging.error(f"完整克隆也失败: {result.stderr}")
                    return None

            # 如果指定了子目录，返回子目录路径
            if subpath:
                target_dir = os.path.join(self.clone_dir, subpath)
                if os.path.exists(target_dir):
                    logging.info(f"目标子目录: {target_dir}")
                    return target_dir
                else:
                    logging.warning(f"子目录不存在: {subpath}，使用根目录")
                    return self.clone_dir

            logging.info("克隆成功!")
            return self.clone_dir

        except Exception as e:
            logging.error(f"克隆过程中出错: {str(e)}")
            return None

    def cleanup(self):
        """清理临时目录"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logging.info(f"已清理临时目录: {self.temp_dir}")
            except Exception as e:
                logging.warning(f"清理临时目录失败: {str(e)}")

    def fetch_file_content(self, url):
        """
        获取单个文件的内容（通过 GitHub API）

        Args:
            url: 指向具体文件的 GitHub URL

        Returns:
            文件内容字符串
        """
        import subprocess

        parsed = self.parse_github_url(url)
        if not parsed:
            return None

        owner = parsed['owner']
        repo = parsed['repo']
        branch = parsed['branch']
        filepath = parsed['subpath']

        if not filepath:
            return None

        # 使用 git sparse-checkout 获取单个文件
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix='github-file-')

            # 克隆仓库
            clone_url = f"https://github.com/{owner}/{repo}.git"
            subprocess.run(
                ['git', 'clone', '--depth', '1', '--filter=blob:none',
                 '--sparse', clone_url, temp_dir],
                capture_output=True
            )

            # 使用 sparse-checkout 获取文件
            subprocess.run(
                ['git', 'sparse-checkout', 'set', filepath],
                cwd=temp_dir,
                capture_output=True
            )

            # 读取文件
            file_path = os.path.join(temp_dir, filepath)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 清理
                shutil.rmtree(temp_dir)
                return content

            shutil.rmtree(temp_dir)
            return None

        except Exception as e:
            logging.error(f"获取文件内容失败: {str(e)}")
            return None


def is_github_url(input_str):
    """判断输入是否为 GitHub URL"""
    if not input_str:
        return False

    # 检查是否包含 github.com
    if 'github.com' in input_str:
        return True

    # 检查是否是 git@ 格式
    if input_str.startswith('git@github.com:'):
        return True

    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        fetcher = GitHubFetcher()

        if is_github_url(url):
            print(f"检测到 GitHub URL: {url}")

            parsed = fetcher.parse_github_url(url)
            if parsed:
                print(f"Owner: {parsed['owner']}")
                print(f"Repo: {parsed['repo']}")
                print(f"Branch: {parsed['branch']}")
                print(f"Subpath: {parsed['subpath']}")

            # 克隆仓库
            local_path = fetcher.clone_repo(url)
            if local_path:
                print(f"\n克隆成功! 本地路径: {local_path}")

                # 列出目录内容
                print("\n目录内容:")
                for item in os.listdir(local_path)[:10]:
                    print(f"  {item}")

                # 清理
                fetcher.cleanup()
        else:
            print(f"不是 GitHub URL: {url}")
    else:
        print("用法: python github_fetcher.py <github-url>")