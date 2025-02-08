# cli/src/main.py
import click
import requests
import os
from pathlib import Path
from cli.src.logger import logger


def validate_project_path(ctx, param, value):
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"O caminho '{value}' não existe")
    if not path.is_dir():
        raise click.BadParameter(f"'{value}' não é um diretório")
    if not os.access(str(path), os.R_OK):
        raise click.BadParameter(f"O caminho '{value}' não tem permissões de leitura. Verifique e use 'chmod +r'.")
    return str(path.resolve())


@click.group()
def cli():
    pass


@cli.command()
@click.option('--path', callback=validate_project_path, required=True, help="Caminho do projeto")
@click.option('--output-format', type=click.Choice(['simple', 'detailed'], case_sensitive=False), default='simple', help="Formato de saída")
def analyze(path, output_format):
    logger.info("Análise solicitada", path=path, user=os.getenv('USER'), output_format=output_format)
    api_url = os.getenv("API_URL", "http://localhost:8000")
    response = requests.post(f"{api_url}/analyze", json={"path": path})
    if response.status_code == 200:
        click.echo(response.json())
    elif response.status_code == 403:
        click.echo("Erro 403: Permissões de leitura insuficientes. Verifique o diretório ou use 'chmod +r'.")
    else:
        click.echo(f"Erro: {response.status_code}")


@cli.command()
@click.option('--task-id', required=True, help='ID da tarefa para consulta')
def status(task_id):
    response = requests.get(f"http://api:8000/status/{task_id}")
    click.echo(response.json())


if __name__ == "__main__":
    cli()
