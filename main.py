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

# Carregar textura para o caro
carro_img = pygame.image.load("carro.png").convert_alpha()
carro_img = pygame.transform.scale(carro_img, (77, 110))

# Carregar textura para o caminhão
caminhao_img = pygame.image.load("caminhao.png").convert_alpha()
caminhao_img = pygame.transform.scale(caminhao_img, (80, 150))

# Carregar textura para as pessoas
pessoa_img = pygame.image.load("pessoa.png").convert_alpha()
pessoa_img = pygame.transform.scale(pessoa_img, (30, 30))

# Carregar textura do poste
poste_img = pygame.image.load("poste.png").convert_alpha()
poste_img = pygame.transform.scale(poste_img, (60, 160))

# Carregar textura do cachorro
cachorro_img = pygame.image.load("cachorro.png").convert_alpha()
cachorro_img = pygame.transform.scale(cachorro_img, (50, 50))

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

# --- PESSOAS ---
chance_roxo = 0.005
largura_roxo, altura_roxo = 30, 30
vel_lateral_roxo = 1

# --- CACHORRO ---
chance_cachorro = 0.01 
distancia_ativacao_cachorro = 200
duracao_seguir = 3000

# --- RADAR ---
radar_visivel = False
probabilidade_radar = 0.001
radar_pos = (20, 20)
radar_tamanho = (300, 150)
radar_img = pygame.image.load("radar.png").convert_alpha()
radar_img = pygame.transform.scale(radar_img, radar_tamanho)

# Controle do radar
radar_piscar_intervalo = 300
ultimo_piscar = 0
radar_mostrar = True

# Timer radar
radar_tempo_total = 5000
radar_inicio = 0

CONFIG_TIPOS = {
    "carro": {
        "largura": 77,
        "altura": 110,
        "cor": (255, 0, 0),
        "imagem": carro_img,
        "move_lateral": False,
    },
    "caminhao": {
        "largura": 80,
        "altura": 150,
        "cor": (0, 0, 255),
        "imagem": caminhao_img,
        "move_lateral": True,
    },
    "pessoa": {
        "largura": 30,
        "altura": 30,
        "cor": (128, 0, 128),
        "imagem": pessoa_img,
        "move_lateral": True,
    },
    "poste": {
        "largura": 30,
        "altura": 30,
        "cor": (255, 255, 0),
        "imagem": poste_img,
        "move_lateral": False,
    },
    "cachorro": {
        "largura": 50,
        "altura": 50,
        "cor": (200, 200, 50),
        "imagem": cachorro_img,
        "move_lateral": False,
    }
}


# Classe Obstáculo
class Obstaculo:
    def __init__(self, tipo, x, y, velocidade=6):
        dados = CONFIG_TIPOS.get(tipo)
        if not dados:
            raise ValueError(f"Tipo de obstáculo desconhecido: {tipo}")

        self.tipo = tipo
        self.cor = dados["cor"]
        self.velocidade = velocidade
        self.move_lateral = dados["move_lateral"]
        self.imagem = dados["imagem"]

        # cria a hitbox
        self.rect = pygame.Rect(x, y, dados["largura"], dados["altura"])

        # comportamento lateral
        self.direcao = random.choice([-1, 1]) if self.move_lateral else 0
        self.vel_lateral = 1 + (random.random() * random.randint(-1, 1)) if self.move_lateral else 0

    def mover(self):
        self.rect.y += self.velocidade
        if self.move_lateral:
            self.rect.x += self.direcao * self.vel_lateral

            # Limites específicos
            if self.tipo == "pessoa":
                # Presa na calçada
                if self.rect.left < 0: 
                    self.rect.left = 0
                    self.direcao *= -1
                elif self.rect.right > MARGEM_LATERAL:  # calçada esquerda
                    self.rect.right = MARGEM_LATERAL
                    self.direcao *= -1

                # Se estiver na calçada direita
                if self.rect.left > largura/2:
                    if self.rect.left < largura - MARGEM_LATERAL:
                        self.rect.left = largura - MARGEM_LATERAL
                    if self.rect.right > largura:
                        self.rect.right = largura
                    if self.rect.left >= largura - MARGEM_LATERAL:
                        self.direcao *= -1
            else:
                # Limites padrão para carros/caminhões/postes
                if self.rect.left < MARGEM_LATERAL:
                    self.rect.left = MARGEM_LATERAL
                    self.direcao *= -1
                elif self.rect.right > largura - MARGEM_LATERAL:
                    self.rect.right = largura - MARGEM_LATERAL
                    self.direcao *= -1


    def desenhar(self, tela):
        if self.imagem:
            img_rect = self.imagem.get_rect(midbottom=self.rect.midbottom)
            tela.blit(self.imagem, img_rect.topleft)
        else:
            pygame.draw.rect(tela, self.cor, self.rect)

# Lista de obstáculos
obstaculos = []

# Inicialmente adiciona 1 carro
inicio = MARGEM_LATERAL
fim = largura - MARGEM_LATERAL - 100
obstaculos.append(Obstaculo("carro", random.randint(inicio, fim), -100, velocidade_atual))

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

            obstaculos.append(Obstaculo("pessoa", x_pos, -30, velocidade_atual))
    
    # CACHORRO
    if not travado and random.random() < chance_cachorro:
        lado = random.choice(["esquerda", "direita"])
        if lado == "esquerda":
            x_pos = random.randint(0, MARGEM_LATERAL - 50)
        else:
            x_pos = random.randint(largura - MARGEM_LATERAL, largura - 50)

        novo_cachorro = Obstaculo("cachorro", x_pos, -30, velocidade_atual)
        novo_cachorro.seguindo = False
        novo_cachorro.tempo_inicio_seguir = 0
        obstaculos.append(novo_cachorro)
    
    # Gerar radar com probabilidade
    if not radar_visivel and random.random() < probabilidade_radar:
        radar_visivel = True
        radar_mostrar = True
        radar_piscar_intervalo = 500  # reseta a velocidade de piscar
        radar_inicio = pygame.time.get_ticks()
        ultimo_piscar = radar_inicio
    
    # Atualizar piscar e tempo do radar
    if radar_visivel:
        tempo_atual = pygame.time.get_ticks()
        tempo_passado = tempo_atual - radar_inicio

        # Aumenta velocidade de piscar progressivamente
        # (quanto mais perto do fim, mais rápido)
        progresso = tempo_passado / radar_tempo_total
        radar_piscar_intervalo = max(100, 500 - int(400 * progresso))  # vai de 500ms até 100ms

        # Alterna o piscar
        if tempo_atual - ultimo_piscar > radar_piscar_intervalo:
            radar_mostrar = not radar_mostrar
            ultimo_piscar = tempo_atual

        # Se tempo acabou
        if tempo_passado >= radar_tempo_total:
            radar_visivel = False
            print("Radar expirou")  # por enquanto, só mostra no console
            # Aqui depois dá pra aplicar punição, travar o personagem, etc.

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
                        obstaculos.append(Obstaculo("caminhao", random.randint(inicio, fim), -150, velocidade_atual))
                    else:
                        obstaculos.append(Obstaculo("carro", random.randint(inicio, fim), -100, velocidade_atual))

            # Atualiza timer e define um novo intervalo aleatório
            ultimo_spawn = tempo_atual
            intervalo_spawn = random.randint(200, 2000)

    # --- GERAR POSTES (sempre em pares, grudados na calçada) ---
    if not travado:
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_poste > intervalo_postes:
            largura_poste, altura_poste = 60, 60

            # Poste da esquerda (grudado na lateral da tela, dentro da calçada)
            obstaculos.append(Obstaculo("poste", 0, -30, velocidade_atual))

            # Poste da direita (grudado na outra lateral da tela, dentro da calçada)
            obstaculos.append(Obstaculo("poste", largura - 30, -30, velocidade_atual))

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
        if ob.tipo == "cachorro":
            dx = personagem_rect.centerx - ob.rect.centerx
            dy = personagem_rect.centery - ob.rect.centery
            distancia = (dx**2 + dy**2) ** 0.5

            # Se está próximo e ainda não seguindo
            if not getattr(ob, "seguindo", False) and distancia < distancia_ativacao_cachorro:
                ob.seguindo = True
                ob.tempo_inicio_seguir = pygame.time.get_ticks()

            # Se está seguindo o jogador
            if getattr(ob, "seguindo", False):
                tempo_agora = pygame.time.get_ticks()
                if tempo_agora - ob.tempo_inicio_seguir < duracao_seguir:
                    # movimento suave em direção ao jogador
                    direcao_x = dx / max(1, abs(dx))
                    ob.rect.x += int(direcao_x * 2)  # velocidade lateral
                else:
                    ob.seguindo = False  # para de seguir após o tempo

    # Desenhar tempo decorrido
    tempo_texto = font.render(f"Tempo: {tempo_decorrido}s", True, (255,255,255))
    tela.blit(tempo_texto, (largura//2 - tempo_texto.get_width()//2, 10))

    # Desenhar radar (se existir)
    if radar_visivel:
        if radar_mostrar:
            tela.blit(radar_img, radar_pos)

        # Barra de tempo (fica abaixo do radar)
        tempo_restante = max(0, radar_tempo_total - (pygame.time.get_ticks() - radar_inicio))
        barra_largura_max = radar_tamanho[0]
        barra_largura = int(barra_largura_max * (tempo_restante / radar_tempo_total))
        barra_altura = 10

        # Cor vai de verde -> amarelo -> vermelho
        progresso = tempo_restante / radar_tempo_total
        if progresso > 0.66:
            cor_barra = (0, 255, 0)
        elif progresso > 0.33:
            cor_barra = (255, 255, 0)
        else:
            cor_barra = (255, 0, 0)

        pygame.draw.rect(tela, cor_barra, (radar_pos[0], radar_pos[1] + radar_tamanho[1] + 5, barra_largura, barra_altura))
        pygame.draw.rect(tela, (255,255,255), (radar_pos[0], radar_pos[1] + radar_tamanho[1] + 5, barra_largura_max, barra_altura), 2)

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
                obstaculos.clear()
                obstaculos.append(Obstaculo("carro", random.randint(inicio, fim), -100, velocidade_inicial))
                tempo_inicial = pygame.time.get_ticks()
                tempo_decorrido = 0
                tempo_ultimo_aumento = 0
                fundo_y = 0
            if evento.key == pygame.K_u:
                invencivel = not invencivel
            if evento.key == pygame.K_s and radar_visivel:
                radar_visivel = False

