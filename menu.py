import pygame
import sys
from config import *

class Menu:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("MAGENTTIS POSTE - Menu")
        self.clock = pygame.time.Clock()
        
        # Cores
        self.cor_fundo = (30, 30, 60)
        self.cor_titulo = (255, 255, 0)  # Amarelo do Coritiba
        self.cor_texto = (255, 255, 255)
        self.cor_destaque = (0, 200, 255)
        self.cor_botao = (50, 150, 50)
        self.cor_botao_hover = (70, 170, 70)
        
        # Fontes
        self.fonte_titulo = pygame.font.SysFont("Arial", 72, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("Arial", 36)
        self.fonte_normal = pygame.font.SysFont("Arial", 28)
        self.fonte_pequena = pygame.font.SysFont("Arial", 22)
        
        # Estado do menu
        self.fase_selecionada = 1
        self.total_fases = 5  # Vamos importar isso depois

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
        """Desenha um card de fase"""
        from fases import get_config_fase
        config = get_config_fase(numero_fase)
        
        # Cor do card
        if selecionada:
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
        self.tela.blit(titulo, (x + 20, y + 20))
        
        # Descrição
        descricao = self.fonte_pequena.render(config["descricao"], True, (200, 200, 200))
        self.tela.blit(descricao, (x + 20, y + 60))
        
        # Estatísticas
        stats_y = y + 100
        stats = [
            f"Velocidade: {config['velocidade_inicial'] * 10}-{config['vel_maxima'] * 10}",
            f"Obstáculos máx: {config['max_obstaculos']}",
            f"Obstáculos: {len(config['obstaculos_ativos'])} tipos"
        ]
        
        for stat in stats:
            stat_text = self.fonte_pequena.render(stat, True, (180, 180, 180))
            self.tela.blit(stat_text, (x + 20, stats_y))
            stats_y += 25
        
        return pygame.Rect(x, y, largura, altura)

    def mostrar_menu_principal(self):
        """Mostra o menu principal e retorna a fase selecionada"""
        from fases import get_total_fases
        self.total_fases = get_total_fases()
        
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
                        fase_rect = pygame.Rect(100 + ((i-1) % 3) * 320, 200 + ((i-1) // 3) * 180, 300, 160)
                        if fase_rect.collidepoint(mouse_pos):
                            return i  # Retorna o número da fase selecionada
                    
                    # Verificar botão sair
                    if sair_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
            
            # Desenhar fundo
            self.tela.fill(self.cor_fundo)
            
            # Título
            titulo = self.fonte_titulo.render("MAGENTTIS POSTE", True, self.cor_titulo)
            subtitulo = self.fonte_subtitulo.render("Selecione uma Fase", True, self.cor_texto)
            
            self.tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 50))
            self.tela.blit(subtitulo, (LARGURA//2 - subtitulo.get_width()//2, 130))
            
            # Desenhar fases
            fase_rects = []
            for i in range(1, self.total_fases + 1):
                x = 100 + ((i-1) % 3) * 320
                y = 200 + ((i-1) // 3) * 180
                fase_rect = self.desenhar_fase(i, x, y, 300, 160, 
                                             selecionada=(i == self.fase_selecionada),
                                             hover=pygame.Rect(x, y, 300, 160).collidepoint(mouse_pos))
                fase_rects.append(fase_rect)
            
            # Botão sair
            sair_rect = self.desenhar_botao("SAIR", LARGURA//2 - 100, ALTURA - 80, 200, 50,
                                          hover=pygame.Rect(LARGURA//2 - 100, ALTURA - 80, 200, 50).collidepoint(mouse_pos))
            
            # Instruções
            instrucoes = self.fonte_pequena.render("Clique em uma fase para começar", True, (150, 150, 150))
            self.tela.blit(instrucoes, (LARGURA//2 - instrucoes.get_width()//2, ALTURA - 120))
            
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