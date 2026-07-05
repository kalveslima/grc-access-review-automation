# Pipeline de Automação: Revisão Periódica de Acessos (IAM & GRC)

## 📌 Contexto do Projeto e Dores de Negócio
A Revisão Periódica de Acessos é um controle obrigatório de conformidade exigido por normas internacionais de Segurança da Informação e Auditoria (como **ISO 27001**, **SOX** e **LGPD**). O objetivo fundamental é garantir o princípio do menor privilégio, mitigando o risco de acessos indevidos acumulados (como funcionários que mudaram de área ou saíram da organização).

Em grandes corporações, a ausência de ferramentas automatizadas de IGA (Identity Governance and Administration) força os analistas de GRC a consolidarem planilhas brutas manualmente e cobrarem os gestores via e-mails individuais. Esse processo manual é suscetível a erros, atrasos e falhas de conformidade.

**Esta solução em Python automatiza o pipeline fim a fim:** valida a integridade dos dados brutos, extrai métricas executivas, gera relatórios de auditoria e descentraliza as cobranças operacionais, notificando cada gerente automaticamente com seus respectivos desvios de acesso.

---

## 🛠️ Decisões de Arquitetura e Engenharia

O projeto foi construído seguindo rigorosos padrões de portabilidade, segurança e engenharia de software:

* **Versionamento Estável (Python 3.10):** Fixado em uma versão de alta estabilidade e compatibilidade com ambientes produtivos (AWS, Azure, Docker), evitando fricções de compilação local de bibliotecas de dados.
* **Princípio de Responsabilidade Única (SRP):** Desacoplamento total entre o motor analítico (`processa_dados.py`) e o serviço de mensageria (`envia_gmail.py`), permitindo fácil manutenção e testes isolados.
* **Validação de Data Quality (Schema Check):** O pipeline realiza uma auditoria prévia na estrutura e nos dados do arquivo ingerido (CSV/Excel). Campos nulos ou colunas ausentes barram a execução para evitar falsos positivos de compliance.
* **Segurança da Informação e Compliance:** Nenhuma credencial sensível ou token de acesso é exposto no código. Toda a autenticação com o servidor SMTP utiliza variáveis de ambiente isoladas em um arquivo `.env` e chaves criptográficas de aplicativos.

---

## 🏗️ Estrutura do Projeto

```text
grc-access-review-automation/
│
├── data/
│   └── controles_acesso.csv     # Base de dados bruta (IDs, Sistemas, Status e Gestores)
│
├── src/
│   ├── processa_dados.py        # Core do pipeline: validação, métricas e orquestração
│   └── envia_gmail.py          # Módulo isolado de mensageria via protocolo SMTP
│
├── .env                         # Arquivo isolado de credenciais (Não monitorado pelo Git)
├── .gitignore                   # Proteção para não versionar arquivos locais e o .env
├── relatorio_auditoria.txt       # Artefato gerado: Evidência física para auditores externos
├── dashboard.png                # Artefato gerado: Indicador visual para nível executivo (CISO)
└── requirements.txt             # Dependências estritas e portáveis do projeto