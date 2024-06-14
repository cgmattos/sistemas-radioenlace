import matplotlib.pyplot as plt
import numpy as np

def quantizar_sinal(sinal, num_niveis):
    valor_min = np.min(sinal)
    valor_max = np.max(sinal)
    q = (valor_max - valor_min) / num_niveis
    niveis_quant = np.linspace(valor_min, valor_max, num_niveis)
    sinal_quantizado = np.int64(np.rint(q * np.round(sinal/q)))
    return sinal_quantizado, niveis_quant

def gerar_codigo_binario(sinal_quantizado, num_niveis):
    num_bits = int(np.ceil(np.log2(num_niveis)))
    codigo_binario = [np.binary_repr(nivel, width=num_bits) for nivel in sinal_quantizado]
    return codigo_binario

# Caracteristica do sinal
potencia = float(input("Digite a potência desejada (dB): "))  
frequencia = int(input("Digite a frequência desejada (Hz): "))
ciclos = int(input("Digite o número de ciclos: "))
duracao = float((1/frequencia) * ciclos)
amostragem = int(input("Digite o número de amostras por período (Maior ou igual a 2): "))
taxa_amostragem = int(amostragem * ciclos) 

# Cálculo da amplitude a partir da potência
amplitude = 10**(potencia/10) 

# Número de níveis de quantização 
num_niveis = int(input("Digite os níveis de quantização: ")) 

tempo = np.linspace(0, duracao, taxa_amostragem, endpoint=True)
sinal = amplitude * np.cos(2 * np.pi * frequencia * tempo)

# Quantização do sinal
sinal_quantizado, niveis_quant = quantizar_sinal(sinal, num_niveis)

# gerador código binário
codigo_binario = gerar_codigo_binario(sinal_quantizado, num_niveis)

# dados plotagem do código binário (NRZ)
grafico_binario = []
tempo_grafico = []
for i in range(len(codigo_binario)):
    for bit in codigo_binario[i]:
        if bit == '1':
            grafico_binario.append(1)
        else:
            grafico_binario.append(0)
        tempo_grafico.append(tempo[i])


# plot do sinal original sem amostras
tempo_alta_resolucao = np.linspace(0, duracao, 200)  # Alta resolução no tempo
sinal_continuo = amplitude * np.cos(2 * np.pi * frequencia * tempo_alta_resolucao)

plt.subplot(5, 1, 5)
plt.plot(tempo_alta_resolucao, sinal_continuo, label='Sinal Contínuo')
plt.xlabel('Tempo (ms)')
plt.ylabel('Amplitude')
plt.title('Sinal Contínuo')


# plot do sinal original com pontos de amostragem
plt.figure(figsize=(12, 12))

plt.subplot(5, 1, 1)
plt.plot(tempo, sinal, label='Sinal Original')
plt.scatter(tempo, sinal, color='red')  
plt.xlabel('Tempo (ms)')
plt.ylabel('Amplitude')
plt.title('Sinal Original com Pontos de Amostragem')
plt.legend()

# plot do sinal quantizado com pontos de amostragem
plt.subplot(5, 1, 2)
plt.step(tempo, sinal_quantizado, where='mid', label='Sinal Quantizado')
plt.scatter(tempo, sinal_quantizado, color='red')  
plt.xlabel('Tempo (ms)')
plt.ylabel('Nível de Quantização')
plt.title('Sinal Quantizado com Pontos de Amostragem')
plt.legend()

# plot do código binário NRZ com pontos de amostragem
plt.subplot(5, 1, 3)
plt.step(tempo_grafico, grafico_binario, where='mid', label='Código Binário NRZ')
plt.scatter(tempo_grafico, grafico_binario, color='red')  # Adiciona pequenas bolas nos pontos de amostragem
plt.xlabel('Tempo (ms)')
plt.ylabel('NRZ')
plt.title('Código Binário NRZ com Pontos de Amostragem')
plt.ylim(-0.1, 1.1)
plt.legend()

# Gráfico discretizado (apenas os pontos)
plt.subplot(5, 1, 4)
plt.scatter(tempo, sinal, color='blue', label='Pontos Amostrados (Sinal Original)')
plt.scatter(tempo_grafico, grafico_binario, color='red', label='Pontos Amostrados (NRZ)')
plt.xlabel('Tempo (ms)')
plt.ylabel('Valor')
plt.title('Pontos Amostrados (Discretizado)')
plt.legend()


plt.tight_layout()
plt.show()

# Exibir o código binário 
codigo_binario_completo = ''.join([str(bit) for bit in grafico_binario])
print("Código binário de todas as amostras (NRZ):")
print(codigo_binario_completo)

# Exibir os primeiros valores do código binário para verificação
print("Primeiros 10 valores do código binário:")
for i in range(min(10, len(codigo_binario))):
    print(f"t={tempo[i]:.2f} ms -> Quantização: {sinal_quantizado[i]} -> Código Binário: {codigo_binario[i]}")
