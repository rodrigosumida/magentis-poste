import json
import os

SAVE_FILE = "save_data.json"

class SaveSystem:
    def __init__(self):
        self.dados = self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega os dados do save ou cria um novo"""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self.criar_dados_novos()
        else:
            return self.criar_dados_novos()
    
    def criar_dados_novos(self):
        """Cria dados iniciais para um novo jogo"""
        dados = {
            "dinheiro": 0,
            "objetivo_total": 10000,  # Objetivo total para vencer o jogo
            "fases_completas": {},
            "fase_atual": 1  # Fase que o jogador pode acessar
        }
        
        # Inicializar todas as fases como não completas
        from fases import get_total_fases
        total_fases = get_total_fases()
        for fase in range(1, total_fases + 1):
            dados["fases_completas"][f"fase_{fase}"] = {
                "completa": False,
                "dinheiro_ganho": 0,
                "melhor_tempo": 0
            }
        
        self.salvar_dados(dados)
        return dados
    
    def salvar_dados(self, dados=None):
        """Salva os dados no arquivo"""
        if dados is None:
            dados = self.dados
        
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(dados, f, indent=4)
            return True
        except:
            return False
    
    def completar_fase(self, numero_fase, tempo_decorrido, dinheiro_ganho):
        """Marca uma fase como completa e adiciona o dinheiro"""
        chave_fase = f"fase_{numero_fase}"
        
        if chave_fase not in self.dados["fases_completas"]:
            self.dados["fases_completas"][chave_fase] = {
                "completa": False,
                "dinheiro_ganho": 0,
                "melhor_tempo": 0
            }
        
        # Só adiciona dinheiro se for a primeira vez completando
        if not self.dados["fases_completas"][chave_fase]["completa"]:
            self.dados["dinheiro"] += dinheiro_ganho
        
        # Marca como completa
        self.dados["fases_completas"][chave_fase]["completa"] = True
        
        # Atualiza melhor tempo se for menor
        tempo_atual = self.dados["fases_completas"][chave_fase]["melhor_tempo"]
        if tempo_atual == 0 or tempo_decorrido < tempo_atual:
            self.dados["fases_completas"][chave_fase]["melhor_tempo"] = tempo_decorrido
        
        # Atualiza dinheiro ganho
        self.dados["fases_completas"][chave_fase]["dinheiro_ganho"] = dinheiro_ganho
        
        # Libera próxima fase se existir
        from fases import get_total_fases
        total_fases = get_total_fases()
        if numero_fase < total_fases and numero_fase >= self.dados["fase_atual"]:
            self.dados["fase_atual"] = numero_fase + 1
        
        return self.salvar_dados()
    
    def get_dinheiro(self):
        return self.dados["dinheiro"]
    
    def get_objetivo_total(self):
        return self.dados["objetivo_total"]
    
    def get_fase_completa(self, numero_fase):
        chave_fase = f"fase_{numero_fase}"
        if chave_fase in self.dados["fases_completas"]:
            return self.dados["fases_completas"][chave_fase]["completa"]
        return False
    
    def get_fase_acessivel(self, numero_fase):
        """Verifica se a fase pode ser acessada pelo jogador"""
        return numero_fase <= self.dados["fase_atual"]
    
    def get_melhor_tempo(self, numero_fase):
        chave_fase = f"fase_{numero_fase}"
        if chave_fase in self.dados["fases_completas"]:
            return self.dados["fases_completas"][chave_fase]["melhor_tempo"]
        return 0
    
    def resetar_progresso(self):
        """Reseta todo o progresso do jogador"""
        self.dados = self.criar_dados_novos()
        return self.salvar_dados()
    
    def jogo_completo(self):
        """Verifica se o jogador atingiu o objetivo total"""
        return self.dados["dinheiro"] >= self.dados["objetivo_total"]