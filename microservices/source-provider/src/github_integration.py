"""
Módulo de integração com GitHub para o Refactool.
"""

import os
import aiohttp
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
import structlog

logger = structlog.get_logger()

class GitHubError(Exception):
    """Exceção base para erros relacionados ao GitHub."""
    pass

class GitHubManager:
    """Gerenciador de integração com GitHub."""
    
    def __init__(self, token: str, api_url: Optional[str] = None):
        """
        Inicializa o gerenciador do GitHub.
        
        Args:
            token: Token de acesso do GitHub
            api_url: URL base da API do GitHub (opcional)
        """
        self.token = token
        self.api_url = api_url or "https://api.github.com"
        self.session = None
        self._headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def start(self):
        """Inicializa a sessão HTTP."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self._headers)
    
    async def stop(self):
        """Finaliza a sessão HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        """Suporte para context manager."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager."""
        await self.stop()
    
    async def get_repository(self, repo: str) -> Dict:
        """
        Obtém informações sobre um repositório.
        
        Args:
            repo: Nome do repositório (formato: "usuario/repo")
            
        Returns:
            Dict com informações do repositório
        """
        url = f"{self.api_url}/repos/{repo}"
        async with self.session.get(url) as response:
            if response.status == 404:
                raise GitHubError(f"Repositório {repo} não encontrado")
            response.raise_for_status()
            return await response.json()
    
    async def clone_repository(self, repo: str, branch: str = "main") -> str:
        """
        Clona um repositório do GitHub.
        
        Args:
            repo: Nome do repositório (formato: "usuario/repo")
            branch: Branch a ser clonada
            
        Returns:
            Caminho do diretório temporário com o repositório
        """
        repo_info = await self.get_repository(repo)
        clone_url = repo_info["clone_url"]
        
        # Cria diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clona o repositório
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "-b", branch, clone_url, temp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise GitHubError(f"Erro ao clonar repositório: {stderr.decode()}")
            
            return temp_dir
            
        except Exception as e:
            shutil.rmtree(temp_dir)
            raise GitHubError(f"Erro ao clonar repositório: {str(e)}")
    
    async def create_branch(self, repo: str, branch: str, base: str = "main") -> None:
        """
        Cria uma nova branch no repositório.
        
        Args:
            repo: Nome do repositório
            branch: Nome da nova branch
            base: Branch base
        """
        # Obtém o SHA da branch base
        url = f"{self.api_url}/repos/{repo}/git/refs/heads/{base}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            base_ref = await response.json()
            base_sha = base_ref["object"]["sha"]
        
        # Cria nova branch
        url = f"{self.api_url}/repos/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch}",
            "sha": base_sha
        }
        
        async with self.session.post(url, json=data) as response:
            if response.status == 422:  # Branch já existe
                return
            response.raise_for_status()
    
    async def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict:
        """
        Cria um Pull Request.
        
        Args:
            repo: Nome do repositório
            title: Título do PR
            body: Descrição do PR
            head: Branch com as alterações
            base: Branch de destino
            
        Returns:
            Dict com informações do PR criado
        """
        url = f"{self.api_url}/repos/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        async with self.session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_commit(
        self,
        repo: str,
        branch: str,
        message: str,
        changes: List[Dict[str, str]]
    ) -> str:
        """
        Cria um commit no repositório.
        
        Args:
            repo: Nome do repositório
            branch: Branch para o commit
            message: Mensagem do commit
            changes: Lista de alterações (dicts com 'path' e 'content')
            
        Returns:
            SHA do commit criado
        """
        # Obtém o último commit da branch
        url = f"{self.api_url}/repos/{repo}/git/refs/heads/{branch}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            ref = await response.json()
            base_tree = ref["object"]["sha"]
        
        # Cria blobs para os arquivos
        tree_items = []
        for change in changes:
            # Cria blob
            url = f"{self.api_url}/repos/{repo}/git/blobs"
            blob_data = {
                "content": change["content"],
                "encoding": "utf-8"
            }
            async with self.session.post(url, json=blob_data) as response:
                response.raise_for_status()
                blob = await response.json()
            
            # Adiciona à árvore
            tree_items.append({
                "path": change["path"],
                "mode": "100644",
                "type": "blob",
                "sha": blob["sha"]
            })
        
        # Cria nova árvore
        url = f"{self.api_url}/repos/{repo}/git/trees"
        tree_data = {
            "base_tree": base_tree,
            "tree": tree_items
        }
        async with self.session.post(url, json=tree_data) as response:
            response.raise_for_status()
            tree = await response.json()
        
        # Cria commit
        url = f"{self.api_url}/repos/{repo}/git/commits"
        commit_data = {
            "message": message,
            "tree": tree["sha"],
            "parents": [base_tree]
        }
        async with self.session.post(url, json=commit_data) as response:
            response.raise_for_status()
            commit = await response.json()
        
        # Atualiza referência
        url = f"{self.api_url}/repos/{repo}/git/refs/heads/{branch}"
        ref_data = {"sha": commit["sha"]}
        async with self.session.patch(url, json=ref_data) as response:
            response.raise_for_status()
        
        return commit["sha"]
    
    async def get_pull_request(self, repo: str, number: int) -> Dict:
        """
        Obtém informações sobre um Pull Request.
        
        Args:
            repo: Nome do repositório
            number: Número do PR
            
        Returns:
            Dict com informações do PR
        """
        url = f"{self.api_url}/repos/{repo}/pulls/{number}"
        async with self.session.get(url) as response:
            if response.status == 404:
                raise GitHubError(f"PR #{number} não encontrado")
            response.raise_for_status()
            return await response.json()
    
    async def get_pull_request_files(self, repo: str, number: int) -> List[Dict]:
        """
        Obtém a lista de arquivos modificados em um PR.
        
        Args:
            repo: Nome do repositório
            number: Número do PR
            
        Returns:
            Lista de arquivos modificados
        """
        url = f"{self.api_url}/repos/{repo}/pulls/{number}/files"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_review_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int
    ) -> Dict:
        """
        Cria um comentário em uma linha específica de um PR.
        
        Args:
            repo: Nome do repositório
            pr_number: Número do PR
            body: Conteúdo do comentário
            commit_id: SHA do commit
            path: Caminho do arquivo
            line: Número da linha
            
        Returns:
            Dict com informações do comentário criado
        """
        url = f"{self.api_url}/repos/{repo}/pulls/{pr_number}/comments"
        data = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line,
            "side": "RIGHT"
        }
        
        async with self.session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_review(
        self,
        repo: str,
        pr_number: int,
        comments: List[Dict],
        event: str = "COMMENT"
    ) -> Dict:
        """
        Cria uma review em um PR.
        
        Args:
            repo: Nome do repositório
            pr_number: Número do PR
            comments: Lista de comentários
            event: Tipo de review (COMMENT, APPROVE, REQUEST_CHANGES)
            
        Returns:
            Dict com informações da review criada
        """
        url = f"{self.api_url}/repos/{repo}/pulls/{pr_number}/reviews"
        data = {
            "commit_id": comments[0]["commit_id"],
            "body": "Análise automática da Refactool",
            "event": event,
            "comments": comments
        }
        
        async with self.session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json() 