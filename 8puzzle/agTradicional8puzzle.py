import pygame
import random
import time
import copy
import statistics

pygame.init()

# Constantes da tela e configuração visual
LARGURA_TELA = 600
ALTURA_TELA = 780  # Aumentado para caber os controles
TAMANHO_PECA = 200
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (38, 114, 100)
AZUL = (70, 130, 180)
CINZA_CLARO = (240, 240, 240)
VERMELHO = (220, 20, 60)
AMARELO = (255, 215, 0)
FONTE_GRANDE = pygame.font.Font(None, 64)
FONTE_MEDIA = pygame.font.Font(None, 32)
FONTE_PEQUENA = pygame.font.Font(None, 24)

# Estado objetivo do puzzle
ESTADO_OBJETIVO = list(range(1, 9)) + [0]

# Configuração da tela
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("8-Puzzle com Algoritmo Genético")

# Carregamento das imagens do gato
try:
    imagens = {i: pygame.image.load(f"{i}.png") for i in range(1, 9)}
    usar_imagens = True
    print("Imagens do gato carregadas com sucesso!")
except:
    imagens = {}
    usar_imagens = False
    print("Não foi possível carregar as imagens - usando números")

# Parâmetros do algoritmo genético
TAMANHO_POPULACAO = 100
TAMANHO_GENOMA = 50
MAXIMO_GERACOES = float('inf')
TAXA_MUTACAO = 0.1

# Movimentos possíveis (cima, baixo, esquerda, direita)
MOVIMENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Variáveis globais para estatísticas corrigidas
estatisticas_globais = {
    'total_execucoes': 0,
    'media_geracoes': 0.0,
    'melhor_geracoes': None,      # Menor número de gerações (melhor desempenho)
    'pior_geracoes': None,        # Maior número de gerações (pior desempenho)
    'melhor_tempo': None,         # Menor tempo de execução
    'pior_tempo': None,           # Maior tempo de execução
    'tempo_total': 0.0,
    'media_tempo': 0.0,
    'historico_geracoes': [],
    'tempos_execucao': [],
    'distancias_iniciais': [],
    'movimentos_solucao': [],
    'desvio_padrao_geracoes': 0.0,
    'desvio_padrao_tempo': 0.0,
    'taxa_sucesso': 100.0,  # Assumindo 100% já que sempre encontra solução
    'execucoes_rapidas': 0,  # Execuções com menos de 1000 gerações
    'execucoes_lentas': 0    # Execuções com mais de 5000 gerações
}

def embaralhar_pecas():
    """Gera um estado inicial válido e solucionável para o puzzle"""
    while True:
        estado = list(range(1, 9)) + [0]
        random.shuffle(estado)
        if eh_solucionavel(estado):
            return estado

def eh_solucionavel(puzzle):
    """Verifica se o puzzle é solucionável usando inversões"""
    contador_inversoes = 0
    puzzle_plano = [peca for peca in puzzle if peca != 0]
    for i in range(len(puzzle_plano)):
        for j in range(i + 1, len(puzzle_plano)):
            if puzzle_plano[i] > puzzle_plano[j]:
                contador_inversoes += 1
    return contador_inversoes % 2 == 0

def distancia_manhattan(estado):
    """Calcula a distância Manhattan do estado atual para o objetivo"""
    distancia = 0
    for i, peca in enumerate(estado):
        if peca == 0:
            continue
        linha_objetivo, coluna_objetivo = divmod(peca - 1, 3)
        linha_atual, coluna_atual = divmod(i, 3)
        distancia += abs(linha_objetivo - linha_atual) + abs(coluna_objetivo - coluna_atual)
    return distancia

def aplicar_genoma(estado, genoma):
    """Aplica uma sequência de movimentos (genoma) ao estado do puzzle"""
    estado = estado[:]
    caminho = []
    for movimento in genoma:
        linha, coluna = divmod(estado.index(0), 3)
        nova_linha, nova_coluna = linha + movimento[0], coluna + movimento[1]
        if 0 <= nova_linha < 3 and 0 <= nova_coluna < 3:
            novo_indice = nova_linha * 3 + nova_coluna
            estado[estado.index(0)], estado[novo_indice] = estado[novo_indice], estado[estado.index(0)]
            caminho.append(novo_indice)
        if estado == ESTADO_OBJETIVO:
            break
    return estado, caminho

def calcular_aptidao(individuo, estado_inicial):
    """Calcula a aptidão de um indivíduo (quanto menor a distância, melhor)"""
    estado, caminho = aplicar_genoma(estado_inicial, individuo)
    return -distancia_manhattan(estado), caminho

def gerar_genoma_aleatorio():
    """Gera um genoma aleatório (sequência de movimentos)"""
    return [random.choice(MOVIMENTOS) for _ in range(TAMANHO_GENOMA)]

def mutar(genoma):
    """Aplica mutação a um genoma"""
    novo_genoma = genoma[:]
    for i in range(len(novo_genoma)):
        if random.random() < TAXA_MUTACAO:
            novo_genoma[i] = random.choice(MOVIMENTOS)
    return novo_genoma

def cruzamento(pai1, pai2):
    """Realiza cruzamento entre dois pais"""
    ponto = random.randint(1, TAMANHO_GENOMA - 1)
    return pai1[:ponto] + pai2[ponto:]

def atualizar_estatisticas(geracoes, tempo_execucao, distancia_inicial, movimentos):
    """Atualiza as estatísticas globais com os dados da execução atual"""
    stats = estatisticas_globais
    
    # Incrementa contador
    stats['total_execucoes'] += 1
    
    # Adiciona aos históricos
    stats['historico_geracoes'].append(geracoes)
    stats['tempos_execucao'].append(tempo_execucao)
    stats['distancias_iniciais'].append(distancia_inicial)
    stats['movimentos_solucao'].append(movimentos)
    
    # Atualiza tempo total
    stats['tempo_total'] += tempo_execucao
    
    # Atualiza melhor e pior gerações (CORRIGIDO)
    if stats['melhor_geracoes'] is None or geracoes < stats['melhor_geracoes']:
        stats['melhor_geracoes'] = geracoes
    
    if stats['pior_geracoes'] is None or geracoes > stats['pior_geracoes']:
        stats['pior_geracoes'] = geracoes
    
    # Atualiza melhor e pior tempo
    if stats['melhor_tempo'] is None or tempo_execucao < stats['melhor_tempo']:
        stats['melhor_tempo'] = tempo_execucao
    
    if stats['pior_tempo'] is None or tempo_execucao > stats['pior_tempo']:
        stats['pior_tempo'] = tempo_execucao
    
    # Calcula médias
    stats['media_geracoes'] = statistics.mean(stats['historico_geracoes'])
    stats['media_tempo'] = statistics.mean(stats['tempos_execucao'])
    
    # Calcula desvios padrão (se houver mais de 1 execução)
    if len(stats['historico_geracoes']) > 1:
        stats['desvio_padrao_geracoes'] = statistics.stdev(stats['historico_geracoes'])
        stats['desvio_padrao_tempo'] = statistics.stdev(stats['tempos_execucao'])
    
    # Conta execuções rápidas e lentas
    stats['execucoes_rapidas'] = sum(1 for g in stats['historico_geracoes'] if g < 1000)
    stats['execucoes_lentas'] = sum(1 for g in stats['historico_geracoes'] if g > 5000)

def desenhar_tabuleiro(pecas):
    """Desenha o tabuleiro do puzzle na tela"""
    tela.fill(BRANCO)
    for i in range(3):
        for j in range(3):
            valor = pecas[i * 3 + j]
            x = j * TAMANHO_PECA
            y = i * TAMANHO_PECA
            
            if valor != 0:
                if usar_imagens and valor in imagens:
                    # Usa as imagens do gato
                    imagem_redimensionada = pygame.transform.scale(imagens[valor], (TAMANHO_PECA - 4, TAMANHO_PECA - 4))
                    tela.blit(imagem_redimensionada, (x + 2, y + 2))
                else:
                    # Fallback para números se não houver imagens
                    pygame.draw.rect(tela, AZUL, (x + 5, y + 5, TAMANHO_PECA - 10, TAMANHO_PECA - 10))
                    texto = FONTE_GRANDE.render(str(valor), True, BRANCO)
                    texto_rect = texto.get_rect(center=(x + TAMANHO_PECA//2, y + TAMANHO_PECA//2))
                    tela.blit(texto, texto_rect)
            
            pygame.draw.rect(tela, PRETO, (x, y, TAMANHO_PECA, TAMANHO_PECA), 2)

def desenhar_controles_navegacao(passo_atual, total_passos):
    """Desenha os controles de navegação na parte inferior"""
    y_controles = 620
    
    # Fundo dos controles
    pygame.draw.rect(tela, CINZA_CLARO, (0, y_controles, LARGURA_TELA, 160))
    pygame.draw.line(tela, PRETO, (0, y_controles), (LARGURA_TELA, y_controles), 2)
    
    # Informações do passo atual
    info_passo = f"Passo {passo_atual} de {total_passos}"
    texto_info = FONTE_MEDIA.render(info_passo, True, PRETO)
    tela.blit(texto_info, (LARGURA_TELA//2 - texto_info.get_width()//2, y_controles + 10))
    
    # Botões de navegação
    botao_altura = 40
    botao_largura = 120  # Aumentado de 80 para 120
    y_botoes = y_controles + 50
    
    # Botão Anterior
    x_anterior = 80  # Ajustado para centralizar melhor
    cor_anterior = VERDE if passo_atual > 0 else CINZA_CLARO
    pygame.draw.rect(tela, cor_anterior, (x_anterior, y_botoes, botao_largura, botao_altura))
    pygame.draw.rect(tela, PRETO, (x_anterior, y_botoes, botao_largura, botao_altura), 2)
    
    # Seta para esquerda
    seta_esq = [(x_anterior + 25, y_botoes + 20), (x_anterior + 40, y_botoes + 10), (x_anterior + 40, y_botoes + 30)]
    if passo_atual > 0:
        pygame.draw.polygon(tela, BRANCO, seta_esq)
    
    texto_ant = FONTE_PEQUENA.render("ANTERIOR", True, BRANCO if passo_atual > 0 else PRETO)
    tela.blit(texto_ant, (x_anterior + 50, y_botoes + 12))
    
    # Botão Próximo
    x_proximo = 400  # Ajustado para centralizar melhor
    cor_proximo = VERDE if passo_atual < total_passos else CINZA_CLARO
    pygame.draw.rect(tela, cor_proximo, (x_proximo, y_botoes, botao_largura, botao_altura))
    pygame.draw.rect(tela, PRETO, (x_proximo, y_botoes, botao_largura, botao_altura), 2)
    
    # Seta para direita
    seta_dir = [(x_proximo + 95, y_botoes + 20), (x_proximo + 80, y_botoes + 10), (x_proximo + 80, y_botoes + 30)]
    if passo_atual < total_passos:
        pygame.draw.polygon(tela, BRANCO, seta_dir)
    
    texto_prox = FONTE_PEQUENA.render("PRÓXIMO", True, BRANCO if passo_atual < total_passos else PRETO)
    tela.blit(texto_prox, (x_proximo + 15, y_botoes + 12))
    
    # Instruções
    y_instrucoes = y_botoes + 60
    instrucoes = [
        "← → : Navegar    ESPAÇO: Nova execução    R: Ver relatório    ESC: Sair"
    ]
    
    for instrucao in instrucoes:
        texto = FONTE_PEQUENA.render(instrucao, True, PRETO)
        tela.blit(texto, (LARGURA_TELA//2 - texto.get_width()//2, y_instrucoes))
    
    pygame.display.flip()
    
    # Retorna as coordenadas dos botões para detecção de clique
    return {
        'anterior': (x_anterior, y_botoes, botao_largura, botao_altura),
        'proximo': (x_proximo, y_botoes, botao_largura, botao_altura)
    }

def executar_algoritmo_genetico():
    """Executa o algoritmo genético para resolver o puzzle"""
    estado_inicial = embaralhar_pecas()
    populacao = [gerar_genoma_aleatorio() for _ in range(TAMANHO_POPULACAO)]
    
    print("Estado inicial:", estado_inicial)
    print("Distância Manhattan inicial:", distancia_manhattan(estado_inicial))
    
    geracao = 0
    tempo_inicio = time.time()
    melhor_distancia_historico = []
    
    while True:
        # Avalia a população
        avaliados = [(calcular_aptidao(ind, estado_inicial), ind) for ind in populacao]
        avaliados.sort(reverse=True, key=lambda x: x[0][0])
        melhor_aptidao, melhor_genoma = avaliados[0]
        
        melhor_distancia_historico.append(-melhor_aptidao[0])
        
        # Verifica se encontrou solução
        if -melhor_aptidao[0] == 0:
            tempo_total = time.time() - tempo_inicio
            print(f"Solução encontrada na geração {geracao}!")
            print(f"Tempo total: {tempo_total:.2f} segundos")
            
            # Calcula informações da solução
            _, caminho_solucao = aplicar_genoma(estado_inicial, melhor_genoma)
            movimentos_solucao = len(caminho_solucao)
            distancia_inicial = distancia_manhattan(estado_inicial)
            
            # Atualiza estatísticas globais (USANDO FUNÇÃO CORRIGIDA)
            atualizar_estatisticas(geracao, tempo_total, distancia_inicial, movimentos_solucao)
            
            return estado_inicial, caminho_solucao, {
                'geracoes': geracao,
                'tempo': tempo_total,
                'distancia_inicial': distancia_inicial,
                'movimentos_solucao': movimentos_solucao,
                'historico_distancias': melhor_distancia_historico
            }
        
        # Log do progresso
        if geracao % 100 == 0:
            print(f"Geração {geracao}, Melhor distância: {-melhor_aptidao[0]}")
        
        # Cria nova população
        nova_populacao = []
        
        # Elitismo - mantém o melhor
        nova_populacao.append(melhor_genoma)
        
        # Gera o resto da população
        for _ in range(TAMANHO_POPULACAO - 1):
            pai1 = random.choice(avaliados[:20])[1]  # Seleção dos 20 melhores
            pai2 = random.choice(avaliados[:20])[1]
            filho = mutar(cruzamento(pai1, pai2))
            nova_populacao.append(filho)
        
        populacao = nova_populacao
        geracao += 1

def gerar_estados_navegacao(inicial, caminho):
    """Gera todos os estados intermediários para navegação"""
    estados = [inicial[:]]  # Estado inicial
    pecas_atual = inicial[:]
    
    for indice_movimento in caminho:
        indice_zero = pecas_atual.index(0)
        pecas_atual[indice_zero], pecas_atual[indice_movimento] = pecas_atual[indice_movimento], pecas_atual[indice_zero]
        estados.append(pecas_atual[:])
    
    return estados

def navegacao_solucao(inicial, caminho):
    """Permite navegação manual pelos passos da solução"""
    estados = gerar_estados_navegacao(inicial, caminho)
    passo_atual = 0
    total_passos = len(estados) - 1
    
    while True:
        # Desenha o estado atual
        desenhar_tabuleiro(estados[passo_atual])
        botoes = desenhar_controles_navegacao(passo_atual, total_passos)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'sair'
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and passo_atual > 0:
                    passo_atual -= 1
                elif evento.key == pygame.K_RIGHT and passo_atual < total_passos:
                    passo_atual += 1
                elif evento.key == pygame.K_SPACE:
                    return 'nova_execucao'
                elif evento.key == pygame.K_r:
                    return 'relatorio'
                elif evento.key == pygame.K_ESCAPE:
                    return 'sair'
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clique esquerdo
                    mouse_x, mouse_y = evento.pos
                    
                    # Verifica clique no botão anterior
                    ant_x, ant_y, ant_w, ant_h = botoes['anterior']
                    if ant_x <= mouse_x <= ant_x + ant_w and ant_y <= mouse_y <= ant_y + ant_h:
                        if passo_atual > 0:
                            passo_atual -= 1
                    
                    # Verifica clique no botão próximo
                    prox_x, prox_y, prox_w, prox_h = botoes['proximo']
                    if prox_x <= mouse_x <= prox_x + prox_w and prox_y <= mouse_y <= prox_y + prox_h:
                        if passo_atual < total_passos:
                            passo_atual += 1

def mostrar_relatorio(info_execucao):
    """Mostra um relatório detalhado da execução"""
    tela.fill(CINZA_CLARO)
    y_pos = 10
    
    # Título
    titulo = FONTE_MEDIA.render("=== RELATÓRIO DE EXECUÇÃO ===", True, PRETO)
    tela.blit(titulo, (LARGURA_TELA//2 - titulo.get_width()//2, y_pos))
    y_pos += 40
    
    # Informações da execução atual
    info_atual = [
        f"Execução #{estatisticas_globais['total_execucoes']}",
        f"Gerações necessárias: {info_execucao['geracoes']}",
        f"Tempo de execução: {info_execucao['tempo']:.2f}s",
        f"Distância Manhattan inicial: {info_execucao['distancia_inicial']}",
        f"Movimentos na solução: {info_execucao['movimentos_solucao']}",
        f"Eficiência: {info_execucao['movimentos_solucao']}/{info_execucao['geracoes']} mov/ger"
    ]
    
    for info in info_atual:
        cor = VERMELHO if "Execução #" in info else PRETO
        texto = FONTE_PEQUENA.render(info, True, cor)
        tela.blit(texto, (20, y_pos))
        y_pos += 22
    
    y_pos += 15
    
    # Estatísticas globais (se houver execuções)
    if estatisticas_globais['total_execucoes'] > 0:
        subtitulo = FONTE_MEDIA.render("=== ESTATÍSTICAS GERAIS ===", True, PRETO)
        tela.blit(subtitulo, (LARGURA_TELA//2 - subtitulo.get_width()//2, y_pos))
        y_pos += 35
        
        stats = estatisticas_globais
        
        # Estatísticas principais
        stats_principais = [
            f"Total de execuções: {stats['total_execucoes']}",
            f"Média de gerações: {stats['media_geracoes']:.1f}",
            f"Melhor desempenho: {stats['melhor_geracoes']} gerações",
            f"Pior desempenho: {stats['pior_geracoes']} gerações",
            f"Variação: {stats['pior_geracoes'] - stats['melhor_geracoes']} gerações"
        ]
        
        for stat in stats_principais:
            cor = VERDE if "Melhor" in stat else (VERMELHO if "Pior" in stat else PRETO)
            texto = FONTE_PEQUENA.render(stat, True, cor)
            tela.blit(texto, (20, y_pos))
            y_pos += 22
        
        y_pos += 10
        
        # Estatísticas de tempo
        stats_tempo = [
            f"Tempo médio: {stats['media_tempo']:.2f}s",
            f"Melhor tempo: {stats['melhor_tempo']:.2f}s",
            f"Pior tempo: {stats['pior_tempo']:.2f}s",
            f"Tempo total: {stats['tempo_total']:.2f}s"
        ]
        
        for stat in stats_tempo:
            texto = FONTE_PEQUENA.render(stat, True, PRETO)
            tela.blit(texto, (20, y_pos))
            y_pos += 22
        
        # Estatísticas avançadas (se houver mais de 1 execução)
        if stats['total_execucoes'] > 1:
            y_pos += 10
            stats_avancadas = [
                f"Desvio padrão (gerações): ±{stats['desvio_padrao_geracoes']:.1f}",
                f"Desvio padrão (tempo): ±{stats['desvio_padrao_tempo']:.2f}s",
                f"Execuções rápidas (<1000 ger): {stats['execucoes_rapidas']}",
                f"Execuções lentas (>5000 ger): {stats['execucoes_lentas']}"
            ]
            
            for stat in stats_avancadas:
                texto = FONTE_PEQUENA.render(stat, True, PRETO)
                tela.blit(texto, (20, y_pos))
                y_pos += 22
    
    # Instruções
    y_pos = ALTURA_TELA - 60
    instrucoes = [
        "ESPAÇO - Nova execução    V - Ver solução    ESC - Sair"
    ]
    
    for instrucao in instrucoes:
        texto = FONTE_PEQUENA.render(instrucao, True, VERDE)
        tela.blit(texto, (20, y_pos))
        y_pos += 22
    
    pygame.display.flip()

# Loop principal
executando = True
estado_inicial = None
caminho = None
info_execucao = None

while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
    
    # Executa o algoritmo genético
    estado_inicial, caminho, info_execucao = executar_algoritmo_genetico()
    
    # Loop de navegação
    navegando = True
    while navegando and executando:
        acao = navegacao_solucao(estado_inicial, caminho)
        
        if acao == 'sair':
            navegando = False
            executando = False
        elif acao == 'nova_execucao':
            navegando = False
        elif acao == 'relatorio':
            # Mostra o relatório
            mostrar_relatorio(info_execucao)
            
            # Aguarda input do usuário no relatório
            aguardando_relatorio = True
            while aguardando_relatorio:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        aguardando_relatorio = False
                        navegando = False
                        executando = False
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_SPACE:
                            aguardando_relatorio = False
                            navegando = False
                        elif evento.key == pygame.K_v:
                            aguardando_relatorio = False
                        elif evento.key == pygame.K_ESCAPE:
                            aguardando_relatorio = False
                            navegando = False
                            executando = False

pygame.quit()

print("\n" + "="*50)
print("           RELATÓRIO FINAL DETALHADO")
print("="*50)

stats = estatisticas_globais
if stats['total_execucoes'] > 0:
    print(f"📊 Execuções totais: {stats['total_execucoes']}")
    print(f"⏱️  Tempo total: {stats['tempo_total']:.2f}s")
    print(f"📈 Média de gerações: {stats['media_geracoes']:.1f}")
    print(f"🏆 Melhor desempenho: {stats['melhor_geracoes']} gerações")
    print(f"📉 Pior desempenho: {stats['pior_geracoes']} gerações")
    print(f"📊 Variação: {stats['pior_geracoes'] - stats['melhor_geracoes']} gerações")
    
    if stats['total_execucoes'] > 1:
        print(f"📏 Desvio padrão: ±{stats['desvio_padrao_geracoes']:.1f} gerações")
        print(f"⚡ Execuções rápidas: {stats['execucoes_rapidas']}")
        print(f"🐌 Execuções lentas: {stats['execucoes_lentas']}")
    
    print(f"🎯 Consistência: {((stats['melhor_geracoes']/stats['media_geracoes']) * 100):.1f}%")
else:
    print("Nenhuma execução foi completada.")

print("="*50)
print("Programa encerrado.")