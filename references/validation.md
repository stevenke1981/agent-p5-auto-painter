# Validation Protocol

## Static checks

- scene IDs unique
- zIndex numeric
- bbox width/height > 0
- normalized bbox within 0..1 unless `allowCrop=true`
- fixed seed present
- renderer/build compatible
- no standalone-only APIs in p5 build
- no p5-only lifecycle APIs in standalone build
- text elements must contain `text.content` and `text.language`
- text renderMode must be one of `p5-text`, `text-outline`, `mixed`

## Visual checks

Score 0–5:

- composition
- silhouette
- relative scale
- palette
- text placement
- text readability
- line character
- local detail
- texture

Prioritize low scores in that order. Do not spend iteration budget on texture when composition < 4.

## Suggested stop rule

Stop when:

- composition >= 4
- silhouette >= 4
- relative scale >= 4
- palette >= 4
- text placement >= 4 (if text exists)
- text readability >= 4 (if text exists)
- no runtime errors
- no high-impact mismatch remains

A task can continue beyond this only if the user requests higher fidelity.
