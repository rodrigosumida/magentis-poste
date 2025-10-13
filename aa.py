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
        
        # --- NOVO: Sistema de penalidades ---
        self.falhas_radar = 0
        self.game_over_por_radar = False
        
        # Criar primeiro obstáculo
        self.criar_obstaculo_inicial()

    def carregar_fundo(self):
        try:
            fundo = pygame.image.load("fundo.jpg")
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
                    # Agora usa o novo método desativar que não conta como falha
                    self.radar.desativar()
        return True

    def update(self):
        teclas = pygame.key.get_pressed()
        
        # Se game over por radar, não atualiza nada
        if self.game_over_por_radar:
            return
        
        # Atualizar tempo
        if not self.player.travado:
            self.tempo_decorrido = (pygame.time.get_ticks() - self.tempo_inicial) // 1000

        # Atualizar player
        self.player.update(teclas)
        personagem_rect = self.player.get_rect()

        # Verificar colisões (só se não estiver em game over)
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
        
        # --- NOVO: Atualizar radar e verificar penalidades ---
        if self.radar.update():  # Retorna True se expirou
            self.falhas_radar += 1
            print(f"Radar falhou! Falhas: {self.falhas_radar}/{MAX_FALHAS_RADAR}")
            
            # Verificar game over
            if self.falhas_radar >= MAX_FALHAS_RADAR:
                self.game_over_por_radar = True
                print("GAME OVER por excesso de falhas no radar!")
        
        # Aumentar velocidade
        self.aumentar_velocidade()
        
        # Atualizar fundo
        if not self.player.travado:
            self.fundo_y += VELOCIDADE_FUNDO
            if self.fundo_y >= ALTURA:
                self.fundo_y = 0

    # ... (mantenha os outros métodos spawn_*)

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

        # --- NOVO: Desenhar sistema de penalidades ---
        self.desenhar_penalidades()

        # --- NOVO: Desenhar mensagem de game over se necessário ---
        if self.game_over_por_radar:
            self.desenhar_game_over_radar()

        # Desenhar player
        self.player.draw(self.tela)

        pygame.display.flip()

    def desenhar_penalidades(self):
        """Desenha os ícones de penalidade (vidas) do radar"""
        x, y = POSICAO_PENALIDADES
        tamanho = TAMANHO_ICONE_PENALIDADE
        espacamento = ESPACAMENTO_PENALIDADES
        
        for i in range(MAX_FALHAS_RADAR):
            # Cor depende se já falhou ou não
            if i < self.falhas_radar:
                cor = COR_PENALIDADE_ATIVA  # Vermelho - já falhou
            else:
                cor = COR_PENALIDADE_INATIVA  # Cinza - ainda disponível
            
            # Desenhar ícone (pode ser um círculo ou um ícone personalizado)
            pygame.draw.circle(self.tela, cor, (x, y), tamanho // 2)
            pygame.draw.circle(self.tela, (255, 255, 255), (x, y), tamanho // 2, 2)
            
            # Mover para a próxima posição
            x += tamanho + espacamento
        
        # Opcional: desenhar texto informativo
        texto_penalidades = self.font.render(f"{self.falhas_radar}/{MAX_FALHAS_RADAR}", True, (255, 255, 255))
        self.tela.blit(texto_penalidades, (POSICAO_PENALIDADES[0], POSICAO_PENALIDADES[1] + TAMANHO_ICONE_PENALIDADE + 5))

    def desenhar_game_over_radar(self):
        """Desenha a mensagem de game over por falhas no radar"""
        # Fundo semi-transparente
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        
        # Texto principal
        fonte_grande = pygame.font.SysFont(None, 72)
        texto_game_over = fonte_grande.render("GAME OVER", True, (255, 0, 0))
        texto_rect = texto_game_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
        self.tela.blit(texto_game_over, texto_rect)
        
        # Texto explicativo
        fonte_media = pygame.font.SysFont(None, 48)
        texto_motivo = fonte_media.render("Muitas falhas no radar!", True, (255, 255, 255))
        texto_motivo_rect = texto_motivo.get_rect(center=(LARGURA // 2, ALTURA // 2 + 20))
        self.tela.blit(texto_motivo, texto_motivo_rect)
        
        # Instrução para reiniciar
        fonte_pequena = pygame.font.SysFont(None, 36)
        texto_reiniciar = fonte_pequena.render("Pressione R para reiniciar", True, (200, 200, 200))
        texto_reiniciar_rect = texto_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 80))
        self.tela.blit(texto_reiniciar, texto_reiniciar_rect)

    def reset_game(self):
        """Reinicia o jogo completamente"""
        self.player.reset()
        self.obstaculos.clear()
        self.velocidade_atual = VELOCIDADE_INICIAL
        self.criar_obstaculo_inicial()
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0
        self.fundo_y = 0
        self.radar.visivel = False
        
        # --- NOVO: Reset das penalidades ---
        self.falhas_radar = 0
        self.game_over_por_radar = False

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)