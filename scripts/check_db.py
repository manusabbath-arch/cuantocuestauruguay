import sqlite3

conn = sqlite3.connect('/home/mamba/cuantocuestauruguay/cuantocuestauruguay/backend/preciosregulados.db')

print("=" * 60)
print("  CONTENIDO DE LA BASE DE DATOS")
print("=" * 60)
print()

print("PRODUCTOS:")
for row in conn.execute('SELECT nombre, categoria, unidad FROM productos ORDER BY categoria, nombre'):
    print(f"  {row[1]:20} | {row[0]:35} | {row[2]}")

print()
print("PRECIOS:")
for row in conn.execute('''
    SELECT p.nombre, pr.valor, pr.fecha, pr.fuente 
    FROM precios pr 
    JOIN productos p ON pr.producto_id = p.id 
    ORDER BY p.categoria, p.nombre
'''):
    print(f"  {row[0]:35} | ${row[1]:6.2f} | {row[2]} | {row[3]}")

conn.close()
