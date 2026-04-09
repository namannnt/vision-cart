import sqlite3
import numpy as np

def load_database(db_path="database/visioncart.db"):
    """
    Load all products from DB.
    Returns: (product_ids, embeddings, prices, stocks, color_hists,
              shape_feats, real_diameters, parent_ids)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT product_id, embedding, price, stock, color_hist, shape_feat,
               COALESCE(real_diameter_mm, 0.0),
               COALESCE(parent_id, '')
        FROM products
    """)
    rows = cursor.fetchall()
    conn.close()

    ids, embeddings, prices, stocks = [], [], [], []
    color_hists, shape_feats, diameters, parent_ids = [], [], [], []

    for pid, emb, price, stock, chist, sfeat, diam, parent in rows:
        ids.append(pid)
        embeddings.append(np.frombuffer(emb, dtype=np.float32))
        prices.append(price)
        stocks.append(stock)
        color_hists.append(np.frombuffer(chist, dtype=np.float32) if chist else None)
        shape_feats.append(np.frombuffer(sfeat, dtype=np.float32) if sfeat else None)
        diameters.append(float(diam) if diam else 0.0)
        parent_ids.append(parent)

    if not embeddings:
        return [], np.array([]), [], [], [], [], [], []

    return ids, np.array(embeddings), prices, stocks, \
           color_hists, shape_feats, diameters, parent_ids
