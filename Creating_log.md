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
