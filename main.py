import math
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from urllib.request import urlopen
from io import BytesIO

# Função para quantizar o sinal (ou imagem)
def quantizar_sinal(sinal, num_niveis):
    valor_min = np.min(sinal)
    valor_max = np.max(sinal)
    # Eixo Y do sinal quantizado
    niveis_quant = np.linspace(valor_min, valor_max, num_niveis)
    sinal_quantizado = np.round((sinal - valor_min) / (valor_max - valor_min) * (num_niveis - 1)) / (num_niveis - 1) * (valor_max - valor_min) + valor_min
    return sinal_quantizado, niveis_quant

# Função para transformar a função quantizada, para uma representação em binários
def gerar_codigo_binario(sinal_quantizado, num_niveis):
    num_bits = int(np.ceil(np.log2(num_niveis)))
    codigo_binario = [
        np.binary_repr(
            int((nivel - np.min(sinal_quantizado)) * (num_niveis - 1) / (np.max(sinal_quantizado) - np.min(sinal_quantizado))), 
            width=num_bits
        ) 
        for nivel in sinal_quantizado.flatten()
    ]
    return codigo_binario, num_bits

def codificar_nrz(sinal, bin=False):
    threshold = None
    sinal_codificado = []
    values = list(set(sinal))
    pair = True
    if bin:
        values_int = sorted([int(v, 2) for v in values], reverse=True)
        if len(values_int) % 2 == 0:
            threshold = values_int[int(len(values_int)/2) - 1]
        else:
            pair = False
            threshold = values_int[int(math.floor(len(values_int)/2))]
        for i in sinal:
            if pair:
                if int(i, 2) > threshold:
                    sinal_codificado.append(1)
                else:
                    sinal_codificado.append(-1)
            else:
                if int(i, 2) >= threshold:
                    sinal_codificado.append(1)
                else:
                    sinal_codificado.append(-1)
    else:
        values = sorted(values)
        if len(values) % 2 == 0:
            threshold = values[int(len(values)/2) - 1]
        else:
            pair = False
            threshold = values[int(math.floor(len(values)/2))]
        for i in sinal:
            if pair:
                if i > threshold:
                    sinal_codificado.append(1)
                else:
                    sinal_codificado.append(-1)
            else:
                if i >= threshold:
                    sinal_codificado.append(1)
                else:
                    sinal_codificado.append(-1)
    return sinal_codificado

# Função para plotar a transformada de Fourier da senoide
def plot_fft_sen(ax, signal, sampling_rate, title):
    N = len(signal)
    T = 1.0 / sampling_rate
    yf = np.fft.fft(signal)
    xf = np.fft.fftfreq(N, T)
    
    yf_shifted = np.fft.fftshift(yf)
    xf_shifted = np.fft.fftshift(xf)
    
    ax.plot(xf_shifted, 2.0/N * np.abs(yf_shifted))
    ax.grid()
    ax.set_xlabel('Frequência (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_title(title)

# Função para plotar a transformada de Fourier da imagem
def plot_fft_img(ax, signal, title):
    fft_signal = np.fft.fftshift(np.fft.fft2(signal))
    magnitude_spectrum = np.abs(fft_signal)
    
    ax.imshow(np.log(1 + magnitude_spectrum), cmap='gray')
    ax.set_title(title)
    ax.axis('off')
    
def converte_img():
    fails = 0
    while fails <= 2:
        try:
            url = input("Digite a URL da imagem: ")
            response = urlopen(url)
            break
        except Exception as e:
            print(f"Erro ao acessar a URL: {e}")
            fails += 1
    if fails > 2:
        raise Exception("Não foi possível acessar as URL's")
    image_bytes = BytesIO(response.read())

    # Tentar abrir a imagem especificando o formato
    try:
        img = Image.open(image_bytes).convert('L')
    except IOError:
        print("Erro ao abrir a imagem. Verifique o formato ou a URL.")
        raise Exception("Erro ao abrir a imagem. Verifique o formato ou a URL.")
    return img
        
def init_senoide():
    # Entrada de características do sinal
    potencia = float(input('Digite a potência desejada Db: '))
    amplitude = 10**(potencia / 10)
    frequencia = float(input('Digite a frequência desejada (hz): '))
    ciclos = int(input('Digite a quantidade de períodos a serem plotados: '))
    duracao = ciclos / frequencia
    amostragem = int(input('Digite a quantidade de amostras por período: '))
    taxa_amostragem = round(amostragem * frequencia)
    num_niveis = int(input('Digite a quantidade de níveis desejada: '))
    if num_niveis <= 1:
        raise ValueError("O número de níveis de quantização deve ser maior que 1.")

    # Cálculo do eixo x (tempo) nos gráficos. Foi adicionado meio período a mais para o cálculo do diagrama de olho
    tempo = np.linspace(0, duracao, int(taxa_amostragem * duracao), endpoint=True)
    
    # Cálculo do sinal original, a senóide no formato A*sen(pi*f*t)
    sinal_original = amplitude * np.sin(2 * np.pi * frequencia * tempo)

    # Entrada da relação Sinal Ruído em DB
    SNR = float(input('Digite a Relação Sinal Ruido em Db (SNR): '))
    print("\n")

    # Quantizar o sinal original ruidoso
    sinal_quantizado, _ = quantizar_sinal(sinal_original, num_niveis)

    # Gerar código binário a partir do sinal quantizado
    # codigo_binario, _ = gerar_codigo_binario(sinal_quantizado, num_niveis)
    sinal_codificado = codificar_nrz(sinal_quantizado, bin=False)
        
    # Plotando sinal original com ruído e sinal original, sinal quantizado sem ruído, sinal quantizado com ruído, código binário sem ruído, código binário com ruído e suas transformadas de Fourier
    fig = plt.figure(num="Trabalho de Sistemas de Radioenlace - Carlos e Alessandro", figsize=(16, 20))

    # Plotando o Sinal Original, o tempo é um corte do array do tempo para pegar apenas de 0 até o número de períodos, ao invés de pegar de 0 até o número de períodos mais meio período
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(tempo, sinal_original)
    ax1.set_xlabel('Tempo (s)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Sinal Original')
    ax1.set()
    ax1.grid(True)

    ax2 = plt.subplot(3, 2, 2)
    plot_fft_sen(ax2, sinal_original, taxa_amostragem, 'Espectro do Sinal Original')

    # Sinal Quantizado
    ax3 = plt.subplot(3, 2, 3)
    ax3.step(tempo, sinal_quantizado, where='mid')
    ax3.set_xlabel('Tempo (s)')
    ax3.set_ylabel('Nível de Quantização')
    ax3.set_title('Sinal Quantizado')
    ax3.grid(True)

    ax4 = plt.subplot(3, 2, 4)
    plot_fft_sen(ax4, sinal_quantizado, taxa_amostragem, 'Espectro do Sinal Quantizado')

    # Código Binário sem Ruído
    ax5 = plt.subplot(3, 2, 5)
    ax5.set_xlabel("Tempo (s)")
    ax5.set_ylabel("Amplitude")
    ax5.set_title('Código Binário (NRZ)')
    ax5.plot(tempo, sinal_codificado)
    ax5.set()
    ax5.grid(True)
    
    # Código do sinal com ruído
    ruido_db = potencia - SNR
    ruido_linear = 10**(ruido_db/10)
    ruido_array = np.random.normal(0, np.sqrt(ruido_linear), len(tempo))
    codigo_com_ruido = [sinal_codificado[i] + ruido_array[i] for i in range(len(sinal_codificado))]
    ax6 = plt.subplot(3, 2, 6)
    ax6.set_xlabel("Tempo (s)")
    ax6.set_ylabel("Amplitude")
    ax6.set_title('Código Binário (NRZ) com Ruído')
    ax6.plot(tempo, codigo_com_ruido)
    ax6.set()
    ax6.grid(True)
    
    # plt.tight_layout()
    plt.subplots_adjust(hspace=1.0)
    plt.show()
    
    if ciclos < 2 or amostragem < 4:
        print("Não é possível calcular o diagrama de olho com um número de períodos menor que 2 ou amostras por período menor que 4")
        exit(0)
        
    ## Contando número de bits de cada olho
    janelas = []
    janelas_tuplas = []
    
    for bit in range(0, len(sinal_codificado)):
        if bit + 1 < len(sinal_codificado):
            if sinal_codificado[bit] != sinal_codificado[bit + 1]:
                janelas.append(bit + 1)
        if bit == len(sinal_codificado) - 1:
            janelas.append(bit)
            
    start = 0
    for j in range(0, len(janelas)):
        end = janelas[j]
        
        if janelas[j] < 2:
            pass
        
        if janelas[j] + 1 <= len(sinal_codificado) - 1:
            end = janelas[j] + 1
        
        if start - 1 >= 0:
            start = start - 1
        
        janelas_tuplas.append((start, end))
        start = janelas[j]

    # Plotando diagrama de olho sem ruído            
    plt.figure(num="Trabalho de Sistemas de Radioenlace - Carlos e Alessandro", figsize=(12, 8))
    olho_sem_ruido = plt.subplot(3, 2, 3)
    olho_sem_ruido.set_xlabel("Tempo (s)")
    olho_sem_ruido.set_xlabel("Amplitude")
    olho_sem_ruido.set_title("Diagrama de olho sem ruído")
    for tp in janelas_tuplas:
        array = sinal_codificado[tp[0]:tp[1]]
        if tp[0] == 0 and (sinal_codificado[tp[0]] != sinal_codificado[tp[0] -1]):
            array = np.insert(array, 0, sinal_codificado[tp[0] -1])
        olho_sem_ruido.plot(array, color='blue', alpha=0.5)        
    olho_sem_ruido.set()
    olho_sem_ruido.grid(True)
    
    # Plotando diagrama de olho com ruído
    olho_com_ruido = plt.subplot(3, 2, 4)
    olho_com_ruido.set_xlabel("Tempo (s)")
    olho_com_ruido.set_xlabel("Amplitude")
    olho_com_ruido.set_title("Diagrama de olho com ruído")
    olho_com_ruido.set()
    for tp in janelas_tuplas:
        array = codigo_com_ruido[tp[0]:tp[1]]
        if tp[0] == 0 and (codigo_com_ruido[tp[0]] != codigo_com_ruido[tp[0] -1]):
            array = np.insert(array, 0, codigo_com_ruido[tp[0] -1])
        olho_com_ruido.plot(array, color='blue', alpha=0.5)       
    olho_com_ruido.grid(True)
    
    plt.tight_layout()
    plt.show()

def init_imagem():
    img = converte_img()
    # Converter a imagem para um array numpy
    img_array = np.array(img)
    # Normalizar os valores dos pixels para o intervalo [0, 1]
    img_normalized = img_array / 255.0
    # Número de níveis de quantização desejado
    num_niveis = int(input("Digite o número de níveis de quantização: "))
    # Processar a imagem como um sinal
    img_quantizada, _ = quantizar_sinal(img_normalized, num_niveis)
    # Gerar código binário para a imagem quantizada
    codigo_binario = gerar_codigo_binario(img_quantizada, num_niveis)
    # Plotar as imagens e a transformada de Fourier
    plt.figure(figsize=(16, 8))

    # Imagem Original e sua transformada de Fourier
    plt.subplot(2, 2, 1)
    plt.imshow(img_array, cmap='gray')
    plt.title('Imagem Original')
    plt.axis('off')

    plt.subplot(2, 2, 2)
    plot_fft_img(plt.gca(), img_array, 'Transformada de Fourier da Imagem Original')

    # Imagem Quantizada e sua transformada de Fourier
    plt.subplot(2, 2, 3)
    plt.imshow(img_quantizada, cmap='gray')
    plt.title(f'Imagem Quantizada com {num_niveis} níveis')
    plt.axis('off')

    plt.subplot(2, 2, 4)
    plot_fft_img(plt.gca(), img_quantizada, f'Transformada de Fourier da Imagem Quantizada com {num_niveis} níveis')

    plt.tight_layout()
    plt.show()

    # Informações sobre os bits gerados
    print(f"Número de bits por amostra: {int(np.ceil(np.log2(num_niveis)))}")
    print(f"Exemplo dos 200 primeiros valores do código binário:")
    for i in range(len(codigo_binario)):
        if isinstance(i/2, float):
            print(f"Amostra {i}: Valor quantizado: {img_quantizada.flatten()[i]} -> Código Binário: {codigo_binario[i]}")
    

if __name__ == "_main_":
    modo = int(input("Digite o tipo de entrada:\n\t1)Senoide\n\t2)Imagem\n"))
    match modo:
        case 1:
            init_senoide()
        case 2:
            init_imagem()