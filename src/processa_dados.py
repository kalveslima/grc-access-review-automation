import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV = os.path.join(BASE_DIR, 'data', 'controles_acesso.csv')
OUTPUT_IMAGE = os.path.join(BASE_DIR, 'dashboard.png')
OUTPUT_REPORT = os.path.join(BASE_DIR, 'relatorio_auditoria.txt')

def validar_e_filtrar_dados(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return None

    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    df = pd.read_excel(caminho_arquivo) if extensao in ['.xlsx', '.xls'] else pd.read_csv(caminho_arquivo)

    colunas_obrigatorias = ['nome_funcionario', 'id_funcionario', 'sistema', 'gerente', 'email_gerente', 'status_revisao']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            print(f"❌ Erro de Schema: A coluna obrigatória '{col}' está ausente.")
            return None

    return df.dropna(subset=['email_gerente', 'status_revisao'])

def gerar_dashboard_grafico(df):
    """Gera o indicador visual executivo para o CISO/Diretoria"""
    status_counts = df['status_revisao'].value_counts()
    revisados = status_counts.get('Revisado', 0)
    pendentes = status_counts.get('Pendente', 0)
    atrasados = status_counts.get('Atrasado', 0)
    
    plt.figure(figsize=(7, 4.5))
    cores = ['#2ec4b6', '#ffbf00', '#e71d36'] # Verde-água, Amarelo, Vermelho
    
    plt.bar(['Revisado', 'Pendente', 'Atrasado'], [revisados, pendentes, atrasados], color=cores, width=0.55, edgecolor='#dddddd')
    plt.title('Mapeamento de Conformidade - Revisão de Acessos (IAM)', fontsize=12, fontweight='bold', pad=15)
    plt.ylabel('Quantidade de Controles', fontsize=10)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    plt.close()
    print(f"📊 Dashboard visual gerado com sucesso em: {os.path.basename(OUTPUT_IMAGE)}")

def enviar_email_smtp(email_destino, nome_gerente, tabela_dados):
    remetente = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")

    if not remetente or not senha:
        print(f"⚠️ Modo Simulação: Sem credenciais no .env. Notificação mockada para {nome_gerente}.")
        return

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = email_destino
    msg['Subject'] = f"🚨 [Ação Requerida] Revisão de Acessos Pendente - Gestão {nome_gerente}"

    corpo_html = f"""
    <html>
        <body style="font-family: sans-serif; color: #333; line-height: 1.6;">
            <h3 style="color: #e71d36;">Atenção Gestor(a) {nome_gerente},</h3>
            <p>Identificamos desvios de conformidade na Revisão Periódica de Acessos (IAM) sob sua responsabilidade.</p>
            <p>Os seguintes acessos estão com o status <b>Pendente</b> ou <b>Atrasado</b> e exigem sua regularização imediata:</p>
            <div style="margin-top: 15px; margin-bottom: 15px;">
                {tabela_dados}
            </div>
            <p><i>Este é um alerta automático gerado pelo pipeline de automação de Governança e Compliance.</i></p>
        </body>
    </html>
    """
    msg.attach(MIMEText(corpo_html, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(remetente, senha)
        server.sendmail(remetente, email_destino, msg.as_string())
        server.quit()
        print(f"✅ Notificação enviada com sucesso para: {email_destino}")
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail via SMTP: {e}")

def disparar_notificacoes_gerentes(df):
    df_desvios = df[df['status_revisao'].isin(['Pendente', 'Atrasado'])]
    
    if df_desvios.empty:
        print("🟢 Nenhum acesso pendente ou atrasado encontrado.")
        return

    gerentes = df_desvios['email_gerente'].unique()
    
    for email_alvo in gerentes:
        acessos_gerente = df_desvios[df_desvios['email_gerente'] == email_alvo]
        nome_gerente = acessos_gerente['gerente'].iloc[0]
        
        # Formata a tabela HTML do e-mail
        tabela_html = acessos_gerente[['nome_funcionario', 'id_funcionario', 'sistema', 'status_revisao']].to_html(
            index=False, border=0
        ).replace('<table', '<table style="width:100%; border-collapse: collapse; font-family: sans-serif;"') \
         .replace('<th', '<th style="background-color: #f4f4f4; padding: 8px; text-align: left; border-bottom: 2px solid #ddd;"') \
         .replace('<td', '<td style="padding: 8px; border-bottom: 1px solid #ddd;"')
        
        enviar_email_smtp(email_alvo, nome_gerente, tabela_html)

def gerar_relatorio_txt(df):
    total = len(df)
    counts = df['status_revisao'].value_counts()
    revisados = counts.get('Revisado', 0)
    pendentes = counts.get('Pendente', 0)
    atrasados = counts.get('Atrasado', 0)
    taxa = (revisados / total) * 100 if total > 0 else 0

    texto_relatorio = f"""========================================================
RELATÓRIO DE AUDITORIA E COMPLIANCE - CONTROLE DE ACESSOS (IAM)
========================================================
- Total de Acessos Mapeados na Base: {total}
- Acessos Revisados (Em Conformidade): {revisados}
- Acessos Pendentes (Dentro do Prazo): {pendentes}
- Acessos Atrasados (Risco Identificado): {atrasados}
- Índice Geral de Conformidade: {taxa:.1f}%
========================================================\n"""
    print(texto_relatorio)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(texto_relatorio)

def executar_pipeline():
    df = validar_e_filtrar_dados(DEFAULT_CSV)
    if df is None: return
    
    # 1. Indicadores textuais e log
    gerar_relatorio_txt(df)
    
    # 2. Geração do gráfico físico (.png)
    gerar_dashboard_grafico(df)
    
    # 3. Disparo das notificações
    disparar_notificacoes_gerentes(df)

if __name__ == "__main__":
    executar_pipeline()