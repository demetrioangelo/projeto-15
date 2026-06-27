# ============================================
# 🌺 FLORES ONLINE - BACK-END EM PYTHON
# ============================================

from flask import Flask, render_template, request, redirect, url_for, session
import re
import datetime
import os

# ===== CRIA A APLICAÇÃO =====
app = Flask(__name__)
app.secret_key = 'flores_online_chave_secreta_2026'

# ============================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================

def validar_nome(nome):
    """Valida o nome do usuário"""
    if not nome or len(nome.strip()) == 0:
        return False, "❌ O nome é obrigatório!"
    
    nome = nome.strip()
    if len(nome) < 3:
        return False, "❌ O nome deve ter pelo menos 3 caracteres!"
    
    if len(nome) > 100:
        return False, "❌ O nome é muito longo (máximo 100 caracteres)!"
    
    # Permite letras, espaços, acentos e ç
    if not re.match(r"^[a-zA-ZáéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇ\s]+$", nome):
        return False, "❌ O nome só pode conter letras e espaços!"
    
    return True, nome

def validar_email(email):
    """Valida o e-mail do usuário"""
    if not email or len(email.strip()) == 0:
        return False, "❌ O e-mail é obrigatório!"
    
    email = email.strip()
    
    # Expressão regular para validar e-mail
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(padrao, email):
        return False, "❌ E-mail inválido! Exemplo: usuario@email.com"
    
    if len(email) > 255:
        return False, "❌ E-mail muito longo!"
    
    return True, email

def validar_telefone(telefone):
    """Valida o telefone (opcional)"""
    if not telefone or len(telefone.strip()) == 0:
        return True, ""  # Campo opcional
    
    telefone = telefone.strip()
    
    # Remove caracteres especiais
    telefone_limpo = re.sub(r'[^0-9]', '', telefone)
    
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 15:
        return False, "❌ Telefone inválido! Use (11) 99999-9999"
    
    return True, telefone

def validar_mensagem(mensagem):
    """Valida a mensagem"""
    if not mensagem or len(mensagem.strip()) == 0:
        return False, "❌ A mensagem é obrigatória!"
    
    mensagem = mensagem.strip()
    
    if len(mensagem) < 10:
        return False, "❌ A mensagem deve ter pelo menos 10 caracteres!"
    
    if len(mensagem) > 5000:
        return False, "❌ Mensagem muito longa (máximo 5000 caracteres)!"
    
    return True, mensagem

def limpar(texto):
    """Remove HTML e caracteres perigosos"""
    if not texto:
        return ""
    
    import html
    texto = html.escape(texto)
    return texto

# ============================================
# ROTAS DA APLICAÇÃO
# ============================================

@app.route('/')
def inicio():
    """Página inicial com o formulário"""
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    """Processa o formulário"""
    
    # ===== 1. RECEBE OS DADOS =====
    nome = request.form.get('nome', '')
    email = request.form.get('email', '')
    telefone = request.form.get('telefone', '')
    mensagem = request.form.get('mensagem', '')
    
    # ===== 2. VALIDA CAMPO POR CAMPO =====
    erros = {}
    dados_validos = {}
    
    # Valida nome
    valido, resultado = validar_nome(nome)
    if not valido:
        erros['nome'] = resultado
    else:
        dados_validos['nome'] = resultado
    
    # Valida email
    valido, resultado = validar_email(email)
    if not valido:
        erros['email'] = resultado
    else:
        dados_validos['email'] = resultado
    
    # Valida telefone (opcional)
    valido, resultado = validar_telefone(telefone)
    if not valido:
        erros['telefone'] = resultado
    else:
        dados_validos['telefone'] = resultado
    
    # Valida mensagem
    valido, resultado = validar_mensagem(mensagem)
    if not valido:
        erros['mensagem'] = resultado
    else:
        dados_validos['mensagem'] = resultado
    
    # ===== 3. LIMPA OS DADOS =====
    nome_limpo = limpar(dados_validos.get('nome', nome))
    email_limpo = limpar(dados_validos.get('email', email))
    telefone_limpo = limpar(dados_validos.get('telefone', telefone))
    mensagem_limpa = limpar(dados_validos.get('mensagem', mensagem))
    
    # ===== 4. VERIFICA SE HOUVE ERROS =====
    if erros:
        # Guarda erros e dados para mostrar no formulário
        session['erros'] = erros
        session['dados'] = {
            'nome': nome_limpo,
            'email': email_limpo,
            'telefone': telefone_limpo,
            'mensagem': mensagem_limpa
        }
        return redirect(url_for('inicio'))
    
    # ===== 5. TUDO VÁLIDO! PROCESSAR OS DADOS =====
    
    # Pega a data/hora atual
    agora = datetime.datetime.now()
    
    # Cria um arquivo de log com os dados
    dados_arquivo = f"""
===========================================
🌺 FLORES ONLINE - NOVO CONTATO
===========================================
DATA/HORA: {agora.strftime('%d/%m/%Y %H:%M:%S')}
IP: {request.remote_addr}
-------------------------------------------
NOME: {nome_limpo}
E-MAIL: {email_limpo}
TELEFONE: {telefone_limpo}
-------------------------------------------
MENSAGEM:
{mensagem_limpa}
-------------------------------------------
NAVEGADOR: {request.headers.get('User-Agent', 'Desconhecido')}
===========================================

"""
    
    # Salva no arquivo (cria se não existir)
    try:
        with open('contatos.txt', 'a', encoding='utf-8') as arquivo:
            arquivo.write(dados_arquivo)
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    
    # ===== 6. REDIRECIONA PARA SUCESSO =====
    session['mensagem_sucesso'] = "Mensagem enviada com sucesso! Entraremos em contato em breve."
    return redirect(url_for('sucesso'))

@app.route('/sucesso')
def sucesso():
    """Página de sucesso"""
    if 'mensagem_sucesso' not in session:
        return redirect(url_for('inicio'))
    
    mensagem = session['mensagem_sucesso']
    session.pop('mensagem_sucesso', None)  # Remove a mensagem
    
    # Pega a data atual para mostrar na página
    agora = datetime.datetime.now()
    
    return render_template('sucesso.html', mensagem=mensagem, agora=agora)

# ============================================
# INICIA O SERVIDOR
# ============================================

if __name__ == '__main__':
    # Cria as pastas se não existirem
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 50)
    print("🌺 FLORES ONLINE - SERVIDOR INICIADO")
    print("=" * 50)
    print(f"📅 Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🔗 Acesse: http://127.0.0.1:5000")
    print("=" * 50)
    print("⚠️  Pressione CTRL+C para parar o servidor")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)