import pygame
import random
from config import *
from player import Player
from obstacle import Obstaculo
from radar import Radar

class Game:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("CORITIBA")
        self.clock = pygame.time.Clock()
        
        # Carregar fundo
        self.fundo = self.carregar_fundo()
        self.fundo_y = 0
        
        # Inicializar sistemas
        self.player = Player()
        self.radar = Radar()
        self.obstaculos = []
        
        # Controle de tempo
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0
        
        # Controle de spawn
        self.ultimo_spawn = pygame.time.get_ticks()
        self.intervalo_spawn = random.randint(INTERVALO_SPAWN_MIN, INTERVALO_SPAWN_MAX)
        self.ultimo_poste = pygame.time.get_ticks()
        
        # Velocidade do jogo
        self.velocidade_atual = VELOCIDADE_INICIAL
        
        # Fonte
        self.font = pygame.font.SysFont(None, 40)
        
        # Criar primeiro obstáculo
        self.criar_obstaculo_inicial()

    def carregar_fundo(self):
        try:
            fundo = pygame.image.load("assets/fundo.jpg")
            return pygame.transform.scale(fundo, (LARGURA, ALTURA))
        except:
            # Fallback: fundo azul
            fundo = pygame.Surface((LARGURA, ALTURA))
            fundo.fill((0, 100, 200))
            return fundo

    def criar_obstaculo_inicial(self):
        inicio = MARGEM_LATERAL
        fim = LARGURA - MARGEM_LATERAL - 100
        self.obstaculos.append(Obstaculo("carro", random.randint(inicio, fim), -100, self.velocidade_atual))

    def handle_events(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    self.reset_game()
                if evento.key == pygame.K_u:
                    self.player.invencivel = not self.player.invencivel
                if evento.key == pygame.K_s and self.radar.visivel:
                    self.radar.visivel = False
        return True

    def update(self):
        teclas = pygame.key.get_pressed()
        
        # Atualizar tempo
        if not self.player.travado:
            self.tempo_decorrido = (pygame.time.get_ticks() - self.tempo_inicial) // 1000

        # Atualizar player
        self.player.update(teclas)
        personagem_rect = self.player.get_rect()

        # Verificar colisões
        if not self.player.travado and not self.player.invencivel:
            for ob in self.obstaculos:
                if personagem_rect.colliderect(ob.rect):
                    if ob.tipo == "buraco":
                        self.player.empurrar(random.choice([-1, 1]))
                    else:
                        self.player.travado = True
                    break

        # Atualizar obstáculos
        for ob in self.obstaculos[:]:
            ob.mover()
            if ob.tipo == "cachorro":
                ob.update_seguir(personagem_rect)
            
            # Remover se saiu da tela
            if ob.rect.top > ALTURA:
                self.obstaculos.remove(ob)

        # Spawn de obstáculos
        self.spawn_obstaculos()
        
        # Spawn de pessoas
        self.spawn_pessoas()
        
        # Spawn de cachorros
        self.spawn_cachorros()
        
        # Spawn de buracos
        self.spawn_buracos()
        
        # Spawn de postes
        self.spawn_postes()
        
        # Spawn de radar
        self.spawn_radar()
        
        # Atualizar radar
        self.radar.update()
        
        # Aumentar velocidade
        self.aumentar_velocidade()
        
        # Atualizar fundo
        if not self.player.travado:
            self.fundo_y += VELOCIDADE_FUNDO
            if self.fundo_y >= ALTURA:
                self.fundo_y = 0

    def spawn_obstaculos(self):
        if self.player.travado or len(self.obstaculos) >= MAX_OBSTACULOS:
            return

        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.ultimo_spawn > self.intervalo_spawn:
            qtd_novos = random.randint(1, 3)
            
            for _ in range(qtd_novos):
                if len(self.obstaculos) < MAX_OBSTACULOS:
                    inicio = MARGEM_LATERAL
                    fim = LARGURA - MARGEM_LATERAL - 100

                    if random.random() < 0.2:
                        self.obstaculos.append(Obstaculo("caminhao", random.randint(inicio, fim), -150, self.velocidade_atual))
                    else:
                        self.obstaculos.append(Obstaculo("carro", random.randint(inicio, fim), -100, self.velocidade_atual))

            self.ultimo_spawn = tempo_atual
            self.intervalo_spawn = random.randint(INTERVALO_SPAWN_MIN, INTERVALO_SPAWN_MAX)

    def spawn_pessoas(self):
        if not self.player.travado and random.random() < CHANCE_ROXO:
            lado = random.choice(["esquerda", "direita"])
            if lado == "esquerda":
                x_pos = random.randint(0, MARGEM_LATERAL - 30)
            else:
                x_pos = random.randint(LARGURA - MARGEM_LATERAL, LARGURA - 30)

            self.obstaculos.append(Obstaculo("pessoa", x_pos, -30, self.velocidade_atual))

    def spawn_cachorros(self):
        if not self.player.travado and random.random() < CHANCE_CACHORRO:
            lado = random.choice(["esquerda", "direita"])
            if lado == "esquerda":
                x_pos = random.randint(0, MARGEM_LATERAL - 50)
            else:
                x_pos = random.randint(LARGURA - MARGEM_LATERAL, LARGURA - 50)

            self.obstaculos.append(Obstaculo("cachorro", x_pos, -30, self.velocidade_atual))

    def spawn_buracos(self):
        if random.random() < CHANCE_BURACO:
            inicio = MARGEM_LATERAL
            fim = LARGURA - MARGEM_LATERAL - 100
            self.obstaculos.append(Obstaculo("buraco", random.randint(inicio, fim), -90, self.velocidade_atual))

    def spawn_postes(self):
        if not self.player.travado:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_poste > INTERVALO_POSTES:
                # Poste da esquerda
                self.obstaculos.append(Obstaculo("poste", 0, -30, self.velocidade_atual))
                # Poste da direita
                self.obstaculos.append(Obstaculo("poste", LARGURA - 60, -30, self.velocidade_atual))
                self.ultimo_poste = tempo_atual

    def spawn_radar(self):
        if not self.radar.visivel and random.random() < PROBABILIDADE_RADAR:
            self.radar.ativar()

    def aumentar_velocidade(self):
        if self.tempo_decorrido - self.tempo_ultimo_aumento >= INTERVALO_AUMENTO:
            self.velocidade_atual = min(self.velocidade_atual + INCREMENTO_VEL, VEL_MAXIMA)
            for ob in self.obstaculos:
                ob.velocidade = self.velocidade_atual
            self.tempo_ultimo_aumento = self.tempo_decorrido

    def draw(self):
        # Desenhar fundo
        self.tela.blit(self.fundo, (0, self.fundo_y))
        self.tela.blit(self.fundo, (0, self.fundo_y - ALTURA))

        # Desenhar margens
        superficie_margem = pygame.Surface((MARGEM_LATERAL, ALTURA), pygame.SRCALPHA)
        superficie_margem.fill((200, 200, 200, 100))
        self.tela.blit(superficie_margem, (0, 0))
        self.tela.blit(superficie_margem, (LARGURA - MARGEM_LATERAL, 0))

        # Desenhar obstáculos
        for ob in self.obstaculos:
            ob.draw(self.tela)

        # Desenhar radar
        self.radar.draw(self.tela)

        # Desenhar tempo
        tempo_texto = self.font.render(f"Tempo: {self.tempo_decorrido}s", True, (255, 255, 255))
        self.tela.blit(tempo_texto, (LARGURA // 2 - tempo_texto.get_width() // 2, 10))

        # Desenhar player
        self.player.draw(self.tela)

        pygame.display.flip()

    def reset_game(self):
        self.player.reset()
        self.obstaculos.clear()
        self.velocidade_atual = VELOCIDADE_INICIAL
        self.criar_obstaculo_inicial()
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0
        self.fundo_y = 0
        self.radar.visivel = False

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)