#!/usr/bin/env python
"""
Script wrapper para o analisador de código Refactool.
"""

import sys
import os
import importlib.util
import subprocess

def find_module_path(module_name):
    """Encontra o caminho do módulo."""
    parts = module_name.split('.')
    for i in range(len(parts), 0, -1):
        path = os.path.join(*parts[:i])
        if os.path.exists(path):
            return path
    return None

def main():
    """Função principal."""
    # Tenta importar o módulo
    try:
        # Primeiro, tenta importar como um módulo instalado
        from microservices.source_provider.src import analyze_repo
        analyze_repo.main()
    except ImportError:
        # Se falhar, tenta encontrar o módulo no sistema de arquivos
        module_path = find_module_path("microservices/source_provider/src")
        
        if module_path and os.path.exists(os.path.join(module_path, "analyze_repo.py")):
            # Executa o script diretamente
            script_path = os.path.join(module_path, "analyze_repo.py")
            subprocess.run([sys.executable, script_path] + sys.argv[1:])
        else:
            # Tenta encontrar o script na pasta source-provider
            alt_path = find_module_path("microservices/source-provider/src")
            
            if alt_path and os.path.exists(os.path.join(alt_path, "analyze_repo.py")):
                script_path = os.path.join(alt_path, "analyze_repo.py")
                subprocess.run([sys.executable, script_path] + sys.argv[1:])
            else:
                print("Erro: Não foi possível encontrar o módulo analyze_repo.")
                print("Verifique se o pacote está instalado corretamente.")
                sys.exit(1)

if __name__ == "__main__":
    main() 