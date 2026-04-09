import sqlite3

conn = sqlite3.connect('database/visioncart.db')
cursor = conn.cursor()
cursor.execute('SELECT product_id, price, stock, parent_id, real_diameter_mm FROM products')
rows = cursor.fetchall()

print('\n' + '='*80)
print('CURRENT PRODUCTS IN DATABASE')
print('='*80)
for r in rows:
    parent = r[3] if r[3] else "None"
    size = r[4] if r[4] else 0.0
    print(f'{r[0]:25s} | ₹{r[1]:6.2f} | Stock: {r[2]:3d} | Parent: {parent:15s} | Size: {size:5.1f}mm')
print('='*80 + '\n')

conn.close()
