import pygame
import random
from config import *

class Obstaculo:
    def __init__(self, x, y, largura, altura, cor, velocidade, move_lateral=False):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor
        self.velocidade = velocidade
        self.move_lateral = move_lateral
        self.direcao = random.choice([-1, 1]) if move_lateral else 0
        self.vel_lateral = 1 if move_lateral else 0

    def mover(self):
        self.rect.y += self.velocidade
        if self.move_lateral:
            self.rect.x += self.direcao * self.vel_lateral
            self._limitar_movimento()

    def _limitar_movimento(self):
        if self.cor == (128, 0, 128):  # Roxo (calçadas)
            if self.rect.left < 0:
                self.rect.left, self.direcao = 0, 1
            if self.rect.right > MARGEM_LATERAL and self.rect.centerx < LARGURA / 2:
                self.rect.right, self.direcao = MARGEM_LATERAL, -1
            if self.rect.left < LARGURA - MARGEM_LATERAL and self.rect.centerx > LARGURA / 2:
                self.rect.left, self.direcao = LARGURA - MARGEM_LATERAL, 1
            if self.rect.right > LARGURA:
                self.rect.right, self.direcao = LARGURA, -1
        else:  # Vermelhos/azuis
            if self.rect.left < MARGEM_LATERAL or self.rect.right > LARGURA - MARGEM_LATERAL:
                self.direcao *= -1
                self.rect.left = max(self.rect.left, MARGEM_LATERAL)
                self.rect.right = min(self.rect.right, LARGURA - MARGEM_LATERAL)

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
