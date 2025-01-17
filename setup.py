import os
from setuptools import setup, find_packages

# 使用 UTF-8 编码读取 README.md
def read_readme():
    try:
        if os.path.exists("README.md"):
            with open("README.md", encoding="utf-8") as f:
                return f.read()
        return ""
    except Exception:
        return ""

setup(
    name="douyin-tiktok-scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiofiles>=23.2.1",
        "fastapi>=0.110.2",
        "httpx>=0.27.0",
        "numpy",
        "pydantic>=2.7.0",
        "pywebio>=1.8.3",
        "gmssl>=3.2.2",
        "tenacity>=9.0.0",
        # 其他依赖项会从 requirements.txt 自动安装
    ],
    author="leyuan",
    author_email="415256473@qq.com",
    description="抖音/TikTok 数据采集器",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 