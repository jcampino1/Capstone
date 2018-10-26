import time
import random
import csv


class Corte:
    def __init__(self, numero, costo, dicc_piezas, metros_sobrantes):
        # Diccionario de la forma pieza: cantidad obtenida
        self.numero = numero
        self.costo = costo
        self.dicc_piezas = dicc_piezas
        self.metros_sobrantes = metros_sobrantes

    def calcular_coef(self, valor_metro_astillado, dias_inventario, indice_dia):
        utilidad_corte = 0
        for pieza, cantidad in self.dicc_piezas.items():
            utilidad_corte += pieza.calcular_coef(cantidad, valor_metro_astillado, dias_inventario, indice_dia)
            #if self.numero == 1:
                #print('Patron de corte {0}, agregando {1} de la pieza {2}. Utilidad:{3}'.format(self.numero, cantidad, pieza.indice, utilidad_corte))
                #time.sleep(2)

        return self.metros_sobrantes*valor_metro_astillado - self.costo + utilidad_corte



class Pieza:
    def __init__(self, lista_coef, largo, qmax, indice, costo_inventario, dias):
        self.indice = indice
        self.lista_coef = lista_coef
        self.largo = largo
        self.qmax = qmax
        self.costo_inventario = costo_inventario
        self.dias = dias

    def calcular_coef(self, unidades_obtenidas, valor_astillado_largo, dias_inventario, indice_dia):
        cantidad_inicial = self.dias[indice_dia + dias_inventario].piezas_vendidas[self.indice]
        cantidad_final = cantidad_inicial + unidades_obtenidas
        u1 = (self.lista_coef[0]/self.lista_coef[1])*cantidad_inicial - (1/self.lista_coef[1])*cantidad_inicial**2
        u2 = (self.lista_coef[0]/self.lista_coef[1])*cantidad_final - (1/self.lista_coef[1])*cantidad_final**2

        # No se si esta bien poner esto, el maximo entre u2 y 0
        # u2 = max(u2, 0)

        #if self.indice == 3:
        #    print('Stock pieza: {0}, agregado: {1}. Utilidad: {2}'.format(self.stock, unidades_obtenidas, u2 - u1))
        #    time.sleep(5)

        # Hay que darle vueltas a esto tambien
        return max(u2-u1-unidades_obtenidas*self.costo_inventario*dias_inventario,
                   self.largo*valor_astillado_largo-unidades_obtenidas*self.costo_inventario*dias_inventario)



class Dia:
    def __init__(self, indice, dicc_patrones, dicc_piezas, lista_inventario, valor_metro_astillado, numero_troncos, dias):
        self.indice = indice
        self.dicc_patrones = dicc_patrones
        self.dicc_piezas = dicc_piezas
        self.lista_inventario = lista_inventario
        self.valor_metro_astillado = valor_metro_astillado
        self.numero_troncos = numero_troncos
        self.costo_total = 0
        self.utilidad_total = 0
        self.dicc_patrones_usados = {}
        self.piezas_producidas = {}
        # Piezas_vendidas guarda todas las piezas de las que me voy a deshacer en un dia, puede ser por venta o por astillado.
        # Informacion estadistica

        self.piezas_vendidas = {}
        self.dias_por_delante = min(5, 15-indice)
        self.dicc_precios = {}
        self.dicc_piezas_a_otros_dias = {}
        self.dicc_piezas_a_astillar = {}
        self.patrones_a_otros_dias = 0
        self.dicc_piezas_recibidas = {}
        self.dicc_paod_por_pieza = {}
        self.dias = dias

        for i in range (0, len(self.dicc_patrones.keys())):
            self.dicc_patrones_usados[i+1] = 0

        for i in range(0, 9):
            self.piezas_producidas[i+1] = 0
            self.piezas_vendidas[i + 1] = 0
            self.dicc_precios[i+1] = 0
            self.dicc_piezas_recibidas[i+1] = 0
            self.dicc_piezas_a_astillar[i+1] = 0
            self.dicc_paod_por_pieza[i+1] = 0

        if self.indice <= 9:
            for i in range(self.indice + 1, self.indice + 7):
                self.dicc_piezas_a_otros_dias[i] = 0

        else:
            for i in range(self.indice + 1, 16):
                self.dicc_piezas_a_otros_dias[i] = 0


    def elegir_corte(self):
        maximo = -10000000
        corte_max = None
        dias_a_gaurdar = 0
        for patron in self.dicc_patrones.values():
            for dias_inventario in range(self.dias_por_delante + 1):
                coef = patron.calcular_coef(self.valor_metro_astillado, dias_inventario, self.indice)
                if coef >= maximo:
                    maximo = coef
                    corte_max = patron
                    dias_a_gaurdar = dias_inventario
        #time.sleep(10)
        return corte_max, maximo, dias_a_gaurdar

    def cortar(self):
        # Para cada tronco elige el mejor corte, considerando que corte hacer y 'para que dia' hacerlo.
        # Agrega las piezas del corte a las piezas producidas del dia, y a las piezas vendidas del dia elegido
        num_troncos = self.numero_troncos
        while num_troncos > 0:
            corte, coef, dias_a_guardar = self.elegir_corte()
            #rint(dias_a_guardar, type(dias_a_guardar))
            #ime.sleep(10)
            self.costo_total += corte.costo
            if dias_a_guardar != 0:
                self.patrones_a_otros_dias += 1

            for pieza, cantidad in corte.dicc_piezas.items():
                self.piezas_producidas[pieza.indice] += cantidad
                self.dias[self.indice+dias_a_guardar].piezas_vendidas[pieza.indice] += cantidad
                self.dias[self.indice+dias_a_guardar].utilidad_total += coef
                if dias_a_guardar != 0:
                    self.dicc_piezas_a_otros_dias[self.indice+dias_a_guardar] += cantidad
                    self.dicc_paod_por_pieza[pieza.indice] += cantidad
                    self.dias[self.indice+dias_a_guardar].dicc_piezas_recibidas[pieza.indice] += cantidad

              #print('Stock de la pieza {0}: {1}'.format(pieza.indice, pieza.stock))

            self.dicc_patrones_usados[corte.numero] += 1
            #print("El corte elegido es el {0}".format(corte.numero))

            num_troncos -= 1
            #time.sleep(0.5)
        #print(self.dicc_patrones_usados.values())
        #print(self.piezas_producidas.values())
        #print('Utilidad total: {0}, costo total: {1}'.format(self.utilidad_total, self.costo_total))

class Simulacion:
    def __init__(self, escribir=False):
        self.piezas = dict()
        self.patrones = dict()
        self.dias = {}
        self.escribir = escribir


        archivo1 = open('piezas.csv', 'r')
        for linea in archivo1:
            linea = linea[:-2].split(',')
            self.piezas[int(linea[0][6:])] = Pieza([float(linea[2]), float(linea[3])], int(linea[1]), 1000,
                                              int(linea[0][6:]), float(linea[4]), self.dias)
        archivo1.close()

        archivo2 = open('patrones.csv', 'r')
        for linea in archivo2:
            linea = linea[:-1].split(',')
            lista_piezas = linea[2:11]
            diccionario_piezas = {}
            for posicion in range(0, len(lista_piezas)):
                if lista_piezas[posicion] != '0':
                    diccionario_piezas[self.piezas[posicion + 1]] = int(lista_piezas[posicion])
            self.patrones[int(linea[0][1:])] = Corte(int(linea[0][1:]), int(linea[1]), diccionario_piezas, int(linea[11]))
        archivo2.close()

    def correr(self):
        lista_insumos = []

        for i in range(0, 14):
            lista_insumos.append(round(random.uniform(0, 1) * 48))
        sum = 0
        contador = 0
        for i in range (10000):
            sum += round(random.uniform(0, 1) * 48)
            contador += 1
        promedio = round(sum/contador)

        for i in range(1, 15):
            self.dias[i] = Dia(i, dicc_patrones=self.patrones, dicc_piezas=self.piezas, lista_inventario=None,
                          valor_metro_astillado=2050, numero_troncos=lista_insumos[i - 1], dias=self.dias)

        self.dias[15] = Dia(15, dicc_patrones=self.patrones, dicc_piezas=self.piezas, lista_inventario=None,
                            valor_metro_astillado=2050, numero_troncos=promedio, dias=self.dias)

        for i in range(0, 15):
            self.dias[15 - i].cortar()

        for i in range(1, 15):
            for indice, cantidad in self.dias[i].piezas_vendidas.items():
                coeficientes = self.dias[i].dicc_piezas[indice].lista_coef
                self.dias[i].dicc_precios[indice] = max(
                    round(coeficientes[0] / coeficientes[1] - (1 / coeficientes[1]) * cantidad, 0),
                    round((coeficientes[0] / (2 * coeficientes[1])), 0))

        dias_con_inventario = {}
        for indice, dia in self.dias.items():
            dias_con_inventario[indice] = dia

        for i in range(1, 15):
            self.dias[i] = Dia(15, dicc_patrones=self.patrones, dicc_piezas=self.piezas, lista_inventario=None,
                          valor_metro_astillado=2050, numero_troncos=lista_insumos[i - 1], dias=self.dias)

        for i in range(1, 15):
            self.dias[i].indice = i
            self.dias[i].cortar()

        diferencia_total = 0
        utilidad_total = 0
        utilidad_total_sin = 0

        if self.escribir:
            archivo_escrito = open('resultados.csv', 'w')

        for i in range(1, 15):
            for indice, cantidad in self.dias[i].piezas_vendidas.items():
                coeficientes = self.dias[i].dicc_piezas[indice].lista_coef
                self.dias[i].dicc_precios[indice] = max(
                    round(coeficientes[0] / coeficientes[1] - (1 / coeficientes[1]) * cantidad, 0),
                    round((coeficientes[0] / (2 * coeficientes[1])), 0))

            if self.escribir:
                archivo_escrito.write("Dia " + str(i) + "," + "Troncos recibidos: " + str(lista_insumos[i-1]) + "\n")
                writer = csv.DictWriter(archivo_escrito, fieldnames=dias_con_inventario[i].piezas_producidas.keys())
                writer.writeheader()
                writer.writerow(dias_con_inventario[i].piezas_producidas)
                writer.writerow(dias_con_inventario[i].piezas_vendidas)
                writer.writerow(dias_con_inventario[i].dicc_piezas_recibidas)
                writer.writerow(dias_con_inventario[i].dicc_precios)
                archivo_escrito.write("\n\n")

            print("Dia {}".format(i))
            print("Troncos a cortar ese dia: {0}".format(self.dias[i].numero_troncos))
            print("Patrones cortados: " + str(dias_con_inventario[i].dicc_patrones_usados) + "  |  " + str(
                self.dias[i].dicc_patrones_usados))
            print("Piezas producidas: " + str(dias_con_inventario[i].piezas_producidas) + "  |  " + str(
                self.dias[i].piezas_producidas))
            print(
            "Piezas vendidas: " + str(dias_con_inventario[i].piezas_vendidas) + "  |  " + str(self.dias[i].piezas_vendidas))
            print("Piezas recibidas: " + str(dias_con_inventario[i].dicc_piezas_recibidas) + "  |  " + str(
                self.dias[i].dicc_piezas_recibidas))
            print("Precios: " + str(dias_con_inventario[i].dicc_precios) + "  |  " + str(self.dias[i].dicc_precios))
            print("Piezas a otros dias: " + str(dias_con_inventario[i].dicc_piezas_a_otros_dias) + "  |  " + str(
                self.dias[i].dicc_piezas_a_otros_dias))
            print("Patrones a otros dias: " + str(dias_con_inventario[i].patrones_a_otros_dias) + "  |  " + str(
                self.dias[i].patrones_a_otros_dias))
            print(
            "Utilidad del dia: " + str(dias_con_inventario[i].utilidad_total) + "  |  " + str(self.dias[i].utilidad_total))
            print("Diferencia de utilidad: " + str(dias_con_inventario[i].utilidad_total - self.dias[i].utilidad_total))
            utilidad_total += dias_con_inventario[i].utilidad_total
            diferencia_total += (dias_con_inventario[i].utilidad_total - self.dias[i].utilidad_total)
            # print("Piezas a astillar: " + str(dias[i].dicc_piezas_a_astillar))
            print("\n\n")

        print("Diferencia total de utilidad: " + str(diferencia_total))
        print(round(utilidad_total, 0))
        print("Porcentaje de aumento: " + str((diferencia_total*100)/utilidad_total))

        if self.escribir:
            archivo_escrito.write("\n\n")
            archivo_escrito.write("Patrones usados cada dia")
            writer = csv.DictWriter(archivo_escrito, fieldnames=dias_con_inventario[2].dicc_patrones_usados.keys())
            writer.writeheader()
            for i in range(1, 15):
                writer.writerow(dias_con_inventario[i].dicc_patrones_usados)
            archivo_escrito.close()

        return (diferencia_total*100)/utilidad_total


lista_porcentajes_aumento = []
for i in range(0, 10):
    if i == 0:
        simulacion = Simulacion(escribir=True)
    else:
        simulacion = Simulacion()
    aumento = simulacion.correr()
    lista_porcentajes_aumento.append(aumento)

print("\n\n")
print(lista_porcentajes_aumento)
print("\n\n")
promedio = sum(lista_porcentajes_aumento)/10
print("Promedio: " + str(round(promedio, 2)))

