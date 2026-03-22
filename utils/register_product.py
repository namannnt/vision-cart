import numpy as np
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity


def is_duplicate(new_embedding, existing_embeddings, threshold=0.95):
    if len(existing_embeddings) == 0:
        return False
    sims = cosine_similarity(new_embedding, existing_embeddings)
    return sims.max() > threshold


def register_product(product_id, price, stock, embedding,
                     color_hist=None, shape_feat=None,
                     db_path="database/visioncart.db"):
    """
    Register new product with visual embedding + optional color/shape features.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        color_bytes = color_hist.tobytes() if color_hist is not None else None
        shape_bytes = shape_feat.tobytes() if shape_feat is not None else None

        cursor.execute("""
            INSERT INTO products (product_id, price, stock, embedding, color_hist, shape_feat)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, price, stock,
              embedding.tobytes(), color_bytes, shape_bytes))

        conn.commit()
        conn.close()
        return True, f"Product '{product_id}' registered successfully!"

    except sqlite3.IntegrityError:
        conn.close()
        return False, f"Product '{product_id}' already exists!"

    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"


def get_all_embeddings(db_path="database/visioncart.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT embedding FROM products")
    results = cursor.fetchall()
    conn.close()

    embeddings = []
    for row in results:
        emb = np.frombuffer(row[0], dtype=np.float32)
        embeddings.append(emb)

    return np.array(embeddings) if embeddings else np.array([])
