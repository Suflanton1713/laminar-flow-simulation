#imports y variables globales

import random
import numpy as np
import matplotlib.pyplot as plt
import os

np.set_printoptions(suppress=True, precision=2)

# Parámetros globales
h = 8
Vy = -0.01

class Bloque:
    def __init__(self, x0, xn, y0, yn):
        self.x0 = x0
        self.xn = xn
        self.y0 = y0
        self.yn = yn

    def procesar_bloque_en_malla(self, h, Ny):
        self.i0 = int(self.x0 / h)
        self.j0 = abs(int(np.ceil(self.y0 / h)) - (Ny+1))
        self.in_fin = int(self.xn / h)
        self.jn_fin = abs(int(np.ceil(self.yn / h)) - (Ny+1))
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
        
        # Si se proporciona una matriz inicial, usarla directamente
        if matriz_inicial is not None:
            self.malla = matriz_inicial.copy()
            print("Usando matriz inicial proporcionada")
        else:
            # Proceso normal de generación de malla
            self.__crear_malla()
            self.__procesar_bloques()
            self.__establecer_condiciones_de_frontera()
            self.valores_aleatorios_dentro_de_malla(divisionesHorizontales, divisionesVerticales)
            self.__aplicar_bloque()

    def __crear_malla(self):
        """Método privado: Crea la matriz de la malla"""
        self.malla = np.zeros((self.Ny+2, self.Nx+2))
    
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
        self.malla[self.bloqueSuperior.jn_fin:self.bloqueSuperior.j0+1, self.bloqueSuperior.i0:self.bloqueSuperior.in_fin+1] = 0
        self.malla[self.bloqueInferior.jn_fin:self.bloqueInferior.j0+1, self.bloqueInferior.i0:self.bloqueInferior.in_fin+1] = 0
     
    def mostrar_malla(self):
        """Método público: Muestra la malla"""
        print("Malla actual:")
        print(self.malla)

    def retornar_malla(self):
        return self.malla
    
    def guardar_matriz_txt(self, nombre_archivo="matriz_malla.txt"):
        """Guarda la matriz de la malla en un archivo de texto"""
        try:
            np.savetxt(nombre_archivo, self.malla, fmt='%.6f', delimiter='\t')
            print(f"Matriz guardada en: {nombre_archivo}")
        except Exception as e:
            print(f"Error al guardar la matriz: {e}")
    
    def cargar_matriz_txt(self, nombre_archivo):
        """Carga una matriz desde un archivo de texto"""
        try:
            matriz = np.loadtxt(nombre_archivo, delimiter='\t')
            print(f"Matriz cargada desde: {nombre_archivo}")
            return matriz
        except Exception as e:
            print(f"Error al cargar la matriz: {e}")
            return None

    def valores_aleatorios_dentro_de_malla(self, divisionesHorizontales, divisionesVerticales):
        """Aplica valores aleatorios dentro de la malla"""
        tamaño_horizontal = self.Nx / divisionesHorizontales
        tamaño_vertical = self.Ny / divisionesVerticales
        pasoH = 1 / (2 * divisionesHorizontales)
        pasoV = 1 / (2 * divisionesVerticales)
        
        lista_horizontal = np.append(np.arange(0.95, 0, -pasoH), 0)
        lista_vertical = np.append(np.arange(0.9, 0, -pasoV), 0)
        
        k = 1
        m = 1
        count_i = 1
        
        for i in range(1, self.Ny+1):
            for j in range(1, self.Nx+1):
                if i != count_i:
                    count_i += 1
                    k += 2
                
                if j % tamaño_horizontal == 1: 
                    if j == 1:
                        m = 1
                    else:
                        m += 2
                
                aleatorio_horizontal = random.choice([lista_horizontal[m-1], lista_horizontal[m]])
                aleatorio_vertical = random.choice([lista_vertical[k-1], lista_vertical[k]])
                numerandom = (aleatorio_horizontal + aleatorio_vertical) / 2
                self.malla[i, j] = numerandom

    def visualizar_malla(self, titulo="Malla de Valores", guardar=False, nombre_archivo="malla.png", mostrar_numeros=True):
        """Visualiza la malla con colores y valores"""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        im = ax.imshow(self.malla, cmap='viridis', origin='upper', 
                      extent=[0, self.Nx+2, 0, self.Ny+2], aspect='equal')
        
        if mostrar_numeros:
            for i in range(self.malla.shape[0]):
                for j in range(self.malla.shape[1]):
                    valor = self.malla[i, j]
                    if valor == int(valor):
                        texto = f"{int(valor)}"
                    else:
                        texto = f"{valor:.2f}"
                    
                    color_texto = 'white' if valor > 0.5 else 'black'
                    y_pos = self.malla.shape[0] - 1 - i + 0.5
                    
                    ax.text(j + 0.5, y_pos, texto, 
                           ha='center', va='center', 
                           color=color_texto, fontsize=5.5, fontweight='bold')
        
        # Líneas de rejilla
        for i in range(self.Nx+3):
            ax.axvline(x=i, color='black', linewidth=1.2, alpha=0.9)
        for j in range(self.Ny+3):
            ax.axhline(y=j, color='black', linewidth=1.2, alpha=0.9)
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
        cbar.set_label('Valor', rotation=270, labelpad=25, fontsize=14)
        
        ax.set_xlabel('Índice de Columna', fontsize=14, fontweight='bold')
        ax.set_ylabel('Índice de Fila', fontsize=14, fontweight='bold')
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        
        ax.set_aspect('equal')
        ax.set_xlim(0, self.Nx+2)
        ax.set_ylim(0, self.Ny+2)
        
        plt.tight_layout()
        
        if guardar:
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            print(f"Imagen guardada como: {nombre_archivo}")
        
        plt.show()


class Vector:
    def __init__(self, matrizMalla):
        """Convierte la matriz de malla en un vector"""
        self.vec = np.zeros(matrizMalla.shape[0] * matrizMalla.shape[1])
        self.vectFunction = np.zeros(matrizMalla.shape[0] * matrizMalla.shape[1])
        self.matrixJacobiana = np.zeros((len(self.vec), len(self.vec)))
        self.filas = matrizMalla.shape[0]
        self.columnas = matrizMalla.shape[1]
        
        # Convertir matriz a vector
        for i in range(matrizMalla.shape[0]):
            for j in range(matrizMalla.shape[1]):
                self.vec[i * matrizMalla.shape[1] + j] = matrizMalla[i, j]
    
    def cal_function(self, malla_obj):
        """Calcula el vector función F(x)"""
        val_Vij = Vy
        x0 = self.vec
        
        for i in range(self.filas):
            for j in range(self.columnas):
                indice = i * self.columnas + j
                
                # Condiciones de frontera
                if i == 0 and j < malla_obj.bloqueSuperior.i0:
                    self.vectFunction[indice] = 0
                elif i == 0 and j >= malla_obj.bloqueSuperior.i0:
                    self.vectFunction[indice] = 0
                elif j == 0:
                    self.vectFunction[indice] = 0
                elif i == self.filas - 1:
                    self.vectFunction[indice] = 0
                elif j == self.columnas - 1:
                    self.vectFunction[indice] = 0
                elif self.esta_en_bloque(i, j, malla_obj):
                    self.vectFunction[indice] = 0
                else:
                    # Aplicar ecuación
                    X_ij = x0[indice]
                    X_i_j_plus_1 = x0[i * self.columnas + (j + 1)]
                    X_i_j_minus_1 = x0[i * self.columnas + (j - 1)]
                    X_i_minus_1_j = x0[(i - 1) * self.columnas + j]
                    X_i_plus_1_j = x0[(i + 1) * self.columnas + j]
                    
                    self.vectFunction[indice] = -X_ij + (1/4) * (
                        X_i_j_plus_1 + X_i_j_minus_1 + X_i_minus_1_j + X_i_plus_1_j
                        - 4 * X_ij * (X_i_j_plus_1 - X_i_j_minus_1)
                        - 4 * val_Vij * (X_i_minus_1_j - X_i_plus_1_j)
                    )
    
    def esta_en_bloque(self, i, j, malla_obj):
        """Verifica si la posición está en un bloque"""
        if (malla_obj.bloqueSuperior.jn_fin <= i <= malla_obj.bloqueSuperior.j0 and
            malla_obj.bloqueSuperior.i0 <= j <= malla_obj.bloqueSuperior.in_fin):
            return True
        
        if (malla_obj.bloqueInferior.jn_fin <= i <= malla_obj.bloqueInferior.j0 and
            malla_obj.bloqueInferior.i0 <= j <= malla_obj.bloqueInferior.in_fin):
            return True
        
        return False

    def cal_jacobiano(self, malla_obj):
        """Calcula la matriz jacobiana"""
        v_ij = Vy
        vec_0 = self.vec
        self.matrixJacobiana.fill(0.0)
        
        for i in range(self.filas):
            for j in range(self.columnas):
                ecuacion = i * self.columnas + j
                
                # Condiciones de frontera
                if (i == 0 or j == 0 or i == self.filas - 1 or 
                    j == self.columnas - 1 or self.esta_en_bloque(i, j, malla_obj)):
                    self.matrixJacobiana[ecuacion, ecuacion] = 1
                else:
                    # Derivadas parciales
                    idx = ecuacion
                    self.matrixJacobiana[ecuacion, idx] = -1 - vec_0[idx+1] + vec_0[idx-1]
                    self.matrixJacobiana[ecuacion, idx+1] = (1/4) - vec_0[idx]
                    self.matrixJacobiana[ecuacion, idx-1] = (1/4) + vec_0[idx]
                    self.matrixJacobiana[ecuacion, idx+self.columnas] = (1/4) + v_ij
                    self.matrixJacobiana[ecuacion, idx-self.columnas] = (1/4) - v_ij

    def newVector(self, forma, jacobiana_SDP, vector_SDP, iteracion):
        """Actualiza el vector usando Newton-Raphson"""

        if forma == "inversa":
            jacobiano_inv = np.linalg.inv(jacobiana_SDP)
            xn = np.subtract(vector_SDP, np.matmul(jacobiano_inv, self.vectFunction))
            self.vec = xn
        elif forma == "conjugado":
            if iteracion == 0:
                p0 = vector_SDP - np.dot(jacobiana_SDP, self.vectFunction)
                r0 = p0.copy()
                alpha0 = np.dot(r0.T, r0) / np.dot(p0.T, np.dot(jacobiana_SDP, p0))

                xn = vector_SDP + (alpha0 * p0)
                return xn
            else:
                rk = vector_SDP - np.dot(jacobiana_SDP, self.vectFunction)
                beta_k = np.dot(rk.T, rk) / np.dot(r0.T, r0)
                pk = rk + beta_k * p0
                alpha_k = np.dot(rk.T, rk) / np.dot(pk.T, np.dot(jacobiana_SDP, pk))

                xn = vector_SDP + (alpha_k * pk)
                return xn
                
            
        else:
            delta_x = np.linalg.solve(self.matrixJacobiana, self.vectFunction)
            xn = self.vec - delta_x
            self.vec = xn

        

    def showInConsole(self, condicion=False):
        """Muestra el vector en consola"""
        if condicion:
            x0 = self.vec
            for i in reversed(range(self.filas)):
                fila = x0[i*self.columnas:(i+1)*self.columnas]
                fila_str = " ".join(f"{val:4.2f}" for val in fila)
                print(fila_str)

    def showPlot(self, condicion=False):
        """Muestra un mapa de calor del vector"""
        if condicion:
            x0 = self.vec
            matriz = np.array(x0).reshape(self.filas, self.columnas)
            
            escala = 0.6
            plt.figure(figsize=(self.columnas * escala, self.filas * escala))
            cmap = plt.cm.viridis
            
            im = plt.imshow(matriz, cmap=cmap, vmin=0.0001, vmax=1, origin="upper")
            
            plt.colorbar(im, label="Valores")
            plt.title("Distribución de valores en la malla")
            plt.xlabel("Columna (j)")
            plt.ylabel("Fila (i)")
            
            plt.xticks(np.arange(0, self.columnas, 5))
            plt.yticks(np.arange(0, self.filas, 1))
            plt.show()

    def showPlotDetail(self, condicion=False):
        """Muestra un mapa de calor detallado con valores"""
        if condicion:
            x0 = self.vec
            matriz = np.array(x0).reshape(self.filas, self.columnas)
            
            escala = 0.6
            plt.figure(figsize=(self.columnas * escala, self.filas * escala))
            
            cmap = plt.cm.viridis
            im = plt.imshow(matriz, cmap=cmap, vmin=0.0001, vmax=1, origin="upper")
            
            plt.colorbar(im, label="Valores")
            plt.title("Distribución detallada de valores en la malla")
            plt.xlabel("Columna (j)")
            plt.ylabel("Fila (i)")
            
            # Cuadrícula
            ax = plt.gca()
            ax.set_xticks(np.arange(-0.5, self.columnas, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, self.filas, 1), minor=True)
            ax.grid(which="minor", color="white", linestyle='-', linewidth=0.5)
            ax.tick_params(which="minor", bottom=False, left=False)
            
            # Escribir valores en cada celda
            for i in range(self.filas):
                for j in range(self.columnas):
                    valor = matriz[i, j]
                    if valor == 1 or valor == 0:
                        texto = f"{int(valor)}"
                    else:
                        texto = f"{valor:.2f}"[1:]
                    
                    color_texto = "#333333" if valor == 0 else "white"
                    
                    plt.text(j, i, texto, ha="center", va="center",
                            color=color_texto, fontsize=6)
            plt.show()

    def visualizar_jacobiana(self, titulo="Matriz Jacobiana", guardar=False, nombre_archivo="jacobiana.png"):
        """Visualiza la matriz jacobiana como una imagen de calor"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        im = ax.imshow(self.matrixJacobiana, cmap='RdBu_r', aspect='equal')
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Valor', rotation=270, labelpad=20)
        
        ax.set_xlabel('Índice de Columna', fontsize=12)
        ax.set_ylabel('Índice de Fila', fontsize=12)
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        plt.tight_layout()
        
        if guardar:
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            print(f"Visualización guardada como: {nombre_archivo}")
        
        plt.show()


def main():
    # Crear bloques
    bloqueSuperior = Bloque(296, 400, 32, 40)
    bloqueInferior = Bloque(176, 232, 1, 16)

    print("Generando nueva matriz inicial con algoritmo aleatorio...")
    mallaInicial = Malla(400, 40, h, 1, bloqueSuperior, bloqueInferior, 10, 5, matriz_inicial=None)
    
    # Crear vector inicial
    xinit = Vector(mallaInicial.retornar_malla())
    
    # Método de Newton-Raphson
    max_iterations = 100
    tolerance_residuo = 1e-10 #Cambio entre iteraciones 
    tolerance_epsilon = 1e-8
    
    print("\n" + "="*50)
    print("Iniciando método de Newton-Raphson...")
    print("="*50)
    print(f"Condiciones de parada:")
    print(f"  1. Norma del residuo < {tolerance_residuo:.0e}")
    print(f"  2. Epsilon (cambio entre iteraciones) < {tolerance_epsilon:.0e}")
    print(f"  3. Número máximo de iteraciones: {max_iterations}")
    
    # Guardar vector anterior para calcular epsilon
    vec_anterior = xinit.vec.copy()
    
    for i in range(max_iterations):
        print(f"\nIteración: {i+1}")
        
        
        xinit.cal_function(mallaInicial) #calcula F(X) para vector actual
        residuo_norm = np.linalg.norm(xinit.vectFunction) #calcula la norma del residuo
        print(f"  Norma del residuo: {residuo_norm:.10e}")
        
        # Condición 1: Norma del residuo
        if residuo_norm < tolerance_residuo:
            print(f"\n¡Convergencia alcanzada en {i + 1} iteraciones!")
            print(f"Criterio: Norma del residuo < {tolerance_residuo:.0e}")
            break
        
        xinit.cal_jacobiano(mallaInicial)
        
        
        cond = np.linalg.cond(xinit.matrixJacobiana,2)
        print(f"  Condición de la Jacobiana: {cond}")

        JacobTrans = xinit.matrixJacobiana.T
        vectorTrans = xinit.vectFunction.T

        nuevaJacob = np.dot(JacobTrans, xinit.matrixJacobiana)
        nuevaVector = np.dot(vectorTrans, xinit.vectFunction)

        xinit.newVector(forma=None, jacobiana_SDP=nuevaJacob, vector_SDP=nuevaVector, iteracion=i)


        condTrans = np.linalg.cond(nuevaJacob,2)
        print(f"  Condición de la nueva Jacobiana: {condTrans}")



        # Condición 2: Epsilon (cambio entre iteraciones)
        epsilon = np.linalg.norm(xinit.vec - vec_anterior)
        print(f"  Epsilon (cambio): {epsilon:.10e}")
        
        if epsilon < tolerance_epsilon:
            print(f"\n¡Convergencia alcanzada en {i + 1} iteraciones!")
            print(f"Criterio: Epsilon < {tolerance_epsilon:.0e}")
            break
        
        # Actualizar vector anterior
        vec_anterior = xinit.vec.copy()
    else:
        # Condición 3: Máximo de iteraciones alcanzado
        print(f"\nNo convergió después de {max_iterations} iteraciones")
        print(f"Criterio: Se alcanzó el número máximo de iteraciones")
    
    # Visualizar resultados finales
    print("\n=== Resultados Finales ===")
    xinit.showPlotDetail(True)
    xinit.showPlot(True)
    xinit.showInConsole(True)
    
    # Convertir vector final a matriz y visualizar
    matriz_final = xinit.vec.reshape(xinit.filas, xinit.columnas)
    
    # Verificar si hay valores mayores a 1
    print(f"\nValor máximo en matriz_final: {np.max(matriz_final)}")
    print(f"Valor mínimo en matriz_final: {np.min(matriz_final)}")
    
    # Actualizar la malla inicial con los valores finales
    mallaInicial.malla = matriz_final.copy()
    
    # Verificar después de actualizar
    print(f"Valor máximo en mallaInicial.malla: {np.max(mallaInicial.malla)}")
    print(f"Valor mínimo en mallaInicial.malla: {np.min(mallaInicial.malla)}")
    
    # Guardar matriz final
    
    """

    mallaInicial.guardar_matriz_txt("matriz_valores_finales.txt")

    mallaInicial.visualizar_malla(
        titulo="Malla de valores finales - Simulación",
        guardar=True,
        nombre_archivo="malla_final.png",
        mostrar_numeros=True
    )
    """
    
    
    print("\n" + "="*50)
    print("Simulación completada")
    print("="*50)


if __name__ == "__main__":
    main()