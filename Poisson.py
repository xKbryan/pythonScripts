import math
print ("A fórmula do cálculo é: P = (X = k) = (e ^ -λ) * (λ ^ k) / k!")
n = float(input("Y - Lambda: "))
k = int(input("K - Esperadas de Tentativas: "))

e = math.e ** -n
s = n ** k

res = e * s
fat = math.factorial(k)

resp = res / fat

resultado = resp * 100

print ('P ( X =', k, ') =', e, ' * ', s, ' / ', fat)
print ('P ( X =', k, ') =', resp)
print ('P ( X =', k, ') =', resultado, '%')
