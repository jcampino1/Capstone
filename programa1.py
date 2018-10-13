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
            #if self.numero == 1:
                #print('Patron de corte {0}, agregando {1} de la pieza {2}. Utilidad:{3}'.format(self.numero, cantidad, pieza.indice, utilidad_corte))
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
        u2 = (self.lista_coef[0]/self.lista_coef[1])*cantidad_final - (1/self.lista_coef[1])*cantidad_final**2

        # No se si esta bien poner esto, el maximo entre u2 y 0
        u2 = max(u2, 0)

        #if self.indice == 3:
        #    print('Stock pieza: {0}, agregado: {1}. Utilidad: {2}'.format(self.stock, unidades_obtenidas, u2 - u1))
        #    time.sleep(5)

        # Hay que darle vueltas a esto tambien
        return max(u2-u1, self.largo*valor_astillado_largo)



class Dia:
    def __init__(self, dicc_patrones, lista_inventario, valor_metro_astillado):
        self.dicc_patrones = dicc_patrones
        self.lista_inventario = lista_inventario
        self.valor_metro_astillado = valor_metro_astillado
        self.costo_total = 0
        self.utilidad_total = 0
        self.dicc_patrones_usados = {}
        self.stock_piezas = {}

        for i in range (0, len(self.dicc_patrones.keys())):
            self.dicc_patrones_usados[i+1] = 0

        for i in range(0, 10):
            self.stock_piezas[i+1] = 0


    def elegir_corte(self):
        maximo = -10000000
        corte_max = None
        for patron in self.dicc_patrones.values():
            coef = patron.calcular_coef(self.valor_metro_astillado)
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
                self.stock_piezas[pieza.indice] += cantidad
                self.utilidad_total += coef
                #print('Stock de la pieza {0}: {1}'.format(pieza.indice, pieza.stock))

            self.dicc_patrones_usados[corte.numero] += 1
            #print("El corte elegido es el {0}".format(corte.numero))

            num_troncos -= 1
            #time.sleep(0.5)
        print(self.dicc_patrones_usados.values())
        print(self.stock_piezas.values())
        print('Utilidad total: {0}, costo total: {1}'.format(self.utilidad_total, self.costo_total))

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

# Por ahora no hay inventario
inventario = None
metro_astillado = 2050

dia1 = Dia(dicc_patrones=patrones, lista_inventario=inventario, valor_metro_astillado=metro_astillado)
dia1.cortar(126)
