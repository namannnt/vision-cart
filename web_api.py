import cv2
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import threading
import time

# Global event loop reference — set once FastAPI starts
_main_loop: asyncio.AbstractEventLoop = None

# Import the existing ML logic
from customer_checkout_backend import CheckoutCounter

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    global _main_loop
    _main_loop = asyncio.get_event_loop()
    print("✅ Main event loop captured")

# Allow Next.js frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to share between camera thread and API
latest_frame = None
latest_frame_lock = threading.Lock()
latest_raw_frame = None
latest_raw_frame_lock = threading.Lock()
cart_state = {"items": [], "total": 0.0, "status": "idle"}
cart_state_lock = threading.Lock()

# Initialize ML counter
print("Initializing AI Checkout Counter...")
counter = CheckoutCounter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"WS error: {e}")

manager = ConnectionManager()


def camera_thread_function():
    global latest_frame, latest_raw_frame, cart_state

    from config import CAMERA_INDEX
    print(f"  Opening camera index {CAMERA_INDEX} (from config.py)...")
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"❌ Could not open camera index {CAMERA_INDEX}")
        return

    # Warm up — read a few frames
    for _ in range(5):
        cap.read()

    ret, test_frame = cap.read()
    if ret:
        import numpy as np_t
        print(f"✅ Using camera index {CAMERA_INDEX} ({int(cap.get(3))}x{int(cap.get(4))}) brightness={np_t.mean(test_frame):.1f}")

    frame_count = 0
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            with latest_raw_frame_lock:
                latest_raw_frame = frame.copy()

            frame_count += 1

            # Queue frame for AI detection every 3 frames (faster response)
            if frame_count % 3 == 0:
                threading.Thread(
                    target=run_detection_async,
                    args=(frame.copy(),),
                    daemon=True
                ).start()

            # Encode for web stream immediately — never blocked by AI
            display_small = cv2.resize(frame, (640, 480))
            ret2, buffer = cv2.imencode('.jpg', display_small,
                                        [cv2.IMWRITE_JPEG_QUALITY, 60])
            if ret2:
                with latest_frame_lock:
                    latest_frame = buffer.tobytes()

            time.sleep(0.033)

        except Exception as e:
            print(f"⚠️ Camera thread error: {e}")
            time.sleep(0.5)


_detection_lock = threading.Lock()

def run_detection_async(frame):
    """Run AI detection in a separate thread so camera feed is never blocked."""
    global cart_state
    # Skip if a detection is already running
    if not _detection_lock.acquire(blocking=False):
        return
    try:
        detected, product, confidence, message = counter.detect_and_add_to_cart(frame)

        # Update cart state regardless of detection result (for status messages)
        with cart_state_lock:
            cart_state["items"] = counter.cart.copy()
            cart_state["total"] = counter.get_cart_total()
            
            if detected:
                cart_state["status"] = f"✅ Added {product}!"
            elif product:
                # Show progress messages (Confirming..., etc.)
                cart_state["status"] = message
            else:
                # No detection or error
                cart_state["status"] = message if message else "Scanning..."

        # Broadcast to all connected clients
        try:
            if _main_loop is not None and _main_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(cart_state), _main_loop)
        except Exception as be:
            print(f"[Broadcast] Error: {be}")
            
    except Exception as e:
        print(f"⚠️ Detection thread error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        _detection_lock.release()

# Start camera immediately in background
threading.Thread(target=camera_thread_function, daemon=True).start()


def generate_mjpeg_stream():
    global latest_frame
    # Create a simple "waiting" JPEG to send while camera warms up
    import numpy as np
    waiting_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(waiting_img, "Camera warming up...", (120, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
    _, waiting_buf = cv2.imencode('.jpg', waiting_img)
    waiting_frame = waiting_buf.tobytes()

    while True:
        with latest_frame_lock:
            frame_data = latest_frame

        send_frame = frame_data if frame_data is not None else waiting_frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + send_frame + b'\r\n')
        time.sleep(0.033)


@app.post("/api/reload_database")
def reload_database_endpoint():
    """Called after inventory changes (delete/update) to refresh in-memory embeddings"""
    counter.product_ids, counter.db_embeddings, counter.prices, counter.stocks, \
        counter.color_hists, counter.shape_feats, counter.real_diameters, counter.parent_ids = load_database()
    counter.booster.reset()
    return {"status": "ok", "products": len(counter.product_ids)}


@app.get("/debug/detection")
def debug_detection():
    """Test endpoint — runs one detection on current frame and returns result"""
    global latest_raw_frame
    with latest_raw_frame_lock:
        if latest_raw_frame is None:
            return {"error": "No frame available"}
        frame = latest_raw_frame.copy()

    detected, product, confidence, message = counter.detect_and_add_to_cart(frame)
    return {
        "detected": detected,
        "product": product,
        "confidence": round(float(confidence), 4) if confidence else 0,
        "message": message,
        "cart_size": len(counter.cart),
        "db_products": len(counter.product_ids),
        "vote_buffer": counter.vote_buffer,
        "recent_detections": counter.recent_detections[-5:] if counter.recent_detections else []
    }


@app.get("/api/status")
def get_status():
    """Get current system status"""
    with cart_state_lock:
        return {
            "cart": cart_state,
            "camera_active": latest_raw_frame is not None,
            "products_loaded": len(counter.product_ids),
            "vote_buffer": counter.vote_buffer,
            "last_detected": counter.last_detected_product,
            "cooldown_remaining": max(0, counter.cooldown_seconds - (time.time() - counter.last_detection_time))
        }


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/ws/cart")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        with cart_state_lock:
            await websocket.send_json(cart_state)
            
        while True:
            # Wait for messages from Next.js (like clear cart, checkout)
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
                        cart_state["stock_updated"] = True  # signal dashboard to refresh
                    else:
                        cart_state["status"] = f"Checkout failed: {result}"
                        cart_state["stock_updated"] = False
                await manager.broadcast(cart_state)
                # Reset flag after broadcast
                with cart_state_lock:
                    cart_state["stock_updated"] = False
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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
from PIL import Image

import numpy as np

class RegisterRequest(BaseModel):
    product_id: str
    price: float
    stock: int
    is_cylindrical: bool = False
    capture_step: int = 1
    parent_id: str = ""
    require_coin: bool = False  # if True, block registration when coin not in frame

partial_registrations = {}

@app.post("/api/register")
async def register_new_product(request: RegisterRequest):
    global latest_raw_frame, partial_registrations
    
    with latest_raw_frame_lock:
        if latest_raw_frame is None:
            return {"error": "Camera stream not initialized. Please wait a moment."}
        frame = latest_raw_frame.copy()
    
    # --- COIN DETECTION CHECK (if required) ---
    coin = detect_coin(frame)
    if request.require_coin and coin is None:
        return {"error": "⚠️ Coin not detected in frame. Place a ₹1 coin in the corner and try again."}
        
    try:
        results = counter.yolo_model(frame, conf=0.10, verbose=False)

        # Skip person class (0) — pick largest non-person masked object
        SKIP_CLASSES = {0}
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
            # YOLO fallback — GrabCut center crop
            final_crop, binary_mask = fallback_crop_no_yolo(frame)
            if final_crop is None or final_crop.size == 0:
                return {"error": "⚠️ No product detected in frame. Show the product clearly to the camera."}

        if final_crop is None or final_crop.size == 0:
            return {"error": "Invalid segmentation crop"}
            
        if best_idx is not None:
            is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
            if not is_valid:
                return {"error": f"Invalid detection: {reason}"}
            
        pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
        clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, counter.device)
        dino_tensor = counter.dino_transform(pil_crop).unsqueeze(0)
        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, counter.device)
        current_embedding = fuse_embeddings(clip_emb, dino_emb, alpha=0.6)
        
        if request.is_cylindrical:
            if request.capture_step == 1 or request.product_id not in partial_registrations:
                partial_registrations[request.product_id] = {"embeddings": [], "image": final_crop}

            partial_registrations[request.product_id]["embeddings"].append(current_embedding)

            if request.capture_step < 3:
                return {"status": "partial", "message": f"Successfully captured side {request.capture_step}/3. Please rotate the object.", "step": request.capture_step}
            else:
                embeddings = partial_registrations[request.product_id]["embeddings"]
                avg_emb = np.mean(embeddings, axis=0)
                final_embedding = avg_emb / np.linalg.norm(avg_emb)
                final_crop_for_save = partial_registrations[request.product_id]["image"]
                del partial_registrations[request.product_id]
        else:
            final_embedding = current_embedding
            final_crop_for_save = final_crop

        # Extract color and shape features
        color_hist = extract_color_histogram(final_crop_for_save)
        shape_feat = extract_shape_features(final_crop_for_save, binary_mask)

        # --- Coin-based real size measurement ---
        real_diameter_mm = 0.0
        if coin is not None:
            ppm = pixels_per_mm(coin[2])
            real_diameter_mm = estimate_product_real_diameter_mm(binary_mask, ppm)
            print(f"📏 Coin detected — product real diameter: {real_diameter_mm:.1f}mm")
        else:
            print("⚠️ No coin detected — size measurement skipped")

        parent_id = request.parent_id.strip() if request.parent_id else None

        existing_ids, existing_embeddings = get_all_embeddings()
        if len(existing_embeddings) > 0 and is_duplicate(
            final_embedding.reshape(1, -1), existing_embeddings,
            threshold=0.95, existing_ids=existing_ids, parent_id=parent_id
        ):
            return {"error": "DUPLICATE DETECTED: Product physically identical to existing item."}

        success, message = register_product(
            request.product_id, request.price, request.stock, final_embedding,
            color_hist=color_hist, shape_feat=shape_feat,
            real_diameter_mm=real_diameter_mm, parent_id=parent_id
        )

        if success:
            image_path = f"data/registered_products/{request.product_id}.jpg"
            cv2.imwrite(image_path, final_crop_for_save)
            counter.product_ids, counter.db_embeddings, counter.prices, counter.stocks, \
                counter.color_hists, counter.shape_feats, counter.real_diameters, counter.parent_ids = load_database()
            counter.booster.reset()
            counter.last_detected_product = request.product_id
            counter.last_detection_time = time.time() + 10
            size_info = f" | Size: {real_diameter_mm:.1f}mm" if real_diameter_mm > 0 else " | No coin detected"
            return {"status": "success", "message": message + size_info}
        else:
            return {"error": message}
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Server processing error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run inside venv
    uvicorn.run(app, host="0.0.0.0", port=8000)
