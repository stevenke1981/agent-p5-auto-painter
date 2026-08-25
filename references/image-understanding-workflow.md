# Image Understanding → Drawing Workflow

## Observation checklist

1. Read actual image dimensions.
2. Identify background and global composition.
3. Find 3–8 major masses before details.
4. Estimate normalized bbox for each mass.
5. Identify dominant contour type: geometric / organic / mixed.
6. Extract 5–10 useful palette colors, not every pixel variation.
7. Identify repeated textures separately from semantic objects.
8. Record occlusion and z-order.
9. Mark uncertainty instead of inventing details.

## Normalized bbox

Use `[x, y, w, h]` in range 0..1 during analysis.

Convert with:

```text
px = x * canvasWidth
py = y * canvasHeight
pw = w * canvasWidth
ph = h * canvasHeight
```

## Subject decomposition

Good:

```text
head
  face mass
  hair mass
  left eye
  right eye
  nose curve
  mouth curve
  shadow wash
```

Bad:

```text
pixel 1
pixel 2
pixel 3
...
```

## Texture separation

Texture is a rendering layer, not geometry.

Examples:
- paper grain
- watercolor bloom
- pencil hatching
- hair strands
- fabric fibers
- stipple

Only add texture after composition and silhouette pass acceptance.
