import sys
import subprocess as s
import os
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.Chatbot
colFrases = db.frases
colUsuarios = db.usuarios

class Chatbot():
    def __init__(self):
        self.usuarios = []
        self.historico = []
        self.frases = {}

        cursor = colFrases.find()
        for doc in cursor:
            self.frases[doc['chave']] = doc['valor']

        cursor = list(colUsuarios.find())
        for doc in cursor:
            self.usuarios.append(doc['nome'])

    def escuta(self):
        frase = input('>: ')
        frase = frase.lower()
        frase = frase.replace('é','eh')
        return frase

    def pensa(self, frase):
        if frase in self.frases:
            return self.frases[frase]

        if frase == 'aprende':
            chave = input('Digite a frase: ')
            resp = input('Digite a resposta: ')
            self.frases[chave] = resp

            aprendizado = {
                "chave": chave,
                "valor": resp
            }
            colFrases.insert_one(aprendizado)
            return 'Aprendido'

        if not len(self.historico) == 0:
            if self.historico[-1] == 'Olá, qual o seu nome?':
                nome = self.pegaNome(frase)
                frase = self.respondeNome(nome)
                return frase
        try:
            resp = str(eval(frase))
            return resp
        except:
            pass
        return 'Não entendi'
            
    def pegaNome(self, nome):
        if 'o meu nome eh ' in nome:
            nome = nome[14:]
        nome = nome.title()
        return nome

    def respondeNome(self, nome):
        if nome in self.usuarios:
            frase = 'Eaew '
        else:
            frase = 'Muito prazer '
            self.usuarios.append(nome)
            colUsuarios.insert_one({'nome' : nome})
            
        return frase+nome

    def fala(self, frase):
        if 'executa' in frase:
            plataforma = sys.platform
            comando = frase.replace('executa ', '')
            if 'win' in plataforma:
                os.startfile(comando)
            if 'linux' in plataforma:
                try:
                    s.Popen(comando)
                except FileNotFoundError:
                    s.Popen(['xdg-open', comando])
        else:
            print(frase)
        self.historico.append(frase)