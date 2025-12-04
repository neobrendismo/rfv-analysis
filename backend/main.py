from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import io
import os
import tempfile
from datetime import datetime, timedelta
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = FastAPI(title="RFV Analysis API")

# CORS middleware para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento temporário de arquivos processados
temp_files = {}

# Modelos Pydantic
class ColumnMapping(BaseModel):
    id_cliente: str
    id_transacao: str
    data: str
    valor: str
    file_id: Optional[str] = None

class OutlierTreatment(BaseModel):
    method: str  # "keep", "winsorize", "remove"
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None

class ProcessRequest(BaseModel):
    column_mapping: ColumnMapping
    outlier_treatment: OutlierTreatment

@app.get("/")
async def root():
    return {"message": "RFV Analysis API"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Recebe um arquivo CSV e retorna a lista de colunas"""
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), encoding='utf-8', nrows=1000)  # Lê primeiras 1000 linhas para preview
        
        # Salva o arquivo completo temporariamente
        file_id = f"{datetime.now().timestamp()}_{file.filename}"
        temp_path = os.path.join(tempfile.gettempdir(), file_id)
        
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        temp_files[file_id] = temp_path
        
        return {
            "file_id": file_id,
            "columns": df.columns.tolist(),
            "preview": df.head(10).to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")

@app.post("/analyze-outliers")
async def analyze_outliers(request: ProcessRequest):
    """Analisa outliers na coluna de valor monetário"""
    try:
        # Carrega o arquivo completo
        file_id = request.column_mapping.file_id
        if not file_id or file_id not in temp_files:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        df = pd.read_csv(temp_files[file_id], encoding='utf-8')
        
        # Mapeia colunas
        mapping = request.column_mapping
        df_mapped = df.rename(columns={
            mapping.id_cliente: 'id_cliente',
            mapping.id_transacao: 'id_transacao',
            mapping.data: 'data',
            mapping.valor: 'valor'
        })
        
        # Converte data
        df_mapped['data'] = pd.to_datetime(df_mapped['data'], errors='coerce', infer_datetime_format=True)
        df_mapped['valor'] = pd.to_numeric(df_mapped['valor'], errors='coerce')
        
        # Remove linhas com valores nulos
        df_mapped = df_mapped.dropna(subset=['data', 'valor'])
        
        # Calcula estatísticas para box plot
        valores = df_mapped['valor'].dropna()
        q1 = valores.quantile(0.25)
        q3 = valores.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        median = valores.median()
        mean = valores.mean()
        min_val = valores.min()
        max_val = valores.max()
        
        outliers_count = len(valores[(valores < lower_bound) | (valores > upper_bound)])
        
        return {
            "statistics": {
                "q1": float(q1),
                "median": float(median),
                "q3": float(q3),
                "mean": float(mean),
                "min": float(min_val),
                "max": float(max_val),
                "iqr": float(iqr),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outliers_count": int(outliers_count),
                "total_count": int(len(valores))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao analisar outliers: {str(e)}")

def calculate_rfv_scores(df: pd.DataFrame, outlier_treatment: OutlierTreatment) -> tuple:
    """Calcula os scores RFV para cada cliente e retorna também os quintis calculados"""
    
    # Aplica tratamento de outliers
    if outlier_treatment.method == "winsorize":
        lower = outlier_treatment.lower_limit if outlier_treatment.lower_limit else df['valor'].quantile(0.05)
        upper = outlier_treatment.upper_limit if outlier_treatment.upper_limit else df['valor'].quantile(0.95)
        df['valor'] = df['valor'].clip(lower=lower, upper=upper)
    elif outlier_treatment.method == "remove":
        lower = outlier_treatment.lower_limit if outlier_treatment.lower_limit else df['valor'].quantile(0.05)
        upper = outlier_treatment.upper_limit if outlier_treatment.upper_limit else df['valor'].quantile(0.95)
        df = df[(df['valor'] >= lower) & (df['valor'] <= upper)]
    
    # Define data de referência (última data + 1 dia)
    data_referencia = df['data'].max() + timedelta(days=1)
    
    # Filtra últimos 12 meses
    data_limite = data_referencia - timedelta(days=365)
    df = df[df['data'] >= data_limite]
    
    # Agrega por cliente
    df_agg = df.groupby('id_cliente').agg({
        'data': 'max',  # Última compra
        'id_transacao': 'count',  # Frequência
        'valor': 'sum'  # Valor total
    }).reset_index()
    
    df_agg.columns = ['id_cliente', 'ultima_compra', 'frequencia', 'valor_total']
    
    # Calcula Recência (dias desde última compra)
    df_agg['recencia_dias'] = (data_referencia - df_agg['ultima_compra']).dt.days
    
    # Calcula quintis para Recência (R)
    recencia_quintis = df_agg['recencia_dias'].quantile([0.2, 0.4, 0.6, 0.8]).tolist()
    recencia_quintis = [float(q) for q in recencia_quintis]
    
    # Calcula quintis para Frequência (F)
    frequencia_quintis = df_agg['frequencia'].quantile([0.2, 0.4, 0.6, 0.8]).tolist()
    frequencia_quintis = [float(q) for q in frequencia_quintis]
    
    # Calcula quintis para Valor (V)
    valor_quintis = df_agg['valor_total'].quantile([0.2, 0.4, 0.6, 0.8]).tolist()
    valor_quintis = [float(q) for q in valor_quintis]
    
    # Score de Recência (R) - baseado em quintis (maior recência = menor score)
    def score_recencia(dias):
        if dias >= recencia_quintis[3]:  # >= 80º percentil
            return 1
        elif dias >= recencia_quintis[2]:  # >= 60º percentil
            return 2
        elif dias >= recencia_quintis[1]:  # >= 40º percentil
            return 3
        elif dias >= recencia_quintis[0]:  # >= 20º percentil
            return 4
        else:  # < 20º percentil (mais recente)
            return 5
    
    # Score de Frequência (F) - baseado em quintis (maior frequência = maior score)
    def score_frequencia(freq):
        if freq <= frequencia_quintis[0]:  # <= 20º percentil
            return 1
        elif freq <= frequencia_quintis[1]:  # <= 40º percentil
            return 2
        elif freq <= frequencia_quintis[2]:  # <= 60º percentil
            return 3
        elif freq <= frequencia_quintis[3]:  # <= 80º percentil
            return 4
        else:  # > 80º percentil
            return 5
    
    # Score de Valor (V) - baseado em quintis (maior valor = maior score)
    def score_valor(valor):
        if valor <= valor_quintis[0]:  # <= 20º percentil
            return 1
        elif valor <= valor_quintis[1]:  # <= 40º percentil
            return 2
        elif valor <= valor_quintis[2]:  # <= 60º percentil
            return 3
        elif valor <= valor_quintis[3]:  # <= 80º percentil
            return 4
        else:  # > 80º percentil
            return 5
    
    df_agg['R_score'] = df_agg['recencia_dias'].apply(score_recencia)
    df_agg['F_score'] = df_agg['frequencia'].apply(score_frequencia)
    df_agg['V_score'] = df_agg['valor_total'].apply(score_valor)
    
    # Calcula média de F e V para segmentação
    df_agg['media_fv'] = (df_agg['F_score'] + df_agg['V_score']) / 2
    
    # Segmentação de clientes (ordem de prioridade: código 1 a 9)
    def segmentar_cliente(row):
        r = row['R_score']
        f = row['F_score']
        v = row['V_score']
        media = row['media_fv']
        recencia_dias = row['recencia_dias']
        
        # Código 1: NOVOS - 1ª compra nos últimos 60 dias
        if recencia_dias <= 60 and row['frequencia'] == 1:
            return 'NOVOS'
        
        # Código 2: CAMPEÃO - R=5, F>=3, V=5
        if r == 5 and f >= 3 and v == 5:
            return 'CAMPEÃO'
        
        # Código 3: LEAIS - R=3 ou 4 e média de F+V >= 3
        if r in [3, 4] and media >= 3:
            return 'LEAIS'
        
        # Código 4: POTENCIAIS - (R=5 e média>=3 e V>=3) OU (R=4 e média>=2 e V=3 ou 4)
        if (r == 5 and media >= 3 and v >= 3) or (r == 4 and media >= 2 and v in [3, 4]):
            return 'POTENCIAIS'
        
        # Código 5: PROMISSORES - (R=4 e média<=2) OU (R=3 e média<3) OU (R=5 e média<=3)
        if (r == 4 and media <= 2) or (r == 3 and media < 3) or (r == 5 and media <= 3):
            return 'PROMISSORES'
        
        # Código 6: HIBERNANDO - R=2 e média < 4
        if r == 2 and media < 4:
            return 'HIBERNANDO'
        
        # Código 7: PREOCUPANTES - R=2 e média >= 4
        if r == 2 and media >= 4:
            return 'PREOCUPANTES'
        
        # Código 8: RISCO - R=1 e média < 4
        if r == 1 and media < 4:
            return 'RISCO'
        
        # Código 9: NAO_PODEMOS_PERDER - R=1 e média >= 4
        if r == 1 and media >= 4:
            return 'NAO_PODEMOS_PERDER'
        
        return 'OUTROS'
    
    df_agg['Segmento'] = df_agg.apply(segmentar_cliente, axis=1)
    
    # Retorna o dataframe e os quintis calculados
    quintis_info = {
        'recencia': recencia_quintis,
        'frequencia': frequencia_quintis,
        'valor': valor_quintis
    }
    
    return df_agg[['id_cliente', 'R_score', 'F_score', 'V_score', 'Segmento', 'recencia_dias', 'frequencia', 'valor_total']], quintis_info

@app.post("/process-rfv")
async def process_rfv(request: ProcessRequest):
    """Processa o arquivo e calcula os scores RFV"""
    try:
        # Carrega o arquivo
        file_id = request.column_mapping.file_id
        if not file_id or file_id not in temp_files:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        df = pd.read_csv(temp_files[file_id], encoding='utf-8')
        
        # Mapeia colunas
        mapping = request.column_mapping
        df_mapped = df.rename(columns={
            mapping.id_cliente: 'id_cliente',
            mapping.id_transacao: 'id_transacao',
            mapping.data: 'data',
            mapping.valor: 'valor'
        })
        
        # Converte tipos
        df_mapped['data'] = pd.to_datetime(df_mapped['data'], errors='coerce', infer_datetime_format=True)
        df_mapped['valor'] = pd.to_numeric(df_mapped['valor'], errors='coerce')
        
        # Remove nulos
        df_mapped = df_mapped.dropna(subset=['data', 'valor', 'id_cliente', 'id_transacao'])
        
        # Calcula RFV
        df_rfv, quintis_info = calculate_rfv_scores(df_mapped, request.outlier_treatment)
        
        # Salva resultado processado
        result_file_id = f"result_{datetime.now().timestamp()}"
        result_path = os.path.join(tempfile.gettempdir(), result_file_id)
        df_rfv.to_csv(result_path, index=False, encoding='utf-8')
        temp_files[result_file_id] = result_path
        
        # Salva os quintis em um arquivo JSON separado
        quintis_file_id = f"quintis_{result_file_id}"
        quintis_path = os.path.join(tempfile.gettempdir(), quintis_file_id)
        with open(quintis_path, 'w', encoding='utf-8') as f:
            json.dump(quintis_info, f, indent=2)
        temp_files[quintis_file_id] = quintis_path
        print(f"Quintis salvos em: {quintis_path}")
        print(f"Quintis info: {quintis_info}")
        
        # Estatísticas para dashboard
        total_clientes = len(df_rfv)
        receita_total = df_rfv['valor_total'].sum()
        segmentos = df_rfv['Segmento'].value_counts().to_dict()
        
        return {
            "file_id": result_file_id,
            "statistics": {
                "total_clientes": int(total_clientes),
                "receita_total": float(receita_total),
                "segmentos": {k: int(v) for k, v in segmentos.items()}
            },
            "preview": df_rfv.head(20).to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar RFV: {str(e)}")

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download do arquivo processado"""
    if file_id not in temp_files:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    file_path = temp_files[file_id]
    return FileResponse(
        file_path,
        media_type='text/csv',
        filename=f"rfv_analysis_{file_id}.csv"
    )

def generate_pdf_report(df_rfv: pd.DataFrame, statistics: dict, quintis_info: dict) -> bytes:
    """Gera relatório PDF com análise RFV"""
    try:
        # Valida e converte quintis
        recencia_quintis = [float(q) for q in quintis_info.get('recencia', [])]
        frequencia_quintis = [float(q) for q in quintis_info.get('frequencia', [])]
        valor_quintis = [float(q) for q in quintis_info.get('valor', [])]
        
        if len(recencia_quintis) != 4 or len(frequencia_quintis) != 4 or len(valor_quintis) != 4:
            raise ValueError("Quintis devem ter exatamente 4 valores cada")
        
        # Verifica se há valores NaN
        for q_list, name in [(recencia_quintis, 'recencia'), (frequencia_quintis, 'frequencia'), (valor_quintis, 'valor')]:
            if any(pd.isna(q) or q is None for q in q_list):
                raise ValueError(f"Quintis de {name} contém valores inválidos: {q_list}")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Centralizado
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Título
        story.append(Paragraph("Relatório de Análise RFV", title_style))
        story.append(Paragraph(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Seção 1: Conceitos
        story.append(Paragraph("Conceitos", heading_style))
        
        # Recência - usando quintis dinâmicos
        story.append(Paragraph("<b>Recência (R)</b>", styles['Heading3']))
        
        # Texto descritivo dos conceitos
        story.append(Paragraph(
            f"<b>1</b> - Última compra ocorreu há {recencia_quintis[3]:.0f} dias ou mais;<br/>"
            f"<b>2</b> - Última compra ocorreu entre {recencia_quintis[2]:.0f} e {recencia_quintis[3]:.0f} dias atrás;<br/>"
            f"<b>3</b> - Última compra ocorreu entre {recencia_quintis[1]:.0f} e {recencia_quintis[2]:.0f} dias atrás;<br/>"
            f"<b>4</b> - Última compra ocorreu entre {recencia_quintis[0]:.0f} e {recencia_quintis[1]:.0f} dias atrás;<br/>"
            f"<b>5</b> - Última compra ocorreu nos últimos {recencia_quintis[0]:.0f} dias.",
            styles['Normal']
        ))
        story.append(Spacer(1, 10))
        
        # Tabela
        recencia_data = [
            ['Score', 'Período (dias)'],
            ['1', f'≥ {recencia_quintis[3]:.0f} dias'],
            ['2', f'{recencia_quintis[2]:.0f} a {recencia_quintis[3]:.0f} dias'],
            ['3', f'{recencia_quintis[1]:.0f} a {recencia_quintis[2]:.0f} dias'],
            ['4', f'{recencia_quintis[0]:.0f} a {recencia_quintis[1]:.0f} dias'],
            ['5', f'< {recencia_quintis[0]:.0f} dias'],
        ]
        recencia_table = Table(recencia_data, colWidths=[1*inch, 4.5*inch])
        recencia_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(recencia_table)
        story.append(Spacer(1, 15))
        
        # Frequência - usando quintis dinâmicos
        story.append(Paragraph("<b>Frequência (F)</b>", styles['Heading3']))
        story.append(Paragraph("Os limiares de quantidade de pedidos para a atribuição do score de frequência foram calculados através dos quintis", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Texto descritivo dos conceitos
        story.append(Paragraph(
            f"<b>1</b> - Realizou de 1 a {frequencia_quintis[0]:.0f} compras nos últimos doze meses;<br/>"
            f"<b>2</b> - Realizou de {frequencia_quintis[0]:.0f} a {frequencia_quintis[1]:.0f} compras nos últimos doze meses;<br/>"
            f"<b>3</b> - Realizou de {frequencia_quintis[1]:.0f} a {frequencia_quintis[2]:.0f} compras nos últimos doze meses;<br/>"
            f"<b>4</b> - Realizou de {frequencia_quintis[2]:.0f} a {frequencia_quintis[3]:.0f} compras nos últimos doze meses;<br/>"
            f"<b>5</b> - Realizou {frequencia_quintis[3]:.0f} ou mais compras nos últimos doze meses.",
            styles['Normal']
        ))
        story.append(Spacer(1, 10))
        
        # Tabela
        frequencia_data = [
            ['Score', 'Quantidade de Compras'],
            ['1', f'1 a {frequencia_quintis[0]:.0f} compras'],
            ['2', f'{frequencia_quintis[0]:.0f} a {frequencia_quintis[1]:.0f} compras'],
            ['3', f'{frequencia_quintis[1]:.0f} a {frequencia_quintis[2]:.0f} compras'],
            ['4', f'{frequencia_quintis[2]:.0f} a {frequencia_quintis[3]:.0f} compras'],
            ['5', f'{frequencia_quintis[3]:.0f} ou mais compras'],
        ]
        frequencia_table = Table(frequencia_data, colWidths=[1*inch, 4.5*inch])
        frequencia_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(frequencia_table)
        story.append(Spacer(1, 15))
        
        # Valor Monetário - usando quintis dinâmicos
        story.append(Paragraph("<b>Valor Monetário (V)</b>", styles['Heading3']))
        story.append(Paragraph("Os limiares de valores monetários para a atribuição do score de valor foram calculados através dos quintis", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Texto descritivo dos conceitos
        story.append(Paragraph(
            f"<b>1</b> - Gastou de R$ 0,01 a R$ {valor_quintis[0]:,.2f} nos últimos doze meses;<br/>"
            f"<b>2</b> - Gastou entre R$ {valor_quintis[0]:,.2f} e R$ {valor_quintis[1]:,.2f} nos últimos doze meses;<br/>"
            f"<b>3</b> - Gastou entre R$ {valor_quintis[1]:,.2f} e R$ {valor_quintis[2]:,.2f} nos últimos doze meses;<br/>"
            f"<b>4</b> - Gastou entre R$ {valor_quintis[2]:,.2f} e R$ {valor_quintis[3]:,.2f} nos últimos doze meses;<br/>"
            f"<b>5</b> - Gastou R$ {valor_quintis[3]:,.2f} ou mais nos últimos doze meses.",
            styles['Normal']
        ))
        story.append(Spacer(1, 10))
        
        # Tabela
        valor_data = [
            ['Score', 'Valor Total (R$)'],
            ['1', f'R$ 0,01 a R$ {valor_quintis[0]:,.2f}'],
            ['2', f'R$ {valor_quintis[0]:,.2f} a R$ {valor_quintis[1]:,.2f}'],
            ['3', f'R$ {valor_quintis[1]:,.2f} a R$ {valor_quintis[2]:,.2f}'],
            ['4', f'R$ {valor_quintis[2]:,.2f} a R$ {valor_quintis[3]:,.2f}'],
            ['5', f'R$ {valor_quintis[3]:,.2f} ou mais'],
        ]
        valor_table = Table(valor_data, colWidths=[1*inch, 4.5*inch])
        valor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(valor_table)
        story.append(PageBreak())
        
        # Seção 2: Estatísticas Gerais
        story.append(Paragraph("Estatísticas Gerais", heading_style))
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Clientes', f"{statistics['total_clientes']:,}"],
            ['Receita Total (12 meses)', f"R$ {statistics['receita_total']:,.2f}"],
        ]
        stats_table = Table(stats_data, colWidths=[3*inch, 2.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Seção 3: Distribuição por Segmento
        story.append(Paragraph("Distribuição por Segmento", heading_style))
        segmentos_data = [['Segmento', 'Quantidade', 'Percentual']]
        total = statistics['total_clientes']
        for segmento, quantidade in sorted(statistics['segmentos'].items()):
            percentual = (quantidade / total * 100) if total > 0 else 0
            segmentos_data.append([segmento, f"{quantidade:,}", f"{percentual:.2f}%"])
        
        segmentos_table = Table(segmentos_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        segmentos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(segmentos_table)
        story.append(PageBreak())
        
        # Seção 4: Definições dos Segmentos
        story.append(Paragraph("Definições dos Segmentos", heading_style))
        story.append(Paragraph("<i>Importante: Os segmentos estão na ordem de priorização de classificação. Clientes que se encaixarem em mais de um perfil, terão o perfil de menor código atribuído.</i>", styles['Italic']))
        story.append(Spacer(1, 15))
        
        segmentos_def = [
            ['Código', 'Segmento', 'Definição', 'Perfil'],
            ['1', 'NOVOS', 'Clientes que realizaram sua primeira compra nos últimos 60 dias.', 'Clientes que compraram pela primeira vez na marca. Ainda não é possível determinar seu perfil de compra.'],
            ['2', 'CAMPEÃO', 'R = 5, F ≥ 3, V = 5', 'Compraram recentemente, com frequência e gastam muito.'],
            ['3', 'LEAIS', 'R = 3 ou 4 e média de F+V >= 3', 'Compraram recentemente com valor e/ou frequência alta.'],
            ['4', 'POTENCIAIS', 'R = 5 e média de F+V >= 3 e V >= 3 ou R = 4 e média de F+V >= 2 e V = 3 ou 4', 'Compraram recentemente, com alto valor, independentemente da frequência.'],
            ['5', 'PROMISSORES', 'R = 4 e média de F+V <= 2 ou R = 3 e média de F+V < 3 ou R = 5 e média de F+V <= 3', 'Compraram recentemente, mas não compram muitas vezes e as compras não tem valor alto.'],
            ['6', 'HIBERNANDO', 'R = 2 e média de F+V < 4', 'Clientes Hibernando realizaram sua última compra há muito tempo, mas compravam com frequência e/ou com valor considerável.'],
            ['7', 'PREOCUPANTES', 'R = 2 e média de F+V >= 4', 'Clientes Preocupantes também realizaram sua última compra há muito tempo, mas compravam com muita frequência e também gastavam muito.'],
            ['8', 'RISCO', 'R = 1 e média de F+V < 4', 'São clientes que não compram há mais de 270 dias (Recência = 1), mas compraram poucas vezes e/ou com baixo valor.'],
            ['9', 'NAO_PODEMOS_PERDER', 'R = 1 e média de F+V >= 4', 'São clientes que não compram há mais de 270 dias (Recência = 1), mas quando compravam, gastavam bastante e com frequência.'],
        ]
        
        segmentos_def_table = Table(segmentos_def, colWidths=[0.5*inch, 1.2*inch, 2*inch, 2.3*inch])
        segmentos_def_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ec4899')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(segmentos_def_table)
        
        # Gera o PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        import traceback
        print(f"Erro na geração do PDF: {str(e)}")
        print(traceback.format_exc())
        raise

@app.get("/generate-pdf/{file_id}")
async def generate_pdf(file_id: str):
    """Gera relatório PDF com análise RFV"""
    try:
        if file_id not in temp_files:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Carrega os dados processados
        df_rfv = pd.read_csv(temp_files[file_id], encoding='utf-8')
        
        # Carrega os quintis
        quintis_file_id = f"quintis_{file_id}"
        print(f"Procurando quintis: {quintis_file_id}")
        print(f"Arquivos disponíveis: {list(temp_files.keys())[:5]}...")
        
        if quintis_file_id not in temp_files:
            raise HTTPException(status_code=404, detail=f"Arquivo de quintis não encontrado. Processe o RFV primeiro. Procurando: {quintis_file_id}")
        
        quintis_path = temp_files[quintis_file_id]
        print(f"Carregando quintis de: {quintis_path}")
        
        if not os.path.exists(quintis_path):
            raise HTTPException(status_code=404, detail=f"Arquivo de quintis não existe no disco: {quintis_path}")
        
        with open(quintis_path, 'r', encoding='utf-8') as f:
            quintis_info = json.load(f)
        
        print(f"Quintis carregados: {quintis_info}")
        
        # Valida os quintis
        for key in ['recencia', 'frequencia', 'valor']:
            if key not in quintis_info:
                raise HTTPException(status_code=400, detail=f"Quintis incompletos: falta '{key}'")
            if len(quintis_info[key]) != 4:
                raise HTTPException(status_code=400, detail=f"Quintis inválidos: '{key}' deve ter 4 valores, tem {len(quintis_info[key])}")
        
        # Calcula estatísticas
        total_clientes = len(df_rfv)
        receita_total = df_rfv['valor_total'].sum()
        segmentos = df_rfv['Segmento'].value_counts().to_dict()
        
        statistics = {
            'total_clientes': int(total_clientes),
            'receita_total': float(receita_total),
            'segmentos': {k: int(v) for k, v in segmentos.items()}
        }
        
        # Gera o PDF
        pdf_bytes = generate_pdf_report(df_rfv, statistics, quintis_info)
        
        return Response(
            content=pdf_bytes,
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename=relatorio_rfv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Erro ao gerar PDF: {str(e)}"
        print(f"Erro detalhado: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

