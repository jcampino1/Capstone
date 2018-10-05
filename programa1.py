
class Corte:
    def __init__(self, costo, dicc_piezas, metros_sobrantes):
        # Diccionario de la forma instancia: cantidad obtenida
        self.costo = costo
        self.dicc_piezas = dicc_piezas
        self.metros_sobrantes = metros_sobrantes

    def calcular_coef(self, valor_metro_astillado):
        utilidad_corte = 0
        for pieza, cantidad in self.dicc_piezas:
            utilidad_corte += pieza.calcular_coef(cantidad, valor_metro_astillado)

        return self.metros_sobrantes*valor_metro_astillado - self.costo + utilidad_corte



class Pieza:
    def __init__(self, lista_coef, largo, qmax, indice, stock):
        self.indice = indice
        self.lista_coef = lista_coef
        self.largo = largo
        self.qmax = qmax
        self.stock = stock

    def calcular_coef(self, unidades_obtenidas, valor_astillado_largo):
        cantidad_final = self.stock + unidades_obtenidas
        u1 = self.lista_coef[0]*self.stock**2 + self.lista_coef[1]*self.stock + self.lista_coef[2]
        u2 = self.lista_coef[0]*cantidad_final**2 + self.lista_coef[1]*cantidad_final + self.lista_coef[2]
        u2 = max(u2, 0)
        return max(u2-u1, self.largo*valor_astillado_largo)



class Dia:
    def __init__(self, lista_patrones, lista_inventario, valor_metro_astillado):
        self.lista_patrones = lista_patrones
        self.lista_inventario = lista_inventario
        self.valor_metro_astillado = valor_metro_astillado
        self.costo_total = 0


    def elegir_corte(self):
        maximo = -10000000
        corte_max = None
        for patron in self.lista_patrones:
            coef = patron.calcular_coef(self.valor_metro_astillado)
            if coef >= maximo:
                maximo = coef
                corte_max = patron
        return corte_max, maximo

    def cortar(self, numero_troncos):
        while numero_troncos > 0:
            corte, coef = self.elegir_corte()
            self.costo_total += corte.costo
            for pieza, cantidad in corte.dicc_piezas:
                pieza.stock += cantidad
            self.lista_patrones.append((corte, coef))
