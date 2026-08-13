f = open('relatorios/views.py', 'a', encoding='utf-8')
f.write("""

class RelatorioVendasPDFView(LoginRequiredMixin, View):
    def get(self, request):
        vendas, data_inicio, data_fim, status = _get_vendas_filtradas(request)
        vendas_list = list(vendas)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []
        ts = ParagraphStyle('titulo', parent=styles['Title'], fontSize=18, spaceAfter=6)
        elements.append(Paragraph('Relatorio de Vendas', ts))
        periodo = 'Periodo: {} ate {} | Status: {}'.format(data_inicio or 'Inicio', data_fim or 'Hoje', status or 'Todos')
        elements.append(Paragraph(periodo, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        dados = [['#', 'Cliente', 'Data', 'Status', 'Total (R$)']]
        for v in vendas_list:
            t = '{:,.2f}'.format(v.total).replace(',','X').replace('.',',').replace('X','.')
            dados.append([str(v.pk), str(v.cliente), v.data_venda.strftime('%d/%m/%Y'), v.get_status_display(), t])
        tg = sum(v.total for v in vendas_list)
        tgf = '{:,.2f}'.format(tg).replace(',','X').replace('.',',').replace('X','.')
        dados.append(['', '', '', 'TOTAL', tgf])
        tabela = Table(dados, colWidths=[1.5*cm, 7*cm, 3*cm, 3.5*cm, 3*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e9ecef')),
            ('FONTNAME',   (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
            ('PADDING',    (0,0), (-1,-1), 6),
        ]))
        elements.append(tabela)
        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=relatorio_vendas.pdf'
        return response


class RelatorioVendasExcelView(LoginRequiredMixin, View):
    def get(self, request):
        vendas, data_inicio, data_fim, status = _get_vendas_filtradas(request)
        vendas_list = list(vendas)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Relatorio de Vendas'
        hf = PatternFill('solid', fgColor='0D6EFD')
        hn = Font(color='FFFFFF', bold=True, size=11)
        tf = PatternFill('solid', fgColor='E9ECEF')
        tn = Font(bold=True)
        bd = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        ws.merge_cells('A1:E1')
        ws['A1'] = 'Relatorio de Vendas'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')
        ws.merge_cells('A2:E2')
        ws['A2'] = 'Periodo: {} ate {} | Status: {}'.format(data_inicio or 'Inicio', data_fim or 'Hoje', status or 'Todos')
        ws['A2'].alignment = Alignment(horizontal='center')
        for col, h in enumerate(['#', 'Cliente', 'Data', 'Status', 'Total (R$)'], 1):
            cell = ws.cell(row=4, column=col, value=h)
            cell.fill = hf
            cell.font = hn
            cell.alignment = Alignment(horizontal='center')
            cell.border = bd
        for ri, v in enumerate(vendas_list, 5):
            ws.cell(row=ri, column=1, value=v.pk).border = bd
            ws.cell(row=ri, column=2, value=str(v.cliente)).border = bd
            ws.cell(row=ri, column=3, value=v.data_venda.strftime('%d/%m/%Y')).border = bd
            ws.cell(row=ri, column=4, value=v.get_status_display()).border = bd
            c = ws.cell(row=ri, column=5, value=float(v.total))
            c.border = bd
            c.number_format = '#,##0.00'
            if ri % 2 == 0:
                for col in range(1, 6):
                    ws.cell(row=ri, column=col).fill = PatternFill('solid', fgColor='F8F9FA')
        tr = len(vendas_list) + 5
        for col in range(1, 6):
            ws.cell(row=tr, column=col).border = bd
            ws.cell(row=tr, column=col).fill = tf
        ws.cell(row=tr, column=4, value='TOTAL').font = tn
        c = ws.cell(row=tr, column=5, value=float(sum(v.total for v in vendas_list)))
        c.font = tn
        c.number_format = '#,##0.00'
        for col, w in zip('ABCDE', [6, 35, 15, 15, 18]):
            ws.column_dimensions[col].width = w
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        resp = HttpResponse(buf, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename=relatorio_vendas.xlsx'
        return resp
""")
f.close()
print('Parte 2 OK')