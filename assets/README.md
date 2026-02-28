Place required static assets here:

- `assets/fixed_template.png` (fixed radar background template)
- `assets/scores/1.png` ... `assets/scores/10.png` (final-score sticker images)

The app always uses `assets/fixed_template.png` as background.
If a matching score sticker exists in `assets/scores/`, it will be pasted into the final-score area.
Otherwise the app falls back to rendering text like `总分: 8`.
