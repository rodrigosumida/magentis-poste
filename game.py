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

        # Penalidades
        self.falhas_radar = 0
        self.game_over_por_radar = False
        self.game_over_por_colisao = False
        self.obstaculo_culpado = None

        # Penalidades por ficar na calçada
        self.penalidade_calcada_aplicada = False  # Evita aplicar múltiplas penalidades seguidas
        
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
                    if not self.game_over_por_radar and not self.game_over_por_colisao:
                        self.player.invencivel = not self.player.invencivel
                if evento.key == pygame.K_s and self.radar.visivel:
                    if not self.game_over_por_radar and not self.game_over_por_colisao:
                        self.radar.desativar()
        return True

    def update(self):
        teclas = pygame.key.get_pressed()
        
        # Se estiver em qualquer tipo de game over, não atualiza a gameplay
        if self.game_over_por_radar or self.game_over_por_colisao:
            return
        
        # Atualizar tempo
        if not self.player.travado:
            self.tempo_decorrido = (pygame.time.get_ticks() - self.tempo_inicial) // 1000

        # Atualizar player
        self.player.update(teclas)
        personagem_rect = self.player.get_rect()

        # Verificar penalidade por calçada
        self.verificar_penalidade_calcada()

        # Verificar colisões
        if not self.player.travado and not self.player.invencivel:
            for ob in self.obstaculos:
                if personagem_rect.colliderect(ob.rect):
                    if ob.tipo == "buraco":
                        self.player.empurrar(random.choice([-1, 1]))
                    else:
                        self.player.travado = True
                        self.game_over_por_colisao = True
                        self.obstaculo_culpado = ob.tipo
                    break

        # NOVO: Calcular velocidade do fundo para os buracos
        velocidade_fundo_atual = VELOCIDADE_FUNDO if not self.player.travado else 0

        # Atualizar obstáculos
        for ob in self.obstaculos[:]:
            # NOVO: Passar a lista de outros obstáculos para verificação de colisão
            if ob.tipo == "buraco":
                ob.mover(velocidade_fundo_atual)  # Buraco se move com o fundo
            else:
                ob.mover(None, self.obstaculos)  # Outros obstáculos recebem a lista de obstáculos
                
            if ob.tipo == "cachorro":
                ob.update_seguir(personagem_rect)
            
            # Remover se saiu da tela
            if ob.rect.top > ALTURA:
                self.obstaculos.remove(ob)

        # Spawn de obstáculos (só se não estiver em game over)
        if not self.game_over_por_colisao and not self.game_over_por_radar:
            self.spawn_obstaculos()
            self.spawn_pessoas()
            self.spawn_cachorros()
            self.spawn_buracos()
            self.spawn_postes()
            self.spawn_radar()
        
        # Atualizar radar e verificar penalidades
        if self.radar.update():  # Retorna True se expirou
            self.falhas_radar += 1
            print(f"Radar falhou! Falhas: {self.falhas_radar}/{MAX_FALHAS_RADAR}")
            
            # Verificar game over
            if self.falhas_radar >= MAX_FALHAS_RADAR:
                self.game_over_por_radar = True
                print("GAME OVER por excesso de falhas no radar!")
        
        # Aumentar velocidade (só se não estiver em game over)
        if not self.game_over_por_colisao and not self.game_over_por_radar:
            self.aumentar_velocidade()
        
        # Atualizar fundo (só se não estiver em game over)
        if not self.player.travado and not self.game_over_por_colisao and not self.game_over_por_radar:
            self.fundo_y += VELOCIDADE_FUNDO
            if self.fundo_y >= ALTURA:
                self.fundo_y = 0
    
    # Método para verificar penalidade da calçada
    def verificar_penalidade_calcada(self):
        """Verifica se o jogador ficou tempo suficiente na calçada para receber penalidade"""
        if (self.player.na_calcada and 
            not self.player.travado and 
            not self.penalidade_calcada_aplicada and
            self.player.tempo_atual_calcada >= TEMPO_MAXIMO_CALCADA):
            
            self.falhas_radar += 1
            self.penalidade_calcada_aplicada = True
            print(f"Penalidade por calçada! Falhas: {self.falhas_radar}/{MAX_FALHAS_RADAR}")
            
            # Verificar game over
            if self.falhas_radar >= MAX_FALHAS_RADAR:
                self.game_over_por_radar = True
                print("GAME OVER por excesso de penalidades!")
        
        # Reset da flag quando sair da calçada
        if not self.player.na_calcada:
            self.penalidade_calcada_aplicada = False

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

                    # NOVO: Tentar encontrar uma posição sem colisão
                    tentativas = 0
                    while tentativas < 10:  # Máximo de 10 tentativas
                        x_pos = random.randint(inicio, fim)
                        
                        # Criar um retângulo temporário para verificar colisão
                        if random.random() < 0.2:
                            temp_rect = pygame.Rect(x_pos, -150, 80, 150)  # Caminhão
                        else:
                            temp_rect = pygame.Rect(x_pos, -100, 77, 110)  # Carro
                        
                        # Verificar colisão com obstáculos existentes
                        colisao = False
                        for ob in self.obstaculos:
                            if ob.tipo in ["carro", "caminhao"] and temp_rect.colliderect(ob.rect):
                                colisao = True
                                break
                        
                        if not colisao:
                            # Posição válida, criar o obstáculo
                            if random.random() < 0.2:
                                self.obstaculos.append(Obstaculo("caminhao", x_pos, -150, self.velocidade_atual))
                            else:
                                self.obstaculos.append(Obstaculo("carro", x_pos, -100, self.velocidade_atual))
                            break
                        
                        tentativas += 1

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

        # Desenhar buracos primeiro (por baixo)
        for ob in self.obstaculos:
            if ob.tipo == "buraco":
                ob.draw(self.tela)

        # Desenhar outros obstáculos (por cima dos buracos)
        for ob in self.obstaculos:
            if ob.tipo != "buraco":
                ob.draw(self.tela)

        # Desenhar radar
        self.radar.draw(self.tela)

        # Desenhar tempo
        tempo_texto = self.font.render(f"Tempo: {self.tempo_decorrido}s", True, (255, 255, 255))
        self.tela.blit(tempo_texto, (LARGURA // 2 - tempo_texto.get_width() // 2, 10))

        # Desenhar timer da calçada
        self.desenhar_timer_calcada()

        # Desenhar sistema de penalidades
        self.desenhar_penalidades()

        # NOVO: Desenhar mensagem de game over apropriada
        if self.game_over_por_radar:
            self.desenhar_game_over_radar()
        elif self.game_over_por_colisao:
            self.desenhar_game_over_colisao()

        # Desenhar player (mesmo em game over, para mostrar a colisão)
        self.player.draw(self.tela)

        pygame.display.flip()
    
    # Método para desenhar o timer da calçada
    def desenhar_timer_calcada(self):
        """Desenha a barra de tempo indicando quanto tempo falta para penalidade na calçada"""
        if self.player.na_calcada and not self.player.travado and not self.penalidade_calcada_aplicada:
            tempo_restante = max(0, TEMPO_MAXIMO_CALCADA - self.player.tempo_atual_calcada)
            progresso = tempo_restante / TEMPO_MAXIMO_CALCADA
            
            # Tamanho e posição da barra
            barra_largura = 200
            barra_altura = 20
            x, y = POSICAO_TIMER_CALCADA
            
            # Cor da barra (amarelo -> vermelho)
            if progresso > 0.5:
                cor = (255, 255, 0)  # Amarelo
            elif progresso > 0.25:
                cor = (255, 165, 0)  # Laranja
            else:
                cor = (255, 0, 0)    # Vermelho
            
            # Desenhar barra de fundo
            pygame.draw.rect(self.tela, (50, 50, 50), (x, y, barra_largura, barra_altura))
            # Desenhar barra de progresso
            barra_preenchimento = int(barra_largura * progresso)
            pygame.draw.rect(self.tela, cor, (x, y, barra_preenchimento, barra_altura))
            # Borda
            pygame.draw.rect(self.tela, (255, 255, 255), (x, y, barra_largura, barra_altura), 2)
            
            # Texto
            texto_calcada = self.font.render("CALÇADA", True, COR_TIMER_CALCADA)
            self.tela.blit(texto_calcada, (x + barra_largura + 10, y))

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
        
        # Estatísticas
        fonte_pequena = pygame.font.SysFont(None, 36)
        texto_tempo = fonte_pequena.render(f"Tempo sobrevivido: {self.tempo_decorrido} segundos", True, (200, 200, 200))
        texto_tempo_rect = texto_tempo.get_rect(center=(LARGURA // 2, ALTURA // 2 + 70))
        self.tela.blit(texto_tempo, texto_tempo_rect)
        
        # Instrução para reiniciar
        texto_reiniciar = fonte_pequena.render("Pressione R para reiniciar", True, (200, 200, 200))
        texto_reiniciar_rect = texto_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 110))
        self.tela.blit(texto_reiniciar, texto_reiniciar_rect)
    
    def desenhar_game_over_colisao(self):
        """NOVO: Desenha a mensagem de game over por colisão com obstáculo"""
        # Fundo semi-transparente
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        
        # Texto principal
        fonte_grande = pygame.font.SysFont(None, 72)
        texto_game_over = fonte_grande.render("GAME OVER", True, (255, 0, 0))
        texto_rect = texto_game_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 80))
        self.tela.blit(texto_game_over, texto_rect)
        
        # Texto do motivo da colisão
        fonte_media = pygame.font.SysFont(None, 48)
        
        # Mensagem personalizada baseada no tipo de obstáculo
        if self.obstaculo_culpado == "carro":
            mensagem = "Você colidiu com um carro!"
            cor_mensagem = (255, 100, 100)
        elif self.obstaculo_culpado == "caminhao":
            mensagem = "Você colidiu com um caminhão!"
            cor_mensagem = (100, 100, 255)
        elif self.obstaculo_culpado == "pessoa":
            mensagem = "Você atropelou uma pessoa!"
            cor_mensagem = (200, 100, 200)
        elif self.obstaculo_culpado == "poste":
            mensagem = "Você bateu em um poste!"
            cor_mensagem = (255, 255, 100)
        elif self.obstaculo_culpado == "cachorro":
            mensagem = "Você atropelou um cachorro!"
            cor_mensagem = (255, 200, 100)
        else:
            mensagem = "Você colidiu com um obstáculo!"
            cor_mensagem = (255, 255, 255)
        
        texto_motivo = fonte_media.render(mensagem, True, cor_mensagem)
        texto_motivo_rect = texto_motivo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20))
        self.tela.blit(texto_motivo, texto_motivo_rect)
        
        # Estatísticas
        fonte_pequena = pygame.font.SysFont(None, 36)
        
        # Tempo sobrevivido
        texto_tempo = fonte_pequena.render(f"Tempo sobrevivido: {self.tempo_decorrido} segundos", True, (200, 200, 200))
        texto_tempo_rect = texto_tempo.get_rect(center=(LARGURA // 2, ALTURA // 2 + 20))
        self.tela.blit(texto_tempo, texto_tempo_rect)
        
        # Velocidade alcançada
        texto_velocidade = fonte_pequena.render(f"Velocidade máxima: {self.velocidade_atual * 10} km/h", True, (200, 200, 200))
        texto_velocidade_rect = texto_velocidade.get_rect(center=(LARGURA // 2, ALTURA // 2 + 60))
        self.tela.blit(texto_velocidade, texto_velocidade_rect)
        
        # Falhas no radar (se houver)
        if self.falhas_radar > 0:
            texto_falhas = fonte_pequena.render(f"Penalidades recebidas: {self.falhas_radar}", True, (255, 100, 100))
            texto_falhas_rect = texto_falhas.get_rect(center=(LARGURA // 2, ALTURA // 2 + 100))
            self.tela.blit(texto_falhas, texto_falhas_rect)
        
        # Instrução para reiniciar
        texto_reiniciar = fonte_pequena.render("Pressione R para reiniciar", True, (200, 200, 200))
        texto_reiniciar_rect = texto_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 140))
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
        
        # Reset das penalidades e estados de game over
        self.falhas_radar = 0
        self.game_over_por_radar = False
        self.game_over_por_colisao = False
        self.obstaculo_culpado = None

        # Reset da penalidade de calçada
        self.penalidade_calcada_aplicada = False

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)