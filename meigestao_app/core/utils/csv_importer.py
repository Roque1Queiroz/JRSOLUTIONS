import csv
import io
import logging
from typing import List, Dict, Any, Callable, Tuple

logger = logging.getLogger(__name__)

class CSVImportService:
    """
    Serviço genérico para processamento de arquivos CSV e importação de dados.
    """

    def __init__(self, file_content: bytes, required_fields: List[str]):
        self.file_content = file_content
        self.required_fields = required_fields
        self.success_count = 0
        self.errors = []  # Lista de dicionários {'line': int, 'error': str}

    def process(self, save_callable: Callable[[Dict[str, Any]], Tuple[bool, str]]):
        """
        Processa o arquivo CSV linha por linha e executa a função de salvamento fornecida.
        """
        try:
            # Decodifica o conteúdo e prepara o leitor CSV
            decoded_file = self.file_content.decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file, delimiter=';') # Padronizado para ponto e vírgula, comum em Excel BR

            # Se não funcionar com ponto e vírgula, tenta vírgula
            if not all(field in reader.fieldnames for field in self.required_fields if reader.fieldnames):
                reader = csv.DictReader(decoded_file, delimiter=',')

            # Valida os campos obrigatórios no cabeçalho
            if not reader.fieldnames or not all(field in reader.fieldnames for field in self.required_fields):
                missing = [f for f in self.required_fields if f not in (reader.fieldnames or [])]
                self.errors.append({
                    'line': 0, 
                    'error': f"Arquivo inválido. Campos obrigatórios ausentes: {', '.join(missing)}"
                })
                return

            # Processa cada linha
            for i, row in enumerate(reader, start=1):
                try:
                    # Limpa espaços e valores vazios
                    cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                    
                    success, message = save_callable(cleaned_row)
                    
                    if success:
                        self.success_count += 1
                    else:
                        self.errors.append({'line': i, 'error': message})
                
                except Exception as e:
                    logger.error(f"Erro ao processar linha {i}: {str(e)}")
                    self.errors.append({'line': i, 'error': f"Erro inesperado: {str(e)}"})

        except Exception as e:
            logger.error(f"Falha ao ler arquivo CSV: {str(e)}")
            self.errors.append({'line': 0, 'error': f"Erro ao ler o arquivo: Certifique-se de que é um CSV válido (UTF-8)."})

    def get_summary(self) -> Dict[str, Any]:
        return {
            'success': self.success_count,
            'total_errors': len(self.errors),
            'errors': self.errors[:10], # Mostra apenas os primeiros 10 erros para não sobrecarregar
            'has_errors': len(self.errors) > 0
        }
