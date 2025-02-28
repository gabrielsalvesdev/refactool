"""Setup do pacote RefacTool."""
import os
from setuptools import setup, find_packages

# Lê a versão do arquivo version.py
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "api", "version.py"), encoding="utf-8") as f:
    exec(f.read(), about)

# Lê o README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Dependências do projeto
install_requires = [
    "celery>=5.3.0",
    "redis>=5.0.0",
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

# Dependências de desenvolvimento
extras_require = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-timeout>=2.1.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "bandit>=1.7.0",
        "safety>=2.3.0",
        "pip-audit>=2.5.0",
    ],
}

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    license=about["__license__"],
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "refactool=api.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Portuguese (Brazilian)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    project_urls={
        "Source": "https://github.com/yourusername/refactool",
        "Bug Reports": "https://github.com/yourusername/refactool/issues",
        "Documentation": "https://refactool.readthedocs.io/",
    },
) 