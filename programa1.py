import time

class Corte:
    def __init__(self, numero, costo, dicc_piezas, metros_sobrantes):
        # Diccionario de la forma pieza: cantidad obtenida
        self.numero = numero
        self.costo = costo
        self.dicc_piezas = dicc_piezas
        self.metros_sobrantes = metros_sobrantes

    def calcular_coef(self, valor_metro_astillado):
        utilidad_corte = 0
        for pieza, cantidad in self.dicc_piezas.items():
            utilidad_corte += pieza.calcular_coef(cantidad, valor_metro_astillado)
            #print('{0}: {1}, costo={2}'.format(self.numero, utilidad_corte, self.costo))
        #time.sleep(2)

        return self.metros_sobrantes*valor_metro_astillado - self.costo + utilidad_corte



class Pieza:
    def __init__(self, lista_coef, largo, qmax, indice, stock, costo_inventario):
        self.indice = indice
        self.lista_coef = lista_coef
        self.largo = largo
        self.qmax = qmax
        self.stock = stock
        self.costo_inventario = costo_inventario

    def calcular_coef(self, unidades_obtenidas, valor_astillado_largo):
        cantidad_final = self.stock + unidades_obtenidas
        u1 = (self.lista_coef[0]/self.lista_coef[1])*self.stock - (1/self.lista_coef[1])*self.stock**2
        #print(u1)
        u2 = (self.lista_coef[0]/self.lista_coef[1])*cantidad_final - (1/self.lista_coef[1])*cantidad_final**2
        #print(u2)
        u2 = max(u2, 0)
        #print(u2 - u1)
        #time.sleep(20)
        #return u2 - u1
        return max(u2-u1, self.largo*valor_astillado_largo)



class Dia:
    def __init__(self, dicc_patrones, lista_inventario, valor_metro_astillado):
        self.dicc_patrones = dicc_patrones
        self.lista_inventario = lista_inventario
        self.valor_metro_astillado = valor_metro_astillado
        self.costo_total = 0
        self.dicc_patrones_usados = {}

        for i in range (0, len(self.dicc_patrones.keys())):
            self.dicc_patrones_usados[i+1] = 0


    def elegir_corte(self):
        maximo = -10000000
        corte_max = None
        for patron in self.dicc_patrones.values():
            coef = patron.calcular_coef(self.valor_metro_astillado)
            print('{0} final: {1}'.format(patron.numero, coef))
            if coef >= maximo:
                maximo = coef
                corte_max = patron
        #time.sleep(10)
        return corte_max, maximo

    def cortar(self, numero_troncos):
        num_troncos = numero_troncos
        while num_troncos > 0:
            corte, coef = self.elegir_corte()
            self.costo_total += corte.costo
            for pieza, cantidad in corte.dicc_piezas.items():
                pieza.stock += cantidad
                print('Stock de la pieza {0}: {1}'.format(pieza.indice, pieza.stock))
            self.dicc_patrones_usados[corte.numero] += 1
            print("El corte elegido es el {0}".format(corte.numero))
            num_troncos -= 1
            #time.sleep(0.5)
        print(self.dicc_patrones_usados.values())

piezas = dict()
# Diccionario de la forma indice: Pieza()
archivo1 = open('piezas.csv', 'r')
for linea in archivo1:
    linea = linea[:-2].split(',')
    piezas[int(linea[0][6:])] = Pieza([float(linea[2]), float(linea[3])], int(linea[1]), 1000, int(linea[0][6:]), 0, float(linea[4]))
archivo1.close()

patrones = dict()
# Diccionario de la forma numero: Corte()
archivo2 = open('patrones.csv', 'r')
for linea in archivo2:
    linea = linea[:-1].split(',')
    lista_piezas = linea[2:11]
    diccionario_piezas = {}
    for posicion in range(0, len(lista_piezas)):
        if lista_piezas[posicion] != '0':
            diccionario_piezas[piezas[posicion + 1]] = int(lista_piezas[posicion])
    patrones[int(linea[0][1:])] = Corte(int(linea[0][1:]), int(linea[1]), diccionario_piezas, int(linea[11]))
archivo2.close()

inventario = None
metro_astillado = 2050

dia1 = Dia(dicc_patrones=patrones, lista_inventario=inventario, valor_metro_astillado=metro_astillado)
dia1.cortar(126)
