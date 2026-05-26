"""GitHub API 工具模块：获取指定仓库的基本信息。"""

import logging
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json
from typing import Optional

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


@dataclass
class RepoInfo:
    """仓库基本信息。

    Args:
        full_name: 仓库全名（owner/repo）。
        stars: Star 数。
        forks: Fork 数。
        description: 仓库描述。
        language: 主要编程语言。
        url: 仓库 HTML 链接。
    """

    full_name: str
    stars: int
    forks: int
    description: Optional[str]
    language: Optional[str]
    url: str

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "stars": self.stars,
            "forks": self.forks,
            "description": self.description,
            "language": self.language,
            "url": self.url,
        }


def fetch_repo_info(owner: str, repo: str, token: Optional[str] = None) -> RepoInfo:
    """从 GitHub API 获取指定仓库的基本信息。

    Args:
        owner: 仓库所有者。
        repo: 仓库名称。
        token: GitHub Personal Access Token，未提供时从环境变量 GITHUB_TOKEN 读取。

    Returns:
        RepoInfo 实例，包含 Star 数、Fork 数、描述等。

    Raises:
        ValueError: owner 或 repo 为空。
        HTTPError: GitHub API 返回非 2xx 状态码。
        URLError: 网络连接失败。
        KeyError: 响应 JSON 缺少必要字段。
    """
    if not owner or not repo:
        raise ValueError("owner 和 repo 不能为空")

    github_token = token or os.environ.get("GITHUB_TOKEN")
    api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jk-notes-bot",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    request = Request(api_url, headers=headers)

    try:
        logger.info("正在请求 GitHub API: %s", api_url)
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        logger.error("GitHub API 请求失败: %s %s", exc.code, exc.reason)
        raise
    except URLError as exc:
        logger.error("网络连接失败: %s", exc.reason)
        raise

    try:
        return RepoInfo(
            full_name=data["full_name"],
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            description=data.get("description"),
            language=data.get("language"),
            url=data["html_url"],
        )
    except KeyError as exc:
        logger.error("响应 JSON 缺少必要字段: %s", exc)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    info = fetch_repo_info("langchain-ai", "langgraph")
    print(json.dumps(info.to_dict(), ensure_ascii=False, indent=2))
