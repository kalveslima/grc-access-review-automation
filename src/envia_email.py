import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Garante a leitura das variáveis de ambiente
load_dotenv()

def enviar_email_smtp(email_destino, nome_gerente, tabela_dados):
    """Módulo Isolado: Responsável estritamente por disparar o e-mail via SMTP"""
    remetente = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")

    if not remetente or not senha:
        print(f"⚠️ Modo Simulação (envia_gmail): Credenciais ausentes no .env. Alerta mockado para {nome_gerente}.")
        return False

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
        return True
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail via SMTP para {email_destino}: {e}")
        return False