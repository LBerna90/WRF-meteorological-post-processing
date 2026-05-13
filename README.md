# WRF-meteorological-post-processing
Produtos meteorológicos plotados a partir de saídas de simulação do modelo WRF.

# PNMM.py
Este código cria mapas da Pressão Atmosférica em Superfície em cores. Para cada domínio
do modelo processado o código gera: 
1 - Uma pasta dedicada dentro do diretório PNMM.
2 - Um mapa de pressão para cada passo de tempo da simulação.
3 - Um GIF animado, permitindo visualizar a evolução dos sistemas de pressão (centros de alta e baixa pressão) ao longo do tempo.

<img width="2155" height="1625" alt="PNMM_d01_2026-05-06_06" src="https://github.com/user-attachments/assets/5b826830-dc95-4fd9-9ce2-907e151b585e" />

# Precipitacao.py
Este código cria diversos mapas de precipitação acumulada e pressão atmosférica. O script gera imagens de precipitação para cinco janelas diferentes: 1h, 3h, 6h, 12h e 24h. O código organiza os resultados na seguinte estrutura de pastas: 
Precipitação → Domínio (d01, d02, d03) → Janela (01h, 03h, etc.)
Dentro de cada pasta, ele gera: 1 - Mapas (jpg) para cada passo de tempo, mostrando a chuva daquela janela de acumulação e as linhas de pressão. 2 - Uma animação (GIF) da evolução da chuva e da pressão para aquele domínio e aquela janela de tempo.

<img width="1023" height="844" alt="PREC_d01_01h_2026-05-06_05" src="https://github.com/user-attachments/assets/23a85874-19b4-49be-b34b-37c026783065" />

# Prec+windbar.py 
Este código produz mapas com as seguintes informações: Precipitação Acumulada (1h, 3h, 6h, 12h e 24h), Pressão ao Nível Médio do Mar (PNMM) e Velocidade do Vento a 10 metros. Os resultados são organizados em diretórios da seguinte forma: PREC+WINDBAR → Domínio → Janela de Tempo. Dentro de cada pasta, ele gera: 1 - Mapas (jpg) para cada passo de tempo, mostrando a chuva daquela janela de acumulação, velocidade do vento e as isobaras de pressão. 2 - Uma animação (GIF) da evolução da chuva, vento e pressão para aquele domínio e aquela janela de tempo.

<img width="1924" height="1627" alt="PREC_d01_01h_2026-05-06_04" src="https://github.com/user-attachments/assets/87a721ca-8e6b-4880-b0cd-c2aad3235677" />

# TEMP_2m.py 
Este código gera mapas combinando a Temperatura a 2 metros e a Pressão ao Nível Médio do Mar. O script organiza os resultados na pasta Temperatura_PNMM → Domínio (d01, d02, d03). Dentro de cada pasta, ele gera: 1 - Mapas (jpg) da temperatura e pressão NMM para cada passo de tempo. 2 - Uma animação (GIF) da evolução daquela janela de tempo.

<img width="2110" height="1687" alt="T2_PNMM_d01_2026-05-06_02" src="https://github.com/user-attachments/assets/9c53e88f-7669-4862-886b-d6162d9621c3" />

# Vento.py
Este código cria mapas de vento (barbelas) em diferentes níveis da atmosfera (Superfície, 925hPa, 850hPa, 700hPa, 500hPa, 300hPa, 250hPa e 200hPa). O script organiza os resultados na pasta VENTO_SUPERFICIE_ALTURA → Domínio → Nível de Pressão. Dentro de cada pasta, ele gera: 1 - Mapas (jpg) para cada passo de tempo, mostrando a velocidade do vento e as linhas de pressão. 2 - Animação (GIF) da evolução da chuva e da pressão para aquele domínio e aquela janela de tempo.

<img width="1636" height="1627" alt="WIND_d01_surface_2026-05-06_04" src="https://github.com/user-attachments/assets/448c0bbf-4690-4141-b741-0aaae929f71f" />

# vento_cores.py
Este código cria mapas de vento ilustrando a velocidade em cores, para diferentes níveis da atmosfera (Superfície, 925hPa, 850hPa, 700hPa, 500hPa, 300hPa, 250hPa e 200hPa). O script organiza os resultados na pasta VENTO_SUPERFICIE_ALTURA → Domínio → Nível de Pressão. Dentro de cada pasta, ele gera: 1 - Mapas (jpg) para cada passo de tempo, mostrando a velocidade do vento e as linhas de pressão. 2 - Animação (GIF) da evolução da chuva e da pressão para aquele domínio e aquela janela de tempo.

<img width="1927" height="1651" alt="WINDSPD_d01_surface_2026-05-06_05" src="https://github.com/user-attachments/assets/701c895c-fa0f-4391-b91b-aa96ddb00e27" />

# skew-t.py
Este script cria um diagrama skew-t de uma localização lat/lon para cada passo de tempo da simulação e para cada domínio encontrado no diretório. Os resultados são organizados em diretórios da seguinte forma: skew-t_horario → Domínio 

<img width="1233" height="1235" alt="skewt_d01_20260506_0102" src="https://github.com/user-attachments/assets/e1e85875-adae-46a0-9c12-f2e875706ad4" />

# painel.py
Este código extrai a evolução temporal de diversas variáveis atmosféricas em um ponto lat/lon específico e gera uma imagem com 4 painéis para cada domínio disponível.
Painel 1: Secção atmosférica vertical ao longo do tempo. Eixo X: Tempo (Horário Local). Eixo Y: Altitude (metros) à esquerda e Pressão (hPa) à direita. Linhas isotermas com destaque para a linha de 0 °C e barbelas de vento.
Painel 2: Gráfico de linhas ao longo do tempo ilustrando a evolução da Temperatura (2m), Ponto de Orvalho e Umidade Relativa. 
Painel 3: Gráfico em barras da precipitação horária.
Painel 4: Gráfico de linha ilustrando a Velocidade do vento em 10m e a Pressão Atmosférica em superfície.

<img width="4500" height="5400" alt="secao_vertical_superficie_real_isotermas_precip_d02" src="https://github.com/user-attachments/assets/d4630d67-3daf-4f56-83b9-ffb2b30042b8" />

# imagem.sh
Esse script roda todos os códigos python deste diretório.


