"""
Configurações do analisador.
"""

from typing import Dict

# Configurações gerais
DEFAULT_CONFIG = {
    # Configurações do analisador
    "timeout": 300,  # timeout em segundos
    "temp_dir": "temp",  # diretório temporário
    
    # Configurações do Ollama
    "ollama_model": "llama2:13b",
    "ollama_timeout": 60,
    "ollama_url": "http://localhost:11434/api/generate",
    
    # Configurações do OpenAI
    "openai_model": "gpt-3.5-turbo-instruct",
    "openai_timeout": 30,
    "openai_url": "https://api.openai.com/v1/completions",
    
    # Configurações do DeepSeek
    "deepseek_model": "deepseek-coder-33b-instruct",
    "deepseek_timeout": 30,
    "deepseek_url": "https://api.deepseek.com/v1/completions",
    
    # Configurações de análise
    "max_method_lines": 30,
    "max_complexity": 10,
    "max_class_lines": 300,
    "max_parameters": 5,
    "min_duplicate_lines": 6,
    "min_similarity": 0.8,
    
    # Arquivos importantes para análise
    "important_files": {
        "build": [
            "setup.py", "requirements.txt", "package.json", "Cargo.toml",
            "build.gradle", "pom.xml", "Makefile", "CMakeLists.txt"
        ],
        "config": [
            ".env", "config.yaml", "config.json", ".gitignore", "docker-compose.yml",
            "Dockerfile", "nginx.conf", "webpack.config.js", "tsconfig.json"
        ],
        "docs": [
            "README.md", "CONTRIBUTING.md", "API.md", "CHANGELOG.md",
            "docs/", "wiki/", "specifications/"
        ],
        "tests": [
            "test/", "tests/", "spec/", "__tests__/",
            "pytest.ini", "jest.config.js", "phpunit.xml"
        ],
        "ci": [
            ".github/workflows/", ".gitlab-ci.yml", "Jenkinsfile",
            "azure-pipelines.yml", ".travis.yml", ".circleci/"
        ]
    },
    
    # Extensões de arquivos suportadas
    "language_extensions": {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".r": "R",
        ".m": "Objective-C",
        ".h": "C/C++ Header"
    }
} 