import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Definir caminhos dos arquivos de forma segura
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'controles_acesso.csv')
OUTPUT_IMAGE = os.path.join(BASE_DIR, 'dashboard.png')

def analisar_dados():
    print("📊 Iniciando análise de dados de conformidade...")
    
    # 2. Ler o arquivo CSV usando o Pandas
    if not os.path.exists(CSV_PATH):
        print(f"❌ Erro: O arquivo {CSV_PATH} não foi encontrado.")
        return
        
    df = pd.read_csv(CSV_PATH)
    
    # 3. Extrair métricas de Governança
    total_acessos = len(df)
    status_counts = df['status_revisao'].value_counts()
    
    revisados = status_counts.get('Revisado', 0)
    pendentes = status_counts.get('Pendente', 0)
    atrasados = status_counts.get('Atrasado', 0)
    
    taxa_conformidade = (revisados / total_acessos) * 100
    
    print(f"\n--- INDICADORES DE GRC ---")
    print(f"Total de Acessos Mapeados: {total_acessos}")
    print(f"✅ Revisados: {revisados}")
    print(f"⏳ Pendentes: {pendentes}")
    print(f"🚨 Atrasados: {atrasados}")
    print(f"📈 Taxa de Conformidade: {taxa_conformidade:.1f}%\n")
    
    # 4. Criar o Gráfico (Dashboard)
    plt.figure(figsize=(8, 5))
    
    # Definindo as cores corporativas (Verde para OK, Amarelo para Atenção, Vermelho para Alerta)
    cores = ['#2ec4b6', '#ffbf00', '#e71d36']
    
    # Criar gráfico de barras
    status_labels = ['Revisado', 'Pendente', 'Atrasado']
    valores = [revisados, pendentes, atrasados]
    
    plt.bar(status_labels, valores, color=cores, edgecolor='gray', width=0.6)
    
    # Customização do layout (Clean e Profissional)
    plt.title('Status da Revisão Periódica de Acessos (IAM)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Status da Revisão', fontsize=12, labelpad=10)
    plt.ylabel('Quantidade de Acessos', fontsize=12, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Salvar o gráfico como imagem
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"✨ Dashboard gerado com sucesso em: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    analisar_dados()