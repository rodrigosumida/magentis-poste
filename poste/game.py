import pygame
import sys
import random
from config import *
from jogador import Jogador
from obstaculo import Obstaculo

class Game:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("CORITIBA")
        self.clock = pygame.time.Clock()

        # Fundo
        self.fundo = pygame.image.load("poste/assets/fundo.jpg")
        self.fundo = pygame.transform.scale(self.fundo, (LARGURA, ALTURA))

        # Jogador
        self.jogador = Jogador(50, ALTURA - JOGADOR_ALT - 30)

        # Obstáculos
        self.obstaculos = []
        self.vel_atual = VEL_INICIAL
        self.ultimo_spawn = pygame.time.get_ticks()
        self.intervalo_spawn = random.randint(INTERVALO_SPAWN_MIN, INTERVALO_SPAWN_MAX)
        self.ultimo_poste = pygame.time.get_ticks()

        # Tempo
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0
        self.font = pygame.font.SysFont(None, 40)

        # Estado inicial
        self.resetar()

    def resetar(self):
        self.jogador.travado = False
        self.obstaculos.clear()
        self.vel_atual = VEL_INICIAL
        inicio = MARGEM_LATERAL
        fim = LARGURA - MARGEM_LATERAL - 100
        self.obstaculos.append(Obstaculo(random.randint(inicio, fim), -100, 100, 100, (255, 0, 0), self.vel_atual))
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0

    def atualizar(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.atualizar_animacao()

        # Atualizar tempo
        if not self.jogador.travado:
            self.tempo_decorrido = (pygame.time.get_ticks() - self.tempo_inicial) // 1000

        # Colisões
        if not self.jogador.travado and not self.jogador.invencivel:
            for ob in self.obstaculos:
                if self.jogador.rect.colliderect(ob.rect):
                    self.jogador.travado = True
                    break

        # Obstáculos
        for ob in self.obstaculos[:]:
            ob.mover()
            if ob.rect.top > ALTURA:
                self.obstaculos.remove(ob)

        self._spawn_obstaculos()
        self._spawn_postes()
        self._aumentar_velocidade()

    def _spawn_obstaculos(self):
        agora = pygame.time.get_ticks()
        if not self.jogador.travado and len(self.obstaculos) < MAX_OBSTACULOS:
            if agora - self.ultimo_spawn > self.intervalo_spawn:
                for _ in range(random.randint(1, 3)):
                    if len(self.obstaculos) < MAX_OBSTACULOS:
                        largura = 100
                        inicio = MARGEM_LATERAL
                        fim = LARGURA - MARGEM_LATERAL - largura
                        x = random.randrange(inicio, fim, largura + 20)

                        if random.random() < 0.2:
                            self.obstaculos.append(Obstaculo(x, -120, 130, 130, (0, 0, 255), self.vel_atual, True))
                        else:
                            self.obstaculos.append(Obstaculo(x, -100, largura, largura, (255, 0, 0), self.vel_atual))

                self.ultimo_spawn = agora
                self.intervalo_spawn = random.randint(INTERVALO_SPAWN_MIN, INTERVALO_SPAWN_MAX)

        # Pessoas roxas
        if not self.jogador.travado and random.random() < CHANCE_ROXO:
            lado = random.choice(["esquerda", "direita"])
            if lado == "esquerda":
                x = random.randint(0, MARGEM_LATERAL - ROXO_LARG)
            else:
                x = random.randint(LARGURA - MARGEM_LATERAL, LARGURA - ROXO_LARG)
            self.obstaculos.append(Obstaculo(x, -ROXO_ALT, ROXO_LARG, ROXO_ALT, (128, 0, 128), self.vel_atual, True))

    def _spawn_postes(self):
        agora = pygame.time.get_ticks()
        if not self.jogador.travado and agora - self.ultimo_poste > INTERVALO_POSTES:
            largura, altura = 30, 30
            self.obstaculos.append(Obstaculo(0, -altura, largura, altura, (255, 255, 0), self.vel_atual))
            self.obstaculos.append(Obstaculo(LARGURA - largura, -altura, largura, altura, (255, 255, 0), self.vel_atual))
            self.ultimo_poste = agora

    def _aumentar_velocidade(self):
        if self.tempo_decorrido - self.tempo_ultimo_aumento >= INTERVALO_AUMENTO:
            self.vel_atual = min(self.vel_atual + VEL_INCREMENTO, VEL_MAX)
            for ob in self.obstaculos:
                ob.velocidade = self.vel_atual
            self.tempo_ultimo_aumento = self.tempo_decorrido

    def desenhar(self):
        self.tela.blit(self.fundo, (0, 0))

        # Margens laterais
        margem = pygame.Surface((MARGEM_LATERAL, ALTURA), pygame.SRCALPHA)
        margem.fill((200, 200, 200, 100))
        self.tela.blit(margem, (0, 0))
        self.tela.blit(margem, (LARGURA - MARGEM_LATERAL, 0))

        # Obstáculos
        for ob in self.obstaculos:
            ob.desenhar(self.tela)

        # Tempo
        tempo_texto = self.font.render(f"Tempo: {self.tempo_decorrido}s", True, (255, 255, 255))
        self.tela.blit(tempo_texto, (LARGURA // 2 - tempo_texto.get_width() // 2, 10))

        # Jogador
        self.jogador.desenhar(self.tela)

        pygame.display.flip()

    def rodar(self):
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        self.resetar()
                    if evento.key == pygame.K_u:
                        self.jogador.invencivel = not self.jogador.invencivel

            self.atualizar()
            self.desenhar()
            self.clock.tick(FPS)
