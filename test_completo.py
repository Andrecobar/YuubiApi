from novelas_api import NovelasAPI
import time

print("=" * 60)
print("🧪 PRUEBA COMPLETA DE LA API DE NOVELAS")
print("=" * 60)

# Crear instancia
api = NovelasAPI("http://localhost:5000")

# Test 1: Agregar serie
print("\n📺 Test 1: Agregando serie 'Como Dice el Dicho'...")
nueva_serie = api.agregar_serie(
    titulo="Como Dice el Dicho",
    descripcion="Serie que presenta historias con moralejas",
    anio=2011,
    genero="Drama/Comedia"
)
if nueva_serie:
    print(f"✅ Serie creada con ID: {nueva_serie['id']}")
    serie_id = nueva_serie['id']
else:
    print("❌ Error al crear serie")
    exit(1)

# Test 2: Agregar episodios
print(f"\n📹 Test 2: Agregando 3 episodios a la serie {serie_id}...")
for i in range(1, 4):
    episodio = api.agregar_episodio(
        serie_id=serie_id,
        numero_episodio=i,
        titulo=f"Capítulo {i}",
        url_video=f"https://ejemplo.com/como-dice-ep{i}.mp4",
        duracion=30
    )
    if episodio:
        print(f"  ✅ Episodio {i} agregado")
    else:
        print(f"  ❌ Error en episodio {i}")

# Test 3: Obtener todas las series
print("\n📋 Test 3: Obteniendo todas las series...")
series = api.obtener_series()
if series:
    print(f"✅ Encontradas {len(series)} series:")
    for serie in series:
        print(f"  - {serie['titulo']} ({serie['anio']})")
else:
    print("❌ No se encontraron series")

# Test 4: Obtener episodios
print(f"\n🎬 Test 4: Obteniendo episodios de la serie {serie_id}...")
episodios = api.obtener_episodios(serie_id)
if episodios:
    print(f"✅ Encontrados {len(episodios)} episodios:")
    for ep in episodios:
        print(f"  {ep['numero_episodio']}. {ep['titulo']}")
else:
    print("❌ No se encontraron episodios")

# Test 5: Buscar
print("\n🔍 Test 5: Buscando 'Dicho'...")
resultados = api.buscar("Dicho")
if resultados and resultados['total'] > 0:
    print(f"✅ Encontrados {resultados['total']} resultados")
else:
    print("❌ No se encontraron resultados")

print("\n" + "=" * 60)
print("✅ ¡TODAS LAS PRUEBAS COMPLETADAS!")
print("=" * 60)