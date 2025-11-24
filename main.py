import pygame
from game import Game
from menu import Menu
from save_system import SaveSystem

def main():
    pygame.init()
    
    menu = Menu()
    save_system = SaveSystem()

    # NOVO: Verificar se o jogo foi completado
    if save_system.jogo_completo():
        # Mostrar tela de fim de jogo
        resultado = menu.mostrar_fim_de_jogo()
        if resultado == "menu":
            # Continuar para o menu normalmente
            pass
        elif resultado == "continuar":
            # Iniciar diretamente na fase extra (ajuste o número conforme suas fases)
            fase_extra = 6  # Supondo que a fase 6 é a extra
            game = Game(fase_extra)
            game.run()
            return
    
    while True:
        # Mostrar menu e obter fase selecionada
        fase_selecionada = menu.mostrar_menu_principal()
        
        if fase_selecionada is None:
            break
        
        # Iniciar jogo com a fase selecionada
        game = Game(fase_selecionada)
        resultado = game.run()
        
        # NOVO: Verificar se o jogo foi completado após cada fase
        if save_system.jogo_completo():
            resultado_fim = menu.mostrar_fim_de_jogo()
            if resultado_fim == "continuar":
                fase_selecionada = 6  # Fase extra
                continue
            elif resultado_fim == "menu":
                continue
        
        if resultado == "menu":
            continue
        elif isinstance(resultado, int):
            # Carregar próxima fase
            fase_selecionada = resultado
            continue

if __name__ == "__main__":
    main()