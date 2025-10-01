import random as random
import numpy as np
np.set_printoptions(suppress=True, precision=2)
import matplotlib.pyplot as plt
import os

class Bloque:
    def __init__(self, x0, xn, y0, yn):
        self.x0 = x0
        self.xn = xn
        self.y0 = y0
        self.yn = yn


    def procesar_bloque_en_malla(self, h, Ny):
        self.i0 = int(self.x0 / h)
        self.j0 =   abs(int(np.ceil(self.y0 / h)) - (Ny+1))
        print("y0 ", self.y0,  "j0 ", self.j0)
        self.in_fin = int(self.xn / h)
        self.jn_fin = abs(int(np.ceil(self.yn / h)) - (Ny+1))
        print("yn ", self.yn,  "jn_fin ", self.jn_fin)
        return self.i0, self.j0, self.in_fin, self.jn_fin

class Malla:
    def __init__(self, Lx, Ly, h, v0, bloqueSuperior, bloqueInferior, divisionesHorizontales, divisionesVerticales, matriz_inicial=None):
        self.Lx = Lx
        self.Ly = Ly
        self.h = h
        self.v0 = v0
        self.bloqueSuperior = bloqueSuperior
        self.bloqueInferior = bloqueInferior
        self.Nx = int(Lx/h)
        self.Ny = int(Ly/h)
        print("Nx ", self.Nx, "Ny ", self.Ny)
        
        # Procesar bloques siempre (necesario para las coordenadas)
        self.__procesar_bloques()
        
        # Si se proporciona una matriz inicial, usarla directamente
        if matriz_inicial is not None:
            self.malla = matriz_inicial.copy()
            print("Usando matriz inicial proporcionada")
        else:
            # Proceso normal de generación de malla
            self.__crear_malla()
            self.__establecer_condiciones_de_frontera()
            self.valores_aleatorios_dentro_de_malla(divisionesHorizontales, divisionesVerticales)
            self.__aplicar_bloque()
        
        

    def __crear_malla(self):
        """Método privado: Crea la matriz de la malla"""
        self.malla = np.zeros((self.Ny+2, self.Nx+2))
        print("x ", self.Nx+2,"y ", self.Ny+2)
    
    def __establecer_condiciones_de_frontera(self):
        """Método privado: Establece condiciones iniciales"""
        self.malla[:,0] = self.v0
        self.malla[0,:(self.bloqueSuperior.i0)] = self.v0
        self.malla[0,(self.bloqueSuperior.i0):]=0
        self.malla[:,self.Nx+1] = 0
        self.malla[self.Ny+1,:] = 0
        
    def __procesar_bloques(self):
        self.bloqueSuperior.procesar_bloque_en_malla(self.h, self.Ny)
        self.bloqueInferior.procesar_bloque_en_malla(self.h, self.Ny)
        
        
    def __aplicar_bloque(self):
        """Método privado: Aplica un bloque específico"""
        # Convertir coordenadas a índices
        self.malla[self.bloqueSuperior.jn_fin:self.bloqueSuperior.j0+1, self.bloqueSuperior.i0:self.bloqueSuperior.in_fin+1] = 0
        self.malla[self.bloqueInferior.jn_fin:self.bloqueInferior.j0+1, self.bloqueInferior.i0:self.bloqueInferior.in_fin+1] = 0
        print("x, superior ",self.bloqueSuperior.i0, self.bloqueSuperior.in_fin+1, "y ",self.bloqueSuperior.j0, self.bloqueSuperior.jn_fin+1)
        print("x, inferior",self.bloqueInferior.i0, self.bloqueInferior.in_fin+1, "y ",self.bloqueInferior.j0, self.bloqueInferior.jn_fin+1)
     
    # Métodos públicos
    def mostrar_malla(self):
        """Método público: Muestra la malla"""
        print("Malla actual:")
        print(self.malla)

    def retornar_malla(self):
        return self.malla
    
    def obtener_valor(self, x, y):
        """Método público: Obtiene valor en coordenadas específicas"""
        i = int(x / self.h)
        j = int(y / self.h)
        return self.malla[i, j]
    
    def guardar_matriz_txt(self, nombre_archivo="matriz_malla.txt"):
        """
        Método público: Guarda la matriz de la malla en un archivo de texto
        
        Args:
            nombre_archivo (str): Nombre del archivo donde guardar la matriz
        """
        try:
            # Guardar la matriz con formato legible
            np.savetxt(nombre_archivo, self.malla, fmt='%.6f', delimiter='\t')
            print(f"Matriz guardada en: {nombre_archivo}")
            print(f"Dimensiones: {self.malla.shape[0]} filas x {self.malla.shape[1]} columnas")
        except Exception as e:
            print(f"Error al guardar la matriz: {e}")
    
    def cargar_matriz_txt(self, nombre_archivo):
        """
        Método público: Carga una matriz desde un archivo de texto
        
        Args:
            nombre_archivo (str): Nombre del archivo a cargar
            
        Returns:
            numpy.ndarray: Matriz cargada desde el archivo
        """
        try:
            matriz = np.loadtxt(nombre_archivo, delimiter='\t')
            print(f"Matriz cargada desde: {nombre_archivo}")
            print(f"Dimensiones: {matriz.shape[0]} filas x {matriz.shape[1]} columnas")
            return matriz
        except Exception as e:
            print(f"Error al cargar la matriz: {e}")
            return None

    def valores_aleatorios_dentro_de_malla(self, divisionesHorizontales, divisionesVerticales):
        """Método privado: Aplica un bloque específico"""
        # Cóloca dentro de la malla, los valores de la velocidad del agua aleatoriamente, entre 0 y 1, de manera uniforme, sin tener en cuenta los bordes ni los bloques.
        tamaño_horizontal = self.Nx / divisionesHorizontales
        tamaño_vertical = self.Ny / divisionesVerticales
        pasoH = 1 / (2 * divisionesHorizontales)  # Si son 10 divisiones, de tamaño 5 cuadritos para malla de Nx=50,el paso = 1/20 = 0.05
        pasoV = 1 / (2 * divisionesVerticales)  # Si son 5 divisiones, de tamaño 1 cuadrito para malla de Ny=5,el paso = 1/10 = 0.1
        # Generar lista de 1 a 0 con paso preciso
        lista_horizontal = np.append(np.arange(0.95,0,-pasoH), 0)
        lista_vertical = np.append(np.arange(0.9, 0,-pasoV), 0)
        

        k=1
        m=1
        count_i=1
        print("lista_horizontal ", lista_horizontal)
        print("lista_vertical ", lista_vertical)
        for i in range(1, self.Ny+1):
            for j in range(1,self.Nx+1):
                
                print("j % tamaño_horizontal ", j % tamaño_horizontal, "tamaño_horizontal-1 ", tamaño_horizontal-1)    
                if i  != count_i:
                    count_i += 1
                    k += 2

                
                if j % tamaño_horizontal  == 1: 
                    if(j==1):
                        m = 1
                    else:
                        m += 2

                    
                
                
                #print("aleatorio_horizontal ", aleatorio_horizontal, "aleatorio_vertical ", aleatorio_vertical)
                aleatorio_horizontal = random.choice([lista_horizontal[m-1], lista_horizontal[m]])
                aleatorio_vertical = random.choice([lista_vertical[k-1], lista_vertical[k]])
                #print("i ", i, "j ", j)
                #print("k ", k, "m ", m, "count_i", count_i, "aleatorio_horizontal ", aleatorio_horizontal, "aleatorio_vertical ", aleatorio_vertical)

                numerandom =(aleatorio_horizontal+aleatorio_vertical)/2

                self.malla[i, j] = numerandom
        





    def visualizar_malla(self, titulo="Malla de Valores", guardar=False, nombre_archivo="malla.png", mostrar_numeros=True):
        """
        Método público: Visualiza la malla con colores y rejillas
        
        Args:
            titulo (str): Título de la gráfica
            guardar (bool): Si True, guarda la imagen
            nombre_archivo (str): Nombre del archivo a guardar
            mostrar_numeros (bool): Si True, muestra los valores numéricos en cada celda
        """
        # Crear la figura más grande
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Usar imshow para los colores con extent correcto
        # La matriz es 7×52, así que extent debe ser [0, 52, 0, 7]
        im = ax.imshow(self.malla, cmap='viridis', origin='upper', 
                      extent=[0, 52, 0, 7], aspect='equal')
        
        # Agregar valores numéricos en cada celda (opcional)
        if mostrar_numeros:
            for i in range(self.malla.shape[0]):  # Filas
                for j in range(self.malla.shape[1]):  # Columnas
                    valor = self.malla[i, j]
                    # Mostrar solo 2 decimales para valores no enteros
                    if valor == int(valor):
                        texto = f"{int(valor)}"
                    else:
                        texto = f"{valor:.2f}"
                    
                    # Color del texto: blanco para valores altos, negro para valores bajos
                    color_texto = 'white' if valor > 0.5 else 'black'
                    
                    # Corregir la posición Y para que coincida con origin='upper'
                    # Con origin='upper', la fila 0 está arriba, así que invertimos i
                    y_pos = self.malla.shape[0] - 1 - i + 0.5
                    
                    # Agregar el texto en el centro de cada celda
                    ax.text(j + 0.5, y_pos, texto, 
                           ha='center', va='center', 
                           color=color_texto, fontsize=5.5, fontweight='bold')
        
        # Crear líneas de rejilla que coincidan exactamente con cada celda
        # Líneas verticales: de 0 a 52 (53 líneas para 52 columnas)
        for i in range(53):  # 0, 1, 2, ..., 52
            ax.axvline(x=i, color='black', linewidth=1.2, alpha=0.9)
        
        # Líneas horizontales: de 0 a 7 (8 líneas para 7 filas)
        for j in range(8):  # 0, 1, 2, ..., 7
            ax.axhline(y=j, color='black', linewidth=1.2, alpha=0.9)
        
        # Configurar la barra de colores
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
        cbar.set_label('Valor', rotation=270, labelpad=25, fontsize=14)
        cbar.ax.tick_params(labelsize=12)
        
        # Configurar ejes
        ax.set_xlabel('Índice de Columna', fontsize=14, fontweight='bold')
        ax.set_ylabel('Índice de Fila', fontsize=14, fontweight='bold')
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        
        # Configurar ticks de los ejes
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # Agregar grid más visible
        ax.grid(True, alpha=0.7, color='black', linewidth=0.8)
        ax.set_axisbelow(True)
        
        # Configurar aspecto
        ax.set_aspect('equal')
        
        # Configurar límites de los ejes
        ax.set_xlim(0, 52)
        ax.set_ylim(0, 7)
        
        # Mejorar la apariencia general
        ax.spines['top'].set_visible(True)
        ax.spines['right'].set_visible(True)
        ax.spines['top'].set_linewidth(1.5)
        ax.spines['right'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        
        # Mostrar la gráfica
        plt.tight_layout()
        
        if guardar:
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"Imagen guardada como: {nombre_archivo}")
        
        plt.show()
        
        # Mostrar estadísticas
        print(f"\nEstadísticas de la malla:")
        print(f"Dimensiones: {self.Nx+2} x {self.Ny+2}")
        print(f"Tamaño de celda: {self.h}")
        print(f"Valor mínimo: {self.malla.min():.3f}")
        print(f"Valor máximo: {self.malla.max():.3f}")
        print(f"Valor promedio: {self.malla.mean():.3f}")
    
class Vector:
    def __init__(self, matrizMalla):
        self.x0 = np.zeros(matrizMalla.shape[0]*matrizMalla.shape[1])
        #print("filas ", matrizMalla.shape[0], "columnas ", matrizMalla.shape[1])
        for i in range(matrizMalla.shape[0]):
            for j in range(matrizMalla.shape[1]):
                self.x0[i*matrizMalla.shape[1]+j] = matrizMalla[i, j]
        
    def retornar_vector(self):
        return self.x0
    
    def mostrar_vector(self):
        print("x0 ", self.x0)


class Vector_evaluado:
    def __init__(self, vector, malla, Vy):
        """
        Inicializa el evaluador de vector
        
        Args:
            vector: Objeto Vector con el vector x0
            malla: Objeto Malla para obtener información de bloques
            Vy: Valor de vorticidad
        """
        self.vector = vector
        self.malla = malla
        self.Vy = Vy
        self.filas = malla.malla.shape[0]  # 7
        self.columnas = malla.malla.shape[1]  # 52
        
    def evaluar_ecuacion(self, X_ij, X_i_j_plus_1, X_i_j_minus_1, X_i_minus_1_j, X_i_plus_1_j):
        """
        Evalúa la ecuación: 0 = - X_{i*52+j} + (1/4) * (
            X_{i*52+(j+1)} + X_{i*52+(j-1)} + X_{(i-1)*52+j} + X_{(i+1)*52+j}
            - 4 * X_{i*52+j} * [X_{i*52+(j+1)} - X_{i*52+(j-1)}]
            - 4 * V_y * [X_{(i-1)*52+j} - X_{(i+1)*52+j}]
        )
        
        Args:

            valores en posicion de la malla:
            X_ij: Valor en posición (i,j)
            X_i_j_plus_1: Valor en posición (i,j+1) 
            X_i_j_minus_1: Valor en posición (i,j-1)
            X_i_minus_1_j: Valor en posición (i-1,j)
            X_i_plus_1_j: Valor en posición (i+1,j)

        Returns:
            float: Resultado de la evaluación de la ecuación
        """
        resultado = -X_ij + (1/4) * (
            X_i_j_plus_1 + X_i_j_minus_1 + X_i_minus_1_j + X_i_plus_1_j
            - 4 * X_ij * (X_i_j_plus_1 - X_i_j_minus_1)
            - 4 * self.Vy * (X_i_minus_1_j - X_i_plus_1_j)
        )
        return resultado
        
    def esta_en_bloque(self, i, j):
        """
        Verifica si la posición (i,j) está dentro de un bloque
        
        Args:
            i: índice de fila
            j: índice de columna
            
        Returns:
            bool: True si está en un bloque, False en caso contrario
        """
         # Verificar bloque superior
        if (self.malla.bloqueSuperior.jn_fin <= i <= self.malla.bloqueSuperior.j0 and
            self.malla.bloqueSuperior.i0 <= j <= self.malla.bloqueSuperior.in_fin):
            return True
            
        # Verificar bloque inferior
        if (self.malla.bloqueInferior.jn_fin <= i <= self.malla.bloqueInferior.j0 and
            self.malla.bloqueInferior.i0 <= j <= self.malla.bloqueInferior.in_fin):
            return True
            
        return False
    
    def evaluar_vector_completo(self):
        """
        Evalúa el vector completo aplicando la ecuación en cada punto
        considerando las condiciones de frontera
        
        Returns:
            numpy.ndarray: Vector evaluado
        """
        self.vector_evaluado = np.zeros_like(self.vector.x0)
        
        for i in range(self.filas):
            for j in range(self.columnas):
                indice = i * self.columnas + j
                
                # Condiciones de frontera
                if i == 0 and j < self.malla.bloqueSuperior.i0:
                    # Frontera superior antes del bloque superior
                    self.vector_evaluado[indice] = 1.0

                elif i == 0 and j >= self.malla.bloqueSuperior.i0:
                    #frontera arriba del bloque superior
                    self.vector_evaluado[indice] = 0.0

                elif j == 0:
                    # Frontera izquierda
                    self.vector_evaluado[indice] = 1.0
                elif i == 6:  # i == Ny+1 (6)
                    # Frontera inferior
                    self.vector_evaluado[indice] = 0.0
                elif j == 51:  # j == Nx+1 (51)
                    # Frontera derecha
                    self.vector_evaluado[indice] = 0.0
                elif self.esta_en_bloque(i, j):
                    # Dentro de los bloques
                    self.vector_evaluado[indice] = 0.0
                else:
                    # Aplicar la ecuación para el resto de puntos
            
                        # Obtener valores vecinos
                    X_ij = self.vector.x0[indice]
                    X_i_j_plus_1 = self.vector.x0[i * self.columnas + (j + 1)]
                    X_i_j_minus_1 = self.vector.x0[i * self.columnas + (j - 1)]
                    X_i_minus_1_j = self.vector.x0[(i - 1) * self.columnas + j]
                    X_i_plus_1_j = self.vector.x0[(i + 1) * self.columnas + j]
                        
                        # Evaluar la ecuación
                    self.vector_evaluado[indice] = self.evaluar_ecuacion(
                        X_ij, X_i_j_plus_1, X_i_j_minus_1, X_i_minus_1_j, X_i_plus_1_j
                    )
                    
        
        return self.vector_evaluado
    
    
    def mostrar_vector_evaluado(self):
        """
        Muestra el vector evaluado de manera sencilla
        """
        print("F(xi):", self.vector_evaluado)


def main():
    # Crear bloques
    bloqueSuperior = Bloque(296, 400, 32, 40)
    bloqueInfierior = Bloque(176, 232, 1, 16)

    # Cargar matriz desde archivo
    if os.path.exists("matriz_valores_iniciales.txt"):
        matriz_cargada = np.loadtxt("matriz_valores_iniciales.txt", delimiter='\t')
        mallaInicial = Malla(400, 40, 8, 1, bloqueSuperior, bloqueInfierior, 10, 5, matriz_inicial=matriz_cargada)
        vector = Vector(mallaInicial.retornar_malla())
        print("=== Vector Original ===")
        vector.mostrar_vector()
    else:
        matriz_cargada = None
        mallaInicial = Malla(400, 40, 8, 1, bloqueSuperior, bloqueInfierior, 10, 5, matriz_inicial=matriz_cargada)
        # Guardar la matriz en un archivo de texto
        mallaInicial.guardar_matriz_txt("matriz_valores_iniciales.txt")
        vector = Vector(mallaInicial.retornar_malla())
        print("=== Vector Original ===")
        vector.mostrar_vector()
    
    # evaluador de vector con vorticidad Vy 
    Vy = 0.1
    evaluador = Vector_evaluado(vector, mallaInicial, Vy)
    
    print(f"\n=== Evaluación del Vector con Vorticidad Vy = {Vy} ===")
    vector_evaluado = evaluador.evaluar_vector_completo()
    
    # Mostrar resultados usando el método sencillo
    evaluador.mostrar_vector_evaluado()
   
    
    
    # Mostrar información de la malla
    #print("=== Información de la Malla ===")
    #mallaInicial.mostrar_malla()   
    
    # Visualizar la malla con colores
    print("\n=== Visualización de la Malla ===")
    """malla.visualizar_malla(
        titulo="Malla de Simulación - Análisis de fluido laminar",
        guardar=True,
        nombre_archivo="malla_simulacion.png",
        mostrar_numeros=True
    )
    """

if __name__ == "__main__":
    main()