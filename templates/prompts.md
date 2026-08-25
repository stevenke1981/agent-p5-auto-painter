# Prompt Templates

## 1. Reference → Reconstruction

You are an image-to-code drawing agent. Inspect the actual reference image before coding.

Goal: reconstruct the reference as editable p5.js / p5.brush code.

Rules:
- Record exact source width, height, and aspect ratio.
- Decompose the image into background, major subjects, secondary elements, texture layers, and any legible text.
- Use normalized bounding boxes first, then convert to canvas coordinates.
- Match composition and silhouette before fine details.
- Use p5 primitives for geometric forms and p5.brush for natural marks.
- Use a fixed seed.
- After rendering, inspect the output and apply delta edits only to the largest mismatches.
- Do not invent unreadable text.

Deliver: scene-analysis.json, scene-plan.json, sketch.js, preview screenshot if available, visual-diff.json.

## 2. Reference → Stylized Drawing

Analyze the reference image and preserve its composition, subject identity, pose, major shapes, palette relationships, and visible text hierarchy. Re-render using preset: {{STYLE_PRESET}}.

Do not merely apply noise. Translate each source material into an intentional drawing technique: contour, fill, hatch, wash, spline, repeated marks, custom brush, or text-outline.

Keep seed={{SEED}} and make only local delta edits after first render.

## 3. Text → Automatic Drawing

Create an editable code drawing from this brief:

{{BRIEF}}

First produce a Scene Plan with canvas, palette, layers, elements, bounding boxes, geometry strategy, brush strategy, and lettering strategy. Then generate deterministic p5.js / p5.brush code.

Default style={{STYLE_PRESET}}, seed={{SEED}}, canvas={{WIDTH}}x{{HEIGHT}}.

## 4. Add Multilingual Lettering

Add lettering on top of the drawing.

Inputs:
- text blocks: {{TEXT_BLOCKS}}
- desired languages: {{LANGUAGES}}
- preferred placement: {{PLACEMENT}}
- style: {{LETTERING_STYLE}}

Rules:
- Create a distinct text element for each text block.
- Preserve UTF-8 characters exactly.
- For zh / ja / ko / th, prefer Noto font families.
- Use p5-text for readable typesetting, and text-outline only when brush-like lettering is needed.
- Do not guess missing content; if the user only gives a concept, create placeholder text labels explicitly marked as placeholders.
- Keep lettering inside safe margins unless the user requests bleed.

Deliver: updated scene-plan.json, sketch.js, and a summary of text placement decisions.

## 5. Visual Repair

Compare the rendered canvas against the reference. Return the top mismatches ranked by impact × confidence.

Only modify up to {{MAX_FIXES}} high-impact regions this round. Preserve all correct geometry, colors, text content, and seed. Prefer parameter changes over rewrites.
