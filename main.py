import pygame
from game import Game
from menu import Menu

def main():
    pygame.init()
    
    menu = Menu()
    
    while True:
        # Mostrar menu e obter fase selecionada
        fase_selecionada = menu.mostrar_menu_principal()
        
        # Iniciar jogo com a fase selecionada
        game = Game(fase_selecionada)
        game.run()
        
        # Quando o jogo terminar, mostrar game over
        motivo = "Colisão com obstáculo" if game.game_over_por_colisao else "Muitas penalidades no radar"
        reiniciar = menu.mostrar_game_over(game.tempo_decorrido, fase_selecionada, motivo)
        
        if not reiniciar:
            # Voltar ao menu principal
            continue

if __name__ == "__main__":
    main()