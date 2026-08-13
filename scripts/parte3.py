f = open('relatorios/views.py', 'a', encoding='utf-8')
f.write("""

class RelatorioEstoqueView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/estoque.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from estoque.models import Categoria
        categoria = self.request.GET.get('categoria', '')
        criticos  = self.request.GET.get('criticos', '')
        produtos  = Produto.objects.select_related('categoria').order_by('nome')
        if categoria:
            produtos = produtos.filter(categoria__id=categoria)
        if criticos == '1':
            produtos = produtos.filter(quantidade__lte=F('estoque_minimo'))
        produtos_list = list(produtos)
        context['produtos']            = produtos_list
        context['categorias']          = Categoria.objects.all()
        context['categoria_sel']       = categoria
        context['criticos_sel']        = criticos
        context['total_produtos']      = len(produtos_list)
        context['produtos_criticos']   = sum(1 for p in produtos_list if p.quantidade<= p.estoque_minimo)
        context['valor_total_estoque'] = sum(p.valor_total_estoque for p in produtos_list)
        return context


class RelatorioEstoqueExcelView(LoginRequiredMixin, View):
    def get(self, request):
        categoria = request.GET.get('categoria', '')
        produtos  = Produto.objects.select_related('categoria').order_by('nome')
        if categoria:
            produtos = produtos.filter(categoria__id=categoria)
        produtos_list = list(produtos)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Estoque'
        hf = PatternFill('solid', fgColor='198754')
        hn = Font(color='FFFFFF', bold=True, size=11)
        bd = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        ws.merge_cells('A1:G1')
        ws['A1'] = 'Relatorio de Estoque'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')
        for col, h in enumerate(['#', 'Produto', 'Categoria', 'Qtd.', 'Minimo', 'Preco (R$)', 'Valor Total (R$)'], 1):
            cell = ws.cell(row=3, column=col, value=h)
            cell.fill = hf
            cell.font = hn
            cell.alignment = Alignment(horizontal='center')
            cell.border = bd
        for ri, p in enumerate(produtos_list, 4):
            ws.cell(row=ri, column=1, value=p.pk).border = bd
            ws.cell(row=ri, column=2, value=p.nome).border = bd
            ws.cell(row=ri, column=3, value=str(p.categoria) if p.categoria else '-').border = bd
            ws.cell(row=ri, column=4, value=p.quantidade).border = bd
            ws.cell(row=ri, column=5, value=p.estoque_minimo).border = bd
            c = ws.cell(row=ri, column=6, value=float(p.preco))
            c.border = bd
            c.number_format = '#,##0.00'
            vt = ws.cell(row=ri, column=7, value=float(p.valor_total_estoque))
            vt.border = bd
            vt.number_format = '#,##0.00'
            if p.quantidade<= p.estoque_minimo:
                for col in range(1, 8):
                    ws.cell(row=ri, column=col).fill = PatternFill('solid', fgColor='FFDEDE')
        for col, w in zip('ABCDEFG', [6, 30, 20, 8, 8, 15, 18]):
            ws.column_dimensions[col].width = w
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        resp = HttpResponse(buf, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename=relatorio_estoque.xlsx'
        return resp
""")
f.close()
print('Parte 3 OK')
