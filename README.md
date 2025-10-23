# 🔍 Escáner de Puertos TCP (Python)

Un escáner de puertos TCP simple, rápido y multihilo, desarrollado en Python.  
Permite identificar puertos abiertos en un host o descubrir equipos activos en una subred mediante `ping`.

---

## 🚀 Características

- Escaneo TCP mediante conexión (`connect_ex`)
- Soporte de **escaneo de un puerto concreto** o **rango de puertos**
- Detección de hosts activos en una **subred** (`ping`)
- Multihilo con control dinámico de número de workers
- Barra de progreso opcional (presionando `ENTER` durante el escaneo)
- Exportación de resultados a `.txt` o `.json`
- Compatible con **Windows**, **Linux** y **macOS**

---

## 🛠️ Requisitos

- Python **3.8 o superior**
- No requiere librerías externas (usa solo la biblioteca estándar)

