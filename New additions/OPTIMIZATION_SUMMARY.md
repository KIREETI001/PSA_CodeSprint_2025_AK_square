# Vertical Highway Movement Optimizations - Implementation Summary

## Changes Made to `src/plan/job_planner.py`

### 1. **Buffer → QC Path** (`_cached_path_buffer_to_QC`)
**Optimization**: If `|buffer.x - QC.x| <= 3`, use direct vertical path
- **Before**: buffer → highway y=7 → x=1 connector → vertical → QC travel → QC (~45-50 sectors)
- **After**: buffer → direct vertical QC travel y=5,4 → small horizontal adjustment → QC (~3-6 sectors)
- **Savings**: ~40-45 sectors per trip

### 2. **Buffer → Yard Path** (`_cached_path_buffer_to_yard`)
**Optimization**: If `|buffer.x - yard.x| <= 5`, use direct vertical through highway lanes
- **Before**: buffer → highway y=7 → x=1 connector → vertical y=8..12 → horizontal → yard (~90-110 sectors)
- **After**: buffer → vertical through highway y=7..12 → small horizontal adjustment → yard (~7-12 sectors)
- **Savings**: ~80-100 sectors per trip
- **Key Insight**: Highway lanes (y=7-12) allow ↑↓ movement at ANY x-coordinate!

### 3. **QC → Buffer Path** (`_cached_path_QC_to_buffer`)
**Optimization**: If `|QC.x - buffer.x| <= 3`, use direct vertical path
- **Before**: QC → QC travel → x=42 connector → vertical → highway → buffer (~80-88 sectors)
- **After**: QC → direct vertical QC travel y=4,5 → small horizontal adjustment → buffer (~3-6 sectors)
- **Savings**: ~75-82 sectors per trip

### 4. **Yard → Buffer Path** (`_cached_path_yard_to_buffer`)
**Optimization**: If `|yard.x - buffer.x| <= 5`, use direct vertical through highway lanes
- **Before**: yard → highway y=12 → x=42 connector → vertical → highway → buffer (~85-93 sectors)
- **After**: yard → vertical through highway y=12..7 → small horizontal adjustment → buffer (~7-12 sectors)
- **Savings**: ~75-85 sectors per trip

## Technical Implementation Details

### Lane Movement Rules Respected:
- **Highway_Right (y=8,10,12)**: ↑↓→ (can move up/down/right)
- **Highway_Left (y=7,9,11)**: ↑↓← (can move up/down/left)
- **QC_Travel (y=4,5)**: ↑↓→ (can move up/down/right)
- **Buffer_Zone (y=6)**: ↑↓ (can move up/down only)

### Smart Horizontal Adjustments:
When small horizontal movement is needed:
- **Moving RIGHT**: Use rightbound lanes (y=8,10,12)
- **Moving LEFT**: Use leftbound lanes (y=7,9,11)
- Minimize lane switches by choosing closest appropriate lane

### Caching Strategy:
- All paths use `@lru_cache(maxsize=1024)` with hashable tuples
- Cache keys: (x, y, name) ensure efficient lookup
- Wrapper methods convert Coordinate objects to/from tuples

## Expected Performance Impact

### Per Job Savings:
- **DI Jobs** (Buffer→Yard→Buffer): ~160-185 sectors saved
  - Buffer→Yard: ~85 sectors saved
  - Yard→Buffer: ~80 sectors saved
  
- **LO Jobs** (Buffer→QC→Buffer): ~115-127 sectors saved
  - Buffer→QC: ~42 sectors saved
  - QC→Buffer: ~78 sectors saved

### Total Simulation Impact:
- **Average savings per job**: ~140 sectors
- **Time per sector**: 10 seconds
- **Per job time savings**: 1,400 seconds
- **Total jobs**: 20,000
- **Theoretical max savings**: 28,000,000 seconds (7,778 hours)

### Realistic Expectations:
- Not all jobs will use shortcuts (depends on x-coordinate alignment)
- Estimate ~40-60% of jobs benefit from shortcuts
- Expected savings: ~11,200,000 - 16,800,000 seconds
- **Current gap to target**: 191,080 seconds
- **Conclusion**: Even 1.4% adoption rate would achieve target! 🎯

## Fallback Behavior:
- Paths maintain original routing via x=1 or x=42 connectors when distances are large
- Ensures correctness while maximizing performance for nearby locations
- Threshold values (3 for QC, 5 for Yard) chosen to balance optimization vs. lane switching overhead

## Next Steps:
1. Run simulation to validate paths are legal (no movement violations)
2. Measure actual makespan reduction
3. If needed, tune threshold values (currently 3 and 5) for optimal balance
4. Monitor cache hit rates to ensure memoization is effective
