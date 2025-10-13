import pygame
from config import *

class Player:
    def __init__(self):
        self.x = 50
        self.y = ALTURA - ALTURA_RET - 30
        self.largura = LARGURA_RET
        self.altura = ALTURA_RET
        self.velocidade = VELOCIDADE_PERSONAGEM
        
        # Carregar sprites
        self.sprite_parado = self.carregar_imagem("assets/Peter_Griffin.png", (self.largura, self.altura))
        self.sprite_travado = self.carregar_imagem("assets/morte.png", (self.largura, self.altura))
        
        # Frames de animação
        self.frames = [self.sprite_parado]  # Por enquanto só um frame
        self.frame_atual = 0
        self.tempo_animacao = 50
        self.ultimo_tempo = pygame.time.get_ticks()
        
        # Estados
        self.animando = False
        self.olhando_esquerda = False
        self.travado = False
        self.invencivel = False
        
        # Empurrão
        self.empurrado = False
        self.direcao_empurrao = 0
        self.tempo_inicio_empurrao = 0

        # Timer para calçada
        self.na_calcada = False
        self.tempo_entrou_calcada = 0
        self.tempo_atual_calcada = 0

    def carregar_imagem(self, caminho, tamanho):
        try:
            img = pygame.image.load(caminho)
            return pygame.transform.scale(img, tamanho)
        except:
            # Fallback: retângulo colorido se a imagem não carregar
            surf = pygame.Surface(tamanho)
            surf.fill((255, 0, 0))
            return surf

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def update(self, teclas):
        self.animando = False

        # Verificar se está na calçada antes de processar movimento
        estava_na_calcada = self.na_calcada
        self.verificar_calcada()
        
        if not self.travado and not self.empurrado:
            if teclas[pygame.K_LEFT]:
                self.x -= self.velocidade
                self.animando = True
                self.olhando_esquerda = True
            if teclas[pygame.K_RIGHT]:
                self.x += self.velocidade
                self.animando = True
                self.olhando_esquerda = False

            # Limites da tela
            self.x = max(0, min(self.x, LARGURA - self.largura))
        
        # Atualizar timer da calçada
        self.atualizar_timer_calcada(estava_na_calcada)

        # Atualizar animação
        if self.animando and not self.travado:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_tempo > self.tempo_animacao:
                self.frame_atual = (self.frame_atual + 1) % len(self.frames)
                self.ultimo_tempo = tempo_atual
        else:
            self.frame_atual = 0

        # Processar empurrão
        if self.empurrado:
            tempo_agora = pygame.time.get_ticks()
            if tempo_agora - self.tempo_inicio_empurrao < DURACAO_EMPURRAO:
                self.x += self.direcao_empurrao * FORCA_EMPURRAO
                self.x = max(0, min(self.x, LARGURA - self.largura))
            else:
                self.empurrado = False
    
    # Método para controle da calçada
    def verificar_calcada(self):
        """Verifica se o jogador está na calçada"""
        # Calçada esquerda: x entre 0 e MARGEM_LATERAL
        # Calçada direita: x entre LARGURA-MARGEM_LATERAL e LARGURA
        self.na_calcada = (self.x < MARGEM_LATERAL) or (self.x > LARGURA - MARGEM_LATERAL - self.largura)

    def atualizar_timer_calcada(self, estava_na_calcada):
        """Atualiza o timer de permanência na calçada"""
        tempo_atual = pygame.time.get_ticks()
        
        if self.na_calcada and not self.travado:
            if not estava_na_calcada:
                # Acabou de entrar na calçada
                self.tempo_entrou_calcada = tempo_atual
                self.tempo_atual_calcada = 0
            else:
                # Já estava na calçada, atualiza o tempo
                self.tempo_atual_calcada = tempo_atual - self.tempo_entrou_calcada
        else:
            # Não está na calçada, reseta o timer
            self.tempo_entrou_calcada = 0
            self.tempo_atual_calcada = 0

    def empurrar(self, direcao):
        self.empurrado = True
        self.direcao_empurrao = direcao
        self.tempo_inicio_empurrao = pygame.time.get_ticks()

    def draw(self, tela):
        if self.travado:
            sprite = self.sprite_travado
            if self.olhando_esquerda:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, (self.x, self.y))
        else:
            if self.animando:
                frame = self.frames[self.frame_atual]
                if self.olhando_esquerda:
                    frame = pygame.transform.flip(frame, True, False)
                tela.blit(frame, (self.x, self.y))
            else:
                sprite = self.sprite_parado
                if self.olhando_esquerda:
                    sprite = pygame.transform.flip(sprite, True, False)
                tela.blit(sprite, (self.x, self.y))

    def reset(self):
        self.x = 50
        self.y = ALTURA - ALTURA_RET - 30
        self.travado = False
        self.empurrado = False
        self.invencivel = False

        # Reset do timer da calçada
        self.na_calcada = False
        self.tempo_entrou_calcada = 0
        self.tempo_atual_calcada = 0