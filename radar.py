import pygame
import random
from config import *

class Radar:
    def __init__(self):
        self.visivel = False
        self.mostrar = True
        self.tempo_inicio = 0
        self.ultimo_piscar = 0
        self.piscar_intervalo = 500
        
        # Carregar imagem do radar
        try:
            self.imagem = pygame.image.load("assets/radar.png").convert_alpha()
            self.imagem = pygame.transform.scale(self.imagem, RADAR_TAMANHO)
        except:
            # Fallback
            self.imagem = pygame.Surface(RADAR_TAMANHO, pygame.SRCALPHA)
            self.imagem.fill((0, 100, 200, 150))
            
        # Nova propriedade para controlar se expirou
        self.expirou = False

    def ativar(self):
        self.visivel = True
        self.mostrar = True
        self.expirou = False  # Reset da flag de expiração
        self.piscar_intervalo = 500
        self.tempo_inicio = pygame.time.get_ticks()
        self.ultimo_piscar = self.tempo_inicio

    def update(self):
        if not self.visivel:
            return False

        tempo_atual = pygame.time.get_ticks()
        tempo_passado = tempo_atual - self.tempo_inicio

        # Aumenta velocidade de piscar progressivamente
        progresso = tempo_passado / RADAR_TEMPO_TOTAL
        self.piscar_intervalo = max(100, 500 - int(400 * progresso))

        # Alterna o piscar
        if tempo_atual - self.ultimo_piscar > self.piscar_intervalo:
            self.mostrar = not self.mostrar
            self.ultimo_piscar = tempo_atual

        # Verifica se expirou
        if tempo_passado >= RADAR_TEMPO_TOTAL:
            self.visivel = False
            self.expirou = True  # Marca que expirou (falhou)
            return True  # Indica que expirou
        
        return False

    # Novo método para desativar manualmente (quando o jogador pressiona 'S')
    def desativar(self):
        if self.visivel:
            self.visivel = False
            self.expirou = False  # Não conta como falha se desativou manualmente
            return True
        return False

    def draw(self, tela):
        if self.visivel and self.mostrar:
            tela.blit(self.imagem, RADAR_POS)

        # Desenhar barra de tempo
        if self.visivel:
            tempo_restante = max(0, RADAR_TEMPO_TOTAL - (pygame.time.get_ticks() - self.tempo_inicio))
            barra_largura_max = RADAR_TAMANHO[0]
            barra_largura = int(barra_largura_max * (tempo_restante / RADAR_TEMPO_TOTAL))
            barra_altura = 10

            # Cor vai de verde -> amarelo -> vermelho
            progresso = tempo_restante / RADAR_TEMPO_TOTAL
            if progresso > 0.66:
                cor_barra = (0, 255, 0)
            elif progresso > 0.33:
                cor_barra = (255, 255, 0)
            else:
                cor_barra = (255, 0, 0)

            pygame.draw.rect(tela, cor_barra, (RADAR_POS[0], RADAR_POS[1] + RADAR_TAMANHO[1] + 5, barra_largura, barra_altura))
            pygame.draw.rect(tela, (255,255,255), (RADAR_POS[0], RADAR_POS[1] + RADAR_TAMANHO[1] + 5, barra_largura_max, barra_altura), 2)