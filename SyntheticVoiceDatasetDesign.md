# Synthetic Voice Dataset Design

This document describes the planned synthetic singing dataset strategy for the Klangio singing transcription challenge.

The goal is not to generate realistic lyrics. The goal is to generate label-preserving, vocal-like audio from the provided note annotations so the transcription model learns onset, offset, and pitch from diverse singing-like signals.

Important implementation boundary: the current pure algorithmic backend is a debugging/baseline synthesizer, not a realistic human singer. It can keep labels aligned and make syllable changes audible, but realistic human timbre likely requires a sample-based or hybrid vocal backend.

## Current Experiment Conclusion

As of 2026-06-28, the practical result of the synthetic-data experiments is:

```text
complexity did not translate into better validation scores
```

We tried pure synthetic vowels/formants, Edge TTS word units, WORLD pitch
replacement, gender/age/style grids, simple words, vowel-heavy units, detune,
drift, vibrato, scoops/fall-ins, same-syllable multi-note groups, release and
voiced-mask tuning, and fully simplified clean versions with no ornaments.

The complex variants often made the audio sound worse: blurred consonants,
unclear attacks, unstable pitch perception, repeated syllable attacks, or timing
that felt less connected to the TSV. The simplified variants were cleaner and
easier to verify, but the model evaluation still stayed around the low `0.1x`
range. After removing most experimental effects, the result remained around
`0.1x`.

Therefore the current final strategy is conservative:

```text
keep labels exact
keep audio simple
avoid most ornamentation
avoid age/style grids
generate one gender-compatible sample per TSV
accept that the final score may remain around the current 0.1x level
```

中文结论：

截至 2026-06-28，目前 synthetic-data 实验的实际结论是：

```text
合成复杂度没有转化成更好的验证分数
```

我们尝试过纯算法元音/formant、Edge TTS 单词素材、WORLD 改音高、男女/年龄/风格网格、simple words、vowel-heavy units、detune、drift、vibrato、scoop/fall-in、单吐字连续多音、release/voiced-mask 调整，以及取消装饰音的极简版本。

复杂版本经常带来更差的听感：辅音模糊、起音不清楚、pitch 感知不稳定、重复吐字攻击，或者节奏听起来和 TSV 不够贴。极简版本更干净、更容易验证，但模型评估仍然停留在低 `0.1x` 区间。即使取消大部分实验性效果，结果仍然大约是 `0.1x`。

因此当前最终策略应保守：

```text
标签绝对准确
音频尽量简单
避免大部分装饰音
避免 age/style 网格
每个 TSV 只生成一个按音域匹配性别的样本
接受最终结果可能仍在当前 0.1x 水平
```

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

## Pitch And Timing Conventions

The TSV pitch column is a MIDI semitone number, not a frequency in Hertz and not a pitch-class-only label. The numeric MIDI value is the authoritative label.

Use the standard twelve-tone equal temperament MIDI conversion:

```text
frequency_hz = 440.0 * 2 ** ((midi_pitch - 69) / 12)
```

Important reference values:

```text
MIDI 69 = A4 = 440.00 Hz
MIDI 60 = C4 = 261.63 Hz in the common scientific pitch naming convention
MIDI 72 = C5 = 523.25 Hz
```

Some libraries or DAWs may display octave names differently, for example C3 instead of C4 for MIDI 60. This does not change the dataset label. In this project, always trust the MIDI number and the frequency formula, not the displayed octave name.

Pitch-class calculations use:

```text
pitch_class = midi_pitch % 12
```

where pitch classes follow the usual MIDI ordering:

```text
0=C, 1=C#/Db, 2=D, 3=D#/Eb, 4=E, 5=F,
6=F#/Gb, 7=G, 8=G#/Ab, 9=A, 10=A#/Bb, 11=B
```

The current project model and dataloader use 127 pitch bins, indexed `0..126`. Therefore generated `score.tsv` files should keep integer MIDI labels inside this project range. The provided visible TSV files currently span MIDI `29..83`, which is a normal singing-range subset and safely inside the project range.

Small pitch details are measured in cents:

```text
100 cents = 1 semitone
1200 cents = 1 octave
frequency_ratio = 2 ** (cents / 1200)
```

Detune, vibrato, scoop, fall-in, and portamento may move the audio frequency by a few cents around the target pitch, but they must stay centered on the TSV MIDI label. They must not create a new TSV note and must not make the stable perceived pitch become another semitone.

The project audio grid is:

```text
sample_rate = 16000 Hz
hop_length = 256 samples
frame_duration = 256 / 16000 = 0.016 seconds
```

So TSV times are continuous seconds, but training labels are quantized to about 16 ms frames. A note at `onset=0.500` seconds maps to approximately frame `round(0.500 / 0.016) = 31`.

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

## Historical Plan: One TSV Generates Range-Compatible Age/Gender/Style WAVs

This section describes the earlier exploratory plan. It is kept for context,
but it is no longer the recommended final dataset shape after the latest
experiments.

Each input TSV can generate one sample for each selected age, gender, and style
combination. The debug full-grid setting was:

```text
3 genders x 5 ages x 8 styles = 120 WAVs per TSV
```

The safer exploratory default was range-aware: compute the TSV pitch summary
first, then skip age/gender presets whose broad singing range is incompatible
with the score. Use `--voice-range-filter off` only when the full debug grid is
needed.

A generated sample is:

```text
one source TSV
+ one fixed gender preset
+ one fixed age preset
+ one fixed style bundle
+ random note-level and phrase-level variations
-> one audio.wav
```

The score labels remain unchanged:

```text
source score.tsv -> copied score.tsv
```

Only the rendered audio differs across generated samples. The default generator
does not need an extra random `version` dimension; `version_index` remains as a
repeat/debug knob and defaults to one repeat per age/gender/style combination.

Current final recommendation:

```text
one source TSV
+ one automatically selected gender-compatible voice
+ middle/normal age behavior only
+ clean/basic style only
+ no same-syllable group rendering
+ no age/style expansion
-> one audio.wav
```

This is less ambitious, but it avoids multiplying low-quality variations that
did not improve validation metrics.

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

Current final run keeps only:

```text
male
female
```

The `neutral` category and age categories were useful for exploration, but the
generated differences were not reliable enough to justify using them in the
final dataset.

Recommended age-like timbre categories:

```text
child
teen
young
middle
old
```

Current final run does not use separate age categories. The middle/normal voice
behavior is used as the stable default.

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

### Voice Range Compatibility

The TSV cannot tell us the original singer's gender or age, but it can tell us
whether a synthetic voice preset is plausible for the melody. Before generating
the age/gender/style grid, compute robust pitch statistics:

```text
min_pitch
max_pitch
p05_pitch
median_pitch
p95_pitch
mean_pitch
```

Use `p05_pitch..p95_pitch` rather than raw min/max so a few ornamental or
outlier notes do not reject an otherwise reasonable voice.

Current broad MIDI range profiles:

```text
male_low:    comfortable 40..64, allowed 36..67
male_tenor:  comfortable 45..72, allowed 40..76
neutral:     comfortable 48..76, allowed 43..80
female_alto: comfortable 52..76, allowed 48..80
female_high: comfortable 57..83, allowed 52..86
child:       comfortable 60..81, allowed 55..84
```

Current filter modes:

```text
allowed:     keep comfortable and extended-range voices; skip incompatible voices
comfortable: keep only comfortable voices
off:         keep the full age/gender/style grid for debugging
```

This filter is not meant to recover the real singer identity. It only avoids
training on obviously fake combinations such as a very low male preset forced
to sing a mostly high soprano-range TSV.

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

The current grid generator binds each style to a stable policy bundle:

```text
clean:              vowel_heavy, clean pitch, no vibrato, no transition
breathy:            breath_phrase_mix, mild detune, light vibrato, light_scoop
bright:             pop_syllable_mix, mild detune, light vibrato, pop_scoop
dark:               vowel_heavy, mild detune, normal vibrato, light_scoop
nasal:              soft_syllable_mix, mild detune, light vibrato, no transition
soft_attack:        soft_syllable_mix, clean pitch, light vibrato, no transition
vibrato_light:      soft_syllable_mix, mild detune, light vibrato, light_scoop
vibrato_expressive: pop_syllable_mix, expressive detune, expressive vibrato, expressive_slide
```

Current final run uses only the clean/basic behavior. The earlier style grid is
kept as an exploratory option, but it did not produce a reliable improvement in
the low-`0.1x` validation range.

### Pitch Imperfection Policy

The nominal target pitch remains the TSV MIDI pitch. The policy defines how much micro-detuning is allowed.

Recommended policies:

```text
intune
mild_detune
expressive_detune
```

Current final simplified run may disable both noticeable detune and drift. These
policies remain documented for future experiments, but they did not provide a
clear score improvement in the current setup.

Every note may have tiny natural micro-variation. This is not treated as
"running out of tune"; it is just normal human-like pitch-center variation.

Suggested micro-variation:

```text
intune:            usually within +/- 6 cents
mild_detune:       usually within +/- 8 cents
expressive_detune: usually within +/- 10 cents
```

Noticeable detune is stricter and must be planned at whole-WAV scope:

```text
intune policy: noticeable_detune_notes = 0
noticeable_detune_notes <= 10% of notes in one WAV
noticeable_detune_duration <= 8% of total sung note duration in one WAV
```

Recommended noticeable-detune magnitude:

```text
70%: 10 to 25 cents
25%: 25 to 40 cents
5%:  40 to 50 cents
```

Avoid deviations above 50 cents in the main training set because the label still
says the original MIDI pitch.

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

Current final simplified run may disable vibrato. The tested vibrato settings
either sounded artificial in the WORLD/TTS renderer or did not improve the
validation score enough to keep by default.

Suggested ranges:

```text
only consider vibrato when note_duration >= 1500 ms
rate: 0.65 to 0.95 Hz for the current WORLD/TTS renderer
light depth: 2 to 5 cents
normal depth: 3 to 8 cents
expressive depth: 5 to 12 cents, sparse
```

Vibrato should usually start well after the note onset, not immediately at the
attack. The current renderer delays it roughly 550 to 950 ms, capped by the
note duration, and fades it in over about 200 ms. These values are intentionally
slower and shallower than typical human vocal-vibrato measurements because the
current WORLD plus TTS-unit renderer makes faster modulation sound too
mechanical.

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

Current final simplified run may disable decorative pitch transitions entirely.
Earlier transition experiments became audible only with exaggerated settings,
but realistic settings did not translate into a clear validation gain.

Definitions:

```text
scoop: start slightly below the target pitch and glide up
fall_in: start slightly above the target pitch and settle down
portamento: glide between neighboring notes in a connected phrase
```

Important rule:

```text
pitch transition is an ornament layer, not a label layer
```

The TSV pitch remains the target and should dominate the note. Transitions should be short and should not make the note sound like a different labeled pitch.

Safe first-pass transition eligibility:

```text
only consider pitch transitions when note_duration >= 500 ms
transition_notes target about 80% of eligible long notes in one WAV
do not put noticeable stable detune and transition on the same note
```

Direction distribution:

```text
low_to_target_scoop: dominant, usually 70% to 80%
high_to_target_fall_in: smaller, usually 15% to 20%
short_portamento_from_previous_note: rare, usually 5% to 10%
```

Duration is proportional to target-note duration, then clamped:

```text
short transition, about 50% of transition events:
    note_duration * 0.08 to 0.12, clamped to 60 to 120 ms

medium transition, about 40% of transition events:
    note_duration * 0.12 to 0.18, clamped to 110 to 190 ms

long transition, about 10% of transition events:
    note_duration * 0.18 to 0.24, clamped to 180 to 280 ms
    only for very long notes
```

The current renderer uses these longer-than-before durations because 30-40 ms
transitions were often too fast to hear clearly after WORLD resynthesis.

The transition curve should use smoothstep, not a hard linear ramp:

```text
pitch_offset(t) = start_offset_cents * (1 - smoothstep(t / duration))
smoothstep(x) = 3x^2 - 2x^3
```

Extra unlabeled melodic turns, grace notes, mordents, and melisma notes are
disabled in the MVP. "Unlabeled" means the audio adds pitches that do not exist
in `score.tsv`. A same-syllable group across several existing TSV notes is
allowed because those pitch changes are already labeled; it is not a decorative
transition added inside one note.

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

### Same-Syllable Multi-Note Groups

Some TSV note sequences should be rendered as one syllable carried across
several labeled pitches. This models a purposeful sung line such as `la-a-a`,
not a decorative scoop inside a single note.

Current final simplified run disables same-syllable group rendering. The idea is
musically valid, but the current TTS/WORLD implementation often sounded like
repeated attacks or unstable pitch movement rather than one continuous sung
vowel. It is safer to keep each labeled note independently rendered for the
final dataset.

Candidate rule:

```text
next_onset - current_offset <= 40 ms
adjacent MIDI pitch interval is 1 or 2 semitones
all adjacent intervals move in one direction only
maximum group size = 3 notes
each note duration >= 180 ms
no repeated pitch inside the selected group
```

Very short notes should not become same-syllable group members. In the current
TTS/WORLD renderer, a 100-150 ms continuation pitch does not sound like a stable
second sung pitch; it tends to sound like a fast wobble inside one utterance.

Only a small subset of candidates should be used:

```text
select about 30% of candidate groups per WAV
```

Important assignment rule:

```text
selected same-syllable group:
    one word/syllable may span multiple TSV pitches
    example: La-a-a

unselected adjacent notes:
    must be treated as separate syllables/words
    must not reuse the same word unit across consecutive pitches
    example: not La-La-La from accidental word reuse
```

The 30% selection fraction controls how often TSV-compatible pitch sequences
become true melisma-like same-syllable groups. It must not mean that the other
70% reuse the same word with repeated attacks. Same-word reuse is valid only
inside a selected group.

Rendering rule:

```text
group first note:
    normal syllable start, optional consonant, normal vowel onset
    render the whole selected group once from this onset

group continuation notes:
    reuse the first note's syllable/vowel
    no new consonant onset
    no new hard attack
    no independent note-level audio render
    no decorative scoop/fall-in
    allow tiny micro detune
    no noticeable stable detune
```

For the edge-tts word-unit WORLD renderer, a selected same-syllable group is
rendered as segmented audio with crossfaded note spans:

```text
group unit choice = prefer stable units: la, yeah
do not use hey or oh for same-syllable groups in the current TTS/WORLD renderer
source split = trim silence, then split the word into onset/consonant and stable vowel core
first note source = onset/consonant + vowel core
continuation note source = vowel core only
segment join = short crossfade across connected note boundaries
target F0 = each segment follows its own TSV note pitch curve
tiny gaps inside the group = bridged by crossfade, not a new consonant
```

WORLD can replace the source F0, but it does not know phoneme boundaries. The
renderer must therefore explicitly remove consonant-like material from
continuation notes. Without this split, a group intended as `la-a-a` can sound
like `la-la-la`.

This is intended to sound like the first word/syllable is articulated once, then
the later TSV pitches are sung on the same vowel. It avoids the earlier
note-by-note continuation behavior, which reused the word but still sounded like
separate attacks.

The pitch movement inside the group comes from the TSV notes themselves, so the
labels remain correct. Tiny micro detune is still allowed on all notes in the
group, including continuation notes. What is disallowed after the first group
note is decorative note-start transition such as scoop/fall-in and noticeable
stable detune.

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

For each note, sample small micro-variation from the fixed pitch policy.
Noticeable stable detune is not sampled independently note by note. Instead, it
is selected by the whole-WAV expression planner so one WAV never exceeds the
detune note-count and duration budgets.

Possible note-level components:

- constant cents offset for the note
- tiny pitch drift across the note
- delayed vibrato

Keep these label-preserving. The pitch center should still correspond to the TSV MIDI pitch.

### Note-Level Pitch Transition Events

Pitch transitions should be planned at whole-WAV scope, then assigned to a
configured subset of eligible long notes according to the fixed transition
policy. The current default target is 80% of eligible long notes.

Possible note-level events:

```text
none
low_to_target_scoop
high_to_target_fall_in
short_portamento_from_previous_note
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
- do not use transitions on notes shorter than 700 ms in the current safe MVP
- do not use decorative transitions on same-syllable continuation notes
- do not generate true melodic turns, grace notes, mordents, or melisma unless
  the TSV labels include those extra notes

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

This avoids needing separate audio samples for every spelling. In the pure algorithmic backend, vowel profiles are intentionally exaggerated so pronunciation changes are audible. In a future sample-based backend, the same syllable representation can choose and pitch-shift real recorded units instead of relying only on synthetic formants.

## Edge TTS Unit Bank

`edge-tts` should be used only to create short reusable source units, not to
directly render every TSV note.

Recommended flow:

```text
edge-tts short unit bank
-> trim / normalize / save as 16 kHz mono WAV
-> sample-based renderer chooses a unit for each TSV note
-> Python pitch-shifts and time-stretches to the target MIDI pitch and duration
-> Python adds vibrato, scoop/fall-in, detune, breath, and style processing
-> final syntheticdataset/<sample>/audio.wav + score.tsv
```

Current target sample renderer:

```text
renderer = edge_tts_word_units_world
unit bank = voice_units/edge_tts_words_10voices
word texture = selected edge-tts WAV word unit
pitch support = WORLD vocoder resynthesis with TSV-aligned F0 curve
duration support = WORLD feature resizing plus crop/pad safety
```

The previous `edge_tts_word_units_carrier` renderer made pitch audible by adding
a separate harmonic carrier behind the TTS word texture. That is no longer the
desired approach because the word itself did not become the target note. The
WORLD renderer instead keeps the word unit's spectral envelope/aperiodicity and
replaces its F0 with the TSV target pitch curve.

Runtime dependency note:

```text
pyworld
setuptools / pkg_resources
```

The current helper script is:

```bash
../.venv/bin/python scripts/generate_edge_tts_units.py \
  --output-dir voice_units/edge_tts \
  --unit-set mvp
```

The default MVP unit set includes:

```text
ah, eh, ee, oh, oo, uh
la, ma, na, ya, wa
hey, yeah, ooh, woo, whoa, doo
ta, ka, sa, sha
```

The default voice set includes two female-labeled and two male-labeled English
Edge voices. Age categories are not directly controlled by `edge-tts`; child,
teen, middle, and old timbre should be simulated later by Python postprocessing
and range-compatible preset selection.

The current 10-voice word bank contains 94 user-provided English lyric-like
words across 5 female-labeled and 5 male-labeled voices:

```text
voice_units/edge_tts_words_10voices/
```

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
  "sample_rate": 16000,
  "syllable_group_summary": {
    "candidate_group_count": 74,
    "selected_group_count": 15,
    "grouped_note_fraction": 0.11,
    "max_group_notes": 3,
    "max_adjacent_interval_semitones": 2,
    "requires_monotonic_direction": true,
    "decorative_transitions_on_continuations": false
  },
  "expression_summary": {
    "noticeable_detune_count": 8,
    "noticeable_detune_note_fraction": 0.06,
    "noticeable_detune_duration_fraction": 0.04,
    "transition_count": 3,
    "transition_min_note_duration_s": 0.7,
    "transition_curve": "smoothstep",
    "extra_unlabeled_melisma": "disabled",
    "protected_continuation_note_count": 12,
    "decorative_transitions_on_continuations": false,
    "noticeable_detune_on_continuations": false
  }
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
      "group_id": 2,
      "group_position": 0,
      "group_size": 3,
      "syllable_role": "start",
      "detune_cents": -4.2,
      "detune_type": "micro",
      "vibrato_depth_cents": 12.0,
      "transition_type": "low_to_target_scoop",
      "transition_start_cents": -28.0,
      "transition_depth_cents": 28.0,
      "transition_duration_s": 0.052,
      "transition_shape": "smoothstep"
    }
  ]
}
```

## Generation Scale

The controlled full grid remains available for debugging:

```text
per TSV: 3 genders x 5 ages x 8 styles x 1 repeat = 120 samples
400 scores x 120 samples = 48000 samples
```

The range-aware default usually generates fewer samples because incompatible
age/gender presets are skipped. This is still conceptually simple: every score
is heard through every compatible age/gender/style identity once, while
note-level expression is randomized inside each WAV. For a probe or listening
pass, restrict the grid:

```text
1 score x 3 genders x 5 ages x 8 styles = 120 samples
1 score x 3 genders x 5 ages x 3 selected styles = 45 samples
```

Additional repeats can be generated later with `versions_per_combination > 1`.

## Current Implementation Status

The current scripts can generate the range-aware planned sample set for one TSV:

```bash
../.venv/bin/python scripts/build_synthetic_dataset.py \
  --scores-dir scores \
  --output-dir syntheticdataset_probe \
  --limit-scores 1 \
  --overwrite
```

This default command uses:

```text
generation_mode = grid
voice_range_filter = allowed
genders = male,female,neutral
ages = child,teen,young,middle,old
styles = clean,breathy,bright,dark,nasal,soft_attack,vibrato_light,vibrato_expressive
versions_per_combination = 1
```

Expected upper bound for one TSV:

```text
3 genders x 5 ages x 8 styles = up to 120 sample folders
actual count depends on TSV pitch range unless --voice-range-filter off is used
```

Each sample folder contains:

```text
audio.wav
score.tsv
metadata.json
```

Validated behavior as of this plan:

```text
one-TSV full-grid probe can be generated with --voice-range-filter off
range-aware generation skips incompatible gender/age/style combinations
edge_tts_word_units_world renderer generated 120 samples for scores/1.tsv
all current syntheticdataset samples for the first TSV use WORLD word-unit F0 resynthesis
10 edge-tts word voices are used across the current first-TSV grid
dataset validator passed
F0 audit on score_1_female_young_bright_v00: median abs error about 9.0 cents, p90 about 64.0 cents for the first 40 audited notes against the expressive target curve
official SyntheticDataset dataloader read the generated samples
same-syllable groups are present and capped at 3 notes
same-syllable group units prefer vowel-friendly words and continuation notes use vowel-core sustain, not repeated consonant attacks
noticeable detune and transition budgets stay within configured limits
```

Current audio-quality limitation:

```text
pure algorithmic synthesis is useful for end-to-end pipeline checks and weak baseline data
edge-tts word-unit rendering adds real spoken word texture
carrier rendering is rejected because the word itself does not carry the TSV pitch
WORLD resynthesis is now the active first-TSV renderer so the word's F0 follows the TSV pitch
WORLD/TTS word-unit output can still sound blurry, especially on short consonant-heavy words and long stretched vowels
```

## MVP Generation Plan

For each input TSV:

1. Iterate over the selected gender, age, and style grid.
2. Compute TSV pitch statistics and skip incompatible age/gender presets unless the voice-range filter is off.
3. For each remaining age/gender/style combination, create one sample directory.
4. Copy the TSV to `score.tsv` with a header.
5. Plan same-syllable multi-note groups from stepwise connected TSV notes.
6. Generate a phrase-aware syllable/word-unit sequence inside the WAV, rendering each selected same-syllable group as one continuous word-onset plus vowel-sustain span.
   Different WAVs generated from the same TSV should not reuse an identical full word-unit sequence; the edge-tts word renderer checks for exact sequence collisions within one TSV generation run and retries with a different seed if needed.
7. Plan whole-WAV expression budgets for noticeable detune and long-note transitions, protecting same-syllable continuation notes from decorative transitions.
8. Render a waveform with either the algorithmic backend or the edge-tts word-unit backend.
9. Normalize audio safely.
10. Write `audio.wav`.
11. Write `metadata.json`.
12. Validate duration, sample rate, silence, clipping, and TSV alignment.

## Things To Avoid

- Do not train on `klangiodataset`.
- Do not change note labels just because the generated voice has micro-detune.
- Do not let consonants obscure most of a short note.
- Do not add long reverb tails that blur offsets.
- Do not make pitch drift so large that the MIDI label becomes wrong.
- Do not treat pitch transitions as new labels; they are short singer ornaments around the original TSV pitch.
- Do not let a scoop, fall-in, slide, or turn occupy most of a note.
- Do not generate true melodic turns or melisma unless the TSV labels contain those notes.
- Do not add decorative scoop/fall-in to continuation notes inside a selected same-syllable group.
- Do not create nested dataset folders unless the dataloader is changed.
