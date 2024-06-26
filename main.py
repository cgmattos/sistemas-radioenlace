
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from urllib.request import urlopen
from io import BytesIO

# Função para quantizar o sinal (ou imagem)
def quantizar_sinal(sinal, num_niveis):
    valor_min = np.min(sinal)
    valor_max = np.max(sinal)
    niveis_quant = np.linspace(valor_min, valor_max, num_niveis)
    sinal_quantizado = np.round((sinal - valor_min) / (valor_max - valor_min) * (num_niveis - 1)) / (num_niveis - 1) * (valor_max - valor_min) + valor_min
    return sinal_quantizado, niveis_quant

# Função para gerar código binário
def gerar_codigo_binario(sinal_quantizado, num_niveis):
    num_bits = int(np.ceil(np.log2(num_niveis)))
    codigo_binario = [
        np.binary_repr(
            int((nivel - np.min(sinal_quantizado)) * (num_niveis - 1) / (np.max(sinal_quantizado) - np.min(sinal_quantizado))), 
            width=num_bits
        ) 
        for nivel in sinal_quantizado.flatten()
    ]
    return codigo_binario

# Função para plotar a transformada de Fourier da senoide
def plot_fft_sen(ax, signal, sampling_rate, title, freq=None):
    N = len(signal)
    T = 1.0 / sampling_rate
    yf = np.fft.fft(signal)
    xf = np.fft.fftfreq(N, T)
    
    yf_shifted = np.fft.fftshift(yf)
    xf_shifted = np.fft.fftshift(xf)
    
    # idx = yf_shifted.argmax()
    # mult = freq/xf_shifted[idx]
    
    # xf_shifted = xf_shifted * mult
    
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
    potencia = float(input('Digite a potência desejada: '))
    amplitude = 10**(potencia / 10)
    frequencia = float(input('Digite a frequência desejada (hz): '))
    ciclos = float(input('Digite a quantidade de períodos a serem plotados: '))
    duracao = float((1 / frequencia) * ciclos)
    amostragem = int(input('Digite a quantidade de amostras por período: '))
    taxa_amostragem = int(amostragem * ciclos)
    num_niveis = int(input('Digite a quantidade de níveis desejada: '))
    if num_niveis <= 1:
        raise ValueError("O número de níveis de quantização deve ser maior que 1.")

    tempo = np.linspace(0, duracao, taxa_amostragem, endpoint=True)
    sinal_original = amplitude * np.cos(2 * np.pi * frequencia * tempo)

    # Adicionar ruído branco ao sinal original
    SNR = float(input('Digite a Relação Sinal Ruido (SNR): '))
    print("\n")

    # Quantizar o sinal original ruidoso
    sinal_quantizado_sem_ruido, _ = quantizar_sinal(sinal_original, num_niveis)
    # sinal_quantizado_com_ruido, _ = quantizar_sinal(sinal_original_ruidoso, num_niveis)

    # Gerar código binário a partir do sinal quantizado
    codigo_binario_sem_ruido = gerar_codigo_binario(sinal_quantizado_sem_ruido, num_niveis)
    # codigo_binario_com_ruido = gerar_codigo_binario(sinal_quantizado_com_ruido, num_niveis)
    
    # Plotando sinal original com ruído e sinal original, sinal quantizado sem ruído, sinal quantizado com ruído, código binário sem ruído, código binário com ruído e suas transformadas de Fourier
    plt.figure(figsize=(16, 20))

    # Sinal Original e Sinal Original com Ruído
    ax1 = plt.subplot(8, 2, 3)
    ax1.plot(tempo, sinal_original, label='Original', color='blue')
    # ax1.plot(tempo, sinal_original_ruidoso, label='Original com Ruído', color='red', alpha=0.7)
    ax1.set_xlabel('Tempo (s)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Sinais Original')
    ax1.legend()
    ax1.set
    ax1.grid(True)

    ax2 = plt.subplot(8, 2, 4)
    plot_fft_sen(ax2, sinal_original, taxa_amostragem, 'Espectro do Sinal Original com Ruído', frequencia)

    # Sinal Quantizado sem Ruído
    ax3 = plt.subplot(8, 2, 7)
    ax3.step(tempo, sinal_quantizado_sem_ruido, where='mid')
    ax3.set_xlabel('Tempo (s)')
    ax3.set_ylabel('Nível de Quantização')
    ax3.set_title('Sinal Quantizado')
    ax3.grid(True)

    ax4 = plt.subplot(8, 2, 8)
    plot_fft_sen(ax4, sinal_quantizado_sem_ruido, taxa_amostragem, 'Espectro do Sinal Quantizado', frequencia)

    # # Sinal Quantizado com Ruído
    # ax5 = plt.subplot(8, 2, 11)
    # ax5.step(tempo, sinal_quantizado_com_ruido, where='mid')
    # ax5.set_xlabel('Tempo (s)')
    # ax5.set_ylabel('Nível de Quantização')
    # ax5.set_title('Sinal Quantizado com Ruído')
    # ax5.grid(True)

    # ax6 = plt.subplot(8, 2, 12)
    # plot_fft_sen(ax6, sinal_quantizado_sem_ruido, taxa_amostragem, 'Espectro do Sinal Quantizado com Ruído', frequencia)

    # Código Binário com Ruído
    ax8 = plt.subplot(8, 2, 15)
    plot_fft_sen(ax8, np.array([int(bit) for bit in codigo_binario_sem_ruido]), len(codigo_binario_sem_ruido), 'Espectro do Código Binário sem Ruído', frequencia)

    # ax9 = plt.subplot(8, 2, 16)
    # plot_fft_sen(ax9, np.array([int(bit) for bit in codigo_binario_com_ruido]), len(codigo_binario_com_ruido), 'Espectro do Código Binário com Ruído', frequencia)
    # # plt.tight_layout()
    plt.show()
    
    # Informações sobre os bits gerados sem ruído
    print(f"Número de bits por amostra: {int(np.ceil(np.log2(num_niveis)))}")
    print(f"Exemplo dos 10 primeiros valores do código binário:")
    for i in range(min(10, len(codigo_binario_sem_ruido))):
        print(f"Amostra {i}: Valor quantizado: {sinal_quantizado_sem_ruido.flatten()[i]} -> Código Binário: {codigo_binario_sem_ruido[i]}")
    print("\n")
    
    # # Informações sobre os bits gerados com ruído
    # print(f"Número de bits por amostra: {int(np.ceil(np.log2(num_niveis)))}")
    # print(f"Exemplo dos 10 primeiros valores do código binário:")
    # for i in range(min(10, len(codigo_binario_com_ruido))):
    #     print(f"Amostra {i}: Valor quantizado: {sinal_quantizado_com_ruido.flatten()[i]} -> Código Binário: {codigo_binario_com_ruido[i]}")

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
    

if __name__ == "__main__":
    modo = int(input("Digite o tipo de entrada:\n\t1)Senoide\n\t2)Imagem\n"))
    match modo:
        case 1:
            init_senoide()
        case 2:
            init_imagem()
