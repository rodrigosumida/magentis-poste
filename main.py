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
        menu.mostrar_fim_de_jogo()
        return
    
    while True:
        # Mostrar menu e obter fase selecionada
        fase_selecionada = menu.mostrar_menu_principal()
        
        if fase_selecionada is None:
            break
        
        # Iniciar jogo com a fase selecionada
        game = Game(fase_selecionada)
        resultado = game.run()
        
        if resultado == "menu":
            continue
        elif isinstance(resultado, int):
            # Carregar próxima fase
            fase_selecionada = resultado
            continue

if __name__ == "__main__":
    main()