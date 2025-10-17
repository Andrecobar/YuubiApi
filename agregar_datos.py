import sqlite3

def crear_datos_ejemplo():
    conn = sqlite3.connect('novelas.db')
    cursor = conn.cursor()
    
    series_datos = [
        ('La Rosa de Guadalupe', 'Serie dramática mexicana que presenta historias de fe y milagros', 2008, 'Drama', 'https://image.tmdb.org/t/p/w500/7H8tEDqCPdJEMFcXfXfPKKOpEfJ.jpg', 7.5, 'Michelle Vieth, Angélica Vale'),
        ('Teresa', 'Historia de una mujer ambiciosa que busca riqueza y poder', 2010, 'Drama/Romance', 'https://image.tmdb.org/t/p/w500/cM0p2V6JnVN0LJP4V6VaFeDCQu1.jpg', 8.2, 'Angelique Boyer, David Zepeda'),
        ('Yo Soy Betty, La Fea', 'Una secretaria inteligente pero fea conquista el mundo', 1999, 'Comedia/Romance', 'https://image.tmdb.org/t/p/w500/hkRCj8OMY2weSZSFSCz4Om8Yyvk.jpg', 8.7, 'Lina Rodríguez, Jorge Enrique Abello'),
        ('Pasión de Gavilanes', 'Tres hermanos buscan venganza por la muerte de su padre', 2003, 'Drama/Romance', 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7hasnYV6i.jpg', 8.4, 'Michel Brown, Danna García'),
        ('Boys Over Flowers', 'Una chica humilde ingresa a una escuela de ricos', 2009, 'Romance/Comedia', 'https://image.tmdb.org/t/p/w500/lOv0ZlZPVXvJ5eVrv9s9k3l8aKj.jpg', 8.5, 'Ku Hye-sun, Lee Min-ho'),
        ('Café con Aroma de Mujer', 'Historia de amor entre una recolectora de café y un millonario', 1994, 'Romance', 'https://image.tmdb.org/t/p/w500/zSJLTqBcQm5RjqNx1fIEFfhMd8g.jpg', 8.6, 'Gaite Jansen, William Levy'),
        ('Descendientes del Sol', 'Un soldado y una doctora se aman en medio de un conflicto', 2016, 'Romance/Acción', 'https://image.tmdb.org/t/p/w500/5A2bMlw9cyS5bBmsvzuIYVsFSxW.jpg', 8.9, 'Song Joong-ki, Song Hye-kyo'),
        ('Goblin', 'Un inmortal busca a la reencarnación de su novia', 2016, 'Fantasía/Romance', 'https://image.tmdb.org/t/p/w500/4bOw5s90oF7tGAJ3rHWlrJgGa8Y.jpg', 9.0, 'Gong Yoo, Kim Go-eun'),
    ]
    
    for titulo, desc, anio, genero, imagen, puntuacion, reparto in series_datos:
        cursor.execute('''
            INSERT OR IGNORE INTO series 
            (titulo, descripcion, anio, genero, imagen_portada, puntuacion, reparto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, desc, anio, genero, imagen, puntuacion, reparto))
        print(f"✅ {titulo}")
    
    for serie_id in range(1, 9):
        for ep_num in range(1, 6):
            cursor.execute('''
                INSERT INTO episodios 
                (serie_id, numero_episodio, titulo, duracion)
                VALUES (?, ?, ?, ?)
            ''', (serie_id, ep_num, f'Episodio {ep_num}', 45))
    
    conn.commit()
    conn.close()
    
    print("\n✅ Base de datos con 8 series")

if __name__ == '__main__':
    crear_datos_ejemplo()
