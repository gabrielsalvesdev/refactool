#!/usr/bin/env python
"""Script para automatizar o processo de release."""
import os
import re
import sys
import platform
import subprocess
from pathlib import Path

def get_git_executable():
    """Retorna o caminho do executável git."""
    if platform.system() == "Windows":
        git_path = r"C:\Program Files\Git\bin\git.exe"
        if os.path.exists(git_path):
            return git_path
    return "git"

def get_current_version():
    """Obtém a versão atual do arquivo version.py."""
    version_file = Path("api/version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else None

def update_version(new_version):
    """Atualiza a versão no arquivo version.py."""
    version_file = Path("api/version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(new_content)

def run_git_command(args):
    """Executa um comando git."""
    git_exe = get_git_executable()
    git_cmd = [git_exe] + args
    print(f"Executando: {' '.join(git_cmd)}")
    try:
        result = subprocess.run(
            git_cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar git {args[0]}: {e}")
        print(f"Output: {e.output}")
        sys.exit(1)

def main():
    """Função principal do script de release."""
    current_version = get_current_version()
    print(f"Versão atual: {current_version}")
    
    # Verifica se há mudanças não commitadas
    result = run_git_command(["status", "--porcelain"])
    if result.stdout.strip():
        print("ERRO: Existem mudanças não commitadas. Faça commit ou stash antes de continuar.")
        return
    
    # Determina o tipo de release
    while True:
        release_type = input("Tipo de release (major/minor/patch): ").lower()
        if release_type in ["major", "minor", "patch"]:
            break
        print("Tipo inválido. Use major, minor ou patch.")
    
    # Calcula nova versão
    major, minor, patch = map(int, current_version.split("."))
    if release_type == "major":
        new_version = f"{major + 1}.0.0"
    elif release_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    else:  # patch
        new_version = f"{major}.{minor}.{patch + 1}"
    
    print(f"Nova versão será: {new_version}")
    if input("Continuar? (s/N) ").lower() != "s":
        return
    
    try:
        # Atualiza versão
        update_version(new_version)
        
        # Commit das mudanças
        run_git_command(["add", "api/version.py"])
        run_git_command(["commit", "-m", f"build: bump version to {new_version}"])
        
        # Cria e pusha a tag
        run_git_command(["tag", "-a", f"v{new_version}", "-m", f"Release version {new_version}"])
        run_git_command(["push", "origin", "main"])
        run_git_command(["push", "origin", f"v{new_version}"])
        
        print(f"\nRelease v{new_version} criada com sucesso!")
        print("\nPróximos passos:")
        print("1. O CI/CD irá construir e publicar o pacote automaticamente")
        print("2. Monitore o progresso em: https://github.com/yourusername/refactool/actions")
        print("3. Verifique a publicação em: https://pypi.org/project/refactool")
        
    except Exception as e:
        print(f"ERRO durante o processo de release: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 