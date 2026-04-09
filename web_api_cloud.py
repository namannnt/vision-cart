"""
VisionCart Cloud Backend - Hugging Face Spaces Compatible
Camera removed - accepts frames from frontend
"""
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
import threading
import time
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

# Import the existing ML logic
from customer_checkout_backend import CheckoutCounter

app = FastAPI()

# Global event loop reference
_main_loop: asyncio.AbstractEventLoop = None

@app.on_event("startup")
async def on_startup():
    global _main_loop
    _main_loop = asyncio.get_event_loop()
    print("✅ Cloud backend started - Camera-less mode")

# CORS - Allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
cart_state = {"items": [], "total": 0.0, "status": "Awaiting cargo..."}
cart_state_lock = threading.Lock()

# Initialize ML counter
print("🤖 Initializing AI Checkout Counter...")
counter = CheckoutCounter()
print(f"✅ Loaded {len(counter.product_ids)} products")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:  # Copy to avoid modification during iteration
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"WS error: {e}")
                self.active_connections.remove(connection)

manager = ConnectionManager()

_detection_lock = threading.Lock()

def run_detection_async(frame):
    """Run AI detection in a separate thread"""
    global cart_state
    
    if not _detection_lock.acquire(blocking=False):
        return
    
    try:
        detected, product, confidence, message = counter.detect_and_add_to_cart(frame)

        with cart_state_lock:
            cart_state["items"] = counter.cart.copy()
            cart_state["total"] = counter.get_cart_total()
            
            if detected:
                cart_state["status"] = f"✅ Added {product}!"
            elif product:
                cart_state["status"] = message
            else:
                cart_state["status"] = message if message else "Scanning..."

        # Broadcast to all connected clients
        try:
            if _main_loop is not None and _main_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(cart_state), _main_loop)
        except Exception as be:
            print(f"[Broadcast] Error: {be}")
            
    except Exception as e:
        print(f"⚠️ Detection error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        _detection_lock.release()


# ============================================
# 🔥 NEW: Frame Upload Endpoint
# ============================================
@app.post("/api/detect_frame")
async def detect_frame(file: UploadFile = File(...)):
    """
    Accept frame from frontend camera
    Process with YOLO + CLIP/DINO
    Return detection result
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Convert to OpenCV format
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"error": "Invalid image format"}
        
        # Run detection in background thread
        threading.Thread(
            target=run_detection_async,
            args=(frame,),
            daemon=True
        ).start()
        
        return {"status": "processing"}
        
    except Exception as e:
        print(f"❌ Frame processing error: {e}")
        return {"error": str(e)}


@app.get("/health")
def health_check():
    """Health check for Hugging Face Spaces"""
    return {
        "status": "healthy",
        "products_loaded": len(counter.product_ids),
        "cart_size": len(counter.cart)
    }


@app.get("/api/status")
def get_status():
    """Get current system status"""
    with cart_state_lock:
        return {
            "cart": cart_state,
            "products_loaded": len(counter.product_ids),
            "vote_buffer": counter.vote_buffer,
            "last_detected": counter.last_detected_product,
            "cooldown_remaining": max(0, counter.cooldown_seconds - (time.time() - counter.last_detection_time))
        }


@app.websocket("/ws/cart")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        with cart_state_lock:
            await websocket.send_json(cart_state)
            
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "clear":
                counter.clear_cart()
                with cart_state_lock:
                    cart_state["items"] = []
                    cart_state["total"] = 0.0
                    cart_state["status"] = "Cart cleared"
                await manager.broadcast(cart_state)
                
            elif message.get("action") == "remove_last":
                removed = counter.remove_last_item()
                with cart_state_lock:
                    cart_state["items"] = counter.cart.copy()
                    cart_state["total"] = counter.get_cart_total()
                    cart_state["status"] = f"Removed {removed['name'] if removed else 'none'}"
                await manager.broadcast(cart_state)
                
            elif message.get("action") == "checkout":
                success, result = counter.checkout()
                with cart_state_lock:
                    if success:
                        cart_state["items"] = []
                        cart_state["total"] = 0.0
                        cart_state["status"] = "Checkout Complete!"
                        cart_state["stock_updated"] = True
                    else:
                        cart_state["status"] = f"Checkout failed: {result}"
                        cart_state["stock_updated"] = False
                await manager.broadcast(cart_state)
                with cart_state_lock:
                    cart_state["stock_updated"] = False
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================
# Product Registration (with frame upload)
# ============================================
from pydantic import BaseModel
from utils.validation import validate_detection
from utils.register_product import register_product, is_duplicate, get_all_embeddings
from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask, fallback_crop_no_yolo
from utils.load_database import load_database
from utils.color_layer import extract_color_histogram
from utils.shape_layer import extract_shape_features
from utils.coin_size_estimator import detect_coin, pixels_per_mm, estimate_product_real_diameter_mm

partial_registrations = {}

class RegisterRequest(BaseModel):
    product_id: str
    price: float
    stock: int
    is_cylindrical: bool = False
    capture_step: int = 1
    parent_id: str = ""
    require_coin: bool = False

@app.post("/api/register_frame")
async def register_with_frame(
    file: UploadFile = File(...),
    product_id: str = "",
    price: float = 0.0,
    stock: int = 0,
    is_cylindrical: bool = False,
    capture_step: int = 1,
    parent_id: str = "",
    require_coin: bool = False
):
    """
    Register product from uploaded frame
    """
    global partial_registrations
    
    try:
        # Read and decode image
        image_bytes = await file.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"error": "Invalid image"}
        
        # Coin detection check
        coin = detect_coin(frame)
        if require_coin and coin is None:
            return {"error": "⚠️ Coin not detected. Place ₹1 coin in corner."}
            
        # YOLO detection
        results = counter.yolo_model(frame, conf=0.10, verbose=False)

        SKIP_CLASSES = {0}  # Skip person
        best_idx = None
        best_area = -1
        
        if results[0].masks is not None:
            boxes = results[0].boxes
            for i in range(len(results[0].masks)):
                cls = int(boxes.cls[i]) if boxes is not None else -1
                if cls in SKIP_CLASSES:
                    continue
                m = results[0].masks.data[i].cpu().numpy()
                area = m.sum()
                if area > best_area:
                    best_area = area
                    best_idx = i

        if best_idx is not None:
            mask = results[0].masks.data[best_idx].cpu().numpy()
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            clean_img, binary_mask = apply_segmentation_mask(frame, mask)
            final_crop = crop_to_mask(clean_img, mask)
        else:
            final_crop, binary_mask = fallback_crop_no_yolo(frame)
            if final_crop is None or final_crop.size == 0:
                return {"error": "⚠️ No product detected"}

        if final_crop is None or final_crop.size == 0:
            return {"error": "Invalid segmentation"}
            
        if best_idx is not None:
            is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
            if not is_valid:
                return {"error": f"Invalid detection: {reason}"}
            
        # Generate embeddings
        pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
        clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, counter.device)
        dino_tensor = counter.dino_transform(pil_crop).unsqueeze(0)
        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, counter.device)
        current_embedding = fuse_embeddings(clip_emb, dino_emb, alpha=0.6)
        
        # Handle cylindrical products (3 angles)
        if is_cylindrical:
            if capture_step == 1 or product_id not in partial_registrations:
                partial_registrations[product_id] = {"embeddings": [], "image": final_crop}

            partial_registrations[product_id]["embeddings"].append(current_embedding)

            if capture_step < 3:
                return {
                    "status": "partial",
                    "message": f"Captured side {capture_step}/3. Rotate object.",
                    "step": capture_step
                }
            else:
                embeddings = partial_registrations[product_id]["embeddings"]
                avg_emb = np.mean(embeddings, axis=0)
                final_embedding = avg_emb / np.linalg.norm(avg_emb)
                final_crop_for_save = partial_registrations[product_id]["image"]
                del partial_registrations[product_id]
        else:
            final_embedding = current_embedding
            final_crop_for_save = final_crop

        # Extract features
        color_hist = extract_color_histogram(final_crop_for_save)
        shape_feat = extract_shape_features(final_crop_for_save, binary_mask)

        # Size measurement
        real_diameter_mm = 0.0
        if coin is not None:
            ppm = pixels_per_mm(coin[2])
            real_diameter_mm = estimate_product_real_diameter_mm(binary_mask, ppm)
            print(f"📏 Product size: {real_diameter_mm:.1f}mm")

        parent_id_clean = parent_id.strip() if parent_id else None

        # Duplicate check
        existing_ids, existing_embeddings = get_all_embeddings()
        if len(existing_embeddings) > 0 and is_duplicate(
            final_embedding.reshape(1, -1), existing_embeddings,
            threshold=0.95, existing_ids=existing_ids, parent_id=parent_id_clean
        ):
            return {"error": "DUPLICATE: Product already exists"}

        # Register
        success, message = register_product(
            product_id, price, stock, final_embedding,
            color_hist=color_hist, shape_feat=shape_feat,
            real_diameter_mm=real_diameter_mm, parent_id=parent_id_clean
        )

        if success:
            image_path = f"data/registered_products/{product_id}.jpg"
            cv2.imwrite(image_path, final_crop_for_save)
            
            # Reload database
            counter.product_ids, counter.db_embeddings, counter.prices, counter.stocks, \
                counter.color_hists, counter.shape_feats, counter.real_diameters, counter.parent_ids = load_database()
            counter.booster.reset()
            
            size_info = f" | Size: {real_diameter_mm:.1f}mm" if real_diameter_mm > 0 else ""
            return {"status": "success", "message": message + size_info}
        else:
            return {"error": message}
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Error: {str(e)}"}


@app.post("/api/reload_database")
def reload_database_endpoint():
    """Reload database after inventory changes"""
    counter.product_ids, counter.db_embeddings, counter.prices, counter.stocks, \
        counter.color_hists, counter.shape_feats, counter.real_diameters, counter.parent_ids = load_database()
    counter.booster.reset()
    return {"status": "ok", "products": len(counter.product_ids)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)  # Hugging Face Spaces default port
