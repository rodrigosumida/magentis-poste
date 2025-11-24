import pygame
from config import *

# Configurações base para todas as fases
CONFIG_BASE = {
    "velocidade_inicial": VELOCIDADE_INICIAL,
    "vel_maxima": VEL_MAXIMA,
    "incremento_vel": INCREMENTO_VEL,
    "intervalo_aumento": INTERVALO_AUMENTO,
    "max_obstaculos": MAX_OBSTACULOS,
    "intervalo_spawn_min": INTERVALO_SPAWN_MIN,
    "intervalo_spawn_max": INTERVALO_SPAWN_MAX,
    "chance_carro": 0.8,  # 80% de chance de ser carro vs caminhão
    "chance_caminhao": 0.2,
    "intervalo_postes": INTERVALO_POSTES,
    "chance_pessoa": CHANCE_ROXO,
    "chance_cachorro": CHANCE_CACHORRO,
    "chance_buraco": CHANCE_BURACO,
    "probabilidade_radar": PROBABILIDADE_RADAR,
    "obstaculos_ativos": ["carro", "caminhao", "pessoa", "poste", "cachorro", "buraco"],
    "tempo_maximo_calcada": 5000,
    "tempo_maximo_radar": RADAR_TEMPO_TOTAL
}

# Configurações específicas para cada fase
CONFIG_FASES = {
    1: {
        "nome": "Fase 1 - Início",
        "descricao": "Aprenda o básico",
        "velocidade_inicial": 4,
        "vel_maxima": 10,
        "max_obstaculos": 3,
        "chance_carro": 0.9,
        "chance_caminhao": 0.1,
        "chance_pessoa": 0.003,
        "chance_cachorro": 0.005,
        "chance_buraco": 0.002,
        "probabilidade_radar": 0.0005,
        "obstaculos_ativos": ["carro", "pessoa", "poste", "buraco"],
        "recompensa": 1000,
        "tempo_bonus": 30,
        "bonus_tempo": 200,
        "musica": "assets/musicas/spooky.mp3"
    },
    2: {
        "nome": "Fase 2 - Trânsito Moderado",
        "descricao": "Mais veículos na pista",
        "velocidade_inicial": 5,
        "vel_maxima": 12,
        "max_obstaculos": 4,
        "chance_carro": 0.7,
        "chance_caminhao": 0.3,
        "chance_pessoa": 0.004,
        "chance_cachorro": 0.006,
        "chance_buraco": 0.003,
        "probabilidade_radar": 0.0008,
        "obstaculos_ativos": ["carro", "caminhao", "poste", "pessoa", "buraco"],
        "recompensa": 1500,
        "tempo_bonus": 45,
        "bonus_tempo": 300,
        "musica": "assets/musicas/spooky.mp3"
    },
    3: {
        "nome": "Fase 3 - Centro da Cidade",
        "descricao": "Trânsito intenso e pedestres",
        "velocidade_inicial": 6,
        "vel_maxima": 15,
        "max_obstaculos": 5,
        "chance_carro": 0.6,
        "chance_caminhao": 0.4,
        "chance_pessoa": 0.005,
        "chance_cachorro": 0.008,
        "chance_buraco": 0.004,
        "probabilidade_radar": 0.001,
        "obstaculos_ativos": ["carro", "caminhao", "pessoa", "poste", "buraco"],
        "tempo_maximo_calcada": 3000,
        "tempo_maximo_radar": 3000,
        "recompensa": 2000,
        "tempo_bonus": 60,
        "bonus_tempo": 400,
        "musica": "assets/musicas/spooky.mp3"
    },
    4: {
        "nome": "Fase 4 - Desafio Total",
        "descricao": "Todos os obstáculos ativos!",
        "velocidade_inicial": 7,
        "vel_maxima": 18,
        "max_obstaculos": 6,
        "chance_carro": 0.5,
        "chance_caminhao": 0.5,
        "chance_pessoa": 0.006,
        "chance_cachorro": 0.01,
        "chance_buraco": 0.005,
        "probabilidade_radar": 0.002,
        "obstaculos_ativos": ["carro", "caminhao", "pessoa", "poste", "cachorro", "buraco"],
        "tempo_maximo_calcada": 3000,
        "tempo_maximo_radar": 2000,
        "recompensa": 2500,
        "tempo_bonus": 75,
        "bonus_tempo": 500,
        "musica": "assets/musicas/spooky.mp3"
    },
    5: {
        "nome": "Fase 5 - Insano",
        "descricao": "Para os mais corajosos",
        "velocidade_inicial": 8,
        "vel_maxima": 20,
        "max_obstaculos": 7,
        "chance_carro": 0.4,
        "chance_caminhao": 0.6,
        "chance_pessoa": 0.008,
        "chance_cachorro": 0.012,
        "chance_buraco": 0.006,
        "probabilidade_radar": 0.003,
        "obstaculos_ativos": ["carro", "caminhao", "pessoa", "poste", "cachorro", "buraco"],
        "tempo_maximo_calcada": 2000,
        "tempo_maximo_radar": 2000,
        "recompensa": 3000,
        "tempo_bonus": 90,
        "bonus_tempo": 600,
        "musica": "assets/musicas/spooky.mp3"
    },
    6: {
        "nome": "Fase Extra - Absurdo",
        "descricao": "Boa sorte",
        "velocidade_inicial": 15,
        "vel_maxima": 100,
        "max_obstaculos": 15,
        "chance_carro": 0.5,
        "chance_caminhao": 0.5,
        "chance_pessoa": 0.01,
        "chance_cachorro": 0.018,
        "chance_buraco": 0.0075,
        "probabilidade_radar": 0.005,
        "recompensa": 0,
        "obstaculos_ativos": ["carro", "caminhao", "pessoa", "poste", "cachorro", "buraco"],
        "tempo_maximo_calcada": 500,
        "tempo_maximo_radar": 1000,
        "musica": "assets/musicas/spooky.mp3"
    }
}

def get_config_fase(numero_fase):
    """Retorna a configuração da fase, mesclando com a base"""
    config_base = CONFIG_BASE.copy()
    if numero_fase in CONFIG_FASES:
        config_base.update(CONFIG_FASES[numero_fase])
    return config_base

def get_total_fases():
    return len(CONFIG_FASES)