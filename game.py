import pygame
import random
from config import *
from player import Player
from obstacle import Obstaculo
from radar import Radar
from fases import get_config_fase

class Game:
    def __init__(self, numero_fase=1):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("MAGENTTIS POSTE")
        self.clock = pygame.time.Clock()

        # Carregar configuração da fase
        self.config_fase = get_config_fase(numero_fase)
        self.numero_fase = numero_fase
        
        # Carregar fundo
        self.fundo = self.carregar_fundo()
        self.fundo_y = 0
        
        # Inicializar sistemas
        self.player = Player()
        self.radar = Radar(self.config_fase["tempo_maximo_radar"])
        self.obstaculos = []
        
        # Controle de tempo
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0
        
        # Controle de spawn
        self.ultimo_spawn = pygame.time.get_ticks()
        self.intervalo_spawn = random.randint(
            self.config_fase["intervalo_spawn_min"], 
            self.config_fase["intervalo_spawn_max"]
        )
        self.ultimo_poste = pygame.time.get_ticks()
        
        # Velocidade do jogo
        self.velocidade_atual = self.config_fase["velocidade_inicial"]
        
        # Fonte
        self.font = pygame.font.SysFont(None, 40)

        # Penalidades
        self.falhas_radar = 0
        self.game_over_por_radar = False
        self.game_over_por_colisao = False
        self.obstaculo_culpado = None

        # Penalidades por ficar na calçada
        self.penalidade_calcada_aplicada = False  # Evita aplicar múltiplas penalidades seguidas

        # Info da fase na tela
        self.fonte_pequena = pygame.font.SysFont(None, 24)

        # Carregar imagens dos corações uma vez
        self.coracao_cheio = None
        self.coracao_quebrado = None
        self.carregar_imagens_coracoes()
        
        # NOVO: Sistema de vitória
        self.vitoria = False
        self.mostrar_tela_vitoria = False
        self.dinheiro_ganho = 0
        self.bonus_tempo = 0
        
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
        
        # NOVO: Verificar vitória (sobreviver por tempo suficiente)
        tempo_para_vitoria = 120  # 2 minutos para vencer uma fase
        if not self.vitoria and self.tempo_decorrido >= tempo_para_vitoria:
            self.vitoria = True
            self.processar_vitoria()
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
            self.player.tempo_atual_calcada >= self.config_fase["tempo_maximo_calcada"]):
            
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

    # NOVO: Método para verificar se um obstáculo está ativo na fase
    def obstaculo_esta_ativo(self, tipo_obstaculo):
        return tipo_obstaculo in self.config_fase["obstaculos_ativos"]

    def spawn_obstaculos(self):
        if self.player.travado or len(self.obstaculos) >= self.config_fase["max_obstaculos"]:
            return

        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.ultimo_spawn > self.intervalo_spawn:
            qtd_novos = random.randint(1, 3)
            
            for _ in range(qtd_novos):
                if len(self.obstaculos) < self.config_fase["max_obstaculos"]:
                    inicio = MARGEM_LATERAL
                    fim = LARGURA - MARGEM_LATERAL - 100

                    # Tentar encontrar uma posição sem colisão
                    tentativas = 0
                    while tentativas < 10:
                        x_pos = random.randint(inicio, fim)
                        
                        # NOVO: Escolher tipo baseado nas chances da fase
                        if random.random() < self.config_fase["chance_caminhao"] and self.obstaculo_esta_ativo("caminhao"):
                            temp_rect = pygame.Rect(x_pos, -150, 80, 150)
                            tipo = "caminhao"
                        elif self.obstaculo_esta_ativo("carro"):
                            temp_rect = pygame.Rect(x_pos, -100, 77, 110)
                            tipo = "carro"
                        else:
                            break
                        
                        # Verificar colisão
                        colisao = False
                        for ob in self.obstaculos:
                            if ob.tipo in ["carro", "caminhao"] and temp_rect.colliderect(ob.rect):
                                colisao = True
                                break
                        
                        if not colisao:
                            self.obstaculos.append(Obstaculo(tipo, x_pos, -100 if tipo == "carro" else -150, self.velocidade_atual))
                            break
                        
                        tentativas += 1

            self.ultimo_spawn = tempo_atual
            self.intervalo_spawn = random.randint(
                self.config_fase["intervalo_spawn_min"], 
                self.config_fase["intervalo_spawn_max"]
            )

    def spawn_pessoas(self):
        if (not self.player.travado and 
            random.random() < self.config_fase["chance_pessoa"] and 
            self.obstaculo_esta_ativo("pessoa")):
            
            lado = random.choice(["esquerda", "direita"])
            if lado == "esquerda":
                x_pos = random.randint(0, MARGEM_LATERAL - 30)
            else:
                x_pos = random.randint(LARGURA - MARGEM_LATERAL, LARGURA - 30)

            self.obstaculos.append(Obstaculo("pessoa", x_pos, -30, self.velocidade_atual))

    def spawn_cachorros(self):
        if (not self.player.travado and 
            random.random() < self.config_fase["chance_cachorro"] and 
            self.obstaculo_esta_ativo("cachorro")):
            
            lado = random.choice(["esquerda", "direita"])
            if lado == "esquerda":
                x_pos = random.randint(0, MARGEM_LATERAL - 50)
            else:
                x_pos = random.randint(LARGURA - MARGEM_LATERAL, LARGURA - 50)

            self.obstaculos.append(Obstaculo("cachorro", x_pos, -30, self.velocidade_atual))

    def spawn_buracos(self):
        if (random.random() < self.config_fase["chance_buraco"] and 
            self.obstaculo_esta_ativo("buraco")):
            
            inicio = MARGEM_LATERAL
            fim = LARGURA - MARGEM_LATERAL - 100
            self.obstaculos.append(Obstaculo("buraco", random.randint(inicio, fim), -90, self.velocidade_atual))

    def spawn_postes(self):
        if (not self.player.travado and 
            self.obstaculo_esta_ativo("poste")):
            
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_poste > self.config_fase["intervalo_postes"]:
                # Poste da esquerda
                self.obstaculos.append(Obstaculo("poste", 0, -30, self.velocidade_atual))
                # Poste da direita
                self.obstaculos.append(Obstaculo("poste", LARGURA - 60, -30, self.velocidade_atual))
                self.ultimo_poste = tempo_atual

    def spawn_radar(self):
        if (not self.radar.visivel and 
            random.random() < self.config_fase["probabilidade_radar"]):
            self.radar.ativar()

    def aumentar_velocidade(self):
        if self.tempo_decorrido - self.tempo_ultimo_aumento >= self.config_fase["intervalo_aumento"]:
            self.velocidade_atual = min(
                self.velocidade_atual + self.config_fase["incremento_vel"], 
                self.config_fase["vel_maxima"]
            )
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
        self.tela.blit(tempo_texto, (LARGURA//2 - tempo_texto.get_width()//2, 10))

        # NOVO: Info da fase
        fase_texto = self.fonte_pequena.render(f"Fase {self.numero_fase}", True, (200, 200, 200))
        self.tela.blit(fase_texto, (20, 20))

        velocidade_texto = self.fonte_pequena.render(f"Vel: {self.velocidade_atual * 10} km/h", True, (200, 200, 200))
        self.tela.blit(velocidade_texto, (20, 50))

        # Desenhar timer da calçada
        self.desenhar_timer_calcada()

        # Desenhar sistema de penalidades
        self.desenhar_penalidades()

        # Desenhar mensagem de game over apropriada
        if self.game_over_por_radar:
            self.desenhar_game_over_radar()
        elif self.game_over_por_colisao:
            self.desenhar_game_over_colisao()

        # Desenhar player
        self.player.draw(self.tela)

        pygame.display.flip()
    
    # Método para desenhar o timer da calçada
    def desenhar_timer_calcada(self):
        """Desenha a barra de tempo indicando quanto tempo falta para penalidade na calçada"""
        if self.player.na_calcada and not self.player.travado and not self.penalidade_calcada_aplicada:
            tempo_restante = max(0, self.config_fase["tempo_maximo_calcada"] - self.player.tempo_atual_calcada)
            progresso = tempo_restante / self.config_fase["tempo_maximo_calcada"]
            
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

    def carregar_imagens_coracoes(self):
        """Carrega as imagens dos corações uma vez no início"""
        try:
            self.coracao_cheio = pygame.image.load(IMAGEM_CORACAO_CHEIO).convert_alpha()
            self.coracao_quebrado = pygame.image.load(IMAGEM_CORACAO_QUEBRADO).convert_alpha()
            
            # Redimensionar se necessário
            tamanho = TAMANHO_ICONE_PENALIDADE
            self.coracao_cheio = pygame.transform.scale(self.coracao_cheio, (tamanho, tamanho))
            self.coracao_quebrado = pygame.transform.scale(self.coracao_quebrado, (tamanho, tamanho))
        except Exception as e:
            print(f"Erro ao carregar imagens dos corações: {e}")
            self.coracao_cheio = None
            self.coracao_quebrado = None

    def desenhar_penalidades(self):
        """Desenha os ícones de penalidade (corações) do radar"""
        x, y = POSICAO_PENALIDADES
        tamanho = TAMANHO_ICONE_PENALIDADE
        espacamento = ESPACAMENTO_PENALIDADES
        
        # Verificar se as imagens carregaram
        if self.coracao_cheio is None or self.coracao_quebrado is None:
            self.desenhar_penalidades_fallback(x, y, tamanho, espacamento)
            return
    
        for i in range(MAX_FALHAS_RADAR):
            # Escolher a imagem baseado se já falhou ou não
            if i < self.falhas_radar:
                imagem = self.coracao_quebrado  # Coração quebrado - já falhou
            else:
                imagem = self.coracao_cheio     # Coração cheio - ainda disponível
            
            # Desenhar a imagem do coração
            self.tela.blit(imagem, (x, y))
            
            # Mover para a próxima posição
            x += tamanho + espacamento
        
        # Texto informativo
        texto_penalidades = self.font.render(f"{self.falhas_radar}/{MAX_FALHAS_RADAR}", True, (255, 255, 255))
        self.tela.blit(texto_penalidades, (POSICAO_PENALIDADES[0], POSICAO_PENALIDADES[1] + TAMANHO_ICONE_PENALIDADE + 5))

    def desenhar_penalidades_fallback(self, x, y, tamanho, espacamento):
        """Método fallback caso as imagens não carreguem"""
        for i in range(MAX_FALHAS_RADAR):
            # Cor depende se já falhou ou não
            if i < self.falhas_radar:
                cor = COR_PENALIDADE_ATIVA  # Vermelho - já falhou
            else:
                cor = COR_PENALIDADE_INATIVA  # Cinza - ainda disponível
            
            # Desenhar círculo (fallback)
            pygame.draw.circle(self.tela, cor, (x + tamanho//2, y + tamanho//2), tamanho // 2)
            pygame.draw.circle(self.tela, (255, 255, 255), (x + tamanho//2, y + tamanho//2), tamanho // 2, 2)
            
            # Mover para a próxima posição
            x += tamanho + espacamento
        
        # Texto informativo
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
    
    # NOVO: Adicione este método ao Game
    def processar_vitoria(self):
        """Processa a vitória da fase e calcula recompensas"""
        from fases import get_config_fase
        config = get_config_fase(self.numero_fase)
        
        # Calcular recompensa
        recompensa_base = config["recompensa"]
        bonus_tempo = 0
        
        # Bônus por completar rápido
        if self.tempo_decorrido <= config["tempo_bonus"]:
            bonus_tempo = config["bonus_tempo"]
        
        dinheiro_total = recompensa_base + bonus_tempo
        
        # Salvar no sistema de save
        from save_system import SaveSystem
        save_system = SaveSystem()
        save_system.completar_fase(self.numero_fase, self.tempo_decorrido, dinheiro_total)
        
        # Mostrar tela de vitória
        self.mostrar_tela_vitoria = True
        self.dinheiro_ganho = dinheiro_total
        self.bonus_tempo = bonus_tempo

    def reset_game(self):
        """Reinicia o jogo mantendo a mesma fase"""
        self.player.reset()
        self.obstaculos.clear()
        self.velocidade_atual = self.config_fase["velocidade_inicial"]
        self.criar_obstaculo_inicial()
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_decorrido = 0
        self.tempo_ultimo_aumento = 0
        self.fundo_y = 0
        self.radar.visivel = False
        
        # Reset das penalidades
        self.falhas_radar = 0
        self.game_over_por_radar = False
        self.game_over_por_colisao = False
        self.obstaculo_culpado = None
        self.penalidade_calcada_aplicada = False

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if not self.mostrar_tela_vitoria:
                self.update()
            
            self.draw()
            
            # NOVO: Se vitória, mostrar tela especial
            if self.mostrar_tela_vitoria:
                from menu import Menu
                menu = Menu()
                acao = menu.mostrar_vitoria_fase(self.numero_fase, self.tempo_decorrido, 
                                            self.dinheiro_ganho, self.bonus_tempo)
                
                if acao == "proxima":
                    # Ir para próxima fase
                    from fases import get_total_fases
                    total_fases = get_total_fases()
                    if self.numero_fase < total_fases:
                        return self.numero_fase + 1  # Indica para carregar próxima fase
                    else:
                        return "menu"
                else:
                    return "menu"  # Voltar ao menu
            
            self.clock.tick(60)
        
        return "menu"