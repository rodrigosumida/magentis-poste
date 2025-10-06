import pygame
import sys
import random

pygame.init()

largura, altura = 1160, 720
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("CORITIBA")

# Carregar plano de fundo
fundo = pygame.image.load("fundo.jpg")
fundo = pygame.transform.scale(fundo, (largura, altura))

# Controle do fundo em movimento
fundo_y = 0
velocidade_fundo = 10

# Carregar sprites
largura_ret, altura_ret = 42, 102
sprite_parado = pygame.image.load("Peter_Griffin.png")
sprite_parado = pygame.transform.scale(sprite_parado, (largura_ret, altura_ret))

sprite_travado = pygame.image.load("morte.png")
sprite_travado = pygame.transform.scale(sprite_travado, (largura_ret, altura_ret))

# Carregar textura para o quadrado vermelho
carro_img = pygame.image.load("carro.png").convert_alpha()
carro_img = pygame.transform.scale(carro_img, (77, 110))

# Carregar frames da animação
# frames = [
#     pygame.image.load(f"frame_{i}_delay-0.1s.gif") for i in range(7)
# ]
frames = [pygame.image.load("Peter_Griffin.png")]
frames = [pygame.transform.scale(f, (largura_ret, altura_ret)) for f in frames]

# Controle de animação
frame_atual = 0
tempo_animacao = 50
ultimo_tempo = pygame.time.get_ticks()
animando = False
olhando_esquerda = False
travado = False

# Posição inicial do personagem
x = 50
y = altura - altura_ret - 30
velocidade = 5

# Margens laterais para os quadrados azuis
MARGEM_LATERAL = 160

# Variáveis de velocidade dos obstáculos
velocidade_inicial = 6
velocidade_atual = velocidade_inicial
vel_maxima = 15
incremento_vel = 1
intervalo_aumento = 15  # segundos
tempo_ultimo_aumento = 0

# --- VARIÁVEL DE CONTROLE DE SPAWN ---
intervalo_spawn = random.randint(200, 2000)
ultimo_spawn = pygame.time.get_ticks()
max_obstaculos = 5

# --- POSTES ROXOS  ---
chance_roxo = 0.005
largura_roxo, altura_roxo = 30, 30
vel_lateral_roxo = 1

# --- RADAR ---
quadrado_especial = None
probabilidade_quadrado = 0.001
pos_quadrado = (largura//2 - 50, altura//2 - 50)
tam_quadrado = 100

# Classe Obstáculo
class Obstaculo:
    def __init__(self, x, y, largura, altura, cor, velocidade, move_lateral=False, imagem=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor
        self.velocidade = velocidade
        self.move_lateral = move_lateral
        self.direcao = random.choice([-1, 1]) if move_lateral else 0
        self.vel_lateral = 1 if move_lateral else 0
        self.imagem = None
        if imagem:
            self.imagem = imagem

    def mover(self):
        self.rect.y += self.velocidade
        if self.move_lateral:
            self.rect.x += self.direcao * self.vel_lateral

            # Limites especiais para roxos (ficarem dentro da calçada)
            if self.cor == (128,0,128):  # roxo
                if self.rect.left < 0:
                    self.direcao *= -1
                    self.rect.left = 0
                if self.rect.right > MARGEM_LATERAL and self.rect.x < largura/2:  # esquerda
                    self.rect.right = MARGEM_LATERAL
                    self.direcao *= -1
                if self.rect.left < largura - MARGEM_LATERAL and self.rect.x > largura/2:  # direita
                    self.rect.left = largura - MARGEM_LATERAL
                    self.direcao *= -1
                if self.rect.right > largura:
                    self.rect.right = largura
                    self.direcao *= -1
            else:
                # lógica antiga para vermelhos/azuis/postes
                if self.rect.left < MARGEM_LATERAL or self.rect.right > largura - MARGEM_LATERAL:
                    self.direcao *= -1
                    if self.rect.left < MARGEM_LATERAL:
                        self.rect.left = MARGEM_LATERAL
                    if self.rect.right > largura - MARGEM_LATERAL:
                        self.rect.right = largura - MARGEM_LATERAL

    def desenhar(self, tela):
        if self.imagem:
            tela.blit(self.imagem, self.rect.topleft)
        else:
            pygame.draw.rect(tela, self.cor, self.rect)


# Lista de obstáculos
obstaculos = []

# Inicialmente adiciona 1 carro
inicio = MARGEM_LATERAL
fim = largura - MARGEM_LATERAL - 100
obstaculos.append(Obstaculo(random.randint(inicio, fim), -100, 100, 100, (255, 0, 0), velocidade_atual, imagem=carro_img))

clock = pygame.time.Clock()

# Controle de tempo
tempo_inicial = pygame.time.get_ticks()
tempo_decorrido = 0
font = pygame.font.SysFont(None, 40)

# No início, definir a flag
invencivel = False

# Intervalo fixo dos postes (em ms)
intervalo_postes = 3000
ultimo_poste = pygame.time.get_ticks()

while True:
    animando = False
    teclas = pygame.key.get_pressed()
    personagem_rect = pygame.Rect(x, y, largura_ret, altura_ret)

    # Atualizar tempo decorrido se não travado
    if not travado:
        tempo_decorrido = (pygame.time.get_ticks() - tempo_inicial) // 1000

    # Movimento do personagem
    if not travado:
        if teclas[pygame.K_LEFT]:
            x -= velocidade
            animando = True
            olhando_esquerda = True
        if teclas[pygame.K_RIGHT]:
            x += velocidade
            animando = True
            olhando_esquerda = False

        if x < 0: x = 0
        if x > largura - largura_ret: x = largura - largura_ret
        personagem_rect.topleft = (x, y)

        # Detectar colisão
        if not travado and not invencivel:
            for ob in obstaculos:
                if personagem_rect.colliderect(ob.rect):

                    travado = True
                    break

    # Movimento dos obstáculos
    for ob in obstaculos[:]:
        ob.mover()
        if ob.move_lateral:
            for outro in obstaculos:
                if outro is not ob and ob.rect.colliderect(outro.rect):
                    ob.direcao *= -1
                    if ob.direcao > 0:
                        ob.rect.left = outro.rect.right
                    else:
                        ob.rect.right = outro.rect.left
        if ob.rect.top > altura:
            obstaculos.remove(ob)
    
    # PESSOAS
    if not travado:
        if random.random() < chance_roxo:
            # Escolher aleatoriamente calçada esquerda ou direita
            lado = random.choice(["esquerda", "direita"])
            if lado == "esquerda":
                x_pos = random.randint(0, MARGEM_LATERAL - largura_roxo)
            else:
                x_pos = random.randint(largura - MARGEM_LATERAL, largura - largura_roxo)

            obstaculos.append(
                Obstaculo(
                    x_pos, -altura_roxo, largura_roxo, altura_roxo, (128, 0, 128), velocidade_atual, move_lateral=True
                )
            )
    
    # Gerar quadrado especial com probabilidade
    if quadrado_especial is None and random.random() < probabilidade_quadrado:
        quadrado_especial = pygame.Rect(pos_quadrado[0], pos_quadrado[1], tam_quadrado, tam_quadrado)

    # Aumenta a velocidade a cada intervalo
    if tempo_decorrido - tempo_ultimo_aumento >= intervalo_aumento:
        velocidade_atual = min(velocidade_atual + incremento_vel, vel_maxima)
        for ob in obstaculos:
            ob.velocidade = velocidade_atual
        tempo_ultimo_aumento = tempo_decorrido

    # --- GERAR NOVOS OBSTÁCULOS AO LONGO DO TEMPO ---
    tempo_atual = pygame.time.get_ticks()
    if not travado and len(obstaculos) < max_obstaculos:
        if tempo_atual - ultimo_spawn > intervalo_spawn:
            # Decide quantos vão cair de uma vez (1 a 3)
            qtd_novos = random.randint(1, 3)
            
            for _ in range(qtd_novos):
                if len(obstaculos) < max_obstaculos:
                    largura_quadrado = 77
                    espaco_minimo = 20
                    inicio = MARGEM_LATERAL
                    fim = largura - MARGEM_LATERAL - largura_quadrado

                    x_pos = random.randrange(inicio, fim, largura_quadrado + espaco_minimo)

                    # Decide se vai ser
                    if random.random() < 0.2:
                        obstaculos.append(
                            Obstaculo(x_pos, -120, 130, 130, (0, 0, 255), velocidade_atual, move_lateral=True)
                        )
                    else:
                        obstaculos.append(
                            Obstaculo(x_pos, -100, largura_quadrado, 110, (255, 0, 0), velocidade_atual, imagem=carro_img)
                        )

            # Atualiza timer e define um novo intervalo aleatório
            ultimo_spawn = tempo_atual
            intervalo_spawn = random.randint(200, 2000)

    # --- GERAR POSTES (sempre em pares, grudados na calçada) ---
    if not travado:
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_poste > intervalo_postes:
            largura_poste, altura_poste = 30, 30

            # Poste da esquerda (grudado na lateral da tela, dentro da calçada)
            obstaculos.append(
                Obstaculo(
                    0, -altura_poste, largura_poste, altura_poste, (255, 255, 0), velocidade_atual
                )
            )

            # Poste da direita (grudado na outra lateral da tela, dentro da calçada)
            obstaculos.append(
                Obstaculo(
                    largura - largura_poste, -altura_poste, largura_poste, altura_poste, (255, 255, 0), velocidade_atual
                )
            )

            ultimo_poste = tempo_atual

    # Atualizar animação
    if animando and not travado:
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_tempo > tempo_animacao:
            frame_atual = (frame_atual + 1) % len(frames)
            ultimo_tempo = tempo_atual
    else:
        frame_atual = 0

    # Atualizar posição do fundo (só se não travado)
    if not travado:
        fundo_y += velocidade_fundo
        if fundo_y >= altura:
            fundo_y = 0

    # Desenhar fundo rolando
    tela.blit(fundo, (0, fundo_y))
    tela.blit(fundo, (0, fundo_y - altura))

    # Desenhar margens transparentes por cima
    superficie_margem = pygame.Surface((MARGEM_LATERAL, altura), pygame.SRCALPHA)
    superficie_margem.fill((200,200,200,100))
    tela.blit(superficie_margem, (0,0))
    tela.blit(superficie_margem, (largura-MARGEM_LATERAL,0))

    # Desenhar obstáculos
    for ob in obstaculos:
        ob.desenhar(tela)

    # Desenhar tempo decorrido
    tempo_texto = font.render(f"Tempo: {tempo_decorrido}s", True, (255,255,255))
    tela.blit(tempo_texto, (largura//2 - tempo_texto.get_width()//2, 10))

    # Desenhar radar (se existir)
    if quadrado_especial:
        pygame.draw.rect(tela, (0, 255, 255), quadrado_especial)  # cor ciano

    # Desenhar personagem
    if travado:
        sprite = sprite_travado
        if olhando_esquerda:
            sprite = pygame.transform.flip(sprite, True, False)
        tela.blit(sprite, (x, y))
    else:
        if animando:
            frame = frames[frame_atual]
            if olhando_esquerda:
                frame = pygame.transform.flip(frame, True, False)
            tela.blit(frame, (x, y))
        else:
            sprite = sprite_parado
            if olhando_esquerda:
                sprite = pygame.transform.flip(sprite_parado, True, False)
            tela.blit(sprite, (x, y))

    pygame.display.flip()
    clock.tick(60)

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                travado = False
                obstaculos.clear()
                velocidade_atual = velocidade_inicial  # reset da velocidade
                inicio = MARGEM_LATERAL
                fim = largura - MARGEM_LATERAL - 100
                obstaculos.append(Obstaculo(random.randint(inicio,fim), -100, 100,100,(255,0,0), velocidade_atual))
                tempo_inicial = pygame.time.get_ticks()
                tempo_decorrido = 0
                tempo_ultimo_aumento = 0
                fundo_y = 0
            if evento.key == pygame.K_u:
                invencivel = not invencivel
            if evento.key == pygame.K_s:
                quadrado_especial = None
