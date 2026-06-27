# Synthetic Voice Dataset Design

This document describes the planned synthetic singing dataset strategy for the Klangio singing transcription challenge.

The goal is not to generate realistic lyrics. The goal is to generate label-preserving, vocal-like audio from the provided note annotations so the transcription model learns onset, offset, and pitch from diverse singing-like signals.

## Core Principle

Each provided TSV contains only:

```text
onset    offset    pitch
```

Therefore, the generated `audio.wav` must follow the TSV timing and MIDI pitch labels as closely as possible. The `score.tsv` should be copied into each generated sample with a header, while all vocal variation is expressed in the audio.

The TSV pitch is the target note, sustained pitch center, and training label. Singer ornaments such as scoops, fall-ins, slides, and turns are audio-expression layers only. They must not change `score.tsv`, and they must not make the main perceived note become a different MIDI pitch.

Priority order:

```text
label accuracy > vocal-like timbre > pronunciation variety > realism of lyrics
```

## Required Dataset Layout

The organizer dataloader expects a flat sample directory layout:

```text
syntheticdataset/
    score_001_male_young_clean_mix01/
        audio.wav
        score.tsv
        metadata.json
    score_001_female_middle_breathy_mix02/
        audio.wav
        score.tsv
        metadata.json
```

Do not use nested category folders such as:

```text
syntheticdataset/male/young/ah/audio.wav
```

unless the official dataloader is changed. The safer design is to encode voice and generation settings in the sample folder name and `metadata.json`.

## One TSV Generates Multiple WAVs

Each input TSV should generate multiple audio versions. A generated sample is:

```text
one source TSV
+ one fixed voice preset
+ one fixed generation policy
+ random note-level and phrase-level variations
-> one audio.wav
```

The score labels remain unchanged:

```text
source score.tsv -> copied score.tsv
```

Only the rendered audio differs across generated samples.

## Fixed Per Generated WAV

These choices should be fixed for one generated sample folder. They define the overall identity of the performance.

### Source Score

- `source_score_id`
- original TSV path
- copied `score.tsv` with header:

```text
# onset,offset,note
```

### Voice Identity

Voice identity is a timbre preset, not a claim about a real singer.

Recommended gender-like categories:

```text
male
female
neutral
```

Recommended age-like timbre categories:

```text
child
teen
young
middle
old
```

These should affect parameters such as:

- formant scale
- vocal brightness
- harmonic balance
- breathiness baseline
- pitch stability
- amplitude dynamics

Example fixed voice presets:

```text
male_young
male_middle
female_young
female_middle
neutral_teen
neutral_child
```

### Overall Style

One generated WAV should use a fixed overall style preset:

```text
clean
breathy
bright
dark
nasal
soft_attack
vibrato_light
vibrato_expressive
```

The style controls the global tendency. Individual notes may still vary slightly inside the WAV.

### Pitch Imperfection Policy

The nominal target pitch remains the TSV MIDI pitch. The policy defines how much micro-detuning is allowed.

Recommended policies:

```text
intune
mild_detune
expressive_detune
```

Suggested distribution:

```text
intune:            0 to 8 cents
mild_detune:       +/- 10 to 25 cents
expressive_detune: +/- 25 to 40 cents, rare
```

Avoid frequent deviations above 50 cents because the label still says the original MIDI pitch.

Pitch imperfection means small pitch-center variation around the target pitch. It is different from pitch transitions and vibrato.

### Vibrato Policy

The policy is fixed per generated WAV, while exact vibrato can vary by phrase or note.

Recommended policies:

```text
none
light
normal
expressive
```

Suggested ranges:

```text
rate: 4 to 7 Hz
light depth: 5 to 15 cents
normal depth: 10 to 35 cents
expressive depth: 25 to 50 cents, sparse
```

Vibrato should usually start after the note onset, not immediately at the attack.

Vibrato means periodic pitch movement around the target pitch. It must remain centered on the TSV pitch.

### Pitch Transition / Ornament Policy

The policy is fixed per generated WAV, while each note may or may not trigger a transition.

Recommended policies:

```text
none
light_scoop
pop_scoop
expressive_slide
```

Definitions:

```text
scoop: start slightly below the target pitch and glide up
fall_in: start slightly above the target pitch and settle down
portamento: glide between neighboring notes in a connected phrase
turn: very short decorative pitch movement around the target
```

Important rule:

```text
pitch transition is an ornament layer, not a label layer
```

The TSV pitch remains the target and should dominate the note. Transitions should be short and should not make the note sound like a different labeled pitch.

Safe first-pass limits:

```text
transition duration <= min(60 ms, note_duration * 0.15)
transition depth <= 30 cents
stable target region >= 70% of note duration
```

Optional expressive limits:

```text
transition duration <= min(80 ms, note_duration * 0.20)
transition depth <= 50 cents
stable target region >= 70% of note duration
```

Avoid pitch transitions on very short notes. A useful rule is to only consider them when:

```text
note_duration > 250 ms
```

### Syllable Policy

The policy is fixed per WAV, but syllables are selected inside the WAV per note or per phrase.

Recommended policies:

```text
vowel_heavy
soft_syllable_mix
pop_syllable_mix
hard_consonant_sparse
breath_phrase_mix
```

## Random Inside One WAV

These elements should vary within a generated WAV. This is what makes one performance sound less repetitive.

### Syllable Sequence

Syllables should not stay fixed for an entire TSV. Instead, select them per phrase or per note.

Recommended behavior:

- phrase-level selection for smoother singing
- note-level variation for occasional diversity
- repeated vowel or syllable within short phrases
- occasional expressive syllables such as `yeah`, `hey`, `whoa`, `ooh`

Phrase grouping can be estimated from the TSV:

```text
new phrase if next_onset - previous_offset > 0.3 to 0.6 seconds
```

Example sequence inside one WAV:

```text
ah, ah, la, oh, ee, ma, na, ooh, yeah, ah
```

### Consonant Timing

Consonants should be short and should not consume the stable pitch region.

Suggested consonant duration:

```text
soft consonants: 15 to 40 ms
hard consonants: 20 to 60 ms
```

Rule:

```text
consonant short, vowel long, stable pitch mainly on the vowel
```

### Note-Level Pitch Variation

For each note, sample a small detune amount from the fixed pitch policy.

Possible note-level components:

- constant cents offset for the note
- tiny pitch drift across the note
- delayed vibrato

Keep these label-preserving. The pitch center should still correspond to the TSV MIDI pitch.

### Note-Level Pitch Transition Events

Pitch transitions should be sampled per note according to the fixed transition policy.

Possible note-level events:

```text
none
low_to_target_scoop
high_to_target_fall_in
short_portamento_from_previous_note
tiny_turn_around_target
```

Context-aware tendencies:

- upward melodic movement can use a small low-to-target scoop
- downward melodic movement can use a small high-to-target fall-in
- phrase starts can use a slightly higher probability of scoop
- connected legato phrases can use short portamento
- clean styles should use few transitions
- pop or expressive styles can use more transitions

Hard constraints:

- do not modify the TSV pitch
- do not extend the transition across most of the note
- do not make the stable pitch center different from the target MIDI pitch
- do not use strong transitions on short notes

### Phrase-Level Pitch Variation

For a phrase, add small correlated behavior:

- slightly sharper or flatter phrase tendency
- gradual drift of a few cents
- more stable pitch for clean voices
- less stable pitch for old, child, or expressive presets

This should be subtle.

### Breath Events

Breath should be randomized inside the WAV.

Recommended breath types:

```text
pre_phrase_breath
light_aspiration_on_attack
breathy_noise_under_vowel
```

Constraints:

- pre-phrase breath should happen before the note onset when possible
- breath should not shift the labeled onset
- breath noise should not dominate the pitched vowel
- avoid long reverb or tails that blur offset labels

### Loudness And Envelope

Randomize slightly per note or phrase:

- amplitude
- attack time
- release time
- note emphasis
- phrase crescendo or decrescendo

Suggested envelope limits:

```text
attack: 5 to 35 ms
release: 10 to 50 ms
```

Long attack can hurt onset recognition. Long release can hurt offset recognition.

## English-Like Syllable Inventory

Use English-like and Latin-letter syllables only. Do not build a broad multilingual or Chinese pinyin inventory for the MVP.

### Core Vowels

These are the most important singing targets:

```text
ah
aa
ae
eh
ee
ih
oh
aw
oo
uh
er
```

Recommended first-pass core:

```text
ah
eh
ee
oh
oo
uh
```

### Soft Consonant Syllables

These are highly useful for singing because they keep pitch stable:

```text
la le li lo lu
ma me mi mo mu
na ne ni no nu
ya ye yi yo yu
wa we wi wo wu
ra re ri ro ru
```

### Hard Consonant Syllables

Use these sparsely. They make onset more realistic but can add noise.

```text
pa pe pi po pu
ta te ti to tu
ka ke ki ko ku
ba be bi bo bu
da de di do du
ga ge gi go gu
```

### Fricative And Breath-Like Syllables

Use sparingly for breathiness and realistic attacks:

```text
ha he hi ho hu
fa fe fi fo fu
sa se si so su
sha she shi sho shu
tha the thi tho thu
```

### Pop-Style Expressive Syllables

These can be parameterized rather than treated as separate samples.

```text
yeah
yea
hey
oh
ooh
woo
whoa
na
nah
la
lah
da
doo
du
mm
hmm
```

## Parameterized Syllable Design

Many written syllables can share the same synthesis engine.

Represent each syllable as:

```text
optional consonant onset + vowel profile + optional vowel glide
```

Examples:

```text
oh   -> vowel: oh
ooh  -> vowel: oo
woo  -> consonant: w, vowel: oo
whoa -> consonant: h/w, glide: oo -> oh
yeah -> consonant: y, glide: ee -> eh/ah
hey  -> consonant: h, glide: eh -> ee
la   -> consonant: l, vowel: ah
ma   -> consonant: m, vowel: ah
```

This avoids needing separate audio samples for every spelling.

## Suggested Sampling Ratios

For one generated WAV, syllables can be sampled from a fixed policy.

Balanced default:

```text
50% pure vowels
30% soft consonant syllables
15% hard consonant syllables
5% expressive or breath-like events
```

Safer early MVP:

```text
65% pure vowels
25% soft consonant syllables
8% hard consonant syllables
2% expressive or breath-like events
```

## Metadata Per Sample

Each generated sample should write a `metadata.json` file. The organizer dataloader will ignore it, but it helps debugging and comparison.

Example:

```json
{
  "source_score": "scores/001.tsv",
  "voice": {
    "gender": "female",
    "age": "young",
    "preset": "female_young_bright"
  },
  "style": "breathy",
  "syllable_policy": "pop_syllable_mix",
  "pitch_policy": "mild_detune",
  "vibrato_policy": "normal",
  "pitch_transition_policy": "light_scoop",
  "random_seed": 12345,
  "sample_rate": 16000
}
```

Optionally include the exact generated syllable and detune sequence:

```json
{
  "notes": [
    {
      "onset": 0.5,
      "offset": 0.9,
      "pitch": 60,
      "syllable": "la",
      "detune_cents": -4.2,
      "vibrato_depth_cents": 12.0,
      "pitch_transition": "low_to_target_scoop",
      "transition_depth_cents": 18.0,
      "transition_duration_ms": 45.0
    }
  ]
}
```

## Generation Scale

Avoid generating every possible combination. That would explode the dataset size.

Recommended first useful scale:

```text
400 scores x 6 to 12 generated versions per score
= 2400 to 4800 samples
```

Each version should sample a different fixed voice/style/policy combination, while varying syllables and micro-expressions inside the WAV.

## MVP Generation Plan

For each input TSV:

1. Choose 6 to 12 generation presets.
2. For each preset, create one sample directory.
3. Copy the TSV to `score.tsv` with a header.
4. Generate a phrase-aware syllable sequence inside the WAV.
5. Render a vocal-like waveform with formants, harmonics, envelope, breath, vibrato, small pitch imperfections, and short label-preserving pitch transitions.
6. Normalize audio safely.
7. Write `audio.wav`.
8. Write `metadata.json`.
9. Validate duration, sample rate, silence, clipping, and TSV alignment.

## Things To Avoid

- Do not train on `klangiodataset`.
- Do not change note labels just because the generated voice has micro-detune.
- Do not let consonants obscure most of a short note.
- Do not add long reverb tails that blur offsets.
- Do not make pitch drift so large that the MIDI label becomes wrong.
- Do not treat pitch transitions as new labels; they are short singer ornaments around the original TSV pitch.
- Do not let a scoop, fall-in, slide, or turn occupy most of a note.
- Do not create nested dataset folders unless the dataloader is changed.
