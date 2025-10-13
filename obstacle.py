import pygame
import random
from config import *

# Configurações dos tipos de obstáculo
CONFIG_TIPOS = {
    "carro": {
        "largura": 77,
        "altura": 110,
        "imagem": "assets/carro.png",
        "move_lateral": False,
    },
    "caminhao": {
        "largura": 80,
        "altura": 150,
        "imagem": "assets/caminhao.png",
        "move_lateral": True,
    },
    "pessoa": {
        "largura": 30,
        "altura": 30,
        "imagem": "assets/pessoa.png",
        "move_lateral": True,
    },
    "poste": {
        "largura": 60,
        "altura": 160,
        "imagem": "assets/poste.png",
        "move_lateral": False,
    },
    "cachorro": {
        "largura": 50,
        "altura": 50,
        "imagem": "assets/cachorro.png",
        "move_lateral": False,
    },
    "buraco": {
        "largura": 80,
        "altura": 60,
        "imagem": "assets/buraco.png",
        "move_lateral": False,
    }
}

class Obstaculo:
    def __init__(self, tipo, x, y, velocidade=6):
        dados = CONFIG_TIPOS.get(tipo)
        if not dados:
            raise ValueError(f"Tipo de obstáculo desconhecido: {tipo}")

        self.tipo = tipo
        self.velocidade = velocidade
        self.move_lateral = dados["move_lateral"]
        
        # Carregar imagem
        self.imagem = self.carregar_imagem(dados["imagem"], (dados["largura"], dados["altura"]))

        # Criar a hitbox
        self.rect = pygame.Rect(x, y, dados["largura"], dados["altura"])

        # Comportamento lateral
        self.direcao = random.choice([-1, 1]) if self.move_lateral else 0
        self.vel_lateral = 1 + (random.random() * random.randint(-1, 1)) if self.move_lateral else 0

        # Comportamento específico do cachorro
        if tipo == "cachorro":
            self.seguindo = False
            self.tempo_inicio_seguir = 0

    def carregar_imagem(self, caminho, tamanho):
        try:
            img = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(img, tamanho)
        except:
            # Fallback: retângulo colorido
            surf = pygame.Surface(tamanho, pygame.SRCALPHA)
            if self.tipo == "carro":
                surf.fill((255, 0, 0))
            elif self.tipo == "caminhao":
                surf.fill((0, 0, 255))
            elif self.tipo == "pessoa":
                surf.fill((128, 0, 128))
            elif self.tipo == "poste":
                surf.fill((255, 255, 0))
            elif self.tipo == "cachorro":
                surf.fill((200, 200, 50))
            elif self.tipo == "buraco":
                surf.fill((50, 50, 50))
            return surf

    def mover(self, velocidade_fundo=None):
        # Buracos se movem com a velocidade do fundo (mais lento)
        if self.tipo == "buraco" and velocidade_fundo is not None:
            self.rect.y += velocidade_fundo
        else:
            # Comportamento normal para outros obstáculos
            self.rect.y += self.velocidade
        
        if self.move_lateral:
            self.rect.x += self.direcao * self.vel_lateral
            self._manter_nos_limites()

    def _manter_nos_limites(self):
        if self.tipo == "pessoa":
            # Presa na calçada
            if self.rect.left < 0: 
                self.rect.left = 0
                self.direcao *= -1
            elif self.rect.right > MARGEM_LATERAL:  # calçada esquerda
                self.rect.right = MARGEM_LATERAL
                self.direcao *= -1

            # Se estiver na calçada direita
            if self.rect.left > LARGURA/2:
                if self.rect.left < LARGURA - MARGEM_LATERAL:
                    self.rect.left = LARGURA - MARGEM_LATERAL
                if self.rect.right > LARGURA:
                    self.rect.right = LARGURA
                if self.rect.left >= LARGURA - MARGEM_LATERAL:
                    self.direcao *= -1
        else:
            # Limites padrão para carros/caminhões/postes
            if self.rect.left < MARGEM_LATERAL:
                self.rect.left = MARGEM_LATERAL
                self.direcao *= -1
            elif self.rect.right > LARGURA - MARGEM_LATERAL:
                self.rect.right = LARGURA - MARGEM_LATERAL
                self.direcao *= -1

    def update_seguir(self, personagem_rect):
        if self.tipo == "cachorro":
            dx = personagem_rect.centerx - self.rect.centerx
            dy = personagem_rect.centery - self.rect.centery
            distancia = (dx**2 + dy**2) ** 0.5

            # Se está próximo e ainda não seguindo
            if not self.seguindo and distancia < DISTANCIA_ATIVACAO_CACHORRO:
                self.seguindo = True
                self.tempo_inicio_seguir = pygame.time.get_ticks()

            # Se está seguindo o jogador
            if self.seguindo:
                tempo_agora = pygame.time.get_ticks()
                if tempo_agora - self.tempo_inicio_seguir < DURACAO_SEGUIR:
                    direcao_x = dx / max(1, abs(dx))
                    self.rect.x += int(direcao_x * 4)
                else:
                    self.seguindo = False

    def draw(self, tela):
        if self.imagem:
            img_rect = self.imagem.get_rect(midbottom=self.rect.midbottom)
            tela.blit(self.imagem, img_rect.topleft)