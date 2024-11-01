import re
import fitz  # PyMuPDF
import pdfplumber
from io import BytesIO

# Função para validar um CPF
def validar_cpf(cpf):
    # Remove caracteres não numéricos (pontuações, espaços, etc.)
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se o CPF tem exatamente 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Elimina CPFs com todos os dígitos iguais (ex: 11111111111)
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0
    
    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0
    
    # Verifica se os dígitos verificadores calculados são iguais aos do CPF
    return cpf[-2:] == f"{digito1}{digito2}"

# Função para identificar e ocultar CPFs e placas no PDF
def ocultar_cpf_e_placa_em_pdf(pdf_bytes, progresso_interno):
    # Padrões para CPF (formatado e não formatado), placa antiga e placa Mercosul
    padrao_cpf = r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b'
    padrao_placa_antiga = r'\b[A-Z]{3}-\d{4}\b'
    padrao_placa_mercosul = r'\b[A-Z]{3}\d[A-Z]\d{2}\b'
    
    # Abre o PDF a partir dos bytes
    pdf_reader = pdfplumber.open(BytesIO(pdf_bytes))
    pdf_writer = fitz.open("pdf", pdf_bytes)

    # Número total de páginas no PDF para atualizar o progresso
    total_pages = len(pdf_reader.pages)
    
    for i, page in enumerate(pdf_reader.pages):
        # Atualiza a barra de progresso conforme cada página é processada
        progresso_interno.progress((i + 1) / total_pages)
        
        text = page.extract_text()
        if text:
            # Procura CPFs (formatados e não formatados) e placas
            possiveis_cpfs = re.findall(padrao_cpf, text)
            placas_antigas = re.findall(padrao_placa_antiga, text)
            placas_mercosul = re.findall(padrao_placa_mercosul, text)
            
            # Filtra e valida os CPFs encontrados
            cpfs_validos = [cpf for cpf in possiveis_cpfs if validar_cpf(cpf)]
            
            for elemento in cpfs_validos + placas_antigas + placas_mercosul:
                # Encontra as áreas onde o elemento aparece
                areas = page.search(elemento)
                page_m = pdf_writer[i]
                for area in areas:
                    # Define o retângulo para cobrir o elemento e aplica a tarja preta
                    rect = fitz.Rect(area['x0'], area['top'], area['x1'], area['bottom'])
                    page_m.draw_rect(rect, color=(0, 0, 0), fill=True)
    
    # Salva o PDF editado em bytes
    pdf_output = BytesIO()
    pdf_writer.save(pdf_output)
    pdf_writer.close()
    pdf_reader.close()
    
    return pdf_output.getvalue()
