from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parents[2]


def test_entrypoint_repassa_comando_explicito():
    script = (BASE_DIR / 'scripts' / 'entrypoint.sh').read_text(encoding='utf-8')
    assert 'if [ "$#" -gt 0 ]; then' in script
    assert 'exec "$@"' in script


def test_worker_executa_celery_com_app_correta():
    compose = yaml.safe_load((BASE_DIR / 'docker-compose.yml').read_text(encoding='utf-8'))
    worker_command = compose['services']['worker']['command']

    assert isinstance(worker_command, list)
    assert worker_command[:4] == ['celery', '-A', 'config', 'worker']


def test_web_nao_redefine_command_para_o_proprio_entrypoint():
    compose = yaml.safe_load((BASE_DIR / 'docker-compose.yml').read_text(encoding='utf-8'))
    web_command = compose['services']['web'].get('command')

    assert web_command in (None, '')
