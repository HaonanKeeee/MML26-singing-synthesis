## 2026-06-27 09:59 — Synthetic Voice Dataset Design Document

### English

**Files changed:**
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Added a dedicated design document for the planned synthetic singing dataset and voice-generation strategy.

**Code changes:**
- No executable code was changed.
- Added Markdown documentation that separates fixed per-sample settings from randomized note-level and phrase-level variations.

**Thought process:**
- The project needs a clear generation specification before implementing the `syntheticdataset` builder.
- The documentation keeps the official flat dataloader layout while capturing the richer voice, syllable, breath, pitch, and vibrato ideas discussed with the user.

**Why this code/change was added:**
- The user requested a dedicated Markdown document describing the voice/sound data synthesis idea, including gender, age, style, pitch imperfection, vibrato, vowels, consonants, and which dimensions are fixed versus randomized.

**Why the previous code needed to change:**
- No previous code needed to change.
- The repository did not yet have a focused design document for this specific synthetic voice dataset strategy.

**Problems encountered:**
- The main design risk is that the organizer dataloader expects a flat `syntheticdataset/<sample>/audio.wav` and `score.tsv` layout, while the conceptual voice taxonomy is hierarchical.

**Solution:**
- Documented that category information should be encoded in sample folder names and `metadata.json`, not nested directories, unless the dataloader is changed later.

**Better result / user experience:**
- The team now has a concrete implementation target for the dataset generator, including voice presets, syllable policies, pitch/vibrato ranges, breath handling, metadata, and validation priorities.

**Remaining risks / TODOs:**
- Implement the actual generator and validation scripts.
- Tune the recommended sampling ratios after the first training/evaluation run.

### 中文

**修改文件：**
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 新增一个专门描述合成歌声数据集和声音生成策略的设计文档。

**代码变化：**
- 没有修改可执行代码。
- 新增 Markdown 文档，把每个样本固定的设置和 wav 内部按 note/phrase 随机变化的设置分开说明。

**思考流程：**
- 在实现 `syntheticdataset` 生成脚本之前，需要先把生成规格写清楚。
- 文档既保留官方 dataloader 需要的扁平目录结构，也记录了与用户讨论过的 voice、syllable、breath、pitch、vibrato 等设计。

**为什么添加这个代码/修改：**
- 用户要求新增一个 Markdown 文档，专门描述声音/声音数据合成思路，包括 gender、age、style、pitch imperfection、vibrato、元音、辅音，以及哪些维度是一个 TSV/wav 内固定的、哪些是随机组合的。

**为什么之前的代码需要修改：**
- 之前的代码不需要修改。
- 仓库里还没有一个聚焦于这个 synthetic voice dataset 策略的独立设计文档。

**遇到的问题：**
- 主要设计风险是概念上的 voice taxonomy 是层级结构，但官方 dataloader 只读取 `syntheticdataset/<sample>/audio.wav` 和 `score.tsv` 这种扁平结构。

**解决方式：**
- 在文档中明确：除非之后修改 dataloader，否则类别信息应该写进 sample folder 名称和 `metadata.json`，不要做嵌套目录。

**带来的更好效果 / 用户体验：**
- 团队现在有了清晰的 dataset generator 实现目标，包括 voice preset、syllable policy、pitch/vibrato 范围、breath 处理、metadata 和验证重点。

**剩余风险 / TODO：**
- 需要继续实现实际 generator 和 validation 脚本。
- 第一次训练/评估后，需要根据指标调整采样比例和生成参数。

## 2026-06-27 10:08 — Clarify Pitch Transition Ornaments

### English

**Files changed:**
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Updated the synthetic voice design document to explicitly describe pitch transitions and vocal ornaments such as scoops, fall-ins, portamento, and turns.

**Code changes:**
- No executable code was changed.
- Added documentation clarifying that pitch transitions are audio-expression layers and must not change TSV pitch labels.

**Thought process:**
- The user clarified an important singing-domain point: transitions are singer-added ornaments, while the score pitch remains the target note.
- The design needed to separate pitch imperfection, vibrato, and pitch transition so the generator does not accidentally create mislabeled training audio.

**Why this code/change was added:**
- To make the dataset-generation rules safer and more musically accurate before implementation.

**Why the previous code needed to change:**
- No code needed to change.
- The previous document mentioned pitch drift and attack scoop, but did not clearly state that transitions cannot affect the labeled pitch.

**Problems encountered:**
- The main risk is confusing expressive pitch motion with a different target note, which would make the generated audio conflict with `score.tsv`.

**Solution:**
- Added fixed per-WAV `pitch_transition_policy`, note-level transition events, safety limits for duration/depth, and explicit rules that the stable pitch center must remain the TSV pitch.

**Better result / user experience:**
- Future generator implementation now has clear guardrails for adding realistic vocal transitions without corrupting transcription labels.

**Remaining risks / TODOs:**
- Implement these transition policies conservatively and validate pitch curves visually or analytically on sample outputs.

### 中文

**修改文件：**
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 更新合成声音设计文档，明确描述 scoop、fall-in、portamento、turn 等转音/装饰音。

**代码变化：**
- 没有修改可执行代码。
- 增加文档说明：转音是音频表现层，不能改变 TSV 里的 pitch label。

**思考流程：**
- 用户指出一个重要声乐理解：转音是歌手添加的演唱修饰，而谱子里的 pitch 仍然是目标音。
- 设计文档需要把 pitch imperfection、vibrato 和 pitch transition 分开，避免生成器做出标签错误的训练音频。

**为什么添加这个代码/修改：**
- 在实现前让数据生成规则更安全，也更符合真实歌唱逻辑。

**为什么之前的代码需要修改：**
- 不需要修改代码。
- 之前文档提到了 pitch drift 和 attack scoop，但没有足够明确地说明转音不能影响标签 pitch。

**遇到的问题：**
- 主要风险是把表现性的音高运动误当成新的目标音，导致生成音频和 `score.tsv` 冲突。

**解决方式：**
- 新增固定在每个 WAV 上的 `pitch_transition_policy`、note-level transition events、duration/depth 安全范围，并明确稳定音高中心必须保持为 TSV pitch。

**带来的更好效果 / 用户体验：**
- 后续实现 generator 时，可以在不污染转谱标签的前提下加入更真实的声乐转音。

**剩余风险 / TODO：**
- 实现这些 transition policy 时要保守，并用可视化或自动分析检查样本 pitch curve。

## 2026-06-27 10:22 — Initial Synthetic Dataset Generator Scripts

### English

**Files changed:**
- `synth/__init__.py`
- `synth/score_io.py`
- `synth/pitch.py`
- `synth/syllables.py`
- `synth/voice_presets.py`
- `synth/policies.py`
- `synth/envelopes.py`
- `synth/formants.py`
- `synth/ornaments.py`
- `synth/render.py`
- `synth/validate.py`
- `scripts/synthesize_score.py`
- `scripts/build_synthetic_dataset.py`
- `scripts/validate_synthetic_dataset.py`
- `Creating_log.md`

**What changed:**
- Added the first runnable synthetic singing dataset generator implementation.
- Added a `synth/` package for score parsing, syllable assignment, voice presets, generation policies, envelopes, formants, pitch ornaments, rendering, and validation.
- Added CLI scripts for single-score synthesis, batch dataset generation, and dataset validation.

**Code changes:**
- Implemented TSV parsing and writing with the required `# onset,offset,note` header.
- Implemented English-like vowel, soft consonant, hard consonant, fricative, and pop-style syllable inventories.
- Implemented per-WAV fixed policies for gender-like voice, age-like timbre, style, pitch imperfection, vibrato, and pitch transition.
- Implemented per-note and per-phrase randomized syllables, detune, drift, vibrato, short transitions, breath, attack/release, and loudness.
- Implemented a first-pass harmonic source plus formant shaping renderer using existing `numpy`, `scipy`, and `soundfile` dependencies.
- Implemented validation for required files, sample rate, silence, clipping risk, header presence, score parsing, and audio duration.

**Thought process:**
- The implementation follows the design discussion: one source TSV can create multiple flat sample folders, each sample has fixed voice/style policies, and the WAV internally varies syllables and note-level expression.
- The generator keeps `score.tsv` labels unchanged, treating vibrato and pitch transitions as audio-expression layers rather than label changes.

**Why this code/change was added:**
- The user asked to generate all planned scripts now, with detailed English comments, initial TODO placeholders, and no unnecessary changes to organizer training code.

**Why the previous code needed to change:**
- The repository had organizer training/evaluation code but no synthetic dataset generation scripts.
- Without `syntheticdataset/` generation, the default training path cannot start because the `SyntheticDataset` has zero samples.

**Problems encountered:**
- The generator needed to satisfy the organizer's flat dataloader layout while still preserving rich voice metadata.
- Some future pieces, such as better vocal synthesis, true time-varying formants, accompaniment, and stronger pitch validation, are not fully known yet.
- macOS sandbox runs showed an OpenMP shared-memory warning after some audio/scipy operations, but commands exited successfully and generated valid samples.

**Solution:**
- Stored category details in sample folder names and `metadata.json`, not nested folders.
- Added TODO comments in code where future vocal-model, accompaniment, policy-file, and formant improvements may be needed.
- Verified the scripts with temporary outputs under `/private/tmp` and did not create a large `syntheticdataset/` in the repository.

**Better result / user experience:**
- The team can now generate a debug sample, build a small or full synthetic dataset, and validate it using clear commands.
- Generated samples are compatible with the existing `SyntheticDataset` dataloader.

**Remaining risks / TODOs:**
- Listen to generated audio and adjust timbre/formant/policy settings.
- Add plots or pitch-curve checks for transition/vibrato safety.
- Run a small real training experiment after generating a starter dataset.
- Consider whether OpenMP warnings need environment-level mitigation on the final machine.

### 中文

**修改文件：**
- `synth/__init__.py`
- `synth/score_io.py`
- `synth/pitch.py`
- `synth/syllables.py`
- `synth/voice_presets.py`
- `synth/policies.py`
- `synth/envelopes.py`
- `synth/formants.py`
- `synth/ornaments.py`
- `synth/render.py`
- `synth/validate.py`
- `scripts/synthesize_score.py`
- `scripts/build_synthetic_dataset.py`
- `scripts/validate_synthetic_dataset.py`
- `Creating_log.md`

**修改内容：**
- 新增第一版可运行的 synthetic singing dataset generator。
- 新增 `synth/` 包，用于 score 读取、syllable 分配、voice preset、generation policy、envelope、formant、pitch ornament、渲染和验证。
- 新增单个 score 合成、批量数据集生成、数据集验证三个 CLI 脚本。

**代码变化：**
- 实现 TSV 读取和写入，并写出官方 dataloader 需要的 `# onset,offset,note` 表头。
- 实现英文类元音、软辅音、硬辅音、摩擦音、pop-style syllable 库。
- 实现每个 WAV 固定的 gender-like voice、age-like timbre、style、pitch imperfection、vibrato、pitch transition policy。
- 实现 wav 内部按 note/phrase 随机变化的 syllable、detune、drift、vibrato、短转音、breath、attack/release 和 loudness。
- 使用已有 `numpy`、`scipy`、`soundfile` 依赖，实现第一版 harmonic source + formant shaping 渲染器。
- 实现验证逻辑，检查必要文件、采样率、静音、削波风险、表头、score 解析和音频长度。

**思考流程：**
- 实现遵循之前讨论的设计：一个 TSV 可以生成多个扁平 sample folder，每个 sample 有固定 voice/style policy，但 wav 内部 syllable 和 note-level expression 会变化。
- 生成器保持 `score.tsv` 标签不变，把 vibrato 和 pitch transition 作为音频表现层，而不是标签变化。

**为什么添加这个代码/修改：**
- 用户要求按照计划生成所有脚本，包含详细英文注释、初版 TODO 占位，并且不无必要地修改主办方训练代码。

**为什么之前的代码需要修改：**
- 仓库之前有主办方训练/评估代码，但没有 synthetic dataset 生成脚本。
- 如果没有生成 `syntheticdataset/`，默认训练路径会因为 `SyntheticDataset` 为 0 samples 而无法启动。

**遇到的问题：**
- 生成器需要符合官方扁平 dataloader 布局，同时还要保存丰富的 voice metadata。
- 更真实的人声模型、真正的动态 formant、伴奏、更强 pitch validation 等内容暂时还需要后续根据情况补充。
- macOS 沙箱测试中，部分 audio/scipy 操作结束后出现 OpenMP shared-memory warning，但命令退出成功，生成样本也通过验证。

**解决方式：**
- 把类别信息写进 sample folder 名和 `metadata.json`，不使用嵌套目录。
- 在代码中对未来 vocal model、accompaniment、policy file、formant 改进位置添加 TODO 注释。
- 使用 `/private/tmp` 做临时输出验证，没有在仓库中直接生成大型 `syntheticdataset/`。

**带来的更好效果 / 用户体验：**
- 团队现在可以用清晰命令生成 debug sample、批量构建 synthetic dataset，并验证生成结果。
- 生成的样本已经能被现有 `SyntheticDataset` dataloader 读取。

**剩余风险 / TODO：**
- 需要试听生成音频，并调整 timbre/formant/policy 参数。
- 需要增加 pitch curve 图或自动检查，确认 transition/vibrato 不污染标签。
- 生成 starter dataset 后，需要跑一次小训练实验。
- 需要观察最终机器上是否需要额外处理 OpenMP warning。

## 2026-06-27 11:43 — Music Theory Pitch Convention Check

### English

**Files changed:**
- `synth/score_io.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Tightened synthetic score parsing around MIDI pitch labels.
- Added explicit pitch and timing conventions to the synthetic dataset design document.

**Code changes:**
- Added `PROJECT_PITCH_BINS = 127` to document the current model/dataloader pitch-bin layout.
- Rejected non-integer TSV pitch labels because the training labels are semitone-indexed MIDI bins.
- Rejected pitch `127` and above because the current project label matrix has columns `0..126`.

**Thought process:**
- Standard MIDI theory allows note numbers up to 127, but this repository's model output and dataloader use 127 bins indexed `0..126`.
- Keeping the parser aligned with the project label matrix is safer than accepting a value that is music-theory valid but would break this codebase.

**Why this code/change was added:**
- The user asked to make sure the music-theory-related logic is correct.
- The dataset generator should fail early if a TSV pitch cannot map cleanly to the project's training labels.

**Why the previous code needed to change:**
- The previous parser accepted `127`, which is a valid MIDI number in general but invalid for this project's `0..126` label matrix.
- The previous design document did not explicitly state MIDI-to-Hz, cents, pitch-class, and frame-grid conventions in one place.

**Problems encountered:**
- MIDI octave names can vary by library or DAW, so relying on names like C4 alone can be ambiguous.
- A quick shell one-liner for pitch-range inspection initially had newline escaping issues.

**Solution:**
- Documented the numeric MIDI formula as the authoritative convention.
- Clarified that displayed octave names are secondary to MIDI numbers and frequencies.
- Verified the visible official TSV files span MIDI `29..83`.

**Better result / user experience:**
- Future dataset changes have a clear reference for MIDI numbers, Hz, cents, pitch classes, and 16 ms frame quantization.
- Invalid synthetic score labels fail before generation instead of breaking the dataloader later.

**Remaining risks / TODOs:**
- If organizer code later changes `N_PITCHES` to 128, the synthetic parser range should be updated accordingly.
- A future automated pitch-curve validator would further confirm that vibrato and transitions stay label-preserving.

### 中文

**修改文件：**
- `synth/score_io.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 收紧 synthetic score 的 MIDI pitch 标签解析。
- 在 synthetic dataset 设计文档中补充明确的音高和时间约定。

**代码变化：**
- 新增 `PROJECT_PITCH_BINS = 127`，记录当前模型和 dataloader 的 pitch-bin 布局。
- 拒绝非整数 TSV pitch，因为训练标签是按 MIDI 半音编号索引的。
- 拒绝 pitch `127` 及以上，因为当前项目的 label matrix 只有 `0..126` 这些列。

**思考流程：**
- 标准 MIDI 乐理里 127 是合法 MIDI note number，但这个仓库的模型输出和 dataloader 使用的是 127 个 bin，索引是 `0..126`。
- 让 parser 和项目 label matrix 对齐，比接受一个乐理上合法但会让代码越界的值更安全。

**为什么添加这个代码/修改：**
- 用户要求确保乐理相关逻辑正确。
- 数据集生成器应该在 TSV pitch 无法干净映射到训练标签时尽早报错。

**为什么之前的代码需要修改：**
- 之前 parser 接受 `127`，它在通用 MIDI 中合法，但对本项目的 `0..126` label matrix 不合法。
- 之前设计文档没有把 MIDI-to-Hz、cent、pitch class、frame grid 约定集中写清楚。

**遇到的问题：**
- 不同库或 DAW 可能用不同 octave name，所以只依赖 C4 这类名称会有歧义。
- 第一次用 shell one-liner 检查 pitch range 时遇到换行转义问题。

**解决方式：**
- 在文档中把 MIDI 数字和频率公式写成权威约定。
- 说明 octave name 只是显示习惯，MIDI 数字和频率才是数据集标签依据。
- 验证可见官方 TSV 文件的音高范围是 MIDI `29..83`。

**带来的更好效果 / 用户体验：**
- 后续修改数据集时，有清晰的 MIDI 数字、Hz、cent、pitch class、16 ms frame 量化参考。
- 无效 synthetic score 标签会在生成前失败，而不是之后让 dataloader 出错。

**剩余风险 / TODO：**
- 如果主办方代码之后把 `N_PITCHES` 改成 128，需要同步更新 synthetic parser 的 pitch 范围。
- 后续可以增加自动 pitch-curve validator，进一步确认 vibrato 和 transition 不污染标签。

## 2026-06-27 12:41 — Grid Generation And WAV-Level Expression Planner

### English

**Files changed:**
- `synth/ornaments.py`
- `synth/render.py`
- `synth/policies.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Changed the default batch generation concept from random versions to an age/gender/style grid.
- Added a whole-WAV pitch-expression planner for noticeable detune and long-note transitions.
- Updated the design document to match the latest detune, transition, and grid-generation decisions.

**Code changes:**
- Added style policy bundles so each style maps to a fixed syllable, detune, vibrato, and transition policy.
- Added `make_grid_policy()` for deterministic gender x age x style generation.
- Updated `scripts/build_synthetic_dataset.py` so default `--generation-mode grid` generates selected gender, age, and style combinations.
- Added `--genders`, `--ages`, `--styles`, and `--versions-per-combination` filters for smaller probe runs.
- Replaced independent per-note expression sampling during rendering with `plan_note_expressions()`.
- Enforced `intune` as micro-variation only, with zero noticeable stable detune.
- Enforced noticeable detune budgets of at most 10% of notes and 8% of total note duration per WAV.
- Enforced pitch transitions only on notes at least 1.5 seconds long.
- Enforced transition budgets of at most 8% of all notes and 20% of eligible long notes per WAV.
- Added signed `transition_start_cents`, smoothstep transition curves, and expression summaries in `metadata.json`.
- Disabled true melodic turns in the MVP planner.

**Thought process:**
- The user clarified that one source TSV should generate age x gender x style WAVs, while single-note behavior should be randomized inside each WAV.
- Whole-WAV budgets are needed because independent per-note sampling cannot guarantee limits such as "at most 10% noticeable detune notes".
- Long-note-only transitions are more conservative for transcription labels than applying scoops to short or medium notes.

**Why this code/change was added:**
- The user asked to implement the latest design: age/gender/style grid generation, note-level randomization inside the WAV, capped light detune, long-note transitions, below-to-target bias, short transitions more common than long transitions, and transition length proportional to note length.

**Why the previous code needed to change:**
- The previous batch generator randomly sampled policy versions instead of covering the full age/gender/style grid.
- The previous ornament sampler decided detune and transitions independently per note, so it could not enforce per-WAV maximum percentages.
- The previous transition ramp was linear and did not record signed start cents directly in metadata.

**Problems encountered:**
- Conservative expressive vibrato initially created an invalid random range when the reduced upper bound became lower than the original lower bound.
- The macOS sandbox still prints an OpenMP shared-memory warning after scipy/audio operations, although generation and validation exit successfully.

**Solution:**
- Recomputed the conservative vibrato lower bound after reducing the upper bound.
- Added metadata summaries and spot-checked generated samples to confirm detune and transition budgets.
- Kept the OpenMP warning as an environment-level known issue because the generated files validate and the dataloader reads them.

**Better result / user experience:**
- A user can now generate controlled probe sets such as one TSV x selected genders x ages x styles.
- Generated metadata now shows whether the WAV actually followed detune and transition safety budgets.
- The generator better matches the latest music/vocal-design assumptions while preserving TSV labels.

**Remaining risks / TODOs:**
- Listen to the new grid samples and tune style bundles if some timbres or policies sound too synthetic.
- Add an automated pitch-curve plot or validator for transition and vibrato safety.
- Decide whether the full 400 x 120 grid is practical for training time and storage.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `synth/render.py`
- `synth/policies.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 将默认批量生成概念从随机 version 改为 age/gender/style 网格。
- 新增 whole-WAV 级 pitch-expression planner，用于控制明显轻微跑调和长音转音。
- 更新设计文档，使其符合最新的 detune、transition 和 grid generation 决策。

**代码变化：**
- 新增 style policy bundle，使每个 style 固定映射到 syllable、detune、vibrato 和 transition policy。
- 新增 `make_grid_policy()`，用于 deterministic 的 gender x age x style 生成。
- 更新 `scripts/build_synthetic_dataset.py`，默认 `--generation-mode grid` 会生成选择的 gender、age、style 组合。
- 新增 `--genders`、`--ages`、`--styles`、`--versions-per-combination`，便于做小型 probe。
- 将渲染时独立的 per-note expression sampling 替换为 `plan_note_expressions()`。
- 将 `intune` 限制为只有微小变化，不允许 noticeable stable detune。
- 限制每个 WAV 中 noticeable detune 最多占 10% note 数量、8% 总 note 时长。
- 限制 pitch transition 只出现在至少 1.5 秒的长音上。
- 限制每个 WAV 中 transition 最多占全部 note 的 8%，且最多占 eligible 长音的 20%。
- 新增 signed `transition_start_cents`、smoothstep transition 曲线，并在 `metadata.json` 中写入 expression summary。
- MVP planner 中禁用真正 melodic turn。

**思考流程：**
- 用户明确一个源 TSV 应生成 age x gender x style 的 WAV，而单个音的处理在每个 WAV 内部随机。
- 如果仍然每个 note 独立随机，就无法保证“最多 10% noticeable detune”这类 WAV 级限制。
- 只在长音上添加转音比给短音或中等音添加 scoop 更保守，更安全地保护 transcription label。

**为什么添加这个代码/修改：**
- 用户要求实现最新设计：age/gender/style 网格生成、WAV 内部 note-level 随机、轻微跑调比例上限、只给长音转音、低到高占大比重、短转音多于长转音、转音长度与目标音时长成比例。

**为什么之前的代码需要修改：**
- 之前批量生成器随机采样 policy version，没有覆盖完整 age/gender/style 网格。
- 之前 ornament sampler 对每个 note 独立决定 detune 和 transition，无法保证每个 WAV 的最大比例。
- 之前 transition 是线性 ramp，metadata 里也没有直接记录 signed start cents。

**遇到的问题：**
- conservative expressive vibrato 初始实现中，缩小后的上界可能低于原下界，导致随机采样区间非法。
- macOS 沙箱在 scipy/audio 操作后仍会打印 OpenMP shared-memory warning，但生成和验证命令成功退出。

**解决方式：**
- 在缩小 conservative vibrato 上界后重新计算下界。
- 新增 metadata summary，并抽查生成样本确认 detune 和 transition budget 正常。
- 将 OpenMP warning 继续视为环境级已知问题，因为生成文件通过验证且 dataloader 可以读取。

**带来的更好效果 / 用户体验：**
- 现在可以生成可控 probe，例如一个 TSV x 指定 genders x ages x styles。
- 生成的 metadata 会直接显示 WAV 是否遵守 detune 和 transition 安全预算。
- 生成器更符合最新声乐/音乐设计，同时保持 TSV 标签不变。

**剩余风险 / TODO：**
- 需要试听新 grid 样本，并根据听感调整 style bundle。
- 后续可以增加 pitch-curve 图或自动 validator，检查 transition 和 vibrato 是否安全。
- 需要评估完整 400 x 120 grid 对训练时间和存储是否实际可承受。

## 2026-06-27 13:18 — Same-Syllable Stepwise Groups

### English

**Files changed:**
- `synth/syllable_groups.py`
- `synth/syllables.py`
- `synth/ornaments.py`
- `synth/render.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Added same-syllable multi-note grouping for stepwise connected TSV notes.
- Updated rendering so continuation notes reuse the group-start syllable without a new consonant or hard attack.
- Protected continuation notes from decorative scoop/fall-in transitions and noticeable stable detune.

**Code changes:**
- Added `synth/syllable_groups.py` with candidate detection and random selection.
- Candidate groups require connected timing, adjacent MIDI intervals of one or two semitones, one-way ascending or descending pitch direction, no repeated pitch, and at most three notes.
- The planner selects about 20% of candidate groups per WAV.
- `choose_syllables_for_notes()` now accepts group marks and reuses one syllable across each selected group.
- `plan_note_expressions()` now accepts protected note indices so same-syllable continuations are excluded from noticeable detune and decorative transitions.
- `render_score_to_sample()` now writes `syllable_group_summary` and per-note group metadata.
- Continuation notes skip consonant onset, skip vowel-glide restart, and use a softer legato attack.

**Thought process:**
- A pitch change across several TSV notes can be a purposeful one-syllable melodic movement, not an unlabeled decorative turn.
- Because these pitches already exist in the TSV, they should be rendered as labeled notes under one syllable instead of being treated as extra ornament notes.
- Continuation notes should not receive the previous note-start scoop rules, because that would stack a decorative transition on top of a labeled pitch movement.

**Why this code/change was added:**
- The user clarified that a small subset of stepwise connected notes should become one-syllable continuous pitch movement, with a maximum of three notes and no decorative transition inside the syllable.

**Why the previous code needed to change:**
- The previous syllable assignment always treated each note as an independent syllable choice.
- The previous ornament planner did not know which notes were same-syllable continuations, so it could still add decorative transitions to them.

**Problems encountered:**
- The candidate definition needed to distinguish stepwise, one-direction pitch movement from any arbitrary pitch change.
- The rendering path needed to preserve the official TSV labels while reducing artificial consonant/onset restarts inside a selected group.

**Solution:**
- Used a strict candidate rule: gap at most 40 ms, adjacent pitch intervals of one or two semitones, monotonic direction, no repeated pitch, and group size at most three.
- Selected only a small fraction of candidates per WAV.
- Added protected continuation indices to the pitch-expression planner.
- Verified metadata shows continuation notes have no decorative transitions and no noticeable detune.

**Better result / user experience:**
- Generated vocals can now include `la-a-a`-like continuous syllables over several labeled pitches.
- The resulting audio is closer to singing while still keeping TSV onset, offset, and pitch labels intact.

**Remaining risks / TODOs:**
- Listen to generated same-syllable groups and tune the 20% selection fraction if it sounds too sparse or too frequent.
- Consider exposing the group selection fraction as a CLI/config option later if experiments show it matters.

### 中文

**修改文件：**
- `synth/syllable_groups.py`
- `synth/syllables.py`
- `synth/ornaments.py`
- `synth/render.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 新增针对 stepwise connected TSV notes 的 same-syllable multi-note grouping。
- 更新渲染逻辑，使 continuation notes 复用 group 起始音的 syllable，不重新加辅音或强起音。
- 保护 continuation notes，不给它们添加装饰性 scoop/fall-in，也不给 noticeable stable detune。

**代码变化：**
- 新增 `synth/syllable_groups.py`，用于检测候选组并随机选择一小部分。
- 候选组必须满足时间连续、相邻 MIDI interval 为 1 或 2 个半音、单向上行或下行、没有重复 pitch、最多三个 note。
- planner 每个 WAV 大约选择 20% 的候选组。
- `choose_syllables_for_notes()` 现在接收 group marks，并在每个选中 group 内复用同一个 syllable。
- `plan_note_expressions()` 现在接收 protected note indices，使 same-syllable continuation 不参与 noticeable detune 和 decorative transition。
- `render_score_to_sample()` 现在写出 `syllable_group_summary` 和每个 note 的 group metadata。
- continuation notes 会跳过 consonant onset、跳过 vowel-glide 重启，并使用更柔和的 legato attack。

**思考流程：**
- TSV 中多个 note 的 pitch change 可能是一个有目的的单吐字旋律运动，不是未标注的装饰性转音。
- 因为这些 pitch 已经在 TSV 里存在，所以应该渲染成同一个 syllable 下的多个 labeled notes，而不是额外 ornament notes。
- continuation notes 不应该再套用之前的 note-start scoop 规则，否则会在已标注的 pitch movement 上叠加额外装饰。

**为什么添加这个代码/修改：**
- 用户明确要求抽一小部分 stepwise connected notes 作为单个吐字的连续转音，最多三个 note，并且吐字内部不允许装饰性转音。

**为什么之前的代码需要修改：**
- 之前 syllable assignment 总是把每个 note 当作独立 syllable 选择。
- 之前 ornament planner 不知道哪些 note 是 same-syllable continuation，因此仍可能给它们加 decorative transition。

**遇到的问题：**
- 候选定义需要区分 stepwise 单方向 pitch movement 和任意 pitch change。
- 渲染路径既要保留官方 TSV 标签，又要减少选中 group 内不自然的重复辅音和重复起音。

**解决方式：**
- 使用严格候选规则：gap 最多 40 ms、相邻 pitch interval 为 1 或 2 个半音、方向单一、不重复 pitch、group 最多三个音。
- 每个 WAV 只选择一小部分候选。
- 给 pitch-expression planner 增加 protected continuation indices。
- 验证 metadata 显示 continuation notes 没有 decorative transition，也没有 noticeable detune。

**带来的更好效果 / 用户体验：**
- 生成的人声现在可以包含类似 `la-a-a` 的单吐字跨多个已标注 pitch 的连续唱法。
- 生成音频更接近真实唱歌，同时仍保持 TSV 的 onset、offset、pitch 标签不变。

**剩余风险 / TODO：**
- 需要试听 same-syllable groups 的效果，并根据听感调整 20% selection fraction。
- 如果实验显示该比例很关键，后续可以把 group selection fraction 暴露为 CLI/config 参数。

## 2026-06-27 13:19 — Clarify Same-Syllable Micro Detune Rule

### English

**Files changed:**
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Clarified that same-syllable continuation notes may keep tiny micro detune.
- Clarified that only decorative note-start transitions and noticeable stable detune are disallowed on continuation notes.

**Code changes:**
- No code behavior changed.
- The existing code already samples `micro` detune for continuation notes while protecting them from decorative transitions and noticeable detune.

**Thought process:**
- The user refined the rule: a single-syllable pitch movement may still have light detune, but notes after the first group note must not receive decorative scoop/fall-in.

**Why this code/change was added:**
- The documentation needed to distinguish "micro detune allowed" from "noticeable detune disallowed" inside same-syllable groups.

**Why the previous code needed to change:**
- The code did not need to change because it already matched the intended behavior.
- The previous wording could be misread as forbidding all detune on continuation notes.

**Problems encountered:**
- None.

**Solution:**
- Updated the design document wording around continuation-note rendering rules.

**Better result / user experience:**
- Future implementation and review are less likely to confuse micro detune with noticeable stable detune.

**Remaining risks / TODOs:**
- Listen to same-syllable groups to decide whether the current micro-detune amount is perceptually safe.

### 中文

**修改文件：**
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 澄清 same-syllable continuation notes 可以保留极轻微 micro detune。
- 澄清 continuation notes 上禁止的是装饰性 note-start transition 和 noticeable stable detune。

**代码变化：**
- 没有改变代码行为。
- 现有代码已经会给 continuation notes 采样 `micro` detune，同时保护它们不被加 decorative transition 和 noticeable detune。

**思考流程：**
- 用户细化了规则：单吐字 pitch movement 可以有轻微 detune，但 group 第一个音以后的音不能加装饰性 scoop/fall-in。

**为什么添加这个代码/修改：**
- 文档需要明确区分“允许 micro detune”和“禁止 noticeable detune”。

**为什么之前的代码需要修改：**
- 代码不需要修改，因为当前行为已经符合这个规则。
- 之前文档表述可能被误读为 continuation notes 完全不能有 detune。

**遇到的问题：**
- 无。

**解决方式：**
- 更新设计文档中 continuation-note 渲染规则的文字。

**带来的更好效果 / 用户体验：**
- 后续实现和 review 时更不容易混淆 micro detune 与 noticeable stable detune。

**剩余风险 / TODO：**
- 需要试听 same-syllable groups，判断当前 micro-detune 幅度在听感上是否安全。

## 2026-06-27 13:23 — Plan Document And Full One-TSV Grid Verification

### English

**Files changed:**
- `SyntheticVoiceDatasetDesign.md`
- `synth/ornaments.py`
- `Creating_log.md`

**What changed:**
- Updated the plan document to match the current generator state.
- Clarified that extra unlabeled melisma is disabled, while labeled same-syllable groups are allowed.
- Added a current implementation status section to the plan.
- Renamed the metadata summary key from `melodic_turns` to `extra_unlabeled_melisma`.

**Code changes:**
- Updated `synth/ornaments.py` metadata output so the expression summary uses `extra_unlabeled_melisma: disabled`.

**Thought process:**
- The previous wording around melisma could be misread as banning same-syllable groups, even though those groups use pitches already present in the TSV.
- The plan should explicitly say that the current code can generate one TSV's full planned gender x age x style grid.

**Why this code/change was added:**
- The user asked whether the plan markdown should be updated to match the current code and whether the current code can generate all planned samples for one TSV.

**Why the previous code needed to change:**
- The metadata key `melodic_turns` was less precise than the actual rule.
- The plan document did not yet include the verified full-grid command and expected 120-sample result.

**Problems encountered:**
- None beyond the known macOS sandbox OpenMP warning during generation.

**Solution:**
- Added the current full-grid generation command and validation status to the design document.
- Updated the metadata wording to distinguish unlabeled melisma from labeled same-syllable groups.

**Better result / user experience:**
- The plan document now serves as a runnable status reference, not just an abstract design.
- Metadata wording is less ambiguous for future debugging and review.

**Remaining risks / TODOs:**
- The full 400-score grid would produce about 48,000 samples, so storage and training time still need to be checked before generating everything.

### 中文

**修改文件：**
- `SyntheticVoiceDatasetDesign.md`
- `synth/ornaments.py`
- `Creating_log.md`

**修改内容：**
- 更新 plan document，使其匹配当前 generator 状态。
- 澄清禁用的是额外未标注的 melisma，而 TSV 中已标注的 same-syllable groups 是允许的。
- 在 plan 中新增当前实现状态部分。
- 将 metadata summary key 从 `melodic_turns` 改为 `extra_unlabeled_melisma`。

**代码变化：**
- 更新 `synth/ornaments.py` 的 metadata 输出，使 expression summary 使用 `extra_unlabeled_melisma: disabled`。

**思考流程：**
- 之前 melisma 的表述可能被误解为禁止 same-syllable groups，但这些 groups 的 pitch 已经在 TSV 中存在。
- plan 应该明确说明当前代码已经可以为一个 TSV 生成完整的 gender x age x style 网格。

**为什么添加这个代码/修改：**
- 用户询问 plan markdown 是否需要结合当前代码更新，以及当前代码是否已经能生成一个 TSV 的所有计划样本。

**为什么之前的代码需要修改：**
- metadata key `melodic_turns` 不如实际规则精确。
- plan 文档还没有写入已验证的 full-grid 命令和 120 sample 结果。

**遇到的问题：**
- 除了生成时已知的 macOS sandbox OpenMP warning 外，没有其他问题。

**解决方式：**
- 在设计文档中加入当前 full-grid 生成命令和验证状态。
- 更新 metadata 表述，区分未标注 melisma 与已标注 same-syllable groups。

**带来的更好效果 / 用户体验：**
- plan 文档现在可以作为可运行的状态参考，而不仅是抽象设计。
- metadata 表述对后续 debug 和 review 更不容易产生歧义。

**剩余风险 / TODO：**
- 完整 400-score grid 约 48,000 个样本，正式全部生成前仍需确认存储和训练时间。

## 2026-06-27 13:37 — Strengthen Pure-Synthesis Pronunciation Contrast

### English

**Files changed:**
- `synth/formants.py`
- `synth/render.py`
- `synth/syllables.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**What changed:**
- Strengthened the pure algorithmic backend so vowel and consonant changes are more audible.
- Regenerated the first TSV's 120-sample grid in `syntheticdataset/`.
- Documented that the pure algorithmic backend remains a debugging/baseline synthesizer, not a realistic human singer.

**Code changes:**
- Replaced broad IIR-style vowel shaping with a stronger FFT-domain vowel spectral envelope.
- Changed diphthong rendering so the start and target vowels are both rendered from the original harmonic source before blending.
- Added consonant-specific noise coloring for plosives, fricatives, breathy `h`, nasals, and soft consonants.
- Reduced full-band breath noise masking by coloring breathiness as high-frequency air.
- Updated syllable selection to avoid immediate repeated vowel colors when the policy decides to change syllables.

**Thought process:**
- The generated files had valid labels and varied metadata, but the audio backend compressed most syllables into a similar electronic timbre.
- The fastest safe improvement was to keep the TSV/data flow unchanged and make the current backend's pronunciation contrast clearer.
- This does not solve the larger realism problem; realistic human timbre still needs real unit samples, a hybrid backend, or a stronger vocal model.

**Why this code/change was added:**
- The user reported that the generated audio did not sound human and that pronunciation changes were not audible.
- The first issue is a backend-quality limit, while the second issue can be partially improved in the current code.

**Why the previous code needed to change:**
- The previous vowel filter kept too much direct harmonic source, so different vowels sounded too similar.
- The previous consonant onset used mostly generic white noise, so different consonants did not have distinct acoustic cues.
- The previous random syllable selection could still repeat very similar vowel colors immediately after a syllable-change decision.

**Problems encountered:**
- A temporary call-site error was introduced while switching diphthong rendering to use the original harmonic source.
- macOS still printed the known OpenMP shared-memory warning during dataset generation.

**Solution:**
- Fixed the call-site error and verified the edited modules with `py_compile`.
- Rendered a temporary pronunciation probe and validated it.
- Regenerated `syntheticdataset/` with `--overwrite` and ran the dataset validator.

**Better result / user experience:**
- The generated audio should now make vowel and consonant changes easier to hear, while preserving the official `audio.wav` + `score.tsv` structure.
- The sample metadata confirms meaningful syllable variety in the regenerated first-score grid.

**Remaining risks / TODOs:**
- The pure algorithmic audio still should not be treated as final realistic human singing data.
- Next major step should be adding a sample-based or hybrid backend using short recorded human syllable/vowel units.
- The OpenMP warning remains an environment/runtime warning even though generation and validation complete successfully.

### 中文

**修改文件：**
- `synth/formants.py`
- `synth/render.py`
- `synth/syllables.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**修改内容：**
- 增强纯算法合成后端，让元音和辅音变化更容易被听出来。
- 重新生成第一个 TSV 对应的 `syntheticdataset/` 120 个样本。
- 在文档中明确：当前纯算法后端仍然只是调试/弱 baseline，不是真正逼真的人声歌手。

**代码变化：**
- 将原来的宽 IIR 式 vowel shaping 改成更强的 FFT 频谱包络。
- 修改 diphthong 渲染，让起始 vowel 和目标 vowel 都从原始谐波声源分别生成后再渐变。
- 为爆破音、擦音、气声 `h`、鼻音和软辅音加入不同频段的噪声着色。
- 将 breathiness 改成更接近高频气声的噪声，减少对白音色的全频遮盖。
- 修改 syllable 选择逻辑：当 policy 决定换 syllable 时，尽量避免立刻重复同一个 vowel 色彩。

**思考流程：**
- 生成文件的 label 和 metadata 是有效的，但音频后端把大多数 syllable 压成了相似的电子音色。
- 最安全的短期改法是不改 TSV 和数据流，只增强当前后端的发音对比度。
- 这并没有解决更大的真人感问题；真实人声 timbre 仍然需要真实 unit samples、hybrid backend 或更强的 vocal model。

**为什么添加这个代码/修改：**
- 用户反馈生成音频不像人声，而且听不出发音变化。
- 前者主要是后端质量上限，后者可以在当前代码里先部分改善。

**为什么之前的代码需要修改：**
- 之前的元音滤波保留了太多原始谐波声源，不同元音听起来太接近。
- 之前的辅音 onset 基本是通用白噪声，不同辅音没有清楚的声学差异。
- 之前随机 syllable 选择在决定切换后仍可能马上抽到非常接近的 vowel 色彩。

**遇到的问题：**
- 切换 diphthong 渲染到原始谐波声源时，短暂引入过一次调用参数错误。
- 生成数据时 macOS 仍然打印已知的 OpenMP shared-memory warning。

**解决方式：**
- 修复调用参数错误，并用 `py_compile` 检查修改过的模块。
- 生成一个临时 pronunciation probe 并通过验证。
- 使用 `--overwrite` 重新生成 `syntheticdataset/`，然后运行 dataset validator。

**带来的更好效果 / 用户体验：**
- 现在生成音频里的元音和辅音变化应该更容易被听到，同时仍然保持官方要求的 `audio.wav` + `score.tsv` 结构。
- 重新生成的 first-score grid metadata 显示 syllable 多样性是有效存在的。

**剩余风险 / TODO：**
- 当前纯算法音频仍然不应该被当作最终逼真人声训练数据。
- 下一步重要工作应该是加入 sample-based 或 hybrid backend，使用短的人声 vowel/syllable unit 采样。
- OpenMP warning 仍然是环境/runtime warning，虽然生成和验证都能正常完成。

## 2026-06-27 14:17 — Range-Aware Voice Filtering And Edge TTS Unit Bank

### English

**Files changed:**
- `synth/voice_ranges.py`
- `scripts/build_synthetic_dataset.py`
- `scripts/generate_edge_tts_units.py`
- `requirements.txt`
- `SyntheticVoiceDatasetDesign.md`
- `voice_units/edge_tts/`
- `Creating_log.md`

**What changed:**
- Added TSV pitch-range statistics and range-aware age/gender voice filtering.
- Added an `edge-tts` helper script that generates short reusable word/syllable WAV units.
- Added `edge-tts` to project requirements and installed it in the parent project virtual environment.
- Generated the default MVP edge-tts unit bank with 84 WAV files.

**Code changes:**
- Added `synth/voice_ranges.py` with robust pitch stats, broad voice range profiles, and filter modes.
- Updated `scripts/build_synthetic_dataset.py` with `--voice-range-filter allowed|comfortable|off`, defaulting to `allowed`.
- Added `scripts/generate_edge_tts_units.py` with default unit sets, default voices, WAV conversion, dry-run support, retries, metadata, and resumable generation.
- Updated the design document to explain range-compatible generation and the edge-tts unit-bank workflow.

**Thought process:**
- TSV files do not contain singer identity, but their pitch ranges can identify when a synthetic voice preset is implausible.
- `edge-tts` should not directly render every note. It is better used to create source units, while Python remains responsible for pitch, timing, vibrato, detune, and transitions.
- Batch online TTS calls can fail intermittently or when a voice name is no longer available, so the unit generator needs retries and resumable behavior.

**Why this code/change was added:**
- The user asked to modify the code so generation respects realistic male/female/child pitch ranges and to add code that generates the requested word audio elements with edge-tts.

**Why the previous code needed to change:**
- The previous grid generated every gender/age/style combination for every TSV, including implausible voice-range pairings.
- There was no script for creating a reusable real-voice unit bank.
- The original default edge voice idea included `en-US-DavisNeural`, which is not present in the current edge-tts voice list and failed for short units.

**Problems encountered:**
- `edge-tts` was missing from the virtual environment.
- The first full edge-tts batch stopped when `en-US-DavisNeural` returned `NoAudioReceived`.
- macOS still prints the known OpenMP shared-memory warning during synthetic dataset rendering.

**Solution:**
- Installed `edge-tts` in the parent virtual environment and confirmed `pip check` has no broken requirements.
- Added retry/continue behavior to the unit generator.
- Replaced the unavailable/unstable `male_davis` default with `male_andrew=en-US-AndrewNeural` after a smoke test.
- Verified the range-aware generator on the first TSV: it generated 104 samples and skipped 16 incompatible combinations.
- Generated and checked 84 edge-tts unit WAV files: 4 voices x 21 units, all 16 kHz mono.

**Better result / user experience:**
- Dataset generation now avoids obviously fake voice-range combinations by default.
- The project now has a real-human TTS unit bank that can become the source for a later sample-based renderer.
- The edge-tts script is resumable and easier to debug.

**Remaining risks / TODOs:**
- Need to implement the sample-based renderer that consumes `voice_units/edge_tts/`.
- Need to confirm edge-tts usage terms before using generated audio in final competition training/submission.
- Age categories are still postprocessing presets, not native edge-tts controls.
- The range profiles are broad heuristics and should be adjusted after listening/training results.

### 中文

**修改文件：**
- `synth/voice_ranges.py`
- `scripts/build_synthetic_dataset.py`
- `scripts/generate_edge_tts_units.py`
- `requirements.txt`
- `SyntheticVoiceDatasetDesign.md`
- `voice_units/edge_tts/`
- `Creating_log.md`

**修改内容：**
- 增加 TSV pitch-range 统计和基于音域的 age/gender voice 过滤。
- 增加 `edge-tts` 辅助脚本，用来生成短的、可复用的单词/音节 WAV 元素。
- 将 `edge-tts` 加入 requirements，并安装到上一级项目虚拟环境。
- 生成默认 MVP edge-tts unit bank，共 84 个 WAV 文件。

**代码变化：**
- 新增 `synth/voice_ranges.py`，包含 robust pitch stats、宽泛 voice range profiles 和过滤模式。
- 更新 `scripts/build_synthetic_dataset.py`，加入 `--voice-range-filter allowed|comfortable|off`，默认是 `allowed`。
- 新增 `scripts/generate_edge_tts_units.py`，包含默认 unit sets、默认 voices、WAV 转换、dry-run、重试、metadata 和可恢复生成。
- 更新设计文档，说明 range-compatible generation 和 edge-tts unit-bank 工作流。

**思考流程：**
- TSV 不包含原始歌手身份，但 pitch range 可以判断某个合成 voice preset 是否明显不合理。
- `edge-tts` 不应该直接渲染每个 note；更合适的是生成 source units，再由 Python 控制 pitch、duration、vibrato、detune 和 transition。
- 在线批量 TTS 调用可能偶发失败，或者 voice name 已经不可用，所以 unit generator 需要重试和可恢复行为。

**为什么添加这个代码/修改：**
- 用户要求修改代码，使生成逻辑考虑男女/童声等真实音域，同时添加用 edge-tts 生成所需单词音频元素的代码。

**为什么之前的代码需要修改：**
- 之前每个 TSV 都生成完整 gender/age/style 网格，包括一些明显不合理的 voice-range 组合。
- 之前没有创建真实人声 unit bank 的脚本。
- 最初设想中的默认 Edge voice 包含 `en-US-DavisNeural`，但它不在当前 edge-tts voice list 中，并且对短 unit 生成失败。

**遇到的问题：**
- 虚拟环境里缺少 `edge-tts`。
- 第一次完整 edge-tts 批量生成在 `en-US-DavisNeural` 返回 `NoAudioReceived` 时中断。
- 合成数据渲染时 macOS 仍然会打印已知的 OpenMP shared-memory warning。

**解决方式：**
- 在上一级虚拟环境安装 `edge-tts`，并确认 `pip check` 没有 broken requirements。
- 给 unit generator 加入 retry/continue 逻辑。
- 经过 smoke test 后，将不可用/不稳定的默认 `male_davis` 替换为 `male_andrew=en-US-AndrewNeural`。
- 用第一个 TSV 验证 range-aware generator：生成 104 个样本，跳过 16 个不合理组合。
- 生成并检查 84 个 edge-tts unit WAV 文件：4 个 voice x 21 个 unit，全部为 16 kHz mono。

**带来的更好效果 / 用户体验：**
- 默认 dataset generation 会避开明显假的 voice-range 组合。
- 项目现在有真实 TTS 人声 unit bank，可作为下一步 sample-based renderer 的声源。
- edge-tts 脚本可以恢复执行，也更容易 debug。

**剩余风险 / TODO：**
- 还需要实现读取 `voice_units/edge_tts/` 的 sample-based renderer。
- 在最终比赛训练/提交前，需要确认 edge-tts 的使用条款是否允许这种用途。
- age categories 仍然是后处理 preset，不是 edge-tts 原生控制。
- 当前 range profiles 是宽泛启发式规则，后续应根据试听和训练结果调整。

## 2026-06-27 14:33 — Ten-Voice Edge TTS Word Bank

### English

**Files changed:**
- `scripts/generate_edge_tts_units.py`
- `voice_units/edge_tts_words_10voices/`
- `Creating_log.md`

**What changed:**
- Added the user's 94-word lyric-like word bank as a named `word_bank_basic` unit set.
- Added support for fetching all current edge-tts voices by locale/gender, while still allowing explicit voice selection.
- Generated a clean 10-voice word bank with 5 female-labeled and 5 male-labeled voices.

**Code changes:**
- Extended `VoiceSpec` with optional gender and locale metadata.
- Added `WORD_BANK_BASIC_UNITS`.
- Added `--edge-voice-locale-prefix` and `--edge-voice-genders` for catalog-based voice selection.
- Kept explicit `--voice label=edgeVoiceName` selection so small curated banks can be generated without using every available voice.

**Thought process:**
- The first interpretation of "all different TTS voices" would have generated 4,418 WAV files from 47 English voices.
- The user clarified that only 10 voices are needed, split evenly by gender.
- A separate output directory avoids mixing the earlier interrupted all-voice attempt with the final curated 10-voice bank.

**Why this code/change was added:**
- The user provided a specific word list and asked for single-word audio elements with different male and female TTS voices.
- After generation began, the user clarified the desired scope: 10 people total, 5 male and 5 female.

**Why the previous code needed to change:**
- The previous named unit sets covered vowels/syllables but not the user's lyric-like English word list.
- The previous all-English-voice mode was useful but too broad for the requested output.

**Problems encountered:**
- The initial all-English generation was stopped after the user clarified the smaller scope.
- Online TTS generation takes time and should be resumable.

**Solution:**
- Stopped the all-voice generation process.
- Generated a new clean directory `voice_units/edge_tts_words_10voices/` using explicit curated voices.
- Verified 940 WAV files: 10 voices x 94 words, all 16 kHz mono, no failures.

**Better result / user experience:**
- The user now has exactly the requested 10-voice word-level unit bank rather than an oversized all-voice bank.
- The files are organized by voice and ready to be consumed by a future sample-based renderer.

**Remaining risks / TODOs:**
- `voice_units/edge_tts_words/` contains a partial interrupted all-voice attempt and can be removed later if the user wants cleanup.
- Need to implement the renderer that converts these word units into TSV-aligned note audio.
- Need to confirm edge-tts usage terms before final training/submission use.

### 中文

**修改文件：**
- `scripts/generate_edge_tts_units.py`
- `voice_units/edge_tts_words_10voices/`
- `Creating_log.md`

**修改内容：**
- 将用户提供的 94 个歌词风格英文词加入为命名 unit set：`word_bank_basic`。
- 增加按 locale/gender 抓取当前 edge-tts voices 的能力，同时保留显式指定 voice 的能力。
- 生成一个干净的 10 voice 词库：5 个女声标签 voice，5 个男声标签 voice。

**代码变化：**
- 扩展 `VoiceSpec`，加入可选 gender 和 locale metadata。
- 新增 `WORD_BANK_BASIC_UNITS`。
- 新增 `--edge-voice-locale-prefix` 和 `--edge-voice-genders`，用于按 catalog 选择 voice。
- 保留 `--voice label=edgeVoiceName` 显式选择，使我们可以生成小而受控的 curated bank。

**思考流程：**
- 最初按“所有不同 TTS voice”理解会从 47 个英文 voice 生成 4,418 个 WAV。
- 用户澄清只需要 10 个 voice，并且男女各 5 个。
- 使用独立输出目录可以避免把之前中断的全量尝试和最终 10 voice 词库混在一起。

**为什么添加这个代码/修改：**
- 用户提供了明确词表，并要求生成男女不同 TTS voice 的单词音频元素。
- 开始生成后，用户进一步澄清目标范围是总共 10 个人声，男女各 5 个。

**为什么之前的代码需要修改：**
- 之前的命名 unit sets 覆盖 vowel/syllable，但没有覆盖用户这批歌词风格英文词。
- 之前的 all-English-voice 模式虽然有用，但对当前需求过大。

**遇到的问题：**
- 用户澄清更小范围后，最初的 all-English generation 需要停止。
- 在线 TTS 生成耗时较长，需要可恢复。

**解决方式：**
- 停止 all-voice 生成进程。
- 用显式选择的 curated voices 生成新目录 `voice_units/edge_tts_words_10voices/`。
- 验证 940 个 WAV 文件：10 voices x 94 words，全部 16 kHz mono，失败数为 0。

**带来的更好效果 / 用户体验：**
- 用户现在得到的是精确符合要求的 10 voice word-level unit bank，而不是过大的全量 voice bank。
- 文件按 voice 分组，后续可以直接给 sample-based renderer 使用。

**剩余风险 / TODO：**
- `voice_units/edge_tts_words/` 中有之前中断的 all-voice 部分结果，如用户需要清理可以之后删除。
- 还需要实现把这些 word units 转成 TSV 对齐 note audio 的 renderer。
- 最终训练/提交前仍需确认 edge-tts 使用条款。

## 2026-06-27 14:40 — Render First TSV With Edge TTS Word Units

### English

**Files changed:**
- `synth/unit_bank.py`
- `synth/sample_render.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**What changed:**
- Added a reusable audio-unit bank loader for generated edge-tts WAV units.
- Added a first-pass sample-based renderer named `edge_tts_word_units_carrier`.
- Updated the dataset build CLI so `--renderer edge_tts_words` can use `voice_units/edge_tts_words_10voices/`.
- Overwrote the first TSV's 120 existing `syntheticdataset` samples with edge-tts word-unit audio.

**Code changes:**
- `synth/unit_bank.py` loads generated WAV units, groups them by voice, caches audio, and maps synthetic gender presets to male/female/all TTS voices.
- `synth/sample_render.py` chooses one TTS voice per generated WAV, assigns random lyric-like word units to notes, preserves selected same-syllable groups, and adds a TSV-pitch harmonic carrier with the existing expression curves.
- `scripts/build_synthetic_dataset.py` now accepts `--renderer algorithmic|edge_tts_words` and `--unit-bank-dir`.
- The design document now describes the implemented carrier-based word-unit renderer and its limitations.

**Thought process:**
- The user wanted the first TSV regenerated from the newly created word audio elements.
- A fully natural pitch-shift/time-stretch backend is still a bigger task, so the first reliable step is a hybrid renderer: real TTS word texture plus a label-aligned pitch carrier.
- The full first-TSV grid was regenerated with `--voice-range-filter off` so all 120 existing sample folders were overwritten and no old pure-algorithmic files were left behind.

**Why this code/change was added:**
- The previous generator still used the algorithmic source-filter backend.
- The newly generated edge-tts word bank needed a code path that actually consumes it to create `audio.wav`.

**Why the previous code needed to change:**
- `build_synthetic_dataset.py` only knew how to call the algorithmic renderer.
- There was no unit-bank abstraction or renderer for external short word WAV files.

**Problems encountered:**
- `librosa.load()` triggered a numba cache error in this environment when loading WAV units.
- The known macOS OpenMP shared-memory warning still appears during rendering.

**Solution:**
- Switched unit-bank WAV loading to `soundfile.read()` with scipy resampling fallback, avoiding the librosa/numba cache path.
- Verified a one-sample smoke render first.
- Regenerated the first TSV into `syntheticdataset/` with `--renderer edge_tts_words --voice-range-filter off --overwrite`.
- Ran the synthetic dataset validator after generation.

**Better result / user experience:**
- The current first-TSV dataset now uses real edge-tts word recordings instead of only synthetic oscillator/formant audio.
- All 10 generated TTS voices are represented across the 120 generated samples.
- Metadata clearly records the renderer, selected TTS voice, and selected word per note.

**Remaining risks / TODOs:**
- The current renderer uses a harmonic carrier for pitch support, so it is not yet natural singing.
- Next step should implement true pitch/time modification for word units.
- The partial `voice_units/edge_tts_words/` all-voice attempt still exists and can be cleaned later if desired.
- Need to confirm edge-tts usage terms before final training/submission use.

### 中文

**修改文件：**
- `synth/unit_bank.py`
- `synth/sample_render.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**修改内容：**
- 新增可复用的 edge-tts WAV 音频元素库 loader。
- 新增第一版 sample-based renderer：`edge_tts_word_units_carrier`。
- 更新 dataset build CLI，使 `--renderer edge_tts_words` 可以使用 `voice_units/edge_tts_words_10voices/`。
- 用 edge-tts word-unit 音频覆盖生成第一个 TSV 对应的 120 个已有 `syntheticdataset` 样本。

**代码变化：**
- `synth/unit_bank.py` 负责加载生成的 WAV units、按 voice 分组、缓存音频，并将 synthetic gender preset 映射到 male/female/all TTS voices。
- `synth/sample_render.py` 为每个生成 WAV 选择一个 TTS voice，为每个 note 分配随机歌词风格 word unit，保留 selected same-syllable groups，并叠加带已有 expression curve 的 TSV-pitch harmonic carrier。
- `scripts/build_synthetic_dataset.py` 新增 `--renderer algorithmic|edge_tts_words` 和 `--unit-bank-dir`。
- 设计文档补充当前 carrier-based word-unit renderer 及其限制。

**思考流程：**
- 用户希望用刚生成的单词音频元素重新生成第一个 TSV。
- 真正自然的 pitch-shift/time-stretch 后端仍然是更大的任务，所以第一步先做可靠 hybrid renderer：真实 TTS word texture + label-aligned pitch carrier。
- 为了覆盖已有的 120 个样本，这次使用 `--voice-range-filter off` 生成完整 first-TSV grid，避免留下旧的纯算法文件。

**为什么添加这个代码/修改：**
- 之前 generator 仍然使用 algorithmic source-filter 后端。
- 新生成的 edge-tts word bank 需要一个实际消费它并生成 `audio.wav` 的代码路径。

**为什么之前的代码需要修改：**
- `build_synthetic_dataset.py` 只能调用 algorithmic renderer。
- 之前没有针对外部短 word WAV 文件的 unit-bank 抽象和 renderer。

**遇到的问题：**
- 当前环境中用 `librosa.load()` 读取 WAV units 时触发 numba cache 错误。
- 渲染时仍然出现已知的 macOS OpenMP shared-memory warning。

**解决方式：**
- 将 unit-bank WAV 读取改为 `soundfile.read()`，并保留 scipy resampling fallback，绕开 librosa/numba cache 路径。
- 先验证单样本 smoke render。
- 使用 `--renderer edge_tts_words --voice-range-filter off --overwrite` 将第一个 TSV 重新生成到 `syntheticdataset/`。
- 生成后运行 synthetic dataset validator。

**带来的更好效果 / 用户体验：**
- 当前 first-TSV dataset 已使用真实 edge-tts word recordings，而不再只是 oscillator/formant 纯合成音频。
- 10 个生成的 TTS voices 都出现在 120 个生成样本中。
- metadata 会清楚记录 renderer、选中的 TTS voice 和每个 note 的 word。

**剩余风险 / TODO：**
- 当前 renderer 使用 harmonic carrier 支撑 pitch，因此还不是自然唱歌。
- 下一步应该实现 word units 的真实 pitch/time modification。
- 之前中断的 `voice_units/edge_tts_words/` all-voice 部分结果仍然存在，如有需要之后可以清理。
- 最终训练/提交前仍需确认 edge-tts 使用条款。

## 2026-06-27 14:51 — Switch Word Renderer Toward WORLD F0 Resynthesis

### English

**Files changed:**
- `synth/sample_render.py`
- `requirements.txt`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Replaced the carrier-mix rendering path with a WORLD-vocoder resynthesis path in code.
- Added `pyworld` and `setuptools` to `requirements.txt`.
- Updated the design document to reject the previous carrier approach as the final solution.

**Code changes:**
- `synth/sample_render.py` now plans to resynthesize each selected word unit with WORLD using the TSV-aligned F0 curve.
- The renderer now stores `renderer: edge_tts_word_units_world` for future regenerated samples.
- WORLD analysis is cached per source unit/continuation state.
- `pyworld` is lazy-imported so the rest of the project still imports cleanly if the runtime dependency is missing.

**Thought process:**
- The user correctly identified that the previous output sounded like an unpitched spoken word with a pitched synthesizer behind it.
- The correct fix is not another carrier mix. The word audio itself must carry the target F0.
- WORLD is a suitable first local tool because it separates F0 from spectral envelope and aperiodicity, letting us replace F0 with the TSV pitch curve.

**Why this code/change was added:**
- The requested behavior is that each word unit becomes the pitch written in the TSV, including detune, vibrato, and transitions.

**Why the previous code needed to change:**
- The previous `edge_tts_word_units_carrier` renderer made the pitch audible separately, but did not make the spoken word itself pitched.

**Problems encountered:**
- `pyworld` installed successfully, but importing it failed because the venv lacks `pkg_resources`, provided by `setuptools`.
- Installing `setuptools` was blocked by the environment's approval/usage limit, so the regenerated WORLD-based dataset could not be produced in this turn.

**Solution:**
- Added `setuptools` to requirements.
- Changed `pyworld` to a lazy import with a clear runtime error message.
- Verified that the modified modules compile and import without triggering the missing runtime dependency.

**Better result / user experience:**
- The code path now points at the correct technical solution: word-unit F0 resynthesis rather than a background carrier.
- Future generation should fail clearly if the required WORLD runtime dependencies are missing.

**Remaining risks / TODOs:**
- Need to run `../.venv/bin/python -m pip install setuptools pyworld` once the environment allows it.
- Need to regenerate `syntheticdataset/` after the dependency is available.
- Need to listen to WORLD output and tune long-note word stretching so consonants are not unnaturally extended.
- Current on-disk `syntheticdataset/` still contains the previously generated carrier-based output until regeneration succeeds.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `requirements.txt`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 在代码中将 carrier-mix 渲染路径替换为 WORLD vocoder 重合成路径。
- 在 `requirements.txt` 中加入 `pyworld` 和 `setuptools`。
- 更新设计文档，明确之前的 carrier 方法不能作为最终解决方案。

**代码变化：**
- `synth/sample_render.py` 现在计划用 WORLD 将每个选中的 word unit 按 TSV 对齐的 F0 曲线重合成。
- 后续重新生成的样本会写入 `renderer: edge_tts_word_units_world`。
- WORLD analysis 会按 source unit / continuation 状态缓存。
- `pyworld` 改为 lazy import，这样缺少 runtime dependency 时项目其他部分仍然可以正常 import。

**思考流程：**
- 用户正确指出上一版听起来像“没有音高的 spoken word + 背后一个正确 pitch 的合成器”。
- 正确修法不是继续混 carrier，而是让 word audio 本身携带目标 F0。
- WORLD 适合作为第一版本地工具，因为它把 F0、spectral envelope 和 aperiodicity 分开，可以把 F0 替换成 TSV pitch curve。

**为什么添加这个代码/修改：**
- 用户要求每个 word unit 本身变成 TSV 中写的 pitch，并且继续包含 detune、vibrato 和 transition。

**为什么之前的代码需要修改：**
- 之前的 `edge_tts_word_units_carrier` renderer 只是单独让 pitch 可听见，没有让 spoken word 自己变成目标音高。

**遇到的问题：**
- `pyworld` 安装成功，但导入失败，因为当前 venv 缺少 `pkg_resources`，它由 `setuptools` 提供。
- 安装 `setuptools` 被当前环境的 approval/usage limit 阻止，因此本轮无法生成 WORLD 版本 dataset。

**解决方式：**
- 将 `setuptools` 加入 requirements。
- 将 `pyworld` 改为 lazy import，并提供清楚的 runtime error。
- 验证修改后的模块可以编译和 import，不会因为缺少 runtime dependency 直接阻断其他代码。

**带来的更好效果 / 用户体验：**
- 代码路径现在指向正确技术方案：word-unit F0 resynthesis，而不是背景 carrier。
- 如果缺少 WORLD runtime dependency，未来生成会清楚失败，而不是生成错误声音。

**剩余风险 / TODO：**
- 等环境允许后需要运行 `../.venv/bin/python -m pip install setuptools pyworld`。
- dependency 可用后需要重新生成 `syntheticdataset/`。
- 需要试听 WORLD 输出，并调 long-note word stretching，避免辅音被不自然拉长。
- 当前磁盘上的 `syntheticdataset/` 仍然是上一版 carrier 输出，直到重新生成成功。

## 2026-06-27 15:07 — Regenerate First TSV With WORLD-Pitched Word Units

### English

**Files changed:**
- `synth/sample_render.py`
- `requirements.txt`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**What changed:**
- Fixed the environment so PyWORLD can import and run.
- Removed the remaining carrier-related implementation from the word-unit renderer.
- Regenerated all 120 first-TSV samples in `syntheticdataset/` using `edge_tts_word_units_world`.
- Strengthened the voiced-region mask so short words keep enough pitched vowel center.

**Code changes:**
- Pinned `setuptools<81` because current PyWORLD imports `pkg_resources`.
- Removed unused carrier helper functions and carrier wording from `synth/sample_render.py`.
- Updated WORLD voiced-mask resizing to combine detected voiced frames with a default central vowel region.

**Thought process:**
- The user was right that the previous carrier idea did not satisfy the requirement.
- The data must make the word unit itself carry the TSV pitch.
- WORLD resynthesis is the current local solution because it replaces the word unit F0 with the target pitch curve while keeping word timbre.

**Why this code/change was added:**
- The user explicitly required accurate pitch on each word, not a separate pitched background.

**Why the previous code needed to change:**
- The previous carrier implementation made the label pitch audible but did not pitch the word itself.
- Some short words had too little detected voiced material, so the initial WORLD version could still show pitch-estimation outliers.

**Problems encountered:**
- `setuptools` 82 did not provide `pkg_resources` in this environment, which prevented PyWORLD import.
- PyWORLD still prints a deprecation warning for `pkg_resources`; this is why `setuptools<81` is pinned.
- The known macOS OpenMP shared-memory warning still appears during rendering.

**Solution:**
- Installed `setuptools<81` in the parent virtual environment.
- Verified `setuptools`, `pkg_resources`, and `pyworld` import successfully.
- Ran `pip check` successfully.
- Regenerated the first TSV with `--renderer edge_tts_words --voice-range-filter off --overwrite`.
- Validated `syntheticdataset/` and checked metadata/F0 audit.

**Better result / user experience:**
- All 120 current first-TSV samples now use `renderer: edge_tts_word_units_world`.
- The selected word unit itself is resynthesized to follow the TSV F0 curve.
- F0 audit on `score_1_female_young_bright_v00` shows about 5.4 cents median absolute error and about 11.9 cents p90 absolute error over the first 40 audited notes.

**Remaining risks / TODOs:**
- Listen to WORLD samples and tune long-note stretching if consonants sound too extended.
- Extend WORLD generation beyond the first TSV only after listening confirms the quality is acceptable.
- Confirm edge-tts usage terms before final training/submission use.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `requirements.txt`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**修改内容：**
- 修复环境，使 PyWORLD 可以正常 import 和运行。
- 从 word-unit renderer 中移除残留的 carrier 实现。
- 用 `edge_tts_word_units_world` 重新生成 `syntheticdataset/` 中第一个 TSV 的全部 120 个样本。
- 增强 voiced-region mask，让短词也保留足够的有音高元音中心。

**代码变化：**
- pin `setuptools<81`，因为当前 PyWORLD 会 import `pkg_resources`。
- 从 `synth/sample_render.py` 移除未使用的 carrier helper functions 和 carrier 表述。
- 更新 WORLD voiced-mask resizing，将检测到的 voiced frames 和默认中间元音区合并。

**思考流程：**
- 用户指出得对：之前的 carrier 方案不满足需求。
- 数据必须让 word unit 自身携带 TSV pitch。
- WORLD resynthesis 是当前本地可行解，因为它能把 word unit 的 F0 替换成目标 pitch curve，同时保留词的音色。

**为什么添加这个代码/修改：**
- 用户明确要求每个单词本身有准确 pitch，而不是背景里有单独 pitch。

**为什么之前的代码需要修改：**
- 之前 carrier 实现只让 label pitch 可听见，没有给 word 本身变 pitch。
- 部分短词检测到的 voiced material 太短，初版 WORLD 仍可能出现 pitch 估计离群。

**遇到的问题：**
- 当前环境里的 `setuptools` 82 不提供 `pkg_resources`，导致 PyWORLD 无法 import。
- PyWORLD 仍会打印 `pkg_resources` deprecation warning，因此需要 pin `setuptools<81`。
- 渲染时仍然出现已知 macOS OpenMP shared-memory warning。

**解决方式：**
- 在上一级虚拟环境安装 `setuptools<81`。
- 验证 `setuptools`、`pkg_resources` 和 `pyworld` 都能成功 import。
- 成功运行 `pip check`。
- 使用 `--renderer edge_tts_words --voice-range-filter off --overwrite` 重新生成第一个 TSV。
- 运行 `syntheticdataset/` validator，并检查 metadata 和 F0 audit。

**带来的更好效果 / 用户体验：**
- 当前第一个 TSV 的 120 个样本全部使用 `renderer: edge_tts_word_units_world`。
- 选中的 word unit 自身会按 TSV F0 曲线重合成。
- `score_1_female_young_bright_v00` 的 F0 audit 显示，前 40 个 audited notes 的 median absolute error 约 5.4 cents，p90 absolute error 约 11.9 cents。

**剩余风险 / TODO：**
- 需要试听 WORLD 样本，如果长音里辅音被拉得太长，需要继续调 stretching。
- 只有试听确认质量可接受后，再把 WORLD 生成扩展到第一个 TSV 之外。
- 最终训练/提交前仍需确认 edge-tts 使用条款。

## 2026-06-27 15:32 — Render Same-Syllable Groups As Continuous Vowel Pitch Movement

### English

**Files changed:**
- `synth/sample_render.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**What changed:**
- Changed edge-tts WORLD same-syllable group rendering from note-by-note continuation rendering to one continuous group-level render.
- Regenerated all 120 first-TSV samples in `syntheticdataset/`.
- Updated the design document to describe the current word-onset plus vowel-sustain behavior.

**Code changes:**
- `render_score_to_word_unit_sample()` now renders a selected same-syllable group once at the group start.
- Continuation notes now keep metadata and target pitch labels, but they are not mixed as independent new attacks.
- Added group-level target F0 stitching across all TSV notes in the group.
- Added a word-onset plus vowel-center sustain source builder for group rendering.
- Added duration-aware group WORLD cache keys so different group lengths do not reuse the wrong analysis.
- Added a small crossfade to repeated vowel-center sustain loops.
- Added `render_mode` to note metadata so single notes, group starts, and group continuations can be inspected.

**Thought process:**
- The previous implementation reused the same word for continuation notes, but each continuation was still rendered as a separate note with its own source preparation and envelope.
- That behavior could sound disconnected and did not match the intended sung melisma behavior.
- A same-syllable pitch change should sound like one articulated word/syllable whose vowel carries later TSV pitches.

**Why this code/change was added:**
- The user reported that the audio sounded blurry and disconnected, and clarified that same-syllable pitch movement should be the first word attack followed by vowel pitch movement.

**Why the previous code needed to change:**
- The previous continuation handling still created separate note-level audio events.
- The previous group WORLD cache key did not include group duration, which could reuse an analysis generated for a different group length.

**Problems encountered:**
- Full TSV1 regeneration is slow because each sample uses WORLD analysis/resynthesis.
- PyWORLD still emits the known `pkg_resources` deprecation warning.
- macOS still emits the known OpenMP shared-memory warning.
- Pitch audit median stayed reasonable, but p90 has outliers on short/consonant-heavy regions after WORLD/TTS resynthesis.

**Solution:**
- Rendered same-syllable groups as a single continuous WORLD resynthesis span.
- Built the group source from the selected word onset plus repeated vowel-like center material.
- Protected continuation notes from independent rendering, decorative transitions, and noticeable detune.
- Recompiled the Python modules, ran a one-sample smoke test, regenerated the first TSV grid, and validated `syntheticdataset/`.

**Better result / user experience:**
- Same-syllable groups now better match the intended singing behavior: one word/syllable starts, then later notes move on the vowel.
- `syntheticdataset/` now contains 120 regenerated first-TSV samples using this group-level behavior.
- Metadata confirms 960 group starts and 1275 group continuations, with zero decorative transitions and zero noticeable detune on continuation notes.

**Remaining risks / TODOs:**
- The generated audio may still sound blurry because WORLD plus TTS word units is only a first local approximation.
- Short consonant-heavy words can still produce F0-tracking outliers.
- A better next step is to use more vowel-focused units for melisma groups or collect/derive cleaner sung vowel sustain units.
- Final quality still needs human listening before scaling beyond the first TSV.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**修改内容：**
- 将 edge-tts WORLD 的单吐字连续音渲染，从逐 note continuation 渲染改成一次 group-level 连续渲染。
- 重新生成 `syntheticdataset/` 中第一个 TSV 的全部 120 个样本。
- 更新设计文档，写清楚当前是 word onset 加 vowel sustain 的实现。

**代码变化：**
- `render_score_to_word_unit_sample()` 现在会在 selected same-syllable group 的第一个 note 处一次性渲染整组。
- continuation notes 仍保留 metadata 和目标 pitch label，但不会再作为独立新起音混入音频。
- 新增 group-level target F0 stitching，将组内所有 TSV notes 的目标 F0 曲线拼成连续曲线。
- 新增 word-onset plus vowel-center sustain source builder，用于 group 渲染。
- group WORLD cache key 加入 duration，避免不同长度的 group 复用错误 analysis。
- 给重复的 vowel-center sustain loop 加了轻微 crossfade。
- 在 note metadata 里新增 `render_mode`，方便区分 single note、group start 和 group continuation。

**思考流程：**
- 之前实现虽然让 continuation note 使用同一个 word，但每个 continuation 仍然是单独 source preparation 和 envelope。
- 这种行为听起来会断，不符合真正单吐字转多个音的歌唱感觉。
- 单吐字 pitch movement 应该像一个字/音节先发出来，后面的 TSV pitch 在同一个元音上移动。

**为什么添加这个代码/修改：**
- 用户反馈音频听起来模糊且没有连续性，并明确指出单吐字转音应该是第一个字出来后，后面的音在元音上转。

**为什么之前的代码需要修改：**
- 之前 continuation handling 仍然会产生多个独立 note-level audio events。
- 之前 group WORLD cache key 没有包含 group duration，可能让不同长度的 group 复用错误的 analysis。

**遇到的问题：**
- TSV1 全量重新生成较慢，因为每个样本都要做 WORLD analysis/resynthesis。
- PyWORLD 仍会输出已知的 `pkg_resources` deprecation warning。
- macOS 仍会输出已知的 OpenMP shared-memory warning。
- pitch audit 的 median 仍合理，但 WORLD/TTS 重合成后短词和辅音区域仍有 p90 outliers。

**解决方式：**
- 将 same-syllable groups 改为单次连续 WORLD resynthesis span。
- group source 使用选中 word 的 onset/attack 加重复的类元音中段。
- continuation notes 不再独立渲染，并继续禁止 decorative transitions 和 noticeable detune。
- 重新编译 Python 模块，跑单样本 smoke test，重新生成第一个 TSV grid，并验证 `syntheticdataset/`。

**带来的更好效果 / 用户体验：**
- 单吐字连续音现在更接近预期歌唱行为：一个字/音节起音，后续 note 在同一个元音上移动。
- `syntheticdataset/` 当前包含 120 个使用该 group-level 行为重新生成的第一个 TSV 样本。
- metadata 确认有 960 个 group starts 和 1275 个 group continuations，并且 continuation notes 上 decorative transitions 和 noticeable detune 都为 0。

**剩余风险 / TODO：**
- 当前音频仍可能偏模糊，因为 WORLD 加 TTS word units 只是第一版本地近似方案。
- 短词和辅音较多的 word 仍可能导致 F0 tracking outliers。
- 下一步更好的方向是让 melisma groups 优先使用更偏元音的 units，或者采集/生成更干净的 sung vowel sustain units。
- 扩展到第一个 TSV 之外前，仍需要人工试听确认质量。

## 2026-06-27 15:50 — Split Same-Syllable Group Source Into Onset And Vowel Core

### English

**Files changed:**
- `synth/sample_render.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**What changed:**
- Fixed same-syllable group source preparation so continuation notes use vowel-core sustain instead of repeated consonant/word attacks.
- Made same-syllable group unit choice prefer vowel-friendly words.
- Regenerated all 120 first-TSV samples in `syntheticdataset/`.

**Code changes:**
- Added `MELISMA_FRIENDLY_UNIT_KEYS` for group-unit selection.
- Added `_choose_melisma_unit()` so selected same-syllable groups prefer units such as `la`, `oh`, `hey`, `yeah`, `you`, `me`, `we`, `he`, and `she`.
- Removed the early group-source path that directly cropped the whole TTS word when the source was longer than the group.
- Added `_trim_to_active_region()` and `_split_onset_and_vowel_core()` to keep consonant-like onset material only at the group start.
- Updated `_prepare_group_source()` to build each group source as onset once plus repeated vowel core.

**Thought process:**
- WORLD can replace F0, but it does not understand phoneme boundaries.
- If the renderer feeds whole `la`-like material into every continuation area, the output can sound like `la-la-la` instead of `la-a-a`.
- The renderer must explicitly decide which source part is consonant/onset and which part is reusable vowel sustain.

**Why this code/change was added:**
- The user correctly identified that the same-syllable transition was still preserving too much consonant material and therefore did not sound like one syllable carried over multiple pitches.

**Why the previous code needed to change:**
- `_prepare_group_source()` returned a direct crop of the original word whenever the source was longer than the group, skipping the intended onset/vowel split.
- Group units could be hard or consonant-heavy words that are poor sources for melisma-like vowel sustain.

**Problems encountered:**
- Full first-TSV regeneration took longer because the refined group source reduces some WORLD analysis reuse.
- The known PyWORLD `pkg_resources` warning and macOS OpenMP shared-memory warning still appear.
- F0 audit still has p90 outliers around short or consonant-heavy regions, though the median remains stable.

**Solution:**
- Forced same-syllable groups to build sources from active audio, one short onset, and a repeated vowel core.
- Preferred vowel-friendly group units.
- Recompiled the code, ran a one-sample smoke test, regenerated the first TSV grid, validated the dataset, and audited pitch on one sample.

**Better result / user experience:**
- Same-syllable groups now follow the intended `La-a-a` behavior more closely.
- Current metadata shows 960 group starts and 1275 group continuations.
- Continuation notes still have zero decorative transitions and zero noticeable detune.
- Dataset validation passes after regeneration.

**Remaining risks / TODOs:**
- The onset/vowel split is heuristic, not a true phoneme aligner.
- Some words may still have imperfect vowel-core extraction.
- A stronger next step is to generate or collect dedicated sung vowel/syllable units with known onset and vowel regions.
- Human listening is still required before expanding generation beyond the first TSV.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `SyntheticVoiceDatasetDesign.md`
- `syntheticdataset/`
- `Creating_log.md`

**修改内容：**
- 修复 same-syllable group 的 source preparation，让 continuation notes 使用 vowel-core sustain，而不是重复辅音/整词起音。
- 让 same-syllable group 的 unit 选择优先使用更适合拖元音的词。
- 重新生成 `syntheticdataset/` 中第一个 TSV 的全部 120 个样本。

**代码变化：**
- 新增 `MELISMA_FRIENDLY_UNIT_KEYS`，用于 group-unit selection。
- 新增 `_choose_melisma_unit()`，让 selected same-syllable groups 优先使用 `la`、`oh`、`hey`、`yeah`、`you`、`me`、`we`、`he`、`she` 等 units。
- 移除 group source 在原始 TTS word 比 group 更长时直接裁剪整词的早退路径。
- 新增 `_trim_to_active_region()` 和 `_split_onset_and_vowel_core()`，让类辅音 onset material 只保留在 group 开头。
- 更新 `_prepare_group_source()`，让每个 group source 由一次 onset 加重复 vowel core 组成。

**思考流程：**
- WORLD 可以替换 F0，但它不理解 phoneme boundary。
- 如果 renderer 把完整的 `la` 类材料喂给 continuation 区域，输出会像 `la-la-la`，而不是 `la-a-a`。
- renderer 必须显式决定哪一段 source 是 consonant/onset，哪一段是可重复使用的 vowel sustain。

**为什么添加这个代码/修改：**
- 用户正确指出 same-syllable transition 仍然保留了太多辅音材料，因此不像一个音节跨多个 pitch 延续。

**为什么之前的代码需要修改：**
- `_prepare_group_source()` 在 source 比 group 长时会直接返回原始 word crop，跳过本该做的 onset/vowel split。
- group units 可能选到较硬或辅音很多的词，不适合作为 melisma-like vowel sustain。

**遇到的问题：**
- 第一个 TSV 全量生成变慢，因为更细的 group source 降低了一部分 WORLD analysis 复用。
- 已知的 PyWORLD `pkg_resources` warning 和 macOS OpenMP shared-memory warning 仍然存在。
- F0 audit 在短词或辅音较多区域仍有 p90 outliers，但 median 仍稳定。

**解决方式：**
- 强制 same-syllable groups 从 active audio、一次短 onset 和重复 vowel core 构造 source。
- 优先选择 vowel-friendly group units。
- 重新编译代码，跑单样本 smoke test，重新生成第一个 TSV grid，验证 dataset，并对一个样本做 pitch audit。

**带来的更好效果 / 用户体验：**
- same-syllable groups 现在更接近预期的 `La-a-a` 行为。
- 当前 metadata 显示有 960 个 group starts 和 1275 个 group continuations。
- continuation notes 上 decorative transitions 和 noticeable detune 仍然都是 0。
- 重新生成后 dataset validation 通过。

**剩余风险 / TODO：**
- 当前 onset/vowel split 是 heuristic，不是真正的 phoneme aligner。
- 某些 word 的 vowel-core extraction 仍可能不完美。
- 更强的下一步是生成或采集有明确 onset 和 vowel regions 的专门 sung vowel/syllable units。
- 扩展到第一个 TSV 之外前仍需要人工试听。

## 2026-06-27 16:35 — Segment Melisma Groups Into Start And Vowel-Only Continuations

### English

**Files changed:**
- `synth/sample_render.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Reworked same-syllable group rendering again because the previous group-level WORLD source could still sound like repeated syllable attacks.
- Generated only temporary validation audio instead of regenerating the full dataset.

**Code changes:**
- Same-syllable groups now render each TSV note segment separately.
- The first group note uses a source built from onset/consonant plus vowel core.
- Continuation group notes use vowel-core-only sources.
- Connected note boundaries are joined with short crossfades.
- Melisma-friendly unit selection is now restricted to `la`, `oh`, `hey`, and `yeah`.
- The onset/vowel split is more conservative, moving the continuation vowel core later in the source unit.

**Thought process:**
- WORLD changes F0, but it does not remove consonants or understand phoneme boundaries.
- The previous approach built one long group source and ran one WORLD resynthesis over it, which could still leak consonant-like material into later pitch regions.
- A more controllable first fix is explicit segmented rendering: start segment = syllable attack, continuation segments = vowel only.

**Why this code/change was added:**
- The user reported that a three-pitch `la` group still sounded like `la-la-la` instead of the intended `la-a-a`.

**Why the previous code needed to change:**
- The previous group-level renderer did not guarantee that later pitch regions were sourced only from the vowel core.
- The melisma unit list was still too broad, allowing words whose vowel centers are not stable enough for a clear continuation.

**Problems encountered:**
- The phoneme boundary is still heuristic because the current unit bank does not provide true phoneme timing.
- PyWORLD still emits the known `pkg_resources` warning, and macOS still emits the known OpenMP warning during validation generation.

**Solution:**
- Split the renderer into per-segment WORLD calls for same-syllable groups.
- Added a focused `/private/tmp/mml26_middle_melisma_check/audio.wav` clip using one `la` unit over three pitches for listening.
- Ran the public generator for one `female/middle/bright` sample in `/private/tmp/mml26_middle_one_sample` and validated it.

**Better result / user experience:**
- The intended behavior is now encoded directly: `La` appears once, then continuation notes are vowel-only.
- The temporary middle sample validates through the normal dataset validator.
- Metadata for the generated middle sample confirms group words are only `la`, `oh`, `hey`, and `yeah`, with no decorative transitions or noticeable detune on continuation notes.

**Remaining risks / TODOs:**
- The result still needs human listening because heuristic onset/vowel splitting can be wrong for some TTS voices.
- Dedicated sung vowel units or true phoneme alignment would be more reliable than splitting spoken TTS words.
- Full `syntheticdataset/` was not regenerated in this change; only temporary validation audio was generated.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 再次重做 same-syllable group 渲染，因为上一版 group-level WORLD source 仍可能听起来像重复起音。
- 这次没有重新生成完整 dataset，只生成了临时验证音频。

**代码变化：**
- same-syllable groups 现在按 TSV note segment 分段渲染。
- group 第一个 note 使用 onset/consonant 加 vowel core 构成的 source。
- group continuation notes 只使用 vowel-core-only source。
- 连续 note 边界用短 crossfade 连接。
- melisma-friendly unit selection 现在收窄到 `la`、`oh`、`hey`、`yeah`。
- onset/vowel split 更保守，把 continuation vowel core 移到 source 更靠后的位置。

**思考流程：**
- WORLD 可以改变 F0，但不会移除辅音，也不理解 phoneme boundary。
- 上一版方法是构造一个长 group source 后一次 WORLD resynthesis，仍可能把类辅音材料漏到后续 pitch 区域。
- 更可控的第一版修法是显式分段渲染：start segment = syllable attack，continuation segments = vowel only。

**为什么添加这个代码/修改：**
- 用户反馈三段 pitch 的 `la` group 仍然听起来像 `la-la-la`，而不是目标的 `la-a-a`。

**为什么之前的代码需要修改：**
- 之前的 group-level renderer 不能保证后续 pitch 区域只来自 vowel core。
- melisma unit 列表仍然太宽，允许了一些元音中心不够稳定的词进入连续转音。

**遇到的问题：**
- 当前 unit bank 没有真正的 phoneme timing，所以 phoneme boundary 仍然只能 heuristic 估计。
- 生成验证音频时 PyWORLD 仍有已知 `pkg_resources` warning，macOS 仍有已知 OpenMP warning。

**解决方式：**
- 对 same-syllable groups 改为逐 segment WORLD 调用。
- 生成一个专门听感验证 clip：`/private/tmp/mml26_middle_melisma_check/audio.wav`，使用一个 `la` unit 覆盖三个 pitch。
- 用 public generator 生成一个 `female/middle/bright` 临时样本到 `/private/tmp/mml26_middle_one_sample`，并通过 validator。

**带来的更好效果 / 用户体验：**
- 目标行为现在直接写进代码：`La` 只出现一次，continuation notes 只用元音。
- 临时 middle 样本可以通过正常 dataset validator。
- 生成的 middle 样本 metadata 确认 group words 只包含 `la`、`oh`、`hey`、`yeah`，continuation notes 上没有 decorative transitions 或 noticeable detune。

**剩余风险 / TODO：**
- 结果仍需要人工试听，因为 heuristic onset/vowel split 对某些 TTS voice 仍可能不准。
- 专门的 sung vowel units 或真正 phoneme alignment 会比切 spoken TTS words 更可靠。
- 本次没有重新生成完整 `syntheticdataset/`，只生成了临时验证音频。

## 2026-06-27 16:45 — Prevent Accidental Same-Word Reuse Outside Melisma Groups

### English

**Files changed:**
- `synth/sample_render.py`
- `synth/syllable_groups.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Fixed the real TSV-chain issue where non-melisma notes could still reuse the same word unit across adjacent pitches.
- Added debug controls for melisma selection fraction and melisma unit keys.
- Generated one temporary `female/middle/bright` sample for validation, without regenerating the full dataset.

**Code changes:**
- Removed the old phrase-level `repeat_span` unit reuse in `_choose_units_for_notes()`.
- Ordinary adjacent notes now choose a different unit from the previous note.
- Same-word reuse is allowed only for selected same-syllable group continuations.
- `plan_syllable_groups()` now accepts a `selection_fraction` argument while keeping the default at 20%.
- `scripts/build_synthetic_dataset.py` now supports `--melisma-selection-fraction` and `--melisma-unit-keys` for focused listening tests.

**Thought process:**
- The user correctly identified that 20% group selection is not the problem by itself.
- The bug was that the remaining unselected notes could still share the same word unit because phrase-level repetition was designed earlier for generic syllable variety.
- In the current design, a word spanning multiple pitches is a melisma and must be represented as a selected same-syllable group.

**Why this code/change was added:**
- To ensure the renderer does not accidentally create `La-La-La`-like repeated word behavior outside selected melisma groups.

**Why the previous code needed to change:**
- `repeat_span` allowed one word to cover several neighboring notes even when those notes were not marked as a same-syllable group.
- That made the metadata and sound disagree: the audio sounded like one repeated word across pitches, but the notes were not treated as melisma.

**Problems encountered:**
- The existing debug clip was correct, but the public TSV path still had older phrase-level word reuse.
- PyWORLD and macOS warnings still appear during temporary generation, but they do not block validation.

**Solution:**
- Made non-group adjacent notes choose different word units.
- Preserved same-word reuse only inside selected group starts/continuations.
- Generated `/private/tmp/mml26_middle_one_sample_fixed` with default 20% group selection and validated it.

**Better result / user experience:**
- The temporary sample passes validation.
- Metadata check shows `selected_group_count = 8`, `allowed_same_word_inside_group_edges = 12`, and `same_word_outside_group_violations = 0`.
- This makes the 20% policy meaningful: only selected groups become `La-a-a`; unselected notes become separate words/syllables.

**Remaining risks / TODOs:**
- Full `syntheticdataset/` was not regenerated after this fix.
- The next listening step should use `/private/tmp/mml26_middle_one_sample_fixed/score_1_female_middle_bright_v00/audio.wav`.
- If the sample now sounds correct, regenerate the first TSV dataset with this fixed assignment logic.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `synth/syllable_groups.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 修复 TSV 生成链路里的真正问题：非 melisma notes 仍可能在相邻 pitch 上复用同一个 word unit。
- 增加 melisma selection fraction 和 melisma unit keys 的 debug 控制参数。
- 只生成了一个临时 `female/middle/bright` 样本用于验证，没有重新生成完整 dataset。

**代码变化：**
- 移除 `_choose_units_for_notes()` 里旧的 phrase-level `repeat_span` unit 复用。
- 普通相邻 notes 现在会选择和前一个 note 不同的 unit。
- 只有 selected same-syllable group continuations 允许复用同一个 word。
- `plan_syllable_groups()` 现在接受 `selection_fraction` 参数，同时默认仍保持 20%。
- `scripts/build_synthetic_dataset.py` 新增 `--melisma-selection-fraction` 和 `--melisma-unit-keys`，用于集中听感测试。

**思考流程：**
- 用户正确指出 20% group selection 本身不是问题。
- 真正 bug 是剩下没有被选成 group 的 notes，仍然可能因为早期 generic syllable variety 逻辑复用同一个 word unit。
- 在当前设计中，一个 word 跨多个 pitch 就是 melisma，必须被表示为 selected same-syllable group。

**为什么添加这个代码/修改：**
- 确保 renderer 不会在 selected melisma groups 之外意外制造 `La-La-La` 式的重复 word 行为。

**为什么之前的代码需要修改：**
- `repeat_span` 允许一个 word 覆盖多个相邻 note，即使这些 note 没有被标记为 same-syllable group。
- 这会让 metadata 和听感不一致：音频像一个词跨 pitch 重复，但 notes 并没有按 melisma 处理。

**遇到的问题：**
- 之前 debug clip 是对的，但 public TSV path 仍保留旧的 phrase-level word reuse。
- 临时生成时 PyWORLD 和 macOS warning 仍会出现，但不阻止 validation。

**解决方式：**
- 让非 group 的相邻 notes 必须选择不同 word units。
- 只在 selected group start/continuation 内保留 same-word reuse。
- 使用默认 20% group selection 生成 `/private/tmp/mml26_middle_one_sample_fixed` 并通过验证。

**带来的更好效果 / 用户体验：**
- 临时样本通过 validator。
- metadata 检查显示 `selected_group_count = 8`、`allowed_same_word_inside_group_edges = 12`、`same_word_outside_group_violations = 0`。
- 这样 20% policy 才有明确意义：只有 selected groups 会成为 `La-a-a`，未选中的 notes 会是不同 word/syllable。

**剩余风险 / TODO：**
- 这次修复后还没有重新生成完整 `syntheticdataset/`。
- 下一步听感验证应使用 `/private/tmp/mml26_middle_one_sample_fixed/score_1_female_middle_bright_v00/audio.wav`。
- 如果该样本听起来正确，再用这个 fixed assignment logic 重新生成第一个 TSV dataset。

## 2026-06-27 16:57 — Increase Default Melisma Selection To 30 Percent

### English

**Files changed:**
- `synth/syllable_groups.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Increased the default same-syllable group selection fraction from 20% to 30%.
- Generated one temporary `female/middle/bright` sample for listening validation.

**Code changes:**
- Changed `GROUP_SELECTION_FRACTION` from `0.20` to `0.30`.
- Updated the design document so the unselected remainder is described as 70% instead of 80%.

**Thought process:**
- The user reported that the default 20% made continuous single-syllable pitch movement too rare to hear.
- Since accidental same-word reuse outside groups is already prevented, increasing the selected-group fraction should make true melisma more audible without reintroducing `La-La-La` behavior.

**Why this code/change was added:**
- To make same-syllable continuous pitch movement appear more often in generated samples.

**Why the previous code needed to change:**
- The previous 20% default was too sparse for listening checks and likely too sparse for useful training variety.

**Problems encountered:**
- The known PyWORLD `pkg_resources` warning and macOS OpenMP warning still appear during temporary generation.

**Solution:**
- Updated the default fraction to 30%.
- Recompiled the Python modules.
- Generated `/private/tmp/mml26_middle_one_sample_30pct` and validated it.

**Better result / user experience:**
- The temporary sample passes validation.
- Metadata shows `candidate_group_count = 41`, `selected_group_count = 12`, and `continuation_note_count = 14`.
- Metadata still shows `same_word_outside_group_violations = 0`, so the 30% increase does not reintroduce accidental repeated-word behavior.

**Remaining risks / TODOs:**
- Full `syntheticdataset/` was not regenerated after this change.
- Listen to `/private/tmp/mml26_middle_one_sample_30pct/score_1_female_middle_bright_v00/audio.wav`.
- If the 30% density sounds right, regenerate the first TSV dataset with the new default.

### 中文

**修改文件：**
- `synth/syllable_groups.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 将默认 same-syllable group selection fraction 从 20% 提高到 30%。
- 生成了一个临时 `female/middle/bright` 样本用于听感验证。

**代码变化：**
- 将 `GROUP_SELECTION_FRACTION` 从 `0.20` 改为 `0.30`。
- 更新设计文档，把未选中的剩余比例从 80% 改为 70%。

**思考流程：**
- 用户反馈默认 20% 下连续单吐字 pitch movement 太少，听不太出来。
- 因为 selected groups 之外的意外同词复用已经被禁止，提高 selected-group fraction 可以让真正 melisma 更明显，同时不会重新引入 `La-La-La` 问题。

**为什么添加这个代码/修改：**
- 让生成样本里 same-syllable 连续 pitch movement 出现得更频繁。

**为什么之前的代码需要修改：**
- 之前 20% 默认值对听感检查太稀疏，对训练多样性可能也偏少。

**遇到的问题：**
- 临时生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP warning。

**解决方式：**
- 将默认比例更新为 30%。
- 重新编译 Python 模块。
- 生成 `/private/tmp/mml26_middle_one_sample_30pct` 并通过验证。

**带来的更好效果 / 用户体验：**
- 临时样本通过验证。
- metadata 显示 `candidate_group_count = 41`、`selected_group_count = 12`、`continuation_note_count = 14`。
- metadata 仍显示 `same_word_outside_group_violations = 0`，说明 30% 不会重新引入意外重复 word 行为。

**剩余风险 / TODO：**
- 这次修改后没有重新生成完整 `syntheticdataset/`。
- 需要试听 `/private/tmp/mml26_middle_one_sample_30pct/score_1_female_middle_bright_v00/audio.wav`。
- 如果 30% 的密度听起来合适，再用新默认值重新生成第一个 TSV dataset。

## 2026-06-27 17:06 — Slow Vibrato And Increase Decorative Transition Density

### English

**Files changed:**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Made vibrato slower and limited it to relatively long notes.
- Increased decorative transition density to 50% of eligible long notes.
- Generated one temporary `female/middle/bright` sample for validation.

**Code changes:**
- Added `VIBRATO_MIN_NOTE_DURATION_S = 1.20`.
- Changed vibrato rate sampling from `4.2-6.8 Hz` to `3.4-4.8 Hz`.
- Reduced vibrato depth ranges and delayed vibrato onset to about `0.35-0.65 s`.
- Replaced policy-specific transition fractions with `TRANSITION_TARGET_ELIGIBLE_FRACTION = 0.50`.
- Added vibrato and transition eligible-fraction fields to `expression_summary`.

**Thought process:**
- The user reported vibrato sounded too fast and appeared on notes that were not long enough.
- The user also reported decorative transitions were too rare to hear.
- The safest interpretation is to keep transition eligibility strict, but raise the fraction among eligible notes.

**Why this code/change was added:**
- To make vibrato sound less shaky and make decorative scoops/fall-ins audible more often.

**Why the previous code needed to change:**
- Vibrato could trigger on notes as short as 0.45 seconds with rates up to 6.8 Hz.
- Decorative transitions were capped by low policy fractions and an eligible-note cap of 20%, so they were sparse.

**Problems encountered:**
- PyWORLD and macOS OpenMP warnings still appear during temporary sample generation.

**Solution:**
- Restricted vibrato to notes at least 1.2 seconds long.
- Lowered vibrato speed and depth ranges.
- Set decorative transition target and cap to 50% of eligible long notes.
- Recompiled the code, generated `/private/tmp/mml26_middle_one_sample_expr`, and validated it.

**Better result / user experience:**
- The temporary sample passes validation.
- Metadata shows `transition_count = 3`, `eligible_transition_count = 6`, and `transition_eligible_fraction = 0.5`.
- Metadata shows `vibrato_count = 2`, `eligible_vibrato_count = 8`, `short_vibrato_count = 0`, and vibrato rates around `4.05-4.71 Hz`.

**Remaining risks / TODOs:**
- Full `syntheticdataset/` was not regenerated after this change.
- Listen to `/private/tmp/mml26_middle_one_sample_expr/score_1_female_middle_bright_v00/audio.wav`.
- If the expression balance sounds right, regenerate the first TSV dataset with these updated expression rules.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 让 vibrato 更慢，并且只在相对长的音上出现。
- 将装饰性转音密度提高到 eligible long notes 的 50%。
- 生成了一个临时 `female/middle/bright` 样本用于验证。

**代码变化：**
- 新增 `VIBRATO_MIN_NOTE_DURATION_S = 1.20`。
- 将 vibrato rate 采样从 `4.2-6.8 Hz` 改为 `3.4-4.8 Hz`。
- 降低 vibrato depth 范围，并将 vibrato onset 延后到约 `0.35-0.65 s`。
- 用 `TRANSITION_TARGET_ELIGIBLE_FRACTION = 0.50` 替代原来按 policy 的较低 transition fractions。
- 在 `expression_summary` 中加入 vibrato 和 transition eligible-fraction 字段。

**思考流程：**
- 用户反馈 vibrato 太快，并且不应该出现在不够长的音上。
- 用户也反馈装饰性转音太少，基本听不到。
- 更安全的理解是保持 transition eligibility 仍然严格，但提高 eligible notes 中的触发比例。

**为什么添加这个代码/修改：**
- 让 vibrato 听起来不那么抖，并让 decorative scoops/fall-ins 更常被听到。

**为什么之前的代码需要修改：**
- 之前 vibrato 可在短至 0.45 秒的音上触发，速度最高到 6.8 Hz。
- 之前装饰性转音受较低 policy fraction 和 20% eligible-note cap 限制，因此太稀疏。

**遇到的问题：**
- 临时样本生成时仍有 PyWORLD 和 macOS OpenMP warning。

**解决方式：**
- 将 vibrato 限制到至少 1.2 秒的长音。
- 降低 vibrato 速度和深度范围。
- 将装饰性转音目标和上限设为 eligible long notes 的 50%。
- 重新编译代码，生成 `/private/tmp/mml26_middle_one_sample_expr`，并通过验证。

**带来的更好效果 / 用户体验：**
- 临时样本通过验证。
- metadata 显示 `transition_count = 3`、`eligible_transition_count = 6`、`transition_eligible_fraction = 0.5`。
- metadata 显示 `vibrato_count = 2`、`eligible_vibrato_count = 8`、`short_vibrato_count = 0`，vibrato rate 约为 `4.05-4.71 Hz`。

**剩余风险 / TODO：**
- 这次修改后没有重新生成完整 `syntheticdataset/`。
- 需要试听 `/private/tmp/mml26_middle_one_sample_expr/score_1_female_middle_bright_v00/audio.wav`。
- 如果表达效果平衡合适，再用这些更新后的 expression rules 重新生成第一个 TSV dataset。

## 2026-06-27 17:12 — Lower Transition Threshold And Slow Vibrato Again

### English

**Files changed:**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Lowered decorative transition eligibility from 1500 ms to 1000 ms.
- Slowed vibrato rate again.
- Generated one temporary `female/middle/bright` validation sample.

**Code changes:**
- Changed `TRANSITION_MIN_NOTE_DURATION_S` from `1.50` to `1.00`.
- Changed vibrato rate sampling from `3.4-4.8 Hz` to `2.6-3.6 Hz`.
- Updated the design document and example metadata value.

**Thought process:**
- The user clarified that transitions should be allowed on notes longer than about 1000 ms.
- The user also reported that vibrato still sounded too fast, so the rate range needed another downward adjustment.

**Why this code/change was added:**
- To make decorative transitions happen on more moderately long notes and make vibrato audibly slower.

**Why the previous code needed to change:**
- The 1500 ms transition threshold was too strict.
- The `3.4-4.8 Hz` vibrato range still sounded too fast for the current WORLD/TTS rendering.

**Problems encountered:**
- The known PyWORLD `pkg_resources` warning and macOS OpenMP warning still appear during temporary generation.

**Solution:**
- Updated the constants in `synth/ornaments.py`.
- Recompiled the code.
- Generated and validated `/private/tmp/mml26_middle_one_sample_expr_1000ms`.

**Better result / user experience:**
- The temporary sample passes validation.
- Metadata shows `transition_min_note_duration_s = 1.0`, `eligible_transition_count = 10`, `transition_count = 5`, and `transition_eligible_fraction = 0.5`.
- Metadata shows vibrato rates around `2.88-3.18 Hz`, with zero short-note vibrato.

**Remaining risks / TODOs:**
- Full `syntheticdataset/` was not regenerated after this change.
- Listen to `/private/tmp/mml26_middle_one_sample_expr_1000ms/score_1_female_middle_bright_v00/audio.wav`.
- If this feels right, regenerate the first TSV dataset with these updated expression rules.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 将装饰性转音 eligibility 从 1500 ms 降到 1000 ms。
- 再次降低 vibrato 速度。
- 生成了一个临时 `female/middle/bright` 验证样本。

**代码变化：**
- 将 `TRANSITION_MIN_NOTE_DURATION_S` 从 `1.50` 改为 `1.00`。
- 将 vibrato rate 采样从 `3.4-4.8 Hz` 改为 `2.6-3.6 Hz`。
- 更新设计文档和示例 metadata 值。

**思考流程：**
- 用户明确说转音允许条件大于约 1000 ms 就可以。
- 用户也反馈 vibrato 仍然太快，因此 rate range 需要再下调一档。

**为什么添加这个代码/修改：**
- 让装饰性转音出现在更多中长音上，并让 vibrato 听起来明显更慢。

**为什么之前的代码需要修改：**
- 1500 ms 的 transition threshold 太严格。
- `3.4-4.8 Hz` 的 vibrato 范围对当前 WORLD/TTS 渲染仍然听起来太快。

**遇到的问题：**
- 临时生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP warning。

**解决方式：**
- 更新 `synth/ornaments.py` 中的常量。
- 重新编译代码。
- 生成并验证 `/private/tmp/mml26_middle_one_sample_expr_1000ms`。

**带来的更好效果 / 用户体验：**
- 临时样本通过验证。
- metadata 显示 `transition_min_note_duration_s = 1.0`、`eligible_transition_count = 10`、`transition_count = 5`、`transition_eligible_fraction = 0.5`。
- metadata 显示 vibrato rate 约为 `2.88-3.18 Hz`，且短音 vibrato 为 0。

**剩余风险 / TODO：**
- 这次修改后没有重新生成完整 `syntheticdataset/`。
- 需要试听 `/private/tmp/mml26_middle_one_sample_expr_1000ms/score_1_female_middle_bright_v00/audio.wav`。
- 如果这个听感合适，再用这些更新后的 expression rules 重新生成第一个 TSV dataset。

## 2026-06-27 17:20 — Lower Transition Threshold To 700ms And Slow Vibrato Further

### English

**Files changed:**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Lowered decorative transition eligibility from 1000 ms to 700 ms.
- Slowed vibrato rate further.
- Tightened transition sampling so odd eligible-note counts round closer to 50%.
- Generated one temporary `female/middle/bright` validation sample.

**Code changes:**
- Changed `TRANSITION_MIN_NOTE_DURATION_S` from `1.00` to `0.70`.
- Changed vibrato rate sampling from `2.6-3.6 Hz` to `1.8-2.6 Hz`.
- Changed the transition cap rounding from floor to round.
- Continued transition selection over extra candidates when a sampled transition resolves to `none`.
- Aligned `eligible_transition_count` in metadata with the actual planner eligibility rules.

**Thought process:**
- The user clarified that 700 ms is enough for transition eligibility.
- The user also said vibrato was still too fast, so the rate range needed another large reduction.
- Metadata should report the same eligibility definition that the planner uses, otherwise the 50% target looks inconsistent.

**Why this code/change was added:**
- To make decorative transitions more common on medium-length notes and make vibrato audibly slower.

**Why the previous code needed to change:**
- The 1000 ms transition threshold still excluded too many notes.
- The `2.6-3.6 Hz` vibrato range still sounded too fast.
- The previous summary counted duration-eligible notes that were later blocked by melisma continuation or noticeable detune.

**Problems encountered:**
- An initial validation sample showed the transition fraction slightly below 50% because odd eligible counts were floored and some sampled transitions resolved to `none`.
- The known PyWORLD `pkg_resources` warning and macOS OpenMP warning still appear during temporary generation.

**Solution:**
- Lowered the threshold and vibrato rate range.
- Used rounded eligible caps and replacement candidate scanning for transition sampling.
- Regenerated and validated `/private/tmp/mml26_middle_one_sample_expr_700ms`.

**Better result / user experience:**
- The temporary sample passes validation.
- Metadata shows `transition_min_note_duration_s = 0.7`, `eligible_transition_count = 23`, `transition_count = 12`, and `transition_eligible_fraction = 0.522`.
- Metadata shows vibrato rates around `1.83-2.55 Hz`, with zero short-note vibrato.

**Remaining risks / TODOs:**
- Full `syntheticdataset/` was not regenerated after this change.
- Listen to `/private/tmp/mml26_middle_one_sample_expr_700ms/score_1_female_middle_bright_v00/audio.wav`.
- If this feels right, regenerate the first TSV dataset with these updated expression rules.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 将装饰性转音 eligibility 从 1000 ms 降到 700 ms。
- 进一步降低 vibrato 速度。
- 调整 transition sampling，让 eligible note 数为奇数时更接近 50%。
- 生成了一个临时 `female/middle/bright` 验证样本。

**代码变化：**
- 将 `TRANSITION_MIN_NOTE_DURATION_S` 从 `1.00` 改为 `0.70`。
- 将 vibrato rate 采样从 `2.6-3.6 Hz` 改为 `1.8-2.6 Hz`。
- 将 transition cap rounding 从 floor 改为 round。
- 当随机到的 transition 最后变成 `none` 时，会继续扫描额外候选补足数量。
- 将 metadata 中的 `eligible_transition_count` 和 planner 实际 eligibility 规则对齐。

**思考流程：**
- 用户明确 700 ms 就可以作为转音 eligibility 门槛。
- 用户也说明 vibrato 仍然太快，因此 rate range 需要大幅再降一档。
- metadata 应该报告和 planner 一致的 eligibility 定义，否则 50% target 看起来会不一致。

**为什么添加这个代码/修改：**
- 让装饰性转音在更多中等长度的音上出现，并让 vibrato 明显更慢。

**为什么之前的代码需要修改：**
- 1000 ms 的 transition threshold 仍然排除了太多 note。
- `2.6-3.6 Hz` 的 vibrato 范围仍然听起来太快。
- 之前 summary 会统计一些只满足时长但后来被 melisma continuation 或 noticeable detune 阻止的 notes。

**遇到的问题：**
- 初始验证样本显示 transition fraction 略低于 50%，因为奇数 eligible count 被 floor，并且部分随机 transition 最后会变成 `none`。
- 临时生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP warning。

**解决方式：**
- 降低 threshold 和 vibrato rate range。
- transition sampling 使用 rounded eligible cap，并在候选 transition 变成 `none` 时继续扫描补足。
- 重新生成并验证 `/private/tmp/mml26_middle_one_sample_expr_700ms`。

**带来的更好效果 / 用户体验：**
- 临时样本通过验证。
- metadata 显示 `transition_min_note_duration_s = 0.7`、`eligible_transition_count = 23`、`transition_count = 12`、`transition_eligible_fraction = 0.522`。
- metadata 显示 vibrato rate 约为 `1.83-2.55 Hz`，且短音 vibrato 为 0。

**剩余风险 / TODO：**
- 这次修改后没有重新生成完整 `syntheticdataset/`。
- 需要试听 `/private/tmp/mml26_middle_one_sample_expr_700ms/score_1_female_middle_bright_v00/audio.wav`。
- 如果这个听感合适，再用这些更新后的 expression rules 重新生成第一个 TSV dataset。

## 2026-06-27 20:19 — Make Vibrato Slower And Shallower

### English

**Files changed:**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Re-tuned vibrato so it behaves more like a very slow, shallow long-note pitch movement in the current WORLD plus TTS-unit renderer.
- Raised the minimum note duration for vibrato eligibility.
- Updated the design document to match the new renderer-specific vibrato behavior.

**Code changes:**
- Changed `VIBRATO_MIN_NOTE_DURATION_S` from `1.20` to `1.50`.
- Changed vibrato rate sampling from `1.2-1.6 Hz` to `0.65-0.95 Hz`.
- Reduced vibrato depth ranges to `2-5`, `3-8`, and `5-12` cents for light, normal, and expressive policies.
- Reduced the conservative vibrato upper depth cap to `7` cents.
- Delayed vibrato onset to roughly `0.55-0.95 s`, capped by 70% of note duration.
- Increased vibrato fade-in from about `80 ms` to about `200 ms`.

**Thought process:**
- The user reported that the current vibrato still sounded too fast and unlike human singing.
- Although typical measured human vibrato can be faster, the current TTS-unit plus WORLD resynthesis chain makes fast periodic modulation sound artificial.
- The safer first correction is to use a very slow and shallow pitch movement only on longer notes, then validate by listening.

**Why this code/change was added:**
- To remove the mechanical fast-shaking impression from generated long notes.
- To make vibrato a subtle expression detail instead of a dominant artifact.

**Why the previous code needed to change:**
- The previous `1.2-1.6 Hz` range still sounded too fast in the generated sample.
- Vibrato could appear on 1.2-second notes, leaving too little stable vowel time before modulation.
- The 80 ms fade-in could make vibrato onset feel abrupt even when the rate was slow.

**Problems encountered:**
- The perceived speed of vibrato in this renderer does not match textbook vocal-vibrato expectations.
- Raising the duration threshold too high would leave almost no vibrato examples in `scores/1.tsv`.

**Solution:**
- Checked the duration distribution of `scores/1.tsv`.
- Chose `1.50 s` as the new threshold because the first TSV still has enough eligible long notes for listening tests.
- Lowered rate, depth, and onset abruptness together instead of changing only one parameter.

**Better result / user experience:**
- The new middle sample should sound less like a synthetic periodic wobble.
- Metadata clearly shows the slower vibrato rate and longer eligibility threshold.
- The design document now explains that these values are renderer-specific listening choices.
- Generated and validated `/private/tmp/mml26_middle_one_sample_vibrato_slow`.
- Metadata shows `vibrato_min_note_duration_s = 1.5`, `eligible_vibrato_count = 6`, `vibrato_count = 1`, and vibrato rate around `0.767 Hz`.

**Remaining risks / TODOs:**
- Listen to `/private/tmp/mml26_middle_one_sample_vibrato_slow/score_1_female_middle_bright_v00/audio.wav`.
- If the result still sounds artificial, consider disabling periodic vibrato for ordinary styles and keeping only slow drift.
- Full `syntheticdataset/` has not been regenerated after this change.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 重新调整 vibrato，让它在当前 WORLD + TTS 单词素材渲染器里更像很慢、很浅的长音音高浮动。
- 提高 vibrato 的最短音符时长门槛。
- 更新设计文档，使文档和当前代码中的 renderer-specific vibrato 行为一致。

**代码变化：**
- 将 `VIBRATO_MIN_NOTE_DURATION_S` 从 `1.20` 改为 `1.50`。
- 将 vibrato rate 采样从 `1.2-1.6 Hz` 改为 `0.65-0.95 Hz`。
- 将 light、normal、expressive 的 vibrato depth 范围分别降到 `2-5`、`3-8`、`5-12` cents。
- 将 conservative vibrato 的 depth 上限降到 `7` cents。
- 将 vibrato onset 延后到约 `0.55-0.95 s`，并限制在 note 时长的 70% 内。
- 将 vibrato fade-in 从约 `80 ms` 增加到约 `200 ms`。

**思考流程：**
- 用户反馈当前 vibrato 仍然太快，并且不像人唱歌。
- 虽然真实人声测量中的 vibrato 频率可能更高，但当前 TTS 单词素材 + WORLD 重合成链路会让较快周期调制听起来很机械。
- 更安全的第一步是只在更长的音上使用很慢、很浅的音高浮动，然后通过试听判断。

**为什么添加这个代码/修改：**
- 去掉生成长音里机械快速抖动的感觉。
- 让 vibrato 变成轻微表现细节，而不是主导听感的 artifact。

**为什么之前的代码需要修改：**
- 之前 `1.2-1.6 Hz` 的范围在生成样本里仍然听起来太快。
- vibrato 可能出现在 1.2 秒的音上，导致稳定元音区域太短。
- 80 ms 的 fade-in 可能让 vibrato 进入时显得突兀，即使频率已经降低。

**遇到的问题：**
- 这个渲染器里 vibrato 的主观速度和教科书式人声 vibrato 预期不完全一致。
- 如果把时长门槛提得太高，`scores/1.tsv` 里几乎没有足够的 vibrato 样本可听。

**解决方式：**
- 检查了 `scores/1.tsv` 的音符时长分布。
- 选择 `1.50 s` 作为新门槛，因为第一个 TSV 仍然有足够长音用于试听。
- 同时降低 rate、depth，并让 onset 更平滑，而不是只改一个参数。

**带来的更好效果 / 用户体验：**
- 新的 middle 样本应该更少出现合成器式周期抖动。
- metadata 会清楚显示更慢的 vibrato rate 和更长的 eligibility threshold。
- 设计文档也说明这些参数是针对当前 renderer 听感选择的。
- 已生成并验证 `/private/tmp/mml26_middle_one_sample_vibrato_slow`。
- metadata 显示 `vibrato_min_note_duration_s = 1.5`、`eligible_vibrato_count = 6`、`vibrato_count = 1`，vibrato rate 约 `0.767 Hz`。

**剩余风险 / TODO：**
- 需要试听 `/private/tmp/mml26_middle_one_sample_vibrato_slow/score_1_female_middle_bright_v00/audio.wav`。
- 如果结果仍然人工感强，可以考虑普通 style 禁用周期性 vibrato，只保留慢速 drift。
- 完整 `syntheticdataset/` 尚未在这次修改后重新生成。

## 2026-06-27 21:10 — Remove Hey And Oh From Melisma Units

### English

**Files changed:**
- `synth/sample_render.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Removed `hey` and `oh` from the default same-syllable / melisma unit choices.
- Left ordinary single-note word-unit selection unchanged for now.
- Updated CLI help and the design document to avoid recommending `hey` or `oh` for same-syllable groups.

**Code changes:**
- Changed `MELISMA_FRIENDLY_UNIT_KEYS` from `hey, la, oh, yeah` to `la, yeah`.
- Changed the `--melisma-unit-keys` help example from `la,oh` to `la,yeah`.
- Updated the renderer design note to say that the current TTS/WORLD renderer should not use `hey` or `oh` for same-syllable groups.
- Generated and validated `/private/tmp/mml26_middle_no_hey_oh_melisma`.

**Thought process:**
- The user identified the fast wobble as happening when one utterance is split across several TSV pitches, especially with `hey` and `oh`.
- This indicates a same-syllable group artifact, not code-level vibrato.
- `hey` and `oh` contain internal vowel movement, so splitting them across multiple pitches can sound like a fast artificial wobble.

**Why this code/change was added:**
- To stop the most suspicious words from being used in multi-pitch same-syllable rendering.
- To keep the change narrow while preserving the rest of the current generator.

**Why the previous code needed to change:**
- The previous melisma unit defaults included `hey` and `oh`, which are not stable enough for the current TTS/WORLD multi-pitch rendering.

**Problems encountered:**
- `hey` and `oh` can still appear as ordinary single-note words because the user only requested not using them for the current problematic behavior.
- The known PyWORLD `pkg_resources` warning and macOS OpenMP shared-memory warning still appear during temporary generation.

**Solution:**
- Removed only `hey` and `oh` from the default melisma-friendly list.
- Generated a middle probe sample and checked metadata for group word usage.

**Better result / user experience:**
- The new sample has `melisma_unit_keys = ['la', 'yeah']`.
- Metadata shows `hey_or_oh_group_notes = 0`.
- Validation passed for `/private/tmp/mml26_middle_no_hey_oh_melisma`.

**Remaining risks / TODOs:**
- Listen to `/private/tmp/mml26_middle_no_hey_oh_melisma/score_1_female_middle_bright_v00/audio.wav`.
- If `yeah` still causes the same artifact, restrict melisma units to `la` only.
- If `hey` or `oh` are also bad as ordinary single notes, add a separate global blocklist later.
- Full `syntheticdataset/` has not been regenerated after this change.

### 中文

**修改文件：**
- `synth/sample_render.py`
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 从默认 same-syllable / melisma unit 选择中移除 `hey` 和 `oh`。
- 暂时不改变普通 single-note word-unit selection。
- 更新 CLI help 和设计文档，避免继续推荐 `hey` 或 `oh` 用于 same-syllable group。

**代码变化：**
- 将 `MELISMA_FRIENDLY_UNIT_KEYS` 从 `hey, la, oh, yeah` 改为 `la, yeah`。
- 将 `--melisma-unit-keys` 的 help 示例从 `la,oh` 改为 `la,yeah`。
- 更新 renderer 设计说明，明确当前 TTS/WORLD renderer 不应使用 `hey` 或 `oh` 做 same-syllable group。
- 已生成并验证 `/private/tmp/mml26_middle_no_hey_oh_melisma`。

**思考流程：**
- 用户确认快速抖动发生在一次吐字被拆成多个 TSV pitch 的地方，尤其是 `hey` 和 `oh`。
- 这说明问题是 same-syllable group artifact，而不是代码里的 vibrato。
- `hey` 和 `oh` 自身带有元音内部移动，把它们拆到多个 pitch 上会听起来像快速人工抖动。

**为什么添加这个代码/修改：**
- 阻止最可疑的词用于 multi-pitch same-syllable rendering。
- 保持修改范围很窄，同时保留当前 generator 的其他行为。

**为什么之前的代码需要修改：**
- 之前 melisma unit 默认包含 `hey` 和 `oh`，它们对当前 TTS/WORLD multi-pitch rendering 来说不够稳定。

**遇到的问题：**
- `hey` 和 `oh` 仍可能作为普通 single-note word 出现，因为用户这次只要求先处理当前有问题的行为。
- 临时生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP shared-memory warning。

**解决方式：**
- 只从默认 melisma-friendly list 里移除 `hey` 和 `oh`。
- 生成 middle probe sample，并检查 metadata 中的 group word usage。

**带来的更好效果 / 用户体验：**
- 新样本的 `melisma_unit_keys = ['la', 'yeah']`。
- metadata 显示 `hey_or_oh_group_notes = 0`。
- `/private/tmp/mml26_middle_no_hey_oh_melisma` 通过 validation。

**剩余风险 / TODO：**
- 需要试听 `/private/tmp/mml26_middle_no_hey_oh_melisma/score_1_female_middle_bright_v00/audio.wav`。
- 如果 `yeah` 仍然造成同类 artifact，再把 melisma units 限制成只用 `la`。
- 如果 `hey` 或 `oh` 作为普通 single note 也不好听，后续再加单独的全局 blocklist。
- 完整 `syntheticdataset/` 尚未在这次修改后重新生成。

## 2026-06-27 21:15 — Exclude Very Short Notes From Melisma Groups

### English

**Files changed:**
- `synth/syllable_groups.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Added a minimum duration requirement for same-syllable / melisma group candidates.
- Very short notes are no longer allowed to become continuation notes inside one utterance split across several pitches.
- Generated and validated a new middle probe sample.

**Code changes:**
- Added `MIN_GROUP_NOTE_DURATION_S = 0.180`.
- Added this value to `syllable_group_summary` metadata.
- Updated `_is_valid_stepwise_group()` so every note in a candidate group must be at least `180 ms`.
- Updated the design document candidate rule with `each note duration >= 180 ms`.

**Thought process:**
- The user showed a concrete `la` group where the first note lasted about `702 ms` but the continuation note lasted only about `110 ms`.
- Since vibrato was zero, the fast wobble was coming from same-syllable group rendering, not from vibrato.
- In the current TTS/WORLD renderer, a 100-150 ms continuation pitch is too short to sound like a stable sung pitch and tends to become a fast wobble artifact.

**Why this code/change was added:**
- To prevent short decorative-looking TSV notes from being rendered as the continuation of one sustained syllable.
- To keep the fix at the candidate-selection level instead of adding another risky audio-rendering workaround.

**Why the previous code needed to change:**
- The previous group candidate rule only checked connected timing, monotonic pitch direction, interval size, and max group size.
- It could select a group where one note was too short to carry a stable continuation vowel.

**Problems encountered:**
- Short notes still need to remain in `score.tsv`; they should not be deleted or relabeled.
- Lowering melisma selection globally would hide the issue but would not define which groups are musically unsafe.

**Solution:**
- Kept all notes unchanged, but excluded groups where any member note is shorter than `180 ms`.
- Generated `/private/tmp/mml26_middle_no_short_melisma` and checked metadata.

**Better result / user experience:**
- The user-shown index `8/9` pair is no longer a same-syllable group in the new sample.
- Metadata shows `min_group_note_duration_s = 0.18`.
- Metadata shows `groups_with_short_notes_lt_180ms = 0` and the shortest selected group note is about `210 ms`.
- Validation passed for `/private/tmp/mml26_middle_no_short_melisma`.

**Remaining risks / TODOs:**
- Listen to `/private/tmp/mml26_middle_no_short_melisma/score_1_female_middle_bright_v00/audio.wav`.
- If selected groups with `yeah` still sound unstable, restrict melisma units to `la` only.
- If `180 ms` is still too short, raise the threshold to `220-250 ms`.
- Full `syntheticdataset/` has not been regenerated after this change.

### 中文

**修改文件：**
- `synth/syllable_groups.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 为 same-syllable / melisma group candidates 增加最短时长要求。
- 很短的 note 不再允许作为“一次吐字拆成多个 pitch”的 continuation note。
- 生成并验证了新的 middle probe sample。

**代码变化：**
- 新增 `MIN_GROUP_NOTE_DURATION_S = 0.180`。
- 将该值写入 `syllable_group_summary` metadata。
- 更新 `_is_valid_stepwise_group()`，要求 candidate group 中每个 note 至少 `180 ms`。
- 在设计文档的 candidate rule 中加入 `each note duration >= 180 ms`。

**思考流程：**
- 用户给出一个具体 `la` group：第一个 note 约 `702 ms`，continuation note 只有约 `110 ms`。
- metadata 中 vibrato 为 0，因此快速来回抖来自 same-syllable group rendering，而不是 vibrato。
- 在当前 TTS/WORLD renderer 中，100-150 ms 的 continuation pitch 太短，难以听成稳定的第二个唱音，容易变成快速 wobble artifact。

**为什么添加这个代码/修改：**
- 防止类似装饰短音的 TSV note 被渲染成一个 sustained syllable 的 continuation。
- 把修复放在 candidate-selection 层，而不是继续增加高风险音频渲染补丁。

**为什么之前的代码需要修改：**
- 之前 group candidate 规则只检查连接时长、单边 pitch 方向、音程大小和最大 group size。
- 它可能选中某个包含过短 note 的 group，而这个 note 太短，无法稳定承载 continuation vowel。

**遇到的问题：**
- 短 note 仍然必须保留在 `score.tsv` 中，不能删除或改标签。
- 单纯降低 melisma selection 比例只能隐藏问题，不能定义哪些 group 在音乐和渲染上不安全。

**解决方式：**
- 保持所有 note 不变，但排除任何成员 note 短于 `180 ms` 的 group。
- 生成 `/private/tmp/mml26_middle_no_short_melisma` 并检查 metadata。

**带来的更好效果 / 用户体验：**
- 用户指出的 index `8/9` 在新样本中不再是 same-syllable group。
- metadata 显示 `min_group_note_duration_s = 0.18`。
- metadata 显示 `groups_with_short_notes_lt_180ms = 0`，selected group 中最短 note 约 `210 ms`。
- `/private/tmp/mml26_middle_no_short_melisma` 通过 validation。

**剩余风险 / TODO：**
- 需要试听 `/private/tmp/mml26_middle_no_short_melisma/score_1_female_middle_bright_v00/audio.wav`。
- 如果使用 `yeah` 的 selected groups 仍然不稳定，再把 melisma units 限制成只用 `la`。
- 如果 `180 ms` 仍然太短，可以把阈值提高到 `220-250 ms`。
- 完整 `syntheticdataset/` 尚未在这次修改后重新生成。

## 2026-06-27 21:19 — Raise Transition Density To 80 Percent

### English

**Files changed:**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Increased decorative transition density from 50% to 80% of eligible notes.
- Kept the current transition eligibility threshold and melisma protections unchanged.
- Generated and validated a new middle probe sample.

**Code changes:**
- Changed `TRANSITION_TARGET_ELIGIBLE_FRACTION` from `0.50` to `0.80`.
- Changed `TRANSITION_MAX_ELIGIBLE_FRACTION` from `0.50` to `0.80`.
- Updated the design document to say transitions are considered from `500 ms` notes and target about `80%` of eligible notes.

**Thought process:**
- The user asked to raise transition coverage to 80% of eligible notes.
- Because the cap was also 50%, both the target and maximum eligible fraction had to be changed.
- The existing planner already protects same-syllable continuations and noticeable-detune notes, so those safety rules remain in place.

**Why this code/change was added:**
- To make scoop/fall-in/short-portamento events much more frequent on eligible notes.

**Why the previous code needed to change:**
- The previous target and cap limited transitions to about 50% of eligible notes.

**Problems encountered:**
- The design document still mentioned a 700 ms threshold, while the current code uses `0.50 s`.
- The known PyWORLD `pkg_resources` warning and macOS OpenMP shared-memory warning still appear during generation.

**Solution:**
- Updated both code constants and the document text.
- Generated `/private/tmp/mml26_middle_transition_80pct` and checked metadata.

**Better result / user experience:**
- Metadata shows `transition_target_eligible_fraction = 0.8`.
- Metadata shows `eligible_transition_count = 42`, `transition_count = 34`, and `transition_eligible_fraction = 0.8095`.
- Validation passed for `/private/tmp/mml26_middle_transition_80pct`.

**Remaining risks / TODOs:**
- Listen to `/private/tmp/mml26_middle_transition_80pct/score_1_female_middle_bright_v00/audio.wav`.
- If transitions become too busy, lower the target or shorten/deepen only selected transition types.
- Full `syntheticdataset/` has not been regenerated after this change.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 将装饰性 transition 密度从 eligible notes 的 50% 提高到 80%。
- 保持当前 transition eligibility threshold 和 melisma protections 不变。
- 生成并验证了新的 middle probe sample。

**代码变化：**
- 将 `TRANSITION_TARGET_ELIGIBLE_FRACTION` 从 `0.50` 改为 `0.80`。
- 将 `TRANSITION_MAX_ELIGIBLE_FRACTION` 从 `0.50` 改为 `0.80`。
- 更新设计文档，说明当前从 `500 ms` note 开始考虑 transition，并目标覆盖约 `80%` eligible notes。

**思考流程：**
- 用户要求把 transition 覆盖率提高到符合条件 note 的 80%。
- 因为 cap 之前也是 50%，所以 target 和 maximum eligible fraction 都需要同步修改。
- 现有 planner 已经保护 same-syllable continuations 和 noticeable-detune notes，因此这些安全规则保持不变。

**为什么添加这个代码/修改：**
- 让 scoop/fall-in/short-portamento 在 eligible notes 上更频繁出现。

**为什么之前的代码需要修改：**
- 之前 target 和 cap 都把 transition 限制在 eligible notes 的约 50%。

**遇到的问题：**
- 设计文档仍写着 700 ms threshold，而当前代码使用的是 `0.50 s`。
- 生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP shared-memory warning。

**解决方式：**
- 同步更新代码常量和文档文字。
- 生成 `/private/tmp/mml26_middle_transition_80pct` 并检查 metadata。

**带来的更好效果 / 用户体验：**
- metadata 显示 `transition_target_eligible_fraction = 0.8`。
- metadata 显示 `eligible_transition_count = 42`、`transition_count = 34`、`transition_eligible_fraction = 0.8095`。
- `/private/tmp/mml26_middle_transition_80pct` 通过 validation。

**剩余风险 / TODO：**
- 需要试听 `/private/tmp/mml26_middle_transition_80pct/score_1_female_middle_bright_v00/audio.wav`。
- 如果 transition 听起来过密，可以降低 target，或只调整某些 transition type 的长度/深度。
- 完整 `syntheticdataset/` 尚未在这次修改后重新生成。

## 2026-06-27 21:23 — Make Decorative Transitions More Audible

### English

**Files changed:**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Made note-start decorative transitions easier to hear without changing their 80% eligible-note coverage.
- Reduced the number of ultra-short 30-40 ms transitions.
- Increased scoop/fall-in minimum depth slightly.
- Generated and validated a new middle probe sample.

**Code changes:**
- Changed transition duration class weights from `80/17/3` to `50/40/10` for short/medium/long.
- Changed short transition duration from `3-6%` of note duration clamped to `30-80 ms` to `8-12%` clamped to `60-120 ms`.
- Changed medium transition duration from `6-10%` clamped to `80-140 ms` to `12-18%` clamped to `110-190 ms`.
- Changed long transition duration from `10-15%` clamped to `140-220 ms` to `18-24%` clamped to `180-280 ms`.
- Raised the duration safety cap from 20% to 30% of the target note.
- Raised normal scoop depth from `15-50` cents to `25-65` cents.
- Raised normal fall-in depth from `10-40` cents to `20-55` cents.

**Thought process:**
- The user said the decorative transitions were still not very obvious in the current sample.
- Metadata showed that transition quantity was already high, but the average duration was only about `52 ms` and half of the events were `<=40 ms`.
- Therefore the likely issue was per-event audibility, not transition coverage.

**Why this code/change was added:**
- To make scoops and fall-ins audible as note-start ornaments while staying short enough to preserve the TSV pitch label.

**Why the previous code needed to change:**
- The previous transition sampling heavily favored very short durations, which were often lost after WORLD resynthesis.

**Problems encountered:**
- Increasing transition audibility can make ornaments too busy if durations become too long.
- The known PyWORLD `pkg_resources` warning and macOS OpenMP shared-memory warning still appear during generation.

**Solution:**
- Increased duration and depth moderately instead of changing transition coverage again.
- Generated `/private/tmp/mml26_middle_transition_audible` and checked metadata.

**Better result / user experience:**
- Transition coverage remains about 80%: `eligible_transition_count = 42`, `transition_count = 34`, `transition_eligible_fraction = 0.8095`.
- Transition duration range is now about `60-190 ms`, with average about `100 ms`.
- No transition events are `<=40 ms`.
- Validation passed for `/private/tmp/mml26_middle_transition_audible`.

**Remaining risks / TODOs:**
- Listen to `/private/tmp/mml26_middle_transition_audible/score_1_female_middle_bright_v00/audio.wav`.
- If transitions now sound too strong, reduce depth before reducing coverage.
- Full `syntheticdataset/` has not been regenerated after this change.

### 中文

**修改文件：**
- `synth/ornaments.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 让 note-start decorative transitions 更容易听到，同时保持 80% eligible-note 覆盖率不变。
- 减少 30-40 ms 这种超短 transition。
- 略微提高 scoop/fall-in 的最小深度。
- 生成并验证了新的 middle probe sample。

**代码变化：**
- 将 transition duration class 权重从 short/medium/long 的 `80/17/3` 改为 `50/40/10`。
- 将 short transition duration 从 note duration 的 `3-6%`、clamp `30-80 ms` 改为 `8-12%`、clamp `60-120 ms`。
- 将 medium transition duration 从 `6-10%`、clamp `80-140 ms` 改为 `12-18%`、clamp `110-190 ms`。
- 将 long transition duration 从 `10-15%`、clamp `140-220 ms` 改为 `18-24%`、clamp `180-280 ms`。
- 将 duration safety cap 从目标 note 的 20% 提高到 30%。
- 将普通 scoop depth 从 `15-50` cents 提高到 `25-65` cents。
- 将普通 fall-in depth 从 `10-40` cents 提高到 `20-55` cents。

**思考流程：**
- 用户反馈当前样本中装饰性 transition 仍然不明显。
- metadata 显示 transition 数量已经足够高，但平均时长只有约 `52 ms`，并且一半事件 `<=40 ms`。
- 因此更可能是单个 transition 不够可听，而不是覆盖率不够。

**为什么添加这个代码/修改：**
- 让 scoop 和 fall-in 作为 note-start ornament 更容易被听到，同时仍然短到不会破坏 TSV pitch label。

**为什么之前的代码需要修改：**
- 之前 transition sampling 非常偏向很短的 duration，在 WORLD 重合成后经常听不清。

**遇到的问题：**
- 如果 transition duration 过长，装饰音可能会显得过密或过重。
- 生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP shared-memory warning。

**解决方式：**
- 适度提高 duration 和 depth，而不是再次提高 coverage。
- 生成 `/private/tmp/mml26_middle_transition_audible` 并检查 metadata。

**带来的更好效果 / 用户体验：**
- transition 覆盖率仍约 80%：`eligible_transition_count = 42`、`transition_count = 34`、`transition_eligible_fraction = 0.8095`。
- transition duration range 现在约 `60-190 ms`，平均约 `100 ms`。
- 没有 `<=40 ms` 的 transition event。
- `/private/tmp/mml26_middle_transition_audible` 通过 validation。

**剩余风险 / TODO：**
- 需要试听 `/private/tmp/mml26_middle_transition_audible/score_1_female_middle_bright_v00/audio.wav`。
- 如果 transition 现在过强，优先降低 depth，而不是降低 coverage。
- 完整 `syntheticdataset/` 尚未在这次修改后重新生成。

## 2026-06-27 21:37 — Ensure Unique Word Sequences Per TSV Run

### English

**Files changed:**
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**What changed:**
- Added an explicit generation-time safeguard so multiple edge-tts word WAVs from the same TSV do not reuse an identical full word-unit sequence.
- Regenerated the TSV1 male/female clean probe set.

**Code changes:**
- Added `used_word_sequences` tracking for each input TSV in `scripts/build_synthetic_dataset.py`.
- Added `_render_unique_word_sequence_sample()` for the edge-tts word renderer.
- Added `_word_unit_sequence()` to extract the full word-unit sequence from returned metadata.
- If a generated sequence exactly matches an earlier sample from the same TSV in the same run, the generator retries with a deterministic adjusted seed.
- Added a max retry limit of 16 attempts before failing loudly.

**Thought process:**
- The user asked to ensure that even when one TSV is reused, each generated WAV has a different random word combination.
- The previous seed logic already made different gender/style/version combinations very likely to differ, but it did not explicitly check for full word-sequence collisions.
- A lightweight collision check is safer than assuming random seeds will always produce different sequences.

**Why this code/change was added:**
- To guarantee that same-TSV multi-WAV generation does not silently create duplicate full word-unit sequences.

**Why the previous code needed to change:**
- The previous code generated word units from each sample seed but did not compare the resulting sequence against other WAVs from the same TSV.

**Problems encountered:**
- Existing skipped samples are not loaded and compared when `--overwrite` is not used.
- The known PyWORLD `pkg_resources` warning and macOS OpenMP shared-memory warning still appear during generation.

**Solution:**
- Track only samples generated in the current TSV run.
- Retry only when an exact full-sequence collision occurs.
- Regenerated `/private/tmp/mml26_tsv1_gender_only_clean_unique_words` and validated it.

**Better result / user experience:**
- The female and male TSV1 clean samples now have explicitly checked different word-unit sequences.
- Validation passed for `/private/tmp/mml26_tsv1_gender_only_clean_unique_words`.
- Metadata comparison showed `identical_full_sequence = False` and only `4 / 294` notes with the same word at the same position.

**Remaining risks / TODOs:**
- If future runs skip existing samples, exact sequence uniqueness is only guaranteed among samples generated in that run.
- Full `syntheticdataset/` has not been regenerated after this change.

### 中文

**修改文件：**
- `scripts/build_synthetic_dataset.py`
- `SyntheticVoiceDatasetDesign.md`
- `Creating_log.md`

**修改内容：**
- 增加生成期显式保护，确保同一个 TSV 生成的多个 edge-tts word WAV 不会复用完全相同的完整 word-unit 序列。
- 重新生成 TSV1 的男/女 clean probe set。

**代码变化：**
- 在 `scripts/build_synthetic_dataset.py` 中为每个输入 TSV 增加 `used_word_sequences` 跟踪。
- 为 edge-tts word renderer 新增 `_render_unique_word_sequence_sample()`。
- 新增 `_word_unit_sequence()`，从返回的 metadata 中提取完整 word-unit sequence。
- 如果某个新生成序列和同一 TSV 在本轮生成中的早先样本完全一致，生成器会使用 deterministic adjusted seed 重试。
- 最多重试 16 次，仍失败则明确报错。

**思考流程：**
- 用户要求确保即使复用同一个 TSV，每个生成 WAV 也有不同的随机词组合。
- 之前 seed 逻辑已经让不同 gender/style/version 组合大概率不同，但没有显式检查完整词序列是否碰撞。
- 加一个轻量 collision check 比单纯相信随机 seed 更安全。

**为什么添加这个代码/修改：**
- 保证 same-TSV multi-WAV generation 不会静默产生完全重复的 word-unit 序列。

**为什么之前的代码需要修改：**
- 之前代码从每个 sample seed 生成 word units，但不会把结果和同一 TSV 的其他 WAV 做比较。

**遇到的问题：**
- 如果不用 `--overwrite` 而跳过已有 sample，当前实现不会加载那些旧样本做比较。
- 生成时仍有已知 PyWORLD `pkg_resources` warning 和 macOS OpenMP shared-memory warning。

**解决方式：**
- 只跟踪本轮同一 TSV 中实际生成的 samples。
- 只有在完整序列完全碰撞时才重试。
- 重新生成并验证 `/private/tmp/mml26_tsv1_gender_only_clean_unique_words`。

**带来的更好效果 / 用户体验：**
- TSV1 female/male clean samples 的 word-unit sequence 已被显式检查为不同。
- `/private/tmp/mml26_tsv1_gender_only_clean_unique_words` 通过 validation。
- metadata 对比显示 `identical_full_sequence = False`，同位置相同词只有 `4 / 294` 个 note。

**剩余风险 / TODO：**
- 如果后续运行跳过已有 samples，exact sequence uniqueness 只保证本轮实际生成的 samples 之间成立。
- 完整 `syntheticdataset/` 尚未在这次修改后重新生成。

## 2026-06-27 22:24 — Apple Silicon MPS Training Compatibility

### English

**Files changed:**
- `src/basic_pitch_model.py`
- `src/train.py`
- `Creating_log.md`

**What changed:**
- Added a targeted Apple Silicon MPS fallback for the fixed CQT feature extractor.
- Updated the test DataLoader to respect the CLI `--num-workers` value.

**Code changes:**
- Added `_module_device()` in `BasicPitchTorch` to inspect the current device of a module.
- In `_compute_cqt()`, when the input audio is on MPS, the nnAudio CQT layer is kept on CPU, audio is copied to CPU for CQT computation, and the resulting CQT features are moved back to the original MPS device before normalization and trainable network layers.
- Replaced the hard-coded test DataLoader worker count with `args.num_workers`.
- Only sets `multiprocessing_context="fork"` for the test DataLoader when `args.num_workers > 0`.

**Thought process:**
- The user attempted Apple Silicon training and hit PyTorch's MPS Conv1d output-channel limit inside nnAudio's CQT implementation.
- `PYTORCH_ENABLE_MPS_FALLBACK=1` was already set, but this particular nnAudio/PyTorch path still raised the MPS limit error before automatic fallback could help.
- The CQT transform is a fixed feature extractor, so it is safer and narrower to compute only that stage on CPU while keeping the trainable model layers on MPS.
- A local smoke run also exposed that the test DataLoader ignored `--num-workers 0`, which could fail at the post-training test stage on systems with shared-memory restrictions.

**Why this code/change was added:**
- To make the training path usable on Apple Silicon without switching the whole training run to CPU.
- To make `--num-workers 0` consistently disable multiprocessing for train, validation, and test data loading.

**Why the previous code needed to change:**
- The previous CQT path allowed Lightning to move nnAudio's CQT layer to MPS, where the large Conv1d kernel is not supported.
- The previous test loader hard-coded multiprocessing even when the command explicitly requested `--num-workers 0`.

**Problems encountered:**
- The Codex sandbox does not expose MPS, so the exact Apple Silicon path could not be fully executed here.
- CPU smoke testing initially reached training and validation but failed during testing because the test DataLoader still used multiprocessing.

**Solution:**
- Added a small MPS-only CPU CQT branch in `src/basic_pitch_model.py`.
- Updated `src/train.py` so the test loader follows `args.num_workers`.
- Ran a CPU full-chain smoke test with one training batch and one validation batch; it completed training, validation, checkpoint loading, and testing.

**Better result / user experience:**
- The user can keep using `--accelerator mps` on Apple Silicon, with only the unsupported fixed CQT operation handled on CPU.
- The same `--num-workers 0` command is now coherent across all phases and less likely to fail at the final testing step.

**Remaining risks / TODOs:**
- The actual MPS branch still needs to be verified on the user's Apple Silicon terminal because this Codex runtime only exposes CPU.
- CPU CQT on each batch may reduce the speedup from MPS, but it should be much better than forcing the full model to CPU.

### 中文

**修改文件：**
- `src/basic_pitch_model.py`
- `src/train.py`
- `Creating_log.md`

**修改内容：**
- 为 Apple Silicon MPS 训练增加针对固定 CQT 特征提取器的兼容路径。
- 让 test DataLoader 遵守命令行里的 `--num-workers` 设置。

**代码变化：**
- 在 `BasicPitchTorch` 中新增 `_module_device()`，用于检查模块当前所在设备。
- 在 `_compute_cqt()` 中，如果输入音频在 MPS 上，则把 nnAudio CQT 层保持在 CPU，把音频复制到 CPU 做 CQT，再把得到的 CQT 特征移回原本的 MPS 设备，之后继续做 normalization 和可训练网络层。
- 将 test DataLoader 原本硬编码的 worker 数改成 `args.num_workers`。
- 只有在 `args.num_workers > 0` 时，test DataLoader 才设置 `multiprocessing_context="fork"`。

**思考流程：**
- 用户在 Apple Silicon 上训练时，nnAudio 的 CQT 实现内部触发了 PyTorch MPS Conv1d output-channel 限制。
- 用户已经设置 `PYTORCH_ENABLE_MPS_FALLBACK=1`，但这个 nnAudio/PyTorch 路径仍然在自动 fallback 生效前抛出了 MPS 限制错误。
- CQT 是固定特征提取器，不是需要训练的模型主体，因此只把这一段放在 CPU 上计算是最小、最安全的修改。
- 本地 smoke 测试还发现 test DataLoader 忽略了 `--num-workers 0`，可能导致训练完成后在 test 阶段因为共享内存/多进程问题失败。

**为什么添加这个代码/修改：**
- 让训练可以继续使用 Apple Silicon 的 `--accelerator mps`，而不是把整个训练降级到 CPU。
- 让 `--num-workers 0` 在 train、validation、test 三个阶段都一致生效。

**为什么之前的代码需要修改：**
- 之前 Lightning 会把 nnAudio CQT 层一起移动到 MPS，而它的大 Conv1d kernel 当前不被 MPS 支持。
- 之前 test loader 即使命令传了 `--num-workers 0`，仍会硬编码开启 multiprocessing。

**遇到的问题：**
- Codex 沙盒环境没有暴露 MPS，因此无法在这里完整执行用户本机的 Apple Silicon 路径。
- CPU smoke 测试第一次已经跑通训练和验证，但在测试阶段因为 test DataLoader 仍使用 multiprocessing 而失败。

**解决方式：**
- 在 `src/basic_pitch_model.py` 中加入仅 MPS 使用的 CPU CQT 分支。
- 在 `src/train.py` 中让 test loader 使用 `args.num_workers`。
- 运行一个 CPU 全链条 smoke test：1 个训练 batch、1 个验证 batch，最终完成训练、验证、加载 best checkpoint 和测试。

**带来的更好效果 / 用户体验：**
- 用户可以继续在 Apple Silicon 上使用 `--accelerator mps`，只有不兼容的固定 CQT 操作留在 CPU。
- 同一条 `--num-workers 0` 命令现在在所有阶段都一致，减少训练最后测试阶段才失败的概率。

**剩余风险 / TODO：**
- 实际 MPS 分支仍需要用户在 Apple Silicon 终端中验证，因为当前 Codex runtime 只暴露 CPU。
- 每个 batch 的 CQT 在 CPU 上算会降低一部分 MPS 加速收益，但仍应明显好于整个训练都跑 CPU。
