"""Controle de versão do projeto."""

__version__ = "2.0.0"
__version_info__ = tuple(map(int, __version__.split(".")))

# Informações adicionais
__title__ = "refactool"
__description__ = "Analisador de código com cache distribuído e alta performance"
__author__ = "RefacTool Team"
__license__ = "MIT"
__copyright__ = "Copyright 2024 RefacTool Team"

# Metadados da versão
VERSION_MAJOR = __version_info__[0]  # Mudanças incompatíveis
VERSION_MINOR = __version_info__[1]  # Novas funcionalidades
VERSION_PATCH = __version_info__[2]  # Correções de bugs 