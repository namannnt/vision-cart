import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';

// The database path is relative to where the Next.js process starts,
// or we can strictly point it to the VisionCart database parent folder.
// Since Next.js is inside vision-cart-web, we go up one directory.
const dbPath = path.resolve(process.cwd(), '../database/visioncart.db');

let db: Database | null = null;

export async function openDb() {
  if (!db) {
    db = await open({
      filename: dbPath,
      driver: sqlite3.Database,
    });
  }
  return db;
}

export async function getProducts() {
  const db = await openDb();
  // We don't select the embedding BLOB for simple frontend display
  return db.all('SELECT id, product_id, price, stock, image_path, created_at FROM products');
}

export async function updateProductStock(id: number, newStock: number) {
  const db = await openDb();
  return db.run('UPDATE products SET stock = ? WHERE id = ?', [newStock, id]);
}
