import { NextResponse } from 'next/server';
import { openDb } from '@/lib/db';

export async function GET() {
  try {
    const db = await openDb();
    const sales = await db.all(`
      SELECT id, product_id, quantity, price_per_unit, total_amount, sold_at
      FROM sales
      ORDER BY sold_at DESC
      LIMIT 100
    `);
    return NextResponse.json(sales);
  } catch (error) {
    console.error('Error fetching sales:', error);
    return NextResponse.json({ error: 'Failed to fetch sales' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { items } = body; // [{ name, price, quantity }]

    if (!items || !Array.isArray(items) || items.length === 0) {
      return NextResponse.json({ error: 'No items provided' }, { status: 400 });
    }

    const db = await openDb();
    for (const item of items) {
      const qty = item.quantity ?? 1;
      await db.run(
        `INSERT INTO sales (product_id, quantity, price_per_unit, total_amount) VALUES (?, ?, ?, ?)`,
        [item.name, qty, item.price, item.price * qty]
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error saving sale:', error);
    return NextResponse.json({ error: 'Failed to save sale' }, { status: 500 });
  }
}
