import pygame
import random
import time
import statistics
import math

pygame.init()

LARGURA_TELA = 600
ALTURA_TELA = 780  
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

ESTADO_OBJETIVO = [1, 2, 3, 4, 5, 6, 7, 8, 0]

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("8-Puzzle com Algoritmo Genético (Modelo com Ilhas)")

try:
    imagens = {i: pygame.image.load(f"{i}.png") for i in range(1, 9)}
    usar_imagens = True
    print("Imagens do gato carregadas com sucesso!")
except:
    imagens = {}
    usar_imagens = False
    print("Não foi possível carregar as imagens - usando números")

o
TAMANHO_POPULACAO = 100  
NUM_ILHAS = 4  
TAMANHO_GENOMA = 50
MAXIMO_GERACOES = float('inf')
TAXA_MUTACAO = 0.1
INTERVALO_MIGRACAO = 50 
NUM_MIGRANTES = 5  

MOVIMENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

estatisticas_globais = {
    'total_execucoes': 0,
    'media_geracoes': 0.0,
    'melhor_geracoes': None,
    'pior_geracoes': None,
    'melhor_tempo': None,
    'pior_tempo': None,
    'tempo_total': 0.0,
    'media_tempo': 0.0,
    'historico_geracoes': [],
    'tempos_execucao': [],
    'distancias_iniciais': [],
    'movimentos_solucao': [],
    'desvio_padrao_geracoes': 0.0,
    'desvio_padrao_tempo': 0.0,
    'taxa_sucesso': 100.0,
    'execucoes_rapidas': 0,
    'execucoes_lentas': 0,
    'migracoes_realizadas': 0,
    'melhor_ilha': None,
    'historico_migracoes': []
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

def atualizar_estatisticas(geracoes, tempo_execucao, distancia_inicial, movimentos, migracoes, ilha_vencedora):
    """Atualiza as estatísticas globais com os dados da execução atual"""
    stats = estatisticas_globais
    
    stats['total_execucoes'] += 1
    
    stats['historico_geracoes'].append(geracoes)
    stats['tempos_execucao'].append(tempo_execucao)
    stats['distancias_iniciais'].append(distancia_inicial)
    stats['movimentos_solucao'].append(movimentos)
    stats['historico_migracoes'].append({
        'migracoes': migracoes,
        'ilha_vencedora': ilha_vencedora
    })
    stats['migracoes_realizadas'] += migracoes
    stats['melhor_ilha'] = ilha_vencedora
    
    stats['tempo_total'] += tempo_execucao

    if stats['melhor_geracoes'] is None or geracoes < stats['melhor_geracoes']:
        stats['melhor_geracoes'] = geracoes
    
    if stats['pior_geracoes'] is None or geracoes > stats['pior_geracoes']:
        stats['pior_geracoes'] = geracoes

    if stats['melhor_tempo'] is None or tempo_execucao < stats['melhor_tempo']:
        stats['melhor_tempo'] = tempo_execucao
    
    if stats['pior_tempo'] is None or tempo_execucao > stats['pior_tempo']:
        stats['pior_tempo'] = tempo_execucao
    
    stats['media_geracoes'] = statistics.mean(stats['historico_geracoes'])
    stats['media_tempo'] = statistics.mean(stats['tempos_execucao'])
    
    if len(stats['historico_geracoes']) > 1:
        stats['desvio_padrao_geracoes'] = statistics.stdev(stats['historico_geracoes'])
        stats['desvio_padrao_tempo'] = statistics.stdev(stats['tempos_execucao'])
    
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
                    imagem_redimensionada = pygame.transform.scale(imagens[valor], (TAMANHO_PECA - 4, TAMANHO_PECA - 4))
                    tela.blit(imagem_redimensionada, (x + 2, y + 2))
                else:
                    pygame.draw.rect(tela, AZUL, (x + 5, y + 5, TAMANHO_PECA - 10, TAMANHO_PECA - 10))
                    texto = FONTE_GRANDE.render(str(valor), True, BRANCO)
                    texto_rect = texto.get_rect(center=(x + TAMANHO_PECA//2, y + TAMANHO_PECA//2))
                    tela.blit(texto, texto_rect)
            
            pygame.draw.rect(tela, PRETO, (x, y, TAMANHO_PECA, TAMANHO_PECA), 2)

def desenhar_controles_navegacao(passo_atual, total_passos):
    """Desenha os controles de navegação na parte inferior"""
    y_controles = 620
    
    pygame.draw.rect(tela, CINZA_CLARO, (0, y_controles, LARGURA_TELA, 160))
    pygame.draw.line(tela, PRETO, (0, y_controles), (LARGURA_TELA, y_controles), 2)
    
    info_passo = f"Passo {passo_atual} de {total_passos}"
    texto_info = FONTE_MEDIA.render(info_passo, True, PRETO)
    tela.blit(texto_info, (LARGURA_TELA//2 - texto_info.get_width()//2, y_controles + 10))

    botao_altura = 40
    botao_largura = 120
    y_botoes = y_controles + 50

    x_anterior = 80
    cor_anterior = VERDE if passo_atual > 0 else CINZA_CLARO
    pygame.draw.rect(tela, cor_anterior, (x_anterior, y_botoes, botao_largura, botao_altura))
    pygame.draw.rect(tela, PRETO, (x_anterior, y_botoes, botao_largura, botao_altura), 2)

    seta_esq = [(x_anterior + 25, y_botoes + 20), (x_anterior + 40, y_botoes + 10), (x_anterior + 40, y_botoes + 30)]
    if passo_atual > 0:
        pygame.draw.polygon(tela, BRANCO, seta_esq)
    
    texto_ant = FONTE_PEQUENA.render("ANTERIOR", True, BRANCO if passo_atual > 0 else PRETO)
    tela.blit(texto_ant, (x_anterior + 50, y_botoes + 12))

    x_proximo = 400
    cor_proximo = VERDE if passo_atual < total_passos else CINZA_CLARO
    pygame.draw.rect(tela, cor_proximo, (x_proximo, y_botoes, botao_largura, botao_altura))
    pygame.draw.rect(tela, PRETO, (x_proximo, y_botoes, botao_largura, botao_altura), 2)

    seta_dir = [(x_proximo + 95, y_botoes + 20), (x_proximo + 80, y_botoes + 10), (x_proximo + 80, y_botoes + 30)]
    if passo_atual < total_passos:
        pygame.draw.polygon(tela, BRANCO, seta_dir)
    
    texto_prox = FONTE_PEQUENA.render("PRÓXIMO", True, BRANCO if passo_atual < total_passos else PRETO)
    tela.blit(texto_prox, (x_proximo + 15, y_botoes + 12))

    y_instrucoes = y_botoes + 60
    instrucoes = [
        "← → : Navegar    ESPAÇO: Nova execução    R: Ver relatório    ESC: Sair"
    ]
    
    for instrucao in instrucoes:
        texto = FONTE_PEQUENA.render(instrucao, True, PRETO)
        tela.blit(texto, (LARGURA_TELA//2 - texto.get_width()//2, y_instrucoes))
    
    pygame.display.flip()
    
    return {
        'anterior': (x_anterior, y_botoes, botao_largura, botao_altura),
        'proximo': (x_proximo, y_botoes, botao_largura, botao_altura)
    }

def executar_algoritmo_genetico_com_ilhas():
    """Executa o algoritmo genético com modelo de ilhas para resolver o puzzle"""
    estado_inicial = embaralhar_pecas()
    
    ilhas = [[gerar_genoma_aleatorio() for _ in range(TAMANHO_POPULACAO)] for _ in range(NUM_ILHAS)]
    
    print("Estado inicial:", estado_inicial)
    print("Distância Manhattan inicial:", distancia_manhattan(estado_inicial))
    
    geracao = 0
    tempo_inicio = time.time()
    melhor_distancia_historico = []
    migracoes_realizadas = 0
    ilha_vencedora = None
    
    while True:
        melhores_por_ilha = []
        for i in range(NUM_ILHAS):
            avaliados = [(calcular_aptidao(ind, estado_inicial), ind) for ind in ilhas[i]]
            avaliados.sort(reverse=True, key=lambda x: x[0][0])
            melhor_aptidao, melhor_genoma = avaliados[0]
            melhores_por_ilha.append((melhor_aptidao, melhor_genoma, i))

            if -melhor_aptidao[0] == 0:
                tempo_total = time.time() - tempo_inicio
                print(f"Solução encontrada na geração {geracao} na ilha {i}!")
                print(f"Tempo total: {tempo_total:.2f} segundos")
                print(f"Migrações realizadas: {migracoes_realizadas}")

                _, caminho_solucao = aplicar_genoma(estado_inicial, melhor_genoma)
                movimentos_solucao = len(caminho_solucao)
                distancia_inicial = distancia_manhattan(estado_inicial)

                atualizar_estatisticas(geracao, tempo_total, distancia_inicial, 
                                      movimentos_solucao, migracoes_realizadas, i)
                
                return estado_inicial, caminho_solucao, {
                    'geracoes': geracao,
                    'tempo': tempo_total,
                    'distancia_inicial': distancia_inicial,
                    'movimentos_solucao': movimentos_solucao,
                    'historico_distancias': melhor_distancia_historico,
                    'migracoes': migracoes_realizadas,
                    'ilha_vencedora': i
                }
        

        melhor_global = max(melhores_por_ilha, key=lambda x: x[0][0])
        melhor_distancia_historico.append(-melhor_global[0][0])
        
        if geracao % 100 == 0:
            print(f"Geração {geracao}, Melhor distância: {-melhor_global[0][0]}")
        
        if geracao > 0 and geracao % INTERVALO_MIGRACAO == 0:

            migrantes = []
            for i in range(NUM_ILHAS):
        
                avaliados = [(calcular_aptidao(ind, estado_inicial), ind) for ind in ilhas[i]]
                avaliados.sort(reverse=True, key=lambda x: x[0][0])
                migrantes.extend([ind for (_, ind) in avaliados[:NUM_MIGRANTES]])
            

            random.shuffle(migrantes)
            
            for i in range(NUM_ILHAS):
           
                avaliados = [(calcular_aptidao(ind, estado_inicial), ind) for ind in ilhas[i]]
                avaliados.sort(reverse=True, key=lambda x: x[0][0])
                ilhas[i] = [ind for (_, ind) in avaliados[:-NUM_MIGRANTES]]
                 
                ilhas[i].extend(migrantes[i*NUM_MIGRANTES:(i+1)*NUM_MIGRANTES])
            
            migracoes_realizadas += 1
            print(f"Migração realizada na geração {geracao}")
        
     
        for i in range(NUM_ILHAS):
            
            avaliados = [(calcular_aptidao(ind, estado_inicial), ind) for ind in ilhas[i]]
            avaliados.sort(reverse=True, key=lambda x: x[0][0])
            
      
            nova_populacao = []
            

            nova_populacao.append(avaliados[0][1])
            

            for _ in range(TAMANHO_POPULACAO - 1):
                pai1 = random.choice(avaliados[:20])[1]  
                pai2 = random.choice(avaliados[:20])[1]
                filho = mutar(cruzamento(pai1, pai2))
                nova_populacao.append(filho)
            
            ilhas[i] = nova_populacao
        
        geracao += 1

def gerar_estados_navegacao(inicial, caminho):
    """Gera todos os estados intermediários para navegação"""
    estados = [inicial[:]]  
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
                if evento.button == 1:  
                    mouse_x, mouse_y = evento.pos
                    

                    ant_x, ant_y, ant_w, ant_h = botoes['anterior']
                    if ant_x <= mouse_x <= ant_x + ant_w and ant_y <= mouse_y <= ant_y + ant_h:
                        if passo_atual > 0:
                            passo_atual -= 1
                    
                    prox_x, prox_y, prox_w, prox_h = botoes['proximo']
                    if prox_x <= mouse_x <= prox_x + prox_w and prox_y <= mouse_y <= prox_y + prox_h:
                        if passo_atual < total_passos:
                            passo_atual += 1

def mostrar_relatorio(info_execucao):
    """Mostra um relatório detalhado da execução"""
    tela.fill(CINZA_CLARO)
    y_pos = 10
    
    titulo = FONTE_MEDIA.render("=== RELATÓRIO DE EXECUÇÃO ===", True, PRETO)
    tela.blit(titulo, (LARGURA_TELA//2 - titulo.get_width()//2, y_pos))
    y_pos += 40

    info_atual = [
        f"Execução #{estatisticas_globais['total_execucoes']}",
        f"Gerações necessárias: {info_execucao['geracoes']}",
        f"Tempo de execução: {info_execucao['tempo']:.2f}s",
        f"Distância Manhattan inicial: {info_execucao['distancia_inicial']}",
        f"Movimentos na solução: {info_execucao['movimentos_solucao']}",
        f"Eficiência: {info_execucao['movimentos_solucao']}/{info_execucao['geracoes']} mov/ger",
        f"Migrações realizadas: {info_execucao['migracoes']}",
        f"Ilha vencedora: {info_execucao['ilha_vencedora'] + 1}"
    ]
    
    for info in info_atual:
        cor = VERMELHO if "Execução #" in info else (AZUL if "Ilha vencedora" in info else PRETO)
        texto = FONTE_PEQUENA.render(info, True, cor)
        tela.blit(texto, (20, y_pos))
        y_pos += 22
    
    y_pos += 15
    
    if estatisticas_globais['total_execucoes'] > 0:
        subtitulo = FONTE_MEDIA.render("=== ESTATÍSTICAS GERAIS ===", True, PRETO)
        tela.blit(subtitulo, (LARGURA_TELA//2 - subtitulo.get_width()//2, y_pos))
        y_pos += 35
        
        stats = estatisticas_globais
        
        stats_principais = [
            f"Total de execuções: {stats['total_execucoes']}",
            f"Média de gerações: {stats['media_geracoes']:.1f}",
            f"Melhor desempenho: {stats['melhor_geracoes']} gerações",
            f"Pior desempenho: {stats['pior_geracoes']} gerações",
            f"Variação: {stats['pior_geracoes'] - stats['melhor_geracoes']} gerações",
            f"Total de migrações: {stats['migracoes_realizadas']}",
            f"Média de migrações/execução: {stats['migracoes_realizadas']/stats['total_execucoes']:.1f}"
        ]
        
        for stat in stats_principais:
            cor = VERDE if "Melhor" in stat else (VERMELHO if "Pior" in stat else (AZUL if "migrações" in stat else PRETO))
            texto = FONTE_PEQUENA.render(stat, True, cor)
            tela.blit(texto, (20, y_pos))
            y_pos += 22
        
        y_pos += 10
        
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
        
        if stats['melhor_ilha'] is not None:
            y_pos += 10
            texto_ilhas = FONTE_PEQUENA.render("Distribuição de ilhas vencedoras:", True, AZUL)
            tela.blit(texto_ilhas, (20, y_pos))
            y_pos += 22
            
            vitorias_ilhas = [0] * NUM_ILHAS
            for mig in stats['historico_migracoes']:
                if mig['ilha_vencedora'] is not None:
                    vitorias_ilhas[mig['ilha_vencedora']] += 1
            
            for i, vitorias in enumerate(vitorias_ilhas):
                texto = FONTE_PEQUENA.render(f"Ilha {i+1}: {vitorias} vitórias ({vitorias/stats['total_execucoes']:.1%})", True, AZUL)
                tela.blit(texto, (40, y_pos))
                y_pos += 22
    
    y_pos = ALTURA_TELA - 60
    instrucoes = [
        "ESPAÇO - Nova execução    V - Ver solução    ESC - Sair"
    ]
    
    for instrucao in instrucoes:
        texto = FONTE_PEQUENA.render(instrucao, True, VERDE)
        tela.blit(texto, (20, y_pos))
        y_pos += 22
    
    pygame.display.flip()


executando = True
estado_inicial = None
caminho = None
info_execucao = None

while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

    estado_inicial, caminho, info_execucao = executar_algoritmo_genetico_com_ilhas()
    
    navegando = True
    while navegando and executando:
        acao = navegacao_solucao(estado_inicial, caminho)
        
        if acao == 'sair':
            navegando = False
            executando = False
        elif acao == 'nova_execucao':
            navegando = False
        elif acao == 'relatorio':
            mostrar_relatorio(info_execucao)
            
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
    print(f" Execuções totais: {stats['total_execucoes']}")
    print(f"  Tempo total: {stats['tempo_total']:.2f}s")
    print(f" Média de gerações: {stats['media_geracoes']:.1f}")
    print(f"Melhor desempenho: {stats['melhor_geracoes']} gerações")
    print(f"Pior desempenho: {stats['pior_geracoes']} gerações")
    print(f" Variação: {stats['pior_geracoes'] - stats['melhor_geracoes']} gerações")
    print(f" Total de migrações: {stats['migracoes_realizadas']}")
    print(f" Média de migrações/execução: {stats['migracoes_realizadas']/stats['total_execucoes']:.1f}")
    
    if stats['total_execucoes'] > 1:
        print(f" Desvio padrão: ±{stats['desvio_padrao_geracoes']:.1f} gerações")
        print(f"Execuções rápidas: {stats['execucoes_rapidas']}")
        print(f"Execuções lentas: {stats['execucoes_lentas']}")
    
    print(f"Consistência: {((stats['melhor_geracoes']/stats['media_geracoes']) * 100):.1f}%")
    
    if stats['melhor_ilha'] is not None:
        print("\nDistribuição de ilhas vencedoras:")
        vitorias_ilhas = [0] * NUM_ILHAS
        for mig in stats['historico_migracoes']:
            if mig['ilha_vencedora'] is not None:
                vitorias_ilhas[mig['ilha_vencedora']] += 1
        
        for i, vitorias in enumerate(vitorias_ilhas):
            print(f" Ilha {i+1}: {vitorias} vitórias ({vitorias/stats['total_execucoes']:.1%})")
else:
    print("Nenhuma execução foi completada.")

print("="*50)
print("Programa encerrado.")