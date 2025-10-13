import pygame
import sys

largura, altura = 600, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("CORITIBA")

# Carregar plano de fundo
fundo = pygame.image.load("fundo.jpg")  # coloque o caminho da imagem
fundo = pygame.transform.scale(fundo, (largura, altura))

# Carregar personagem
personagem = pygame.image.load("ovni.png")  # pode ser .png com fundo transparente
x, y = 50, 50
largura_ret, altura_ret = 80, 80
velocidade = 5
personagem = pygame.transform.scale(personagem, (largura_ret, altura_ret))

PRETO = (0, 0, 0)
AZUL = (0, 0, 255)

while True:
  teclas = pygame.key.get_pressed()
  if teclas[pygame.K_LEFT]:
    x -= velocidade
  if teclas[pygame.K_RIGHT]:
    x += velocidade
  if teclas[pygame.K_UP]:
    y -= velocidade
  if teclas[pygame.K_DOWN]:
    y += velocidade
  
  # Limpa tela
  # tela.fill(PRETO)

  # Desenha o retângulo
  # pygame.draw.rect(tela, AZUL, (x, y, largura_ret, altura_ret))

  # Desenha o fundo
  tela.blit(fundo, (0, 0))

  # Desenha o personagem
  tela.blit(personagem, (x, y))

  # Atualiza a tela
  pygame.display.flip()

  # Controla FPS
  pygame.time.Clock().tick(60)

  for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
      pygame.quit()
      sys.exit()