import numpy as np
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity


def is_duplicate(new_embedding, existing_embeddings, threshold=0.95,
                 existing_ids=None, parent_id=None):
    """
    Returns True only if an identical product (same parent group) already exists.
    Size variants under the same parent are NOT considered duplicates.
    """
    if len(existing_embeddings) == 0:
        return False

    sims = cosine_similarity(new_embedding, existing_embeddings)[0]

    for i, sim in enumerate(sims):
        if sim > threshold:
            # If both belong to same parent group → it's a size variant, not duplicate
            if parent_id is not None and existing_ids is not None:
                other_id = existing_ids[i]
                other_parent = get_parent_id(other_id)
                if other_parent == parent_id or other_parent is None:
                    # Same parent → allow (size variant)
                    continue
            return True

    return False


def get_parent_id(product_id, db_path="database/visioncart.db"):
    """Get parent_id for a given product_id."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT parent_id FROM products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def get_siblings(parent_id, db_path="database/visioncart.db"):
    """Get all products with the same parent_id."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_id, real_diameter_mm FROM products WHERE parent_id = ?",
        (parent_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def register_product(product_id, price, stock, embedding,
                     color_hist=None, shape_feat=None, real_diameter_mm=0.0,
                     parent_id=None, db_path="database/visioncart.db"):
    """
    Register new product. parent_id groups size variants together.
    e.g. parent_id="vaseline" for both "vaseline 20gm" and "vaseline 50gm"
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        color_bytes = color_hist.tobytes() if color_hist is not None else None
        shape_bytes = shape_feat.tobytes() if shape_feat is not None else None

        cursor.execute("""
            INSERT INTO products
                (product_id, parent_id, price, stock, embedding, color_hist, shape_feat, real_diameter_mm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, parent_id, price, stock,
              embedding.tobytes(), color_bytes, shape_bytes, float(real_diameter_mm)))

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
    cursor.execute("SELECT product_id, embedding FROM products")
    results = cursor.fetchall()
    conn.close()

    ids, embeddings = [], []
    for pid, emb_blob in results:
        ids.append(pid)
        embeddings.append(np.frombuffer(emb_blob, dtype=np.float32))

    return (ids, np.array(embeddings)) if embeddings else ([], np.array([]))
