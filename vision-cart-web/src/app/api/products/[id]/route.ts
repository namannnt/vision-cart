import { NextResponse } from 'next/server';
import { openDb } from '@/lib/db';

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
    
    // Check if product exists first
    const product = await db.get('SELECT * FROM products WHERE id = ?', [id]);
    if (!product) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 });
    }

    // Delete from database
    await db.run('DELETE FROM products WHERE id = ?', [id]);
    
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
    
    // Check if product exists
    const product = await db.get('SELECT * FROM products WHERE id = ?', [id]);
    if (!product) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 });
    }

    // Update in database
    await db.run(
      'UPDATE products SET price = ?, stock = ? WHERE id = ?',
      [parseFloat(price), parseInt(stock, 10), id]
    );
    
    return NextResponse.json({ success: true, message: 'Product updated successfully' });
  } catch (error) {
    console.error('Error updating product:', error);
    return NextResponse.json({ error: 'Failed to update product' }, { status: 500 });
  }
}
