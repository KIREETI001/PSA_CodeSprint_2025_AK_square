# Path Optimization Analysis

## Current Path Rules (from floor.py):
- **QC_IN (y=3)**: → only, capacity=2
- **QC_OUT (y=3)**: ↓ only, capacity=2  
- **QC_Travel (y=4,5)**: ↑↓→, capacity=1
- **Buffer_Zone (y=6)**: ↑↓ only, capacity=2
- **Highway_Right (y=8,10,12)**: ↑↓→, capacity=1
- **Highway_Left (y=7,9,11)**: ↑↓←, capacity=1
- **Yard_IN (y=13)**: → only, capacity=3
- **Yard_OUT (y=13)**: ↑ only, capacity=1

## Current Path Implementations:

### 1. Buffer→QC (buffer y=6 → QC y=3)
```
Current: buffer(x,6) → (x,7) → (x-1..1,7) → (1,6..3) → (2..QC.x,4) → QC(x,3)
Sectors: ~(x+3+QC.x) = ~45-50 sectors
```
**OPTIMIZATION OPPORTUNITY**: 
- Instead of going to x=1 connector, go directly vertical when possible!
- If buffer.x ≈ QC.x: buffer(x,6) → (x,5) → (x,4) → QC(x,3)
- Savings: ~(x+3) sectors → ~3 sectors = 40+ sectors saved!

### 2. Buffer→Yard (buffer y=6 → Yard y=13)
```
Current: buffer(x,6) → (x,7) → (x-1..1,7) → (1,8..12) → (2..yard.x,12) → yard(x,13)
Sectors: ~(x+5+yard.x) = ~90-110 sectors
```
**OPTIMIZATION OPPORTUNITY**:
- If buffer.x ≈ yard.x: buffer(x,6) → vertical down through highway lanes
- Direct path: (x,6) → (x,7/8/9/10/11/12) → (x,13)
- Savings: ~(x+5+yard.x) → ~7 sectors = 80-100 sectors saved!

### 3. QC→Buffer (QC y=3 → buffer y=6)
```
Current: QC(x,3) → (x,4) → (x+1..42,4) → (42,5..7) → (41..buffer.x,7) → buffer(x,6)
Sectors: ~(42-x+3+42-x) = ~80-88 sectors
```
**OPTIMIZATION OPPORTUNITY**:
- If QC.x ≈ buffer.x: QC(x,3) → (x,4) → (x,5) → (x,6)
- Savings: ~85 → ~3 sectors = 82 sectors saved!

### 4. Yard→Buffer (yard y=13 → buffer y=6)
```
Current: yard(x,13) → (x,12) → (x+1..42,12) → (42,11..7) → (41..buffer.x,7) → buffer(x,6)
Sectors: ~(42-x+5+42-x) = ~85-93 sectors
```
**OPTIMIZATION OPPORTUNITY**:
- If yard.x ≈ buffer.x: yard(x,13) → vertical up through highway
- Direct: (x,13) → (x,12/11/10/9/8/7) → (x,6)
- Savings: ~88 → ~7 sectors = 81 sectors saved!

## Key Insight: VERTICAL SHORTCUT CONDITIONS
The highway lanes (y=7-12) allow VERTICAL movement (↑↓):
- **Highway_Right (y=8,10,12)**: Can move ↑↓→
- **Highway_Left (y=7,9,11)**: Can move ↑↓←

This means we CAN move vertically through highway lanes at ANY x-coordinate!

## Optimal Strategy:
For each path, check if source.x and destination.x are close enough to use vertical shortcut:
- **Threshold**: If |source.x - dest.x| <= 5, use vertical path
- **Otherwise**: Use current horizontal routing via x=1 or x=42 connectors

## Estimated Savings Per Job:
- DI job: Buffer→Yard + Yard→Buffer = ~160 sectors saved
- LO job: Buffer→QC + QC→Buffer = ~120 sectors saved
- Average: ~140 sectors × 10s = 1,400s per job
- Total (20k jobs): 28,000,000s = 7,778 hours!

**BUT**: We only need 191,080s savings to hit target, so even partial optimization will work!
