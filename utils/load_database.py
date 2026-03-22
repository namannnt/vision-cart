import sqlite3
import numpy as np

def load_database(db_path="database/visioncart.db"):
    """
    Load all products, embeddings, color histograms and shape features from DB.
    Returns: (product_ids, embeddings, prices, stocks, color_hists, shape_feats)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT product_id, embedding, price, stock, color_hist, shape_feat FROM products")
    rows = cursor.fetchall()
    conn.close()

    ids, embeddings, prices, stocks, color_hists, shape_feats = [], [], [], [], [], []

    for pid, emb, price, stock, chist, sfeat in rows:
        ids.append(pid)
        embeddings.append(np.frombuffer(emb, dtype=np.float32))
        prices.append(price)
        stocks.append(stock)

        # color_hist — may be None for old products registered before this update
        if chist is not None:
            color_hists.append(np.frombuffer(chist, dtype=np.float32))
        else:
            color_hists.append(None)

        # shape_feat — may be None for old products
        if sfeat is not None:
            shape_feats.append(np.frombuffer(sfeat, dtype=np.float32))
        else:
            shape_feats.append(None)

    if len(embeddings) == 0:
        return [], np.array([]), [], [], [], []

    return ids, np.array(embeddings), prices, stocks, color_hists, shape_feats
