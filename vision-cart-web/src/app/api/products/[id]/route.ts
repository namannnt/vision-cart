import { NextResponse } from 'next/server';
import { openDb } from '@/lib/db';

// Notify Python backend to reload its in-memory DB
async function notifyBackendReload() {
  try {
    await fetch('http://127.0.0.1:8000/api/reload_database', { method: 'POST' });
  } catch {
    // backend might not be running, non-blocking
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    if (!id) {
      return NextResponse.json({ error: 'Product ID is required' }, { status: 400 });
    }

    const db = await openDb();
    
    const product = await db.get('SELECT * FROM products WHERE id = ?', [id]);
    if (!product) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 });
    }

    await db.run('DELETE FROM products WHERE id = ?', [id]);
    
    // Tell Python backend to reload — deleted product won't be detected anymore
    await notifyBackendReload();
    
    return NextResponse.json({ success: true, message: 'Product deleted successfully' });
  } catch (error) {
    console.error('Error deleting product:', error);
    return NextResponse.json({ error: 'Failed to delete product' }, { status: 500 });
  }
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    if (!id) {
      return NextResponse.json({ error: 'Product ID is required' }, { status: 400 });
    }

    const body = await request.json();
    const { price, stock } = body;

    if (price === undefined || stock === undefined) {
      return NextResponse.json({ error: 'Price and stock are required' }, { status: 400 });
    }

    const db = await openDb();
    
    const product = await db.get('SELECT * FROM products WHERE id = ?', [id]);
    if (!product) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 });
    }

    await db.run(
      'UPDATE products SET price = ?, stock = ? WHERE id = ?',
      [parseFloat(price), parseInt(stock, 10), id]
    );

    // Tell Python backend to reload updated price/stock
    await notifyBackendReload();
    
    return NextResponse.json({ success: true, message: 'Product updated successfully' });
  } catch (error) {
    console.error('Error updating product:', error);
    return NextResponse.json({ error: 'Failed to update product' }, { status: 500 });
  }
}
