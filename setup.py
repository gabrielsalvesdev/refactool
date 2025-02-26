from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="refactool",
    version="0.1.0",
    author="Refactool Team",
    author_email="contato@refactool.com.br",
    description="Analisador de código que utiliza múltiplos provedores de IA para fornecer sugestões de melhoria",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/refactool-beta",
    packages=find_packages(include=["microservices", "microservices.*", "src", "src.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi",
        "uvicorn",
        "celery",
        "redis",
        "requests",
        "click",
        "pytest>=7.0.0",
        "pylint",
        "structlog>=22.1.0",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-exporter-prometheus",
        "opentelemetry-instrumentation-fastapi",
        "bandit",
        "pandas",
        "prophet",
        "xgboost",
        "httpx",
        "redisbloom",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "PyGithub>=2.1.0",
        "gitpython>=3.1.0",
        "python-dotenv>=0.19.0"
    ],
    entry_points={
        "console_scripts": [
            "refactool=refactool:main",
        ],
    },
    py_modules=["refactool"],
) 