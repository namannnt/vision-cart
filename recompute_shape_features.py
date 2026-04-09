"""
Run this once to recompute shape features for all registered products
that currently have NULL shape_feat in the database.

Usage: python recompute_shape_features.py
"""
import sqlite3
import cv2
import numpy as np
import os
from utils.shape_layer import extract_shape_features
from utils.color_layer import extract_color_histogram

DB_PATH = "database/visioncart.db"
IMG_DIR = "data/registered_products"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, product_id, shape_feat, color_hist FROM products")
rows = cursor.fetchall()

updated = 0
skipped = 0

for row_id, product_id, shape_feat, color_hist in rows:
    needs_shape = shape_feat is None
    needs_color = color_hist is None

    if not needs_shape and not needs_color:
        skipped += 1
        continue

    # Find image
    img_path = None
    for ext in [".jpg", ".jpeg", ".png"]:
        p = os.path.join(IMG_DIR, f"{product_id}{ext}")
        if os.path.exists(p):
            img_path = p
            break

    if img_path is None:
        print(f"⚠️  No image found for '{product_id}' — skipping")
        skipped += 1
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"⚠️  Could not read image for '{product_id}' — skipping")
        skipped += 1
        continue

    shape_bytes = shape_feat
    color_bytes = color_hist

    if needs_shape:
        sf = extract_shape_features(img)
        shape_bytes = sf.tobytes()

    if needs_color:
        ch = extract_color_histogram(img)
        color_bytes = ch.tobytes()

    cursor.execute(
        "UPDATE products SET shape_feat = ?, color_hist = ? WHERE id = ?",
        (shape_bytes, color_bytes, row_id)
    )
    print(f"✅ Updated '{product_id}'")
    updated += 1

conn.commit()
conn.close()

print(f"\nDone. Updated: {updated}, Skipped: {skipped}")
print("Now restart web_api.py for changes to take effect.")
