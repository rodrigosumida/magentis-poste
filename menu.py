import pygame
import sys
from config import *
from save_system import SaveSystem

class Menu:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("MAGENTTIS POSTE - Menu")
        self.clock = pygame.time.Clock()

        # Sistema de save
        self.save_system = SaveSystem()
        
        # Cores
        self.cor_fundo = (30, 30, 60)
        self.cor_titulo = (255, 255, 0)
        self.cor_texto = (255, 255, 255)
        self.cor_destaque = (0, 200, 255)
        self.cor_botao = (50, 150, 50)
        self.cor_botao_hover = (70, 170, 70)
        
        # Fontes (AJUSTADAS para melhor espaçamento)
        self.fonte_titulo = pygame.font.SysFont("Arial", 60, bold=True)  # REDUZIDA
        self.fonte_subtitulo = pygame.font.SysFont("Arial", 30)  # REDUZIDA
        self.fonte_normal = pygame.font.SysFont("Arial", 24)  # REDUZIDA
        self.fonte_pequena = pygame.font.SysFont("Arial", 20)  # REDUZIDA
        self.fonte_muito_pequena = pygame.font.SysFont("Arial", 16)  # REDUZIDA
        self.fonte_minima = pygame.font.SysFont("Arial", 14)
        
        # Estado do menu
        self.fase_selecionada = 1
        self.total_fases = 5

    def desenhar_botao(self, texto, x, y, largura, altura, hover=False):
        """Desenha um botão com efeito hover"""
        cor = self.cor_botao_hover if hover else self.cor_botao
        pygame.draw.rect(self.tela, cor, (x, y, largura, altura), border_radius=10)
        pygame.draw.rect(self.tela, self.cor_texto, (x, y, largura, altura), 2, border_radius=10)
        
        texto_surf = self.fonte_normal.render(texto, True, self.cor_texto)
        texto_rect = texto_surf.get_rect(center=(x + largura//2, y + altura//2))
        self.tela.blit(texto_surf, texto_rect)
        
        return pygame.Rect(x, y, largura, altura)

    def desenhar_fase(self, numero_fase, x, y, largura, altura, selecionada=False, hover=False):
        """Desenha um card de fase - VERSÃO OTIMIZADA"""
        from fases import get_config_fase
        config = get_config_fase(numero_fase)

        # Verificar estado da fase
        fase_completa = self.save_system.get_fase_completa(numero_fase)
        fase_acessivel = self.save_system.get_fase_acessivel(numero_fase)
        melhor_tempo = self.save_system.get_melhor_tempo(numero_fase)
        
        # Cor do card
        if not fase_acessivel:
            cor_card = (30, 30, 30)
            cor_borda = (60, 60, 60)
        elif fase_completa:
            cor_card = (40, 80, 40)
            cor_borda = (100, 200, 100)
        elif selecionada:
            cor_card = (80, 80, 120)
            cor_borda = self.cor_destaque
        elif hover:
            cor_card = (60, 60, 100)
            cor_borda = self.cor_texto
        else:
            cor_card = (40, 40, 80)
            cor_borda = (100, 100, 100)
        
        # Desenhar card
        pygame.draw.rect(self.tela, cor_card, (x, y, largura, altura), border_radius=15)
        pygame.draw.rect(self.tela, cor_borda, (x, y, largura, altura), 3, border_radius=15)
        
        # Título da fase
        titulo = self.fonte_normal.render(config["nome"], True, self.cor_texto)
        self.tela.blit(titulo, (x + 15, y + 12))
        
        # Descrição
        descricao = self.fonte_muito_pequena.render(config["descricao"], True, (200, 200, 200))
        self.tela.blit(descricao, (x + 15, y + 40))

        # Layout em duas colunas
        coluna_esq = x + 15
        coluna_dir = x + largura // 2 + 10
        
        # Informações de progresso - LADO ESQUERDO
        info_y = y + 65

        if not fase_acessivel:
            status_text = self.fonte_pequena.render("BLOQUEADA", True, (255, 100, 100))
            self.tela.blit(status_text, (coluna_esq, info_y))
            
            # Apenas estatísticas básicas para fases bloqueadas
            stats = [
                f"Vel: {config['velocidade_inicial'] * 10}-{config['vel_maxima'] * 10}",
                f"Obs: {config['max_obstaculos']}",
                f"Tipos: {len(config['obstaculos_ativos'])}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self.fonte_minima.render(stat, True, (150, 150, 150))
                self.tela.blit(stat_text, (coluna_dir, info_y + i * 18))
                
        elif fase_completa:
            status_text = self.fonte_pequena.render("COMPLETA!", True, (100, 255, 100))
            self.tela.blit(status_text, (coluna_esq, info_y))
            
            tempo_text = self.fonte_minima.render(f"Melhor: {melhor_tempo}s", True, (180, 180, 180))
            self.tela.blit(tempo_text, (coluna_esq, info_y + 22))
            
            recompensa_text = self.fonte_minima.render(f"Ganho: ${config['recompensa']}", True, (255, 255, 100))
            self.tela.blit(recompensa_text, (coluna_esq, info_y + 40))
            
            # Estatísticas - LADO DIREITO
            stats = [
                f"Vel: {config['velocidade_inicial'] * 10}-{config['vel_maxima'] * 10}",
                f"Obs: {config['max_obstaculos']}",
                f"Tipos: {len(config['obstaculos_ativos'])}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self.fonte_minima.render(stat, True, (180, 180, 180))
                self.tela.blit(stat_text, (coluna_dir, info_y + i * 18))
        else:
            status_text = self.fonte_pequena.render("DISPONÍVEL", True, (100, 200, 255))
            self.tela.blit(status_text, (coluna_esq, info_y))
            
            recompensa_text = self.fonte_minima.render(f"Recompensa: ${config['recompensa']}", True, (255, 255, 100))
            self.tela.blit(recompensa_text, (coluna_esq, info_y + 22))
            
            # Estatísticas - LADO DIREITO
            stats = [
                f"Vel: {config['velocidade_inicial'] * 10}-{config['vel_maxima'] * 10}",
                f"Obs: {config['max_obstaculos']}",
                f"Tipos: {len(config['obstaculos_ativos'])}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self.fonte_minima.render(stat, True, (180, 180, 180))
                self.tela.blit(stat_text, (coluna_dir, info_y + i * 18))
        
        return pygame.Rect(x, y, largura, altura)

    def mostrar_menu_principal(self):
        """Mostra o menu principal - VERSÃO COM LAYOUT CORRIGIDO"""
        from fases import get_total_fases
        self.total_fases = get_total_fases()
        
        # LAYOUT RESPONSIVO MELHORADO
        if self.total_fases <= 4:
            colunas = 2  # Sempre 2 colunas para melhor aproveitamento
        else:
            colunas = 2
        
        # Calcular dimensões com margens de segurança
        margem_horizontal = 40
        margem_superior = 180  # Aumentado para caber título + barra
        espacamento = 25
        
        largura_card = (LARGURA - 2 * margem_horizontal - (colunas - 1) * espacamento) // colunas
        altura_card = 140  # REDUZIDA para caber melhor na tela
        
        # Calcular altura máxima necessária
        linhas_necessarias = (self.total_fases + colunas - 1) // colunas
        altura_total_cards = linhas_necessarias * (altura_card + espacamento)
        
        # Verificar se cabe na tela
        altura_disponivel = ALTURA - margem_superior - 120  # 120px para botões inferiores
        if altura_total_cards > altura_disponivel:
            # Se não couber, reduzir altura dos cards
            altura_card = (altura_disponivel - (linhas_necessarias - 1) * espacamento) // linhas_necessarias
            altura_card = max(120, altura_card)  # Mínimo de 120px
        
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    # Verificar clique nos botões de fase
                    for i in range(1, self.total_fases + 1):
                        linha = (i - 1) // colunas
                        coluna = (i - 1) % colunas
                        x = margem_horizontal + coluna * (largura_card + espacamento)
                        y = margem_superior + linha * (altura_card + espacamento)
                        fase_rect = pygame.Rect(x, y, largura_card, altura_card)
                        if fase_rect.collidepoint(mouse_pos) and self.save_system.get_fase_acessivel(i):
                            return i
                    
                    # Verificar botões inferiores
                    if sair_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                    if reset_rect.collidepoint(mouse_pos):
                        self.save_system.resetar_progresso()
                        # Recarregar o menu para atualizar o estado
                        return self.mostrar_menu_principal()
            
            # Desenhar fundo
            self.tela.fill(self.cor_fundo)

            # CABEÇALHO COMPACTO
            # Título
            titulo = self.fonte_titulo.render("MAGENTTIS POSTE", True, self.cor_titulo)
            self.tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 30))
            
            # Subtítulo
            subtitulo = self.fonte_subtitulo.render("Selecione uma Fase", True, self.cor_texto)
            self.tela.blit(subtitulo, (LARGURA//2 - subtitulo.get_width()//2, 95))
            
            # Informações de progresso geral (MAIS COMPACTO)
            dinheiro = self.save_system.get_dinheiro()
            objetivo = self.save_system.get_objetivo_total()
            progresso = min(100, (dinheiro / objetivo) * 100)

            # Barra de progresso compacta
            barra_largura = 350
            barra_altura = 16
            barra_x = LARGURA // 2 - barra_largura // 2
            barra_y = 140
            
            pygame.draw.rect(self.tela, (50, 50, 50), (barra_x, barra_y, barra_largura, barra_altura))
            pygame.draw.rect(self.tela, (0, 200, 0), (barra_x, barra_y, int(barra_largura * progresso / 100), barra_altura))
            pygame.draw.rect(self.tela, (255, 255, 255), (barra_x, barra_y, barra_largura, barra_altura), 2)
            
            # Texto do objetivo compacto
            objetivo_text = self.fonte_muito_pequena.render(f"Objetivo: ${dinheiro}/${objetivo}", True, self.cor_texto)
            self.tela.blit(objetivo_text, (LARGURA//2 - objetivo_text.get_width()//2, barra_y - 25))
            
            # Desenhar fases
            fase_rects = []
            for i in range(1, self.total_fases + 1):
                linha = (i - 1) // colunas
                coluna = (i - 1) % colunas
                x = margem_horizontal + coluna * (largura_card + espacamento)
                y = margem_superior + linha * (altura_card + espacamento)
                
                # Verificar se está dentro da tela
                if y + altura_card < ALTURA - 100:  # 100px margem para botões
                    fase_rect = self.desenhar_fase(i, x, y, largura_card, altura_card, 
                                                 selecionada=(i == self.fase_selecionada),
                                                 hover=pygame.Rect(x, y, largura_card, altura_card).collidepoint(mouse_pos))
                    fase_rects.append(fase_rect)
            
            # BOTÕES INFERIORES
            botao_y = ALTURA - 70
            sair_rect = self.desenhar_botao("SAIR", LARGURA//2 - 220, botao_y, 200, 50,
                                          hover=pygame.Rect(LARGURA//2 - 220, botao_y, 200, 50).collidepoint(mouse_pos))
            
            reset_rect = self.desenhar_botao("RESETAR", LARGURA//2 + 20, botao_y, 200, 50,
                                           hover=pygame.Rect(LARGURA//2 + 20, botao_y, 200, 50).collidepoint(mouse_pos))
            
            # Instruções
            instrucoes = self.fonte_pequena.render("Clique em uma fase disponível para começar", True, (150, 150, 150))
            self.tela.blit(instrucoes, (LARGURA//2 - instrucoes.get_width()//2, ALTURA - 110))
            
            pygame.display.flip()
            self.clock.tick(60)

    # Os métodos mostrar_vitoria_fase e mostrar_game_over permanecem os mesmos
    def mostrar_vitoria_fase(self, numero_fase, tempo_decorrido, dinheiro_ganho, bonus_tempo=0):
        """Mostra tela de vitória da fase"""
        from fases import get_config_fase
        config = get_config_fase(numero_fase)
        
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "menu"
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if 'proxima_rect' in locals() and proxima_rect.collidepoint(mouse_pos):
                        return "proxima"
                    if menu_rect.collidepoint(mouse_pos):
                        return "menu"
            
            # Fundo de vitória
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 50, 0, 200))
            self.tela.blit(overlay, (0, 0))
            
            # Texto de vitória
            vitoria_text = self.fonte_titulo.render("FASE COMPLETA!", True, (100, 255, 100))
            self.tela.blit(vitoria_text, (LARGURA//2 - vitoria_text.get_width()//2, 150))
            
            # Estatísticas
            stats_y = 250
            stats = [
                f"Fase: {config['nome']}",
                f"Tempo: {tempo_decorrido} segundos",
                f"Recompensa base: ${config['recompensa']}"
            ]
            
            if bonus_tempo > 0:
                stats.append(f"Bônus por tempo: ${bonus_tempo}")
            
            stats.append(f"Total ganho: ${dinheiro_ganho}")
            stats.append(f"Dinheiro total: ${self.save_system.get_dinheiro()}")
            
            for i, stat in enumerate(stats):
                stat_text = self.fonte_normal.render(stat, True, (200, 255, 200))
                self.tela.blit(stat_text, (LARGURA//2 - stat_text.get_width()//2, stats_y + i * 40))
            
            # Botões
            from fases import get_total_fases
            total_fases = get_total_fases()
            
            if numero_fase < total_fases:
                proxima_rect = self.desenhar_botao("PRÓXIMA FASE", LARGURA//2 - 160, 450, 300, 50,
                                                 hover=pygame.Rect(LARGURA//2 - 160, 450, 300, 50).collidepoint(mouse_pos))
            
            menu_rect = self.desenhar_botao("VOLTAR AO MENU", LARGURA//2 - 160, 520, 300, 50,
                                          hover=pygame.Rect(LARGURA//2 - 160, 520, 300, 50).collidepoint(mouse_pos))
            
            pygame.display.flip()
            self.clock.tick(60)

    def mostrar_game_over(self, tempo_decorrido, fase, motivo):
        """Mostra tela de game over e retorna se o jogador quer reiniciar"""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if reiniciar_rect.collidepoint(mouse_pos):
                        return True
                    if menu_rect.collidepoint(mouse_pos):
                        return False
            
            # Fundo semi-transparente
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.tela.blit(overlay, (0, 0))
            
            # Texto game over
            game_over_text = self.fonte_titulo.render("GAME OVER", True, (255, 0, 0))
            self.tela.blit(game_over_text, (LARGURA//2 - game_over_text.get_width()//2, 150))
            
            # Motivo
            motivo_text = self.fonte_subtitulo.render(motivo, True, self.cor_texto)
            self.tela.blit(motivo_text, (LARGURA//2 - motivo_text.get_width()//2, 250))
            
            # Estatísticas
            stats = [
                f"Fase: {fase}",
                f"Tempo: {tempo_decorrido} segundos"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self.fonte_normal.render(stat, True, (200, 200, 200))
                self.tela.blit(stat_text, (LARGURA//2 - stat_text.get_width()//2, 320 + i * 40))
            
            # Botões
            reiniciar_rect = self.desenhar_botao("TENTAR NOVAMENTE", LARGURA//2 - 150, 450, 300, 50,
                                               hover=pygame.Rect(LARGURA//2 - 150, 450, 300, 50).collidepoint(mouse_pos))
            
            menu_rect = self.desenhar_botao("VOLTAR AO MENU", LARGURA//2 - 150, 520, 300, 50,
                                          hover=pygame.Rect(LARGURA//2 - 150, 520, 300, 50).collidepoint(mouse_pos))
            
            pygame.display.flip()
            self.clock.tick(60)