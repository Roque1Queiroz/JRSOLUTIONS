from datetime import date
from django.db.models import Sum
from .models import Transacao, ContaBancaria

class CientistaFinanceiroService:
    @staticmethod
    def gerar_analise_matinal(empresa):
        hoje = date.today()
        
        entradas = Transacao.objects.filter(
            empresa=empresa, tipo='receita', data_vencimento=hoje
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        saidas = Transacao.objects.filter(
            empresa=empresa, tipo='despesa', data_vencimento=hoje
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        contas = ContaBancaria.objects.filter(empresa=empresa, ativa=True)
        saldo_atual = contas.aggregate(total=Sum('saldo'))['total'] or 0
        
        projecao_fim_dia = float(saldo_atual + entradas - saidas)
        
        if projecao_fim_dia < 0:
            status = 'PERIGO'
            mensagem = "Atenção! As despesas vencendo hoje superam o seu saldo disponível."
        elif projecao_fim_dia < float(saldo_atual):
            status = 'ALERTA'
            mensagem = "O saldo deve diminuir hoje. Verifique se todos os recebimentos estão confirmados."
        else:
            status = 'SUCESSO'
            mensagem = "Saúde financeira estável. O caixa deve fechar o dia no azul."

        return {
            'data': hoje.strftime('%d/%m/%Y'),
            'entradas_hoje': float(entradas),
            'saidas_hoje': float(saidas),
            'projecao': projecao_fim_dia,
            'status': status,
            'mensagem': mensagem
        }