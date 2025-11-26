"""
Simulación de Flujo Laminar 2D - Método de Newton-Raphson con Gradiente Conjugado
==================================================================================
Resuelve las ecuaciones de Navier-Stokes simplificadas para flujo incompresible
usando diferencias finitas y el método de Newton-Raphson.
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline
from mpl_toolkits.mplot3d import Axes3D

np.set_printoptions(suppress=True, precision=2)

# ═══════════════════════════════════════════════════════════════════════════════
# PARÁMETROS GLOBALES
# ═══════════════════════════════════════════════════════════════════════════════
H_DISCRETIZACION = 8      # Paso de discretización espacial
VY_COMPONENTE = -0.000005  # Componente vertical de velocidad


# ═══════════════════════════════════════════════════════════════════════════════
# CLASE BLOQUE - Representa obstáculos sólidos en el dominio
# ═══════════════════════════════════════════════════════════════════════════════
class Bloque:
    def __init__(self, x0, xn, y0, yn):
        """Define un bloque rectangular con coordenadas físicas."""
        self.x0 = x0
        self.xn = xn
        self.y0 = y0
        self.yn = yn

    def procesar_bloque_en_malla(self, h, Ny):
        """Convierte coordenadas físicas a índices de malla."""
        self.i0 = int(self.x0 / h)
        self.j0 = abs(int(np.ceil(self.y0 / h)) - (Ny + 1))
        self.in_fin = int(self.xn / h)
        self.jn_fin = abs(int(np.ceil(self.yn / h)) - (Ny + 1))
        return self.i0, self.j0, self.in_fin, self.jn_fin


# ═══════════════════════════════════════════════════════════════════════════════
# CLASE MALLA - Gestiona el dominio computacional
# ═══════════════════════════════════════════════════════════════════════════════
class Malla:
    def __init__(self, Lx, Ly, h, v0, bloqueSuperior, bloqueInferior, 
                 divisionesHorizontales, divisionesVerticales, matriz_inicial=None):
        """Inicializa la malla con geometría y condiciones de frontera."""
        self.Lx = Lx
        self.Ly = Ly
        self.h = h
        self.v0 = v0
        self.bloqueSuperior = bloqueSuperior
        self.bloqueInferior = bloqueInferior
        self.Nx = int(Lx / h)
        self.Ny = int(Ly / h)
        
        if matriz_inicial is not None:
            self.malla = matriz_inicial.copy()
        else:
            self._crear_malla()
            self._procesar_bloques()
            self._establecer_condiciones_de_frontera()
            self._valores_aleatorios_dentro_de_malla(divisionesHorizontales, divisionesVerticales)
            self._aplicar_bloque()

    def _crear_malla(self):
        self.malla = np.zeros((self.Ny + 2, self.Nx + 2))
    
    def _establecer_condiciones_de_frontera(self):
        self.malla[:, 0] = self.v0                                    # Entrada
        self.malla[0, :self.bloqueSuperior.i0] = 0                    # Borde superior izq
        self.malla[0, self.bloqueSuperior.i0:] = 0                    # Borde superior der
        self.malla[:, self.Nx + 1] = 0                                # Salida
        self.malla[self.Ny + 1, :] = 0                                # Borde inferior
            
    def _procesar_bloques(self):
        self.bloqueSuperior.procesar_bloque_en_malla(self.h, self.Ny)
        self.bloqueInferior.procesar_bloque_en_malla(self.h, self.Ny)
        
    def _aplicar_bloque(self):
        self.malla[self.bloqueSuperior.jn_fin:self.bloqueSuperior.j0 + 1, 
                   self.bloqueSuperior.i0:self.bloqueSuperior.in_fin + 1] = 0
        self.malla[self.bloqueInferior.jn_fin:self.bloqueInferior.j0 + 1, 
                   self.bloqueInferior.i0:self.bloqueInferior.in_fin + 1] = 0

    def _valores_aleatorios_dentro_de_malla(self, divH, divV):
        """Genera valores iniciales decrecientes de izquierda a derecha y arriba a abajo."""
        tam_h = self.Nx / divH
        pasoH = 1 / (2 * divH)
        pasoV = 1 / (2 * divV)
        
        lista_h = np.append(np.arange(0.95, 0, -pasoH), 0)
        lista_v = np.append(np.arange(0.9, 0, -pasoV), 0)
        
        k, m, count_i = 1, 1, 1
        
        for i in range(1, self.Ny + 1):
            for j in range(1, self.Nx + 1):
                if i != count_i:
                    count_i += 1
                    k += 2
                
                if j % tam_h == 1:
                    m = 1 if j == 1 else m + 2
                
                aleatorio_h = random.choice([lista_h[m - 1], lista_h[m]])
                aleatorio_v = random.choice([lista_v[k - 1], lista_v[k]])
                self.malla[i, j] = (aleatorio_h + aleatorio_v) / 2

    def retornar_malla(self):
        return self.malla

    def guardar_matriz_txt(self, nombre_archivo="matriz_malla.txt"):
        np.savetxt(nombre_archivo, self.malla, fmt='%.6f', delimiter='\t')

    def visualizar_malla(self, titulo="Malla de Valores", guardar=False, 
                         nombre_archivo="malla.png", mostrar_numeros=True):
        """Visualiza la malla con mapa de calor y valores numéricos."""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        im = ax.imshow(self.malla, cmap='viridis', origin='upper', 
                       extent=[0, self.Nx + 2, 0, self.Ny + 2], aspect='equal')
        
        if mostrar_numeros:
            for i in range(self.malla.shape[0]):
                for j in range(self.malla.shape[1]):
                    valor = self.malla[i, j]
                    texto = f"{int(valor)}" if valor == int(valor) else f"{valor:.2f}"
                    color_texto = 'white' if valor > 0.5 else 'black'
                    y_pos = self.malla.shape[0] - 1 - i + 0.5
                    ax.text(j + 0.5, y_pos, texto, ha='center', va='center', 
                            color=color_texto, fontsize=5.5, fontweight='bold')
        
        for i in range(self.Nx + 3):
            ax.axvline(x=i, color='black', linewidth=1.2, alpha=0.9)
        for j in range(self.Ny + 3):
            ax.axhline(y=j, color='black', linewidth=1.2, alpha=0.9)
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
        cbar.set_label('Valor', rotation=270, labelpad=25, fontsize=14)
        
        ax.set_xlabel('Índice de Columna', fontsize=14, fontweight='bold')
        ax.set_ylabel('Índice de Fila', fontsize=14, fontweight='bold')
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim(0, self.Nx + 2)
        ax.set_ylim(0, self.Ny + 2)
        
        plt.tight_layout()
        if guardar:
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
        plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# CLASE VECTOR - Implementa Newton-Raphson con Gradiente Conjugado
# ═══════════════════════════════════════════════════════════════════════════════
class Vector:
    def __init__(self, matrizMalla):
        """Convierte la matriz de malla en un vector para Newton-Raphson."""
        self.filas = matrizMalla.shape[0]
        self.columnas = matrizMalla.shape[1]
        n = self.filas * self.columnas
        
        self.vec = matrizMalla.flatten()
        self.vectFunction = np.zeros(n)
        self.matrixJacobiana = np.zeros((n, n))
    
    def cal_function(self, malla_obj):
        """Calcula el vector de residuales F(X)."""
        x0 = self.vec
        
        for i in range(self.filas):
            for j in range(self.columnas):
                idx = i * self.columnas + j
                
                if self._es_frontera(i, j, malla_obj):
                    self.vectFunction[idx] = 0
                else:
                    X_ij = x0[idx]
                    X_der = x0[i * self.columnas + (j + 1)]
                    X_izq = x0[i * self.columnas + (j - 1)]
                    X_arr = x0[(i - 1) * self.columnas + j]
                    X_abj = x0[(i + 1) * self.columnas + j]
                    
                    self.vectFunction[idx] = -X_ij + (1/4) * (
                        X_der + X_izq + X_arr + X_abj
                        - 4 * X_ij * (X_der - X_izq)
                        - 4 * VY_COMPONENTE * (X_arr - X_abj)
                    )
    
    def _es_frontera(self, i, j, malla_obj):
        """Verifica si la posición está en frontera o dentro de un bloque."""
        if i == 0 or j == 0 or i == self.filas - 1 or j == self.columnas - 1:
            return True
        return self._esta_en_bloque(i, j, malla_obj)
    
    def _esta_en_bloque(self, i, j, malla_obj):
        """Verifica si la posición está dentro de un bloque sólido."""
        bs = malla_obj.bloqueSuperior
        bi = malla_obj.bloqueInferior
        
        if bs.jn_fin <= i <= bs.j0 and bs.i0 <= j <= bs.in_fin:
            return True
        if bi.jn_fin <= i <= bi.j0 and bi.i0 <= j <= bi.in_fin:
            return True
        return False

    def cal_jacobiano(self, malla_obj):
        """Calcula la matriz Jacobiana J(X)."""
        vec_0 = self.vec
        self.matrixJacobiana.fill(0.0)
        
        for i in range(self.filas):
            for j in range(self.columnas):
                idx = i * self.columnas + j
                
                if self._es_frontera(i, j, malla_obj):
                    self.matrixJacobiana[idx, idx] = 1
                else:
                    self.matrixJacobiana[idx, idx] = -1 - vec_0[idx + 1] + vec_0[idx - 1]
                    self.matrixJacobiana[idx, idx + 1] = 0.25 - vec_0[idx]
                    self.matrixJacobiana[idx, idx - 1] = 0.25 + vec_0[idx]
                    self.matrixJacobiana[idx, idx + self.columnas - 1] = 0.25 + VY_COMPONENTE
                    self.matrixJacobiana[idx, idx - self.columnas - 1] = 0.25 - VY_COMPONENTE

    def actualizar_newton(self, jacobiana_SDP, vector_SDP, verbose=True):
        """
        Resuelve el sistema lineal con Gradiente Conjugado y actualiza el vector.
        
        Parámetros:
        -----------
        jacobiana_SDP : ndarray
            Matriz simétrica definida positiva (J^T @ J)
        vector_SDP : ndarray
            Vector del sistema (-J^T @ F)
        verbose : bool
            Si True, muestra información del proceso
        """
        A = jacobiana_SDP
        b = vector_SDP
        
        tol = 1e-10
        max_iter = len(b)
        
        H = np.zeros_like(b)
        r = b - A @ H
        v = r.copy()
        c = np.dot(r.T, r)
        norm0 = np.sqrt(c)
        
        if verbose:
            print(f"\n  ┌─ Gradiente Conjugado ──────────────────────────┐")
            print(f"  │ Residuo inicial: {norm0:.3e}")
            print(f"  │ Tolerancia:      {tol * norm0:.3e}")
        
        for k in range(max_iter):
            Av = A @ v
            denom = np.dot(v.T, Av)
            
            if abs(denom) < 1e-30:
                if verbose:
                    print(f"  │ ⚠ División por cero en iter {k+1}")
                break
            
            t = c / denom
            H = H + t * v
            r = r - t * Av
            d = np.dot(r.T, r)
            norm_r = np.sqrt(d)
            
            if norm_r < tol * norm0:
                if verbose:
                    print(f"  │ ✓ Convergió en {k+1} iteraciones")
                    print(f"  │ Residuo final:  {norm_r:.3e}")
                break
            
            s = d / c
            v = r + s * v
            c = d
        
        if verbose:
            print(f"  └───────────────────────────────────────────────┘")
        
        self.vec = self.vec + H

    def mostrar_matriz(self, en_consola=False):
        """Muestra el vector como matriz en consola."""
        if en_consola:
            for i in reversed(range(self.filas)):
                fila = self.vec[i * self.columnas:(i + 1) * self.columnas]
                print(" ".join(f"{val:5.2f}" for val in fila))

    def mostrar_mapa_calor(self, detallado=False):
        """Muestra un mapa de calor del campo de velocidades."""
        matriz = self.vec.reshape(self.filas, self.columnas)
        
        escala = 0.6
        plt.figure(figsize=(self.columnas * escala, self.filas * escala))
        
        im = plt.imshow(matriz, cmap='viridis', vmin=0.0001, vmax=1, origin="upper")
        plt.colorbar(im, label="Velocidad")
        plt.title("Campo de velocidades" + (" (detallado)" if detallado else ""))
        plt.xlabel("Columna (j)")
        plt.ylabel("Fila (i)")
        
        if detallado:
            ax = plt.gca()
            ax.set_xticks(np.arange(-0.5, self.columnas, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, self.filas, 1), minor=True)
            ax.grid(which="minor", color="white", linestyle='-', linewidth=0.5)
            
            for i in range(self.filas):
                for j in range(self.columnas):
                    valor = matriz[i, j]
                    texto = f"{int(valor)}" if valor in [0, 1] else f"{valor:.2f}"[1:]
                    color = "#333333" if valor == 0 else "white"
                    plt.text(j, i, texto, ha="center", va="center", color=color, fontsize=6)
        else:
            plt.xticks(np.arange(0, self.columnas, 5))
            plt.yticks(np.arange(0, self.filas, 1))
        
        plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE ANÁLISIS Y VISUALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def es_diagonalmente_dominante(A, strict=False):
    """Verifica si una matriz es diagonalmente dominante."""
    A = np.array(A, dtype=float)
    n = A.shape[0]
    for i in range(n):
        diag = abs(A[i, i])
        off = np.sum(np.abs(A[i, :])) - diag
        if strict:
            if not (diag > off):
                return False, i, diag, off
        else:
            if not (diag >= off):
                return False, i, diag, off
    return True, None, None, None


def visualizar_jacobiano_heatmap(jacobiana, guardar=True, nombre_archivo="jacobiano_heatmap.png"):
    """Visualiza la matriz Jacobiana como mapa de calor."""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    vmax = max(abs(jacobiana.min()), abs(jacobiana.max()))
    im = ax.imshow(jacobiana, cmap='RdBu_r', aspect='equal', vmin=-vmax, vmax=vmax)
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Valor', rotation=270, labelpad=20, fontsize=12)
    
    ax.set_xlabel('Índice de Columna', fontsize=12, fontweight='bold')
    ax.set_ylabel('Índice de Fila', fontsize=12, fontweight='bold')
    ax.set_title('Matriz Jacobiana', fontsize=16, fontweight='bold', pad=15)
    ax.set_xticks(np.arange(0, jacobiana.shape[1], 50))
    ax.set_yticks(np.arange(0, jacobiana.shape[0], 50))
    
    plt.tight_layout()
    if guardar:
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.show()
    
    no_cero = np.count_nonzero(jacobiana)
    print(f"\n  Jacobiano: {jacobiana.shape[0]}×{jacobiana.shape[1]}")
    print(f"  Rango: [{jacobiana.min():.4f}, {jacobiana.max():.4f}]")
    print(f"  Dispersión: {100 - (no_cero / jacobiana.size * 100):.1f}%")


def visualizar_malla_inicial(malla, guardar=True, nombre_archivo="seleccion_valores_iniciales.png"):
    """Visualiza la malla de valores iniciales."""
    fig, ax = plt.subplots(figsize=(14, 4))
    
    im = ax.imshow(malla, cmap='viridis', origin='upper', aspect='auto', vmin=0, vmax=1)
    
    for i in range(malla.shape[0]):
        for j in range(malla.shape[1]):
            valor = malla[i, j]
            texto = "0" if valor == 0 else ("1" if valor >= 1 else f"{valor:.2f}"[1:])
            color = 'white' if valor > 0.5 else 'black'
            ax.text(j, i, texto, ha='center', va='center', color=color, fontsize=5)
    
    ax.set_xlabel('Columna', fontsize=12, fontweight='bold')
    ax.set_ylabel('Fila', fontsize=12, fontweight='bold')
    ax.set_title('Valores Iniciales para Newton-Raphson', fontsize=14, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Velocidad', rotation=270, labelpad=20)
    
    plt.tight_layout()
    if guardar:
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE INTERPOLACIÓN Y SUAVIZADO
# ═══════════════════════════════════════════════════════════════════════════════

def construir_interpolador_superficie(matriz):
    """Construye un spline cúbico bidimensional a partir de una matriz."""
    filas, columnas = matriz.shape
    y = np.arange(filas)
    x = np.arange(columnas)
    return RectBivariateSpline(y, x, matriz, kx=3, ky=3, s=0)


def generar_matriz_suavizada(interpolador, filas, columnas, factor=3):
    """Evalúa el interpolador sobre una malla refinada."""
    y_nuevo = np.linspace(0, filas - 1, (filas - 1) * factor + 1)
    x_nuevo = np.linspace(0, columnas - 1, (columnas - 1) * factor + 1)
    matriz_suave = interpolador(y_nuevo, x_nuevo)
    return matriz_suave, x_nuevo, y_nuevo


def mostrar_mapa_suavizado(matriz, titulo="Malla Suavizada", guardar=True, 
                           nombre_archivo="malla_suavizada.png"):
    """Renderiza el mapa de calor de la matriz suavizada."""
    plt.figure(figsize=(10, 6))
    im = plt.imshow(matriz, cmap='viridis', origin='upper')
    cbar = plt.colorbar(im, shrink=0.8, aspect=20)
    cbar.set_label('Velocidad', rotation=270, labelpad=20)
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('X interpolado')
    plt.ylabel('Y interpolado')
    plt.tight_layout()
    if guardar:
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.show()


def visualizar_superficie_3d(interpolador, filas, columnas, factor=10,
                              guardar=True, nombre_archivo="spline_superficie_3d.png"):
    """Visualiza la función de interpolación como superficie 3D."""
    y_fino = np.linspace(0, filas - 1, (filas - 1) * factor + 1)
    x_fino = np.linspace(0, columnas - 1, (columnas - 1) * factor + 1)
    X, Y = np.meshgrid(x_fino, y_fino)
    Z = interpolador(y_fino, x_fino)
    
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.9)
    
    ax.set_xlabel('X (Columna)', fontsize=11, labelpad=10)
    ax.set_ylabel('Y (Fila)', fontsize=11, labelpad=10)
    ax.set_zlabel('Velocidad u(x,y)', fontsize=11, labelpad=10)
    ax.set_title('Superficie de Interpolación - Spline Cúbico', fontsize=14, fontweight='bold')
    
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20, pad=0.1)
    cbar.set_label('Velocidad', rotation=270, labelpad=20)
    
    ax.view_init(elev=25, azim=-60)
    ax.invert_yaxis()
    
    plt.tight_layout()
    if guardar:
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.show()
    
    return X, Y, Z


def visualizar_cortes_spline(interpolador, filas, columnas, factor=10,
                              guardar=True, nombre_archivo="spline_cortes.png"):
    """Visualiza cortes de la función de interpolación spline."""
    y_fino = np.linspace(0, filas - 1, (filas - 1) * factor + 1)
    x_fino = np.linspace(0, columnas - 1, (columnas - 1) * factor + 1)
    Z = interpolador(y_fino, x_fino)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Perfiles horizontales
    ax1 = axes[0, 0]
    filas_corte = [0, len(y_fino)//4, len(y_fino)//2, 3*len(y_fino)//4, len(y_fino)-1]
    colores = plt.cm.plasma(np.linspace(0, 1, len(filas_corte)))
    for idx, fila in enumerate(filas_corte):
        ax1.plot(x_fino, Z[fila, :], color=colores[idx], linewidth=2, 
                 label=f'y = {y_fino[fila]:.1f}')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Velocidad')
    ax1.set_title('Perfiles horizontales', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Perfiles verticales
    ax2 = axes[0, 1]
    cols_corte = [0, len(x_fino)//4, len(x_fino)//2, 3*len(x_fino)//4, len(x_fino)-1]
    colores = plt.cm.viridis(np.linspace(0, 1, len(cols_corte)))
    for idx, col in enumerate(cols_corte):
        ax2.plot(y_fino, Z[:, col], color=colores[idx], linewidth=2,
                 label=f'x = {x_fino[col]:.1f}')
    ax2.set_xlabel('Y')
    ax2.set_ylabel('Velocidad')
    ax2.set_title('Perfiles verticales', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Contornos
    ax3 = axes[1, 0]
    X, Y = np.meshgrid(x_fino, y_fino)
    contour = ax3.contourf(X, Y, Z, levels=20, cmap='viridis')
    ax3.contour(X, Y, Z, levels=10, colors='white', linewidths=0.5, alpha=0.5)
    plt.colorbar(contour, ax=ax3)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_title('Contornos', fontweight='bold')
    ax3.invert_yaxis()
    
    # Mapa con isolíneas
    ax4 = axes[1, 1]
    im = ax4.imshow(Z, cmap='viridis', origin='upper', aspect='auto',
                    extent=[0, columnas-1, filas-1, 0])
    ax4.contour(X, Y, Z, levels=10, colors='white', linewidths=0.5, alpha=0.7)
    plt.colorbar(im, ax=ax4)
    ax4.set_xlabel('X')
    ax4.set_ylabel('Y')
    ax4.set_title('Mapa con isolíneas', fontweight='bold')
    
    fig.suptitle('Análisis de la Función de Interpolación', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if guardar:
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     SIMULACIÓN DE FLUJO LAMINAR 2D - NEWTON-RAPHSON + CG        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Definición de bloques (obstáculos)
    bloqueSuperior = Bloque(296, 400, 32, 40)
    bloqueInferior = Bloque(176, 232, 1, 16)
    
    # Crear malla con valores iniciales
    print("\n► Generando malla inicial...")
    malla = Malla(400, 40, H_DISCRETIZACION, 1, bloqueSuperior, bloqueInferior, 10, 5)
    
    # Visualizar valores iniciales
    print("► Visualizando valores iniciales...")
    visualizar_malla_inicial(malla.retornar_malla())
    
    # Crear vector para Newton-Raphson
    vector = Vector(malla.retornar_malla())
    
    # Parámetros del método
    max_iter = 200
    tol_residuo = 1e-10
    tol_epsilon = 1e-8
    
    print("\n┌─ Parámetros de Convergencia ─────────────────────────────────────┐")
    print(f"│ Tolerancia residuo:     {tol_residuo:.0e}")
    print(f"│ Tolerancia incremento:  {tol_epsilon:.0e}")
    print(f"│ Iteraciones máximas:    {max_iter}")
    print("└───────────────────────────────────────────────────────────────────┘")
    
    vec_anterior = vector.vec.copy()
    jacobiano_mostrado = False
    
    print("\n► Iniciando iteraciones de Newton-Raphson...\n")
    
    for i in range(max_iter):
        # Calcular residual
        vector.cal_function(malla)
        residuo = np.linalg.norm(vector.vectFunction)
        
        print(f"═══ Iteración {i+1:3d} ═══════════════════════════════════════════════")
        print(f"  ‖F(X)‖ = {residuo:.6e}")
        
        if residuo < tol_residuo:
            print(f"\n  ✓ CONVERGENCIA por residuo < {tol_residuo:.0e}")
            break
        
        # Calcular Jacobiano
        vector.cal_jacobiano(malla)
        
        # Mostrar Jacobiano solo en primera iteración
        if not jacobiano_mostrado:
            print("\n► Visualizando Jacobiano...")
            visualizar_jacobiano_heatmap(vector.matrixJacobiana)
            jacobiano_mostrado = True
        
        cond_J = np.linalg.cond(vector.matrixJacobiana, 2)
        print(f"  κ(J) = {cond_J:.2f}")
        
        # Verificar dominancia diagonal
        dom, _, _, _ = es_diagonalmente_dominante(vector.matrixJacobiana, strict=True)
        print(f"  Diag. dominante: {'Sí' if dom else 'No'}")
        
        # Transformar a sistema SPD: J^T J · H = -J^T F
        JT = vector.matrixJacobiana.T
        A = JT @ vector.matrixJacobiana
        b = -JT @ vector.vectFunction
        
        # Verificar SPD
        eigvals = np.linalg.eigvalsh(A)
        es_spd = np.all(eigvals > 0)
        print(f"  J^T J es SPD: {'Sí ✓' if es_spd else 'No ✗'}")
        
        cond_A = np.linalg.cond(A, 2)
        print(f"  κ(J^T J) = {cond_A:.2f}")
        
        # Resolver con Gradiente Conjugado
        vector.actualizar_newton(A, b, verbose=True)
        
        # Verificar convergencia por incremento
        epsilon = np.linalg.norm(vector.vec - vec_anterior)
        print(f"  ΔX = {epsilon:.6e}")
        
        if epsilon < tol_epsilon:
            print(f"\n  ✓ CONVERGENCIA por ΔX < {tol_epsilon:.0e}")
            break
        
        vec_anterior = vector.vec.copy()
    else:
        print(f"\n  ⚠ No convergió en {max_iter} iteraciones")
    
    # Resultados finales
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      RESULTADOS FINALES                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    matriz_final = vector.vec.reshape(vector.filas, vector.columnas)
    print(f"\n  Dimensiones: {matriz_final.shape}")
    print(f"  Velocidad máxima: {np.max(matriz_final):.6f}")
    print(f"  Velocidad mínima: {np.min(matriz_final):.6f}")
    
    # Mostrar resultados
    print("\n► Visualizando campo de velocidades...")
    vector.mostrar_mapa_calor(detallado=True)
    vector.mostrar_mapa_calor(detallado=False)
    
    # Interpolación y suavizado
    print("\n► Generando visualizaciones de interpolación spline...")
    interpolador = construir_interpolador_superficie(matriz_final)
    
    visualizar_superficie_3d(interpolador, matriz_final.shape[0], matriz_final.shape[1])
    visualizar_cortes_spline(interpolador, matriz_final.shape[0], matriz_final.shape[1])
    
    matriz_suave, _, _ = generar_matriz_suavizada(
        interpolador, matriz_final.shape[0], matriz_final.shape[1], factor=10
    )
    mostrar_mapa_suavizado(matriz_suave, titulo="Campo de Velocidades Suavizado")
    
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                    SIMULACIÓN COMPLETADA                         ║")
    print("╚══════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
