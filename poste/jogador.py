import pygame
from config import *

class Jogador:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.olhando_esquerda = False
        self.travado = False
        self.invencivel = False
        self.animando = False
        self.frame_atual = 0
        self.ultimo_tempo_anim = pygame.time.get_ticks()

        # Sprites
        self.sprite_parado = self.carregar_sprite("poste/assets/Peter_Griffin.png")
        self.sprite_travado = self.carregar_sprite("poste/assets/morte.png")
        self.frames = [self.carregar_sprite(f"poste/assets/frame_{i}_delay-0.1s.gif") for i in range(7)]

    def carregar_sprite(self, caminho):
        img = pygame.image.load(caminho)
        return pygame.transform.scale(img, (JOGADOR_LARG, JOGADOR_ALT))

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, JOGADOR_LARG, JOGADOR_ALT)

    def mover(self, teclas):
        if self.travado:
            return

        self.animando = False
        if teclas[pygame.K_LEFT]:
            self.x -= VEL_JOGADOR
            self.animando = True
            self.olhando_esquerda = True
        if teclas[pygame.K_RIGHT]:
            self.x += VEL_JOGADOR
            self.animando = True
            self.olhando_esquerda = False

        # Limites da tela
        self.x = max(0, min(self.x, LARGURA - JOGADOR_LARG))

    def atualizar_animacao(self):
        if self.animando and not self.travado:
            agora = pygame.time.get_ticks()
            if agora - self.ultimo_tempo_anim > 50:
                self.frame_atual = (self.frame_atual + 1) % len(self.frames)
                self.ultimo_tempo_anim = agora
        else:
            self.frame_atual = 0

    def desenhar(self, tela):
        if self.travado:
            sprite = self.sprite_travado
        elif self.animando:
            sprite = self.frames[self.frame_atual]
        else:
            sprite = self.sprite_parado

        if self.olhando_esquerda:
            sprite = pygame.transform.flip(sprite, True, False)

        tela.blit(sprite, (self.x, self.y))
