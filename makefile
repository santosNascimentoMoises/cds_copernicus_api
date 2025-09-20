# Nome padrão do ambiente
VENV_NAME ?= .venv

# Atalho para ativação do ambiente
ACTIVATE = . $(VENV_NAME)/bin/activate

# ============================
# Alvos principais
# ============================

## Cria o ambiente virtual e instala dependências básicas
setup:
	@echo "==> Criando ambiente virtual: $(VENV_NAME)"
	python3.12 -m venv $(VENV_NAME)
	@echo "==> Ativando ambiente virtual e instalando pacotes principais"
	$(ACTIVATE) && pip install --upgrade pip && pip install jupyter ipykernel
	@echo "==> Registrando kernel no Jupyter"
	$(ACTIVATE) && python -m ipykernel install --user --name=$(VENV_NAME) --display-name "Python ($(VENV_NAME))"
	@echo "==> Ambiente $(VENV_NAME) pronto!"

## Instala dependências de requirements.txt
install:
	@echo "==> Instalando dependências do requirements.txt"
	$(ACTIVATE) && pip install -r requirements.txt

## Exporta dependências para requirements.txt
freeze:
	@echo "==> Exportando dependências para requirements.txt"
	$(ACTIVATE) && pip freeze > requirements.txt

## Remove ambiente virtual
clean:
	@echo "==> Removendo ambiente virtual: $(VENV_NAME)"
	rm -rf $(VENV_NAME)

## Abre Jupyter Notebook
notebook:
	@echo "==> Iniciando Jupyter Notebook com kernel $(VENV_NAME)"
	$(ACTIVATE) && jupyter notebook

## Abre Jupyter Lab
lab:
	@echo "==> Iniciando Jupyter Lab com kernel $(VENV_NAME)"
	$(ACTIVATE) && jupyter lab
