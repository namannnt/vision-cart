# 📏 Size Variant Registration Guide

## Problem: Similar Products Getting Confused

When you have products that look identical but are different sizes (e.g., Vaseline 20gm vs 50gm), the AI can get confused during detection.

## Solution: Parent Grouping + Coin Measurement

### Step 1: Register with Parent Group

When registering size variants:

1. **Enable "Require Coin for Size Measurement"** ✅
2. **Set the same Parent Group ID** for all variants
   - Example: For "vaseline 20gm" and "vaseline 50gm"
   - Parent Group: `vaseline` (same for both)
   - Product Name: `vaseline 20gm` and `vaseline 50gm` (different)

3. **Place ₹1 coin in camera frame** during registration
   - The coin provides scale reference
   - System measures actual product diameter in mm
   - This measurement is saved with the product

### Step 2: Detection with Coin

During billing/checkout:

- **WITH COIN**: System uses coin to measure product size and picks correct variant
  - ✅ Accurate: Detects exact size (20gm vs 50gm)
  
- **WITHOUT COIN**: System uses stricter shape matching
  - ⚠️ May show "Ambiguous size - Place ₹1 coin in frame"
  - This prevents wrong detection

## Example Registration Flow

### Vaseline 20gm:
```
Product Name: vaseline 20gm
Parent Group: vaseline
Price: ₹45
Stock: 50
✅ Require Coin: ON
📸 Place ₹1 coin in corner → Capture
```

### Vaseline 50gm:
```
Product Name: vaseline 50gm
Parent Group: vaseline
Price: ₹95
Stock: 30
✅ Require Coin: ON
📸 Place ₹1 coin in corner → Capture
```

## Detection Improvements

The system now has:

1. **3-frame voting** - Product must appear in 3 consecutive frames
2. **Stricter size gate** - 25% tolerance (was 45%) for parent groups without coin
3. **8-second cooldown** - Prevents duplicate scans
4. **Oscillation prevention** - Blocks if same product detected 3+ times in last 5 frames
5. **Coin-based disambiguation** - Uses real measurements when coin present

## Best Practices

✅ **DO:**
- Always use coin for size variants
- Use consistent parent group names
- Keep coin in same position during registration
- Wait for "Confirming... (3/3)" before item is added

❌ **DON'T:**
- Register similar products without parent grouping
- Skip coin measurement for size variants
- Move product during multi-frame confirmation
- Scan same item repeatedly (respect cooldown)

## Troubleshooting

**"Ambiguous size - Place ₹1 coin in frame"**
→ System can't determine size without coin. Add coin to frame.

**"Already detected recently - Remove item"**
→ Item was just scanned. Remove it from frame to scan next item.

**"Confirming... (1/3)"**
→ System is verifying detection. Keep product steady.

**Both sizes getting detected**
→ Re-register with coin measurement enabled and same parent group.

---

**Pro Tip:** For best results with similar products, always enable coin measurement during registration!
