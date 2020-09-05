import math
print ("A fórmula do cálculo é: P = (X = k) = C(n,k) * p ^ k * q ^ (n-k)")
p = float(input("P - Successo : "))
q = float(input("Q - Fracasso: "))
n = int(input("N - Tentativas: "))
k = int(input("K - Esperadas de Tentativas: "))
print ("Arranjo: P = (X = ",k,") = C(",n,",",k,") * ",p," ^ ",k," * ",q," ^ (",n,"-",k,")")

c = math.comb(n, k)

tentativa = (p ** k) * (q ** (n - k))

res = (c * tentativa) * 100

print (res, '%')
