"""Synthetic singing data generation helpers for the Klangio challenge.

This package intentionally stays independent from the organizer training code.
The generated dataset is consumed through the existing `SyntheticDataset`
dataloader, which expects `syntheticdataset/<sample>/audio.wav` and
`syntheticdataset/<sample>/score.tsv`.
"""

