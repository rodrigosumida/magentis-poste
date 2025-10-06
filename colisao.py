import pygame
import sys
import math

# Inicializa o Pygame
pygame.init()

# Configurações da tela
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Colisão e Ricochete")

# Cores
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

# Classe Bola
class Bola:
  def __init__(self, x, y, raio, cor, vel_x, vel_y):
    self.x = x
    self.y = y
    self.raio = raio
    self.cor = cor
    self.vel_x = vel_x
    self.vel_y = vel_y
  
  def mover(self):
    self.x += self.vel_x
    self.y += self.vel_y

    # Colisão com paredes
    if self.x - self.raio < 0 or self.x + self.raio > largura:
      self.vel_x *= -1
    if self.y - self.raio < 0 or self.y + self.raio > altura:
      self.vel_y *= -1
  
  def desenhar(self, tela):
    pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)))
  
# Função para detectar colisão entre duas bolas
def colidem(b1, b2):
  distancia = math.hypot(b1.x - b2.x, b1.y - b2.y)
  return distancia < b1.raio + b2.raio

# Criação das bolas
bola1 = Bola(200, 150, 30, VERMELHO, 3, 2)
bola2 = Bola(400, 300, 40, AZUL, -2, 3)

# Loop principal
clock = pygame.time.Clock()
while True:

  # Movimento
  bola1.mover()
  bola2.mover()

  # Colisão entre as bolas
  if colidem(bola1, bola2):
    bola1.vel_x *= -1
    bola1.vel_y *= -1
    bola2.vel_x *= -1
    bola2.vel_y *= -1
  
  # Desenho