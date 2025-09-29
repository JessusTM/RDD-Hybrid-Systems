# RDD-Hybrid-Systems

Prototipo que permite transformar modelos i* 2.0 desde el nivel de intenciones y objetivos hacia un nivel de variabilidad, representado en UVL (Universal Variability Language), donde las metas se traducen en configuraciones concretas del sistema mediante árboles de características.

## Requisitos

- Python 3.12 o superior  
- `pip` instalado  

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/usuario/RDD-Hybrid-Systems.git
   cd RDD-Hybrid-Systems
   ```

2. Crear entorno virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   
   ```

3. Instalar dependencias:

   ```bash
   pip install lxml unidecode 
   ```

## Archivos 

* `iStar-UVL.py`  → Script principal.
* `config/`       → Carpeta con diccionarios de mapeo (`algorithms.txt`, `nfrs.txt`, `backend.txt`, `integration.txt`).
* `Chemistry.xml` → Ejemplo de entrada (XML desde draw.io).
* `modelo.uvl`    → Ejemplo de salida (UVL generado).

## Uso

```bash
python3 iStar-UVL.py <archivo_entrada.xml> <archivo_salida.uvl>
```

##### Ejemplo

```bash
python3 iStar-UVL.py examples/Chemistry.xml modelo.uvl
```
