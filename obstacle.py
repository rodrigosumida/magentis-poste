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
        "imagem": ["assets/cachorro_parado_1.png", "assets/cachorro_parado_2.png", "assets/cachorro_andando_1.png", "assets/cachorro_andando_2.png"],
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

        # Determinar a direção inicial baseado na posição X
        self.olhando_esquerda = x < LARGURA // 2  # True se spawnou no lado esquerdo

        # Sistema de animação para cachorro
        if tipo == "cachorro":
            # Carregar as imagens originais
            self.frames_parado_originais = [
                self.carregar_imagem(dados["imagem"][0], (dados["largura"], dados["altura"])),
                self.carregar_imagem(dados["imagem"][1], (dados["largura"], dados["altura"]))
            ]
            self.frames_andando_originais = [
                self.carregar_imagem(dados["imagem"][2], (dados["largura"], dados["altura"])),
                self.carregar_imagem(dados["imagem"][3], (dados["largura"], dados["altura"]))
            ]
            
            # Aplicar espelhamento inicial baseado na posição
            self.frames_parado = self.aplicar_espelhamento(self.frames_parado_originais)
            self.frames_andando = self.aplicar_espelhamento(self.frames_andando_originais)
            
            self.frame_atual = 0
            self.tempo_ultima_animacao = pygame.time.get_ticks()
            self.intervalo_animacao = 200  # ms entre frames
            self.andando = False
        else:
            # Comportamento normal para outros obstáculos
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
    
    # Método para aplicar espelhamento
    def aplicar_espelhamento(self, frames):
        """Aplica espelhamento horizontal nos frames se o cachorro estiver no lado direito"""
        if self.olhando_esquerda:
            return frames  # Mantém original se estiver olhando para esquerda
        else:
            # Espelha horizontalmente todos os frames
            return [pygame.transform.flip(frame, True, False) for frame in frames]

    # Método para atualizar direção quando está seguindo
    def atualizar_direcao_seguindo(self, personagem_rect):
        """Atualiza a direção que o cachorro está olhando quando está seguindo o jogador"""
        if self.tipo == "cachorro" and self.seguindo:
            # Determina para qual lado o cachorro deve olhar baseado na posição do jogador
            deve_olhar_esquerda = personagem_rect.centerx > self.rect.centerx
            
            # Se a direção mudou, atualiza os frames espelhados
            if deve_olhar_esquerda != self.olhando_esquerda:
                self.olhando_esquerda = deve_olhar_esquerda
                self.frames_parado = self.aplicar_espelhamento(self.frames_parado_originais)
                self.frames_andando = self.aplicar_espelhamento(self.frames_andando_originais)

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

    def mover(self, velocidade_fundo=None, outros_obstaculos=None):
        # Buracos se movem com a velocidade do fundo (mais lento)
        if self.tipo == "buraco" and velocidade_fundo is not None:
            self.rect.y += velocidade_fundo
        else:
            # Comportamento normal para outros obstáculos
            self.rect.y += self.velocidade
        
        # Atualizar estado de animação do cachorro
        if self.tipo == "cachorro":
            estava_andando = self.andando
            self.andando = self.seguindo  # Está andando se está seguindo o jogador
            
            # Se mudou de estado, reseta a animação
            if estava_andando != self.andando:
                self.frame_atual = 0
                self.tempo_ultima_animacao = pygame.time.get_ticks()
        
        if self.move_lateral:
            self.rect.x += self.direcao * self.vel_lateral
            self._manter_nos_limites()
            
            # NOVO: Verificar colisão com outros obstáculos
            if outros_obstaculos:
                self._verificar_colisao_obstaculos(outros_obstaculos)

    def _verificar_colisao_obstaculos(self, outros_obstaculos):
        """Verifica colisão com outros obstáculos e muda de direção se necessário"""
        for outro in outros_obstaculos:
            if outro is not self and self.rect.colliderect(outro.rect):
                # Só colide com certos tipos de obstáculos
                if outro.tipo in ["carro", "caminhao", "poste"]:
                    # Muda de direção
                    self.direcao *= -1
                    
                    # Ajusta a posição para evitar sobreposição
                    if self.direcao > 0:
                        self.rect.left = outro.rect.right + 5
                    else:
                        self.rect.right = outro.rect.left - 5
                    break

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

                    # Atualizar direção enquanto segue
                    self.atualizar_direcao_seguindo(personagem_rect)
                else:
                    self.seguindo = False
    
    # Método para atualizar animação
    def atualizar_animacao(self):
        if self.tipo == "cachorro":
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.tempo_ultima_animacao > self.intervalo_animacao:
                self.frame_atual = (self.frame_atual + 1) % 2  # Alterna entre 0 e 1
                self.tempo_ultima_animacao = tempo_atual

    def draw(self, tela):
        if self.tipo == "cachorro":
            # Lógica de animação para cachorro
            self.atualizar_animacao()
            
            # Escolher o frame baseado no estado
            if self.andando:
                imagem = self.frames_andando[self.frame_atual]
            else:
                imagem = self.frames_parado[self.frame_atual]
                
            img_rect = imagem.get_rect(midbottom=self.rect.midbottom)
            tela.blit(imagem, img_rect.topleft)
        elif self.imagem:
            # Comportamento normal para outros obstáculos
            img_rect = self.imagem.get_rect(midbottom=self.rect.midbottom)
            tela.blit(self.imagem, img_rect.topleft)