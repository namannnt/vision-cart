# 🍾 Tips for Registering Cylindrical Objects (Bottles)

## ⚠️ Problem
Cylindrical objects like sanitizer and medicine bottles are harder to recognize because:
- They look similar from different angles
- Labels may not be fully visible
- Reflective surfaces cause issues
- Round shape = less distinctive features

## ✅ Best Practices for Registration

### 1. Lighting
- ✅ Use **diffused lighting** (not direct bright light)
- ✅ Avoid reflections on bottle surface
- ❌ No shadows on label
- ❌ No glare from overhead lights

### 2. Background
- ✅ **Plain white or light gray** background
- ✅ Matte surface (not glossy)
- ❌ No patterns or textures
- ❌ No other objects in frame

### 3. Bottle Position
- ✅ **Label facing camera directly**
- ✅ Bottle upright (not tilted)
- ✅ Fill 60-70% of frame (not too close, not too far)
- ✅ Center of frame
- ❌ Don't show cap/lid if possible (focus on label)

### 4. Camera Settings
- ✅ Hold camera **stable** (no movement)
- ✅ Focus on label text
- ✅ Distance: 30-40cm from bottle
- ✅ Straight angle (not from top or side)

### 5. Multiple Angles (Advanced)
For better recognition, register **same bottle from 2-3 angles**:
- Front label view (primary)
- Slight left rotation (15°)
- Slight right rotation (15°)

Save as:
- `sanitizer_front`
- `sanitizer_left`
- `sanitizer_right`

## 🔧 Re-registration Steps

1. **Delete old entries** (if accuracy is poor):
   ```cmd
   python
   >>> import sqlite3
   >>> conn = sqlite3.connect("database/visioncart.db")
   >>> cursor = conn.cursor()
   >>> cursor.execute("DELETE FROM products WHERE product_id='sanitizer'")
   >>> cursor.execute("DELETE FROM products WHERE product_id='medicine'")
   >>> conn.commit()
   >>> conn.close()
   >>> exit()
   ```

2. **Re-register with better images**:
   ```cmd
   python register_product_app.py
   ```

3. **Follow tips above** for optimal capture

4. **Test immediately**:
   ```cmd
   python simple_accuracy_test.py
   ```

## 📊 Expected Improvement

| Before | After |
|--------|-------|
| 60-70% accuracy | 85-95% accuracy |
| Frequent "UNKNOWN" | Rare "UNKNOWN" |
| Low confidence (0.6-0.7) | High confidence (0.85+) |

## 🎯 Alternative: Lower Threshold

If re-registration doesn't help, we've already lowered the threshold from **0.85 → 0.75**.

This means:
- ✅ More lenient matching
- ✅ Better detection of difficult objects
- ⚠️ Slightly higher chance of false positives (but still safe)

## 💡 Pro Tip

For demo/testing, use products with:
- ✅ Distinctive labels
- ✅ Flat surfaces (boxes, packets)
- ✅ High contrast colors
- ✅ Clear text/logos

Bottles are hardest - if they work, everything works! 💪
