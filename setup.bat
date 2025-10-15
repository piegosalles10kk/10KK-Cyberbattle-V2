@echo off
REM ============================================
REM CyberDuel API - Setup Automatizado (Windows)
REM ============================================

echo.
echo ============================================
echo   CYBERDUEL API - SETUP AUTOMATIZADO
echo ============================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.8+ de https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Verificar se está no diretório correto
if not exist "api.py" (
    echo [ERRO] Arquivo api.py nao encontrado!
    echo.
    echo Certifique-se de executar este script no diretorio raiz do projeto.
    echo.
    pause
    exit /b 1
)

echo [OK] Diretorio correto
echo.

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo [PASSO 1/6] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado
) else (
    echo [PASSO 1/6] Ambiente virtual ja existe
)
echo.

REM Ativar ambiente virtual
echo [PASSO 2/6] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Falha ao ativar ambiente virtual
    pause
    exit /b 1
)
echo [OK] Ambiente virtual ativado
echo.

REM Atualizar pip
echo [PASSO 3/6] Atualizando pip...
python -m pip install --upgrade pip setuptools wheel --quiet
if errorlevel 1 (
    echo [AVISO] Falha ao atualizar pip, continuando...
) else (
    echo [OK] pip atualizado
)
echo.

REM Instalar dependências
echo [PASSO 4/6] Instalando dependencias...
echo.
echo Escolha o arquivo de dependencias:
echo   1. requirements-minimal.txt (Recomendado - apenas essenciais)
echo   2. requirements.txt (Completo - inclui ferramentas de dev)
echo.
set /p choice="Digite sua escolha (1 ou 2): "

if "%choice%"=="2" (
    echo.
    echo Instalando dependencias completas...
    pip install -r requirements.txt
) else (
    echo.
    echo Instalando dependencias minimas...
    pip install -r requirements-minimal.txt
)

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias
    echo.
    echo Tente manualmente:
    echo   pip install flask flask-cors pywinrm requests python-dotenv
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Criar arquivo .env
echo [PASSO 5/6] Configurando arquivo .env...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Arquivo .env criado a partir do template
        echo [IMPORTANTE] Edite o arquivo .env com suas configuracoes!
    ) else (
        echo [AVISO] .env.example nao encontrado, criando .env basico...
        (
            echo # CyberDuel API - Configuracao
            echo FLASK_ENV=development
            echo SECRET_KEY=mude-isto-em-producao
            echo DEBUG=True
            echo.
            echo # Terraform
            echo TERRAFORM_BASE_DIR=./iac
            echo.
            echo # Hyper-V
            echo HYPERV_HOST=127.0.0.1
            echo HYPERV_USER=seu-usuario
            echo HYPERV_PASSWORD=sua-senha
        ) > .env
        echo [OK] Arquivo .env basico criado
    )
) else (
    echo [OK] Arquivo .env ja existe
)
echo.

REM Criar diretórios necessários
echo [PASSO 6/6] Criando diretorios...
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "results" mkdir results
echo [OK] Diretorios criados
echo.

REM Verificar instalação
echo ============================================
echo   VERIFICANDO INSTALACAO
echo ============================================
echo.

python check_install.py
if errorlevel 1 (
    echo.
    echo [AVISO] Algumas verificacoes falharam
    echo Consulte o output acima para detalhes
) else (
    echo.
    echo [OK] Todas as verificacoes passaram!
)

echo.
echo ============================================
echo   SETUP CONCLUIDO!
echo ============================================
echo.
echo Proximos passos:
echo   1. Edite o arquivo .env com suas configuracoes
echo   2. Configure sua VM base no Hyper-V
echo   3. Inicie a API: python api.py
echo   4. Teste: python test_client.py
echo.
echo Documentacao completa em: README.md e INSTALL.md
echo.
pause