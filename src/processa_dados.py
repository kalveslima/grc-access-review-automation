import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import matplotlib.pyplot as plt

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV = os.path.join(BASE_DIR, 'data', 'controles_acesso.csv')
OUTPUT_IMAGE = os.path.join(BASE_DIR, 'dashboard.png')

def validar_e_filtrar_dados(caminho_arquivo):
    """Fase 1: Ingestão e validação rigorosa de Schema de GRC"""
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return None

    # Carrega o arquivo (suporta CSV ou Excel)
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    df = pd.read_excel(caminho_arquivo) if extensao in ['.xlsx', '.xls'] else pd.read_csv(caminho_arquivo)

    # REQUISITO: Validação das colunas obrigatórias
    colunas_obrigatorias = ['nome_funcionario', 'id_funcionario', 'sistema', 'gerente', 'email_gerente', 'status_revisao']
    
    for col in colunas_obrigatorias:
        if col not in df.columns:
            print(f"❌ Erro de Schema: A coluna obrigatória '{col}' está ausente.")
            return None

    # Trata dados nulos em campos críticos para evitar quebras no envio
    df = df.dropna(subset=['email_gerente', 'status_revisao'])
    
    return df

def gerar_dashboard(df):
    """Fase 2: Motor analítico e visualização"""
    status_counts = df['status_revisao'].value_counts()
    revisados = status_counts.get('Revisado', 0)
    pendentes = status_counts.get('Pendente', 0)
    atrasados = status_counts.get('Atrasado', 0)
    
    plt.figure(figsize=(7, 4.5))
    plt.bar(['Revisado', 'Pendente', 'Atrasado'], [revisados, pendentes, atrasados], color=['#2ec4b6', '#ffbf00', '#e71d36'], width=0.55)
    plt.title('Mapeamento de Conformidade - Revisão de Acessos', fontsize=12, fontweight='bold', pad=15)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    plt.close()
    print(f"📊 Dashboard atualizado em: {OUTPUT_IMAGE}")

def disparar_notificacoes_gerentes(df):
    """Fase 3: Pipeline de comunicação nativo via SMTP (Criado por nós)"""
    
    # REQUISITO: Filtrar apenas inconformidades (Pendente ou Atrasado)
    df_desvios = df[df['status_revisao'].isin(['Pendente', 'Atrasado'])]
    
    if df_desvios.empty:
        print("🟢 Excelente! Nenhum acesso pendente ou atrasado encontrado. Notificações dispensadas.")
        return

    # Agrupa por gerente para enviar um único e-mail consolidado para cada um
    gerentes = df_desvios['email_gerente'].unique()
    
    print(f"📬 Iniciando disparo de notificações para {len(gerentes)} gerentes...")
    
    # Aqui simularemos a lógica de envio (no próximo passo conectamos o servidor real)
    for email_alvo in gerentes:
        # Filtra os funcionários específicos daquele gerente
        acessos_gerente = df_desvios[df_desvios['email_gerente'] == email_alvo]
        nome_gerente = acessos_gerente['gerente'].iloc[0]
        
        print(f"\n👉 Preparando e-mail para: {nome_gerente} ({email_alvo})")
        print(f"   Pendências encontradas: {len(acessos_gerente)} acesso(s).")
        
        # Criação da tabela HTML que irá dentro do corpo do e-mail
        tabela_html = acessos_gerente[['nome_funcionario', 'sistema', 'status_revisao']].to_html(index=False, classes='table')
        
        # Estrutura do e-mail (Mock de visualização)
        corpo_email = f"""
        <html>
            <body>
                <p>Olá, <b>{nome_gerente}</b>,</p>
                <p>Identificamos pendências na Revisão Periódica de Acessos sob sua responsabilidade.</p>
                {tabela_html}
                <p>Por favor, acesse o portal de segurança para regularizar os acessos acima.</p>
            </body>
        </html>
        """
        # [A lógica real de conexão SMTP entrará aqui no próximo bloco]

def executar_pipeline():
    # 1. Ingestão e Validação
    df = validar_e_filtrar_dados(DEFAULT_CSV)
    if df is None:
        return
        
    # 2. Visão Executiva (Gráfico)
    gerar_dashboard(df)
    
    # 3. Ação Operacional (Mensageria)
    disparar_notificacoes_gerentes(df)

if __name__ == "__main__":
    executar_pipeline()