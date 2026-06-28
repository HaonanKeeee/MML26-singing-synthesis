# Synthetic Vocal Generation / 合成歌声生成

**Klangio challenge for HACKATUNE 2026 (Munich Music Labs).**

This repository is now planned around the **Synthetic Vocal Generation** challenge. The previous project direction was a Cyanite music recommendation prototype, but the confirmed hackathon task is now Klangio's synthetic vocal generation challenge.

Current experimental status as of 2026-06-28:

- We tried several synthetic singing dataset variants, including pure algorithmic synthesis, Edge TTS word-unit synthesis, WORLD pitch replacement, gender/age/style grids, same-syllable multi-note groups, detune, drift, vibrato, scoops/fall-ins, release tuning, voiced-mask tuning, simple-word units, and finally a heavily simplified vowel-only / clean-pitch version.
- The more complex variants often sounded less natural or blurred note onsets, offsets, or perceived pitch. The simplified variants were cleaner but still did not materially improve the validation result.
- Multiple training runs stayed around the low `0.1x` range on the key evaluation scores. After removing most "messy" synthesis effects, the result was still around `0.1x`, so the current expectation is that this synthetic-data approach may be close to its practical ceiling for this hackathon.
- The current priority is therefore reproducibility, label alignment, and a clean final submission rather than adding more synthesis complexity.

当前实验状态（2026-06-28）：

- 我们已经尝试过多种 synthetic singing dataset 方案，包括纯算法合成、Edge TTS 单词素材、WORLD 改音高、gender/age/style 网格、单吐字连续多音、detune、drift、vibrato、装饰性转音、release 调整、voiced-mask 调整、simple-word 素材，以及最后的 vowel-only / clean-pitch 极简版本。
- 复杂版本经常听感更不自然，或者让 note onset、offset、perceived pitch 更模糊。简化版本更干净，但验证结果没有明显改善。
- 多个训练版本的关键评估分数都停留在低 `0.1x` 区间。即使取消大部分“乱七八糟”的合成效果，结果仍然大约是 `0.1x`，所以目前判断这个 synthetic-data 方案在本次 hackathon 里可能已经接近实际上限。
- 当前优先级应转为：可复现、标签对齐、最终提交清晰，而不是继续增加更多复杂合成效果。

Important distinction:

- **Challenge requirements** are the parts explicitly stated by the organizer: generate singing from provided score annotations, train the provided transcription model using the synthetic data, and submit the singing-generation code plus trained weights/checkpoint.
- **Implementation plan** means our own proposed engineering approach for the hackathon: suggested file structure, scripts, validation checks, synthesis methods, voice presets, timeline, and optimization ideas. These are not official requirements unless the organizer's repository or mentors confirm them.

本仓库现在用于 **Synthetic Vocal Generation（合成歌声生成）** challenge。之前的方向是 Cyanite 音乐推荐系统，但现在实际确定的任务已经变成 Klangio 的合成歌声生成挑战。

重要区分：

- **比赛硬性要求** 是主办方明确写出来的内容：根据提供的 score annotations 生成 singing，用 synthetic data 训练主办方提供的 transcription model，并提交歌声生成代码和训练好的 weights/checkpoint。
- **实现规划** 是我们为了 48 小时 hackathon 落地而提出的工程方案：例如建议的文件结构、脚本、检查流程、合成方法、voice presets、时间安排和优化方向。这些不是主办方硬性要求，除非官方 repo 或 mentor 明确确认。

---

## 1. Hackathon and challenge background / Hackathon 和题目背景

### English

Hackatune 2026 is a music-tech hackathon hosted by Munich Music Labs at TUM. Our selected sponsor challenge is provided by **Klangio**.

The challenge is about **synthetic vocal generation for singing transcription**.

The organizer provides musical score annotations in `.tsv` format. Each score contains note-level information:

```text
onset    offset    pitch
```

These annotations come from commercial-grade pop music, but the organizer does **not** provide the original real vocal audio. Our task is to generate synthetic singing audio that follows the provided annotations.

After generating the synthetic audio, we use the synthetic audio together with the original score annotations to train the organizer-provided singing transcription model. The final evaluation checks whether a model trained only on our synthetic data can perform well on real singing audio.

### 中文

Hackatune 2026 是 Munich Music Labs 在 TUM 举办的 music-tech hackathon。我们现在选择的是 **Klangio** 提供的 sponsor challenge。

这个题目是：**为歌声转谱任务生成合成歌声训练数据**。

主办方会提供 `.tsv` 格式的乐谱标注文件。每个 score 里面包含音符级别的信息：

```text
onset    offset    pitch
```

这些标注来自商业级 pop music，但是主办方不会提供这些标注对应的真实人声录音。我们的任务是根据这些标注生成对应的合成歌声音频。

生成合成音频之后，我们用这些合成音频和原始 score 标注一起训练主办方提供的 singing transcription model。最终评估会看：只用我们 synthetic data 训练出来的模型，能不能在真实歌声上识别出准确的音符。

---

## 2. One-sentence understanding / 一句话理解

### English

We generate fake but label-accurate singing from note annotations, train a transcription model on that synthetic data, and test whether the model can transcribe real singing.

### 中文

我们用主办方给的音符标注合成“假歌声”，再用这些假歌声训练一个歌声转谱模型，最后看这个模型能不能从真实歌声里还原 onset、offset 和 pitch。

Pipeline:

```text
provided score.tsv
    -> our synthetic vocal generator
    -> synthetic audio.wav
    -> organizer-provided training code
    -> trained checkpoint.ckpt
    -> evaluation on real singing audio
```

---

## 3. What the model does / 模型是干什么的

### English

The model in this challenge is a **singing transcription model**. It is not the model that generates vocals.

Its task is:

```text
audio waveform -> note annotations
```

Input:

```text
singing audio.wav
```

Output:

```text
onset, offset, pitch
```

Example:

```text
Input audio: someone sings three notes
Output:
0.00    0.50    60
0.50    1.00    62
1.00    1.50    64
```

We should not redesign or heavily modify the organizer-provided model. Our main contribution is the synthetic data generator.

### 中文

这个 challenge 里的模型是 **singing transcription model（歌声转谱模型）**。它不是用来生成歌声的模型。

它做的是：

```text
歌声音频 -> 音符标注
```

输入：

```text
singing audio.wav
```

输出：

```text
onset, offset, pitch
```

例子：

```text
输入音频：有人唱了三个音
输出：
0.00    0.50    60
0.50    1.00    62
1.00    1.50    64
```

我们不应该重点改主办方提供的模型结构。我们的主要贡献是生成 synthetic training data。

---

## 4. What is provided by the organizer / 主办方提供什么

### Officially stated in the challenge brief / 题目说明中明确写到的内容

Official challenge repository:

```text
https://github.com/Klangio/MML26-singing-synthesis
```

According to the challenge description, the organizer provides:

| Officially provided item | Meaning | How we use it |
|---|---|---|
| Score annotations | Files containing note onset, offset, and pitch. | These are the input to our singing generator. |
| Training and evaluation code | Code for training/evaluating the transcription system. | We run this code; we should not modify the model architecture unless explicitly allowed. |
| At least one real-data evaluation set | A dataset for checking how the trained model performs on real data. | Use for evaluation only, not for training. |
| Hidden final evaluation set | Secret test data used by the organizer. | We cannot see it; our synthetic data must generalize. |

中文：

根据题目说明，主办方明确提供：

| 主办方明确提供 | 含义 | 我们怎么用 |
|---|---|---|
| Score annotations | 包含 onset、offset、pitch 的音符标注文件。 | 作为我们合成歌声的输入。 |
| 训练和评估代码 | 用于训练/评估 transcription system 的代码。 | 我们运行这些代码；除非明确允许，不改模型结构。 |
| 至少一个真实数据 evaluation set | 用于检查模型在真实数据上的效果。 | 只能用于评估，不能用于训练。 |
| 隐藏最终测试集 | 主办方最后评测用的 secret test data。 | 我们看不到，所以 synthetic data 要尽量泛化。 |

### Current implementation assumptions to verify / 当前需要用官方 repo 确认的实现假设

The following items are **our current working assumptions** based on the expected official repository workflow. They are useful for planning, but they must be verified by checking the official repo and mentor instructions:

| Current assumption | Why it matters |
|---|---|
| There may be a `scores/` folder or equivalent input-score directory. | We need to know where TSV score files are stored. |
| There may be a required `syntheticdataset/` folder format. | Our generated WAV/TSV pairs must match the official dataloader. |
| Training may be started by scripts such as `src/train.py` or shell scripts. | We need to run the official training pipeline correctly. |
| The final trained weights may be a `.ckpt` file or another checkpoint format. | We should submit the format expected by the provided code. |
| The required audio sample rate and channel format may be specified in the repo. | Our generated WAV files must match the training pipeline. |

中文：

下面这些是**当前实现假设**，用于开发规划，但必须以官方 GitHub repo 和 mentor 说明为准：

| 当前假设 | 为什么重要 |
|---|---|
| 可能会有 `scores/` 或类似的输入 score 文件夹。 | 我们需要知道 TSV 文件实际放在哪里。 |
| 可能会有规定的 `syntheticdataset/` 文件夹格式。 | 我们生成的 WAV/TSV pair 必须能被官方 dataloader 读取。 |
| 训练可能通过 `src/train.py` 或 shell script 启动。 | 我们需要正确运行官方训练流程。 |
| 最终权重可能是 `.ckpt` 或其他 checkpoint 格式。 | 应该提交官方代码要求的权重格式。 |
| 官方 repo 可能规定音频采样率和声道格式。 | 生成 WAV 时必须匹配训练 pipeline。 |

### APIs / API usage

For the MVP, **no external API is required by the challenge brief**.

Our baseline implementation should work offline with:

- Python
- NumPy / SciPy / soundfile or similar audio libraries
- the official Klangio training repository

Optional external singing synthesis APIs or pretrained models should only be used if mentors confirm they are allowed and their licenses are safe.

中文说明：

根据目前题目说明，MVP 不需要外部 API。最稳的版本可以完全离线完成：读取 TSV，合成 WAV，生成训练数据，再用主办方 repo 里的训练代码训练模型。

如果之后想用外部歌声合成模型或 API，必须先问 mentor 是否允许，并确认 license 没有问题。

---

## 5. What we must build / 我们要做什么

### English

Our main task is to build a **label-preserving synthetic vocal generator**:

```text
score.tsv -> synthetic vocal audio.wav
```

The generated audio must match the score:

- correct onset time,
- correct offset time,
- correct MIDI pitch,
- vocal-like timbre,
- enough diversity to help the model generalize to real singing.

### 中文

我们的主要任务是做一个 **保持标签准确的合成歌声生成器**：

```text
score.tsv -> synthetic vocal audio.wav
```

生成的音频必须和 score 对齐：

- onset 时间准确；
- offset 时间准确；
- MIDI pitch 准确；
- 声音尽量像人声；
- 数据要有一定多样性，让模型不要只学到一种机械声音。

---

## 6. Expected dataset format / 生成数据格式

This section is an **implementation assumption**, not a hard requirement from the PDF. The final folder layout must follow the official Klangio repository's dataloader.

Current assumed structure:

```text
syntheticdataset/
    sample_001/
        audio.wav
        score.tsv
    sample_002/
        audio.wav
        score.tsv
```

For data diversity, the same original score may be rendered multiple times if the official dataloader allows it:

```text
syntheticdataset/
    score_001_clean/
        audio.wav
        score.tsv
    score_001_breathy/
        audio.wav
        score.tsv
    score_001_vibrato/
        audio.wav
        score.tsv
```

Important rule:

```text
audio.wav and score.tsv must stay aligned.
```

Current final practical choice:

```text
one input TSV -> one selected gender-compatible WAV
```

The full gender/age/style grid remains useful as code history and exploration,
but the latest experiments suggest it does not improve the current validation
result enough to justify the extra noise and runtime. The cleaner final dataset
should prefer fewer, better-aligned samples over many heavily processed samples.

中文：

本节是**实现假设**，不是 PDF 里写死的硬性要求。最终目录结构必须以官方 Klangio repo 的 dataloader 为准。

当前先假设每个样本文件夹里需要有：

```text
audio.wav
score.tsv
```

如果官方 dataloader 允许，同一个 score 可以生成多个不同版本，比如 clean、breathy、vibrato。但每个版本都必须保证 `audio.wav` 和 `score.tsv` 对齐。

当前实际最终取舍：

```text
一个输入 TSV -> 一个按音域选择性别的 WAV
```

完整的 gender/age/style 网格仍然可以作为代码历史和探索方向保留，但最新实验说明它对当前验证结果没有足够明显的提升，反而会增加噪声和生成时间。因此最终数据集更应该选择更少、更对齐的样本，而不是大量复杂处理后的样本。


---

## 7. MVP final product / MVP 最终成品

This section describes **our proposed MVP**, not an exact organizer-mandated implementation. The official deliverables are the singing-generation code and trained weights/checkpoint. The following MVP is the practical way we plan to produce those deliverables.

The MVP should include:

```text
1. A CLI script that converts one score.tsv into one vocal audio.wav.
2. A batch script that converts all scores into a training dataset folder.
3. Several voice presets, at least clean and vibrato.
4. A validation script that checks audio-score alignment and file quality.
5. A trained weights/checkpoint file using only synthetic data.
6. Clear reproduction instructions.
```

Example commands, subject to adjustment after checking the official repo:

```bash
python scripts/synthesize_score.py \
  --input scores/example.tsv \
  --output syntheticdataset/example_clean/audio.wav \
  --sample-rate 22050 \
  --voice-preset clean
```

```bash
python scripts/build_synthetic_dataset.py \
  --scores-dir scores \
  --output-dir syntheticdataset \
  --voices clean breathy vibrato
```

```bash
# Use the actual training command from the official Klangio repo.
./experiments_sample.sh
```

Notes:

- `22050` is only an example sample rate. Use the sample rate expected by the official training code.
- `.ckpt` is only an example checkpoint format. Submit the actual weights/checkpoint format expected by the official code.
- Script names and folder names can change after checking the official repo.

中文 MVP：

本节描述的是**我们建议的 MVP 实现方式**，不是主办方逐字规定的实现。主办方硬性提交物是歌声生成代码和训练好的 weights/checkpoint。下面的 MVP 是我们为了产出这些提交物而设计的实用路线。

```text
1. 一个脚本：输入一个 score.tsv，输出一个 vocal audio.wav。
2. 一个批量脚本：把所有 TSV 生成训练数据文件夹。
3. 至少有 clean 和 vibrato 等 voice preset。
4. 一个 validation 脚本检查音频和 score 是否合理。
5. 一个只用 synthetic data 训练出来的 weights/checkpoint。
6. 清楚的复现说明。
```

注意：

- `22050` 只是示例采样率，最终要用官方训练代码要求的采样率。
- `.ckpt` 只是示例权重格式，最终要提交官方代码要求的 checkpoint/weights 格式。
- 脚本名和文件夹名都可以在查看官方 repo 后调整。


---

## 8. Code structure / 建议代码结构

Suggested structure. This is our implementation plan, not an official required structure:

```text
Hackatune2026/
├── README.md
├── AGENTS.md
├── Creating_log.md
├── requirements.txt
├── scripts/
│   ├── synthesize_score.py
│   ├── build_synthetic_dataset.py
│   └── validate_synthetic_dataset.py
├── synth/
│   ├── score_io.py
│   ├── pitch.py
│   ├── voice.py
│   ├── formants.py
│   ├── envelopes.py
│   ├── render.py
│   └── presets.py
├── scores/
├── syntheticdataset/
└── external/
    └── MML26-singing-synthesis/
```

The exact final structure should be adjusted after checking how the official Klangio repo expects data paths, training scripts, and checkpoint outputs.

中文：

建议把合成器核心逻辑放在 `synth/`，命令行入口放在 `scripts/`。主办方 repo 可以放在 `external/MML26-singing-synthesis/` 或者作为独立 clone。

---

## 9. Implementation order / 按代码顺序的实现逻辑

This section is a recommended implementation order for our team and Codex. It is not a fixed requirement from the challenge PDF.
  
本节是我们给团队和 Codex 的建议实现顺序，不是 PDF 里规定的固定步骤。

### Step 1: Read score TSV / 读取 TSV

Function:

```python
def load_score_tsv(path):
    pass
```

Tasks:

- read tab-separated values,
- parse `onset`, `offset`, `pitch`,
- validate `offset > onset`,
- validate MIDI pitch range,
- sort notes by onset.

中文：读取 TSV，把每一行变成内部 note 对象。

---

### Step 2: MIDI pitch to frequency / MIDI 音高转频率

Function:

```python
def midi_to_hz(midi_note):
    pass
```

Formula:

```text
frequency = 440 * 2 ** ((midi_note - 69) / 12)
```

Examples:

```text
69 -> A4 -> 440 Hz
60 -> C4 -> 261.63 Hz
```

中文：TSV 里的 pitch 是 MIDI 编号，需要转成 Hz 才能合成音频。

---

### Step 3: Generate basic vocal excitation / 生成基础声源

Function:

```python
def generate_excitation(f0, duration, sample_rate, voice_params):
    pass
```

Use:

- sine plus harmonics,
- soft sawtooth-like waveform,
- breath noise component.

Do not use only pure sine for final MVP because it is too unlike singing.

中文：生成基础声音。纯 sine wave 太像测试音，不像人声，所以需要泛音和轻微噪声。

---

### Step 4: Add vowel/formant shaping / 加元音共振峰

Function:

```python
def apply_vowel_formants(waveform, sample_rate, vowel, voice_params):
    pass
```

Purpose:

- make the signal more vocal-like,
- simulate vowels such as `ah`, `ee`, `oo`, `oh`, `uh`,
- create different singer timbres.

中文：formant 是人声里很重要的口腔/喉咙共振特征。加简单 formant 可以让声音更像 “ah / ee / oo”。

---

### Step 5: Add amplitude envelope / 加音量包络

Function:

```python
def apply_envelope(waveform, attack, release):
    pass
```

Purpose:

- avoid clicks,
- make onset and offset natural,
- keep labels clear.

Important:

- attack too long makes onset unclear,
- release too long makes offset unclear.

中文：每个音要有短 attack/release，避免 click，但不能太长，否则标注会变模糊。

---

### Step 6: Add controlled vibrato / 加可控 vibrato

Function:

```python
def apply_vibrato(f0_curve, rate_hz, depth_cents):
    pass
```

Safe range:

```text
rate: 4-7 Hz
depth: 10-50 cents
```

中文：真实唱歌有颤音，但太强会影响 pitch 标签，所以要可控。

---

### Step 7: Render the full score / 渲染完整音频

Function:

```python
def render_score(notes, voice_params, sample_rate):
    pass
```

Tasks:

- create full audio buffer,
- place each note at the correct onset,
- end each note at the correct offset,
- handle overlaps if present,
- normalize safely,
- avoid clipping.

中文：把每个音按照 onset/offset 放到完整音频时间轴上。

---

### Step 8: Write WAV / 保存 WAV

Function:

```python
def write_wav(path, waveform, sample_rate):
    pass
```

Tasks:

- save mono WAV unless required otherwise,
- use consistent sample rate,
- prevent clipping,
- make sure duration covers the last offset.

中文：输出标准 WAV 文件。采样率和长度要稳定。

---

### Step 9: Write aligned score.tsv / 写入对应 score.tsv

Function:

```python
def write_score_copy(input_score, output_score):
    pass
```

Usually we copy the original score unchanged. Only change labels if the audio was intentionally shifted or modified.

中文：通常直接复制原始 TSV，因为我们要保持标签不变。

---

### Step 10: Batch generate dataset / 批量生成数据集

Function:

```python
def build_synthetic_dataset(scores_dir, output_dir, voice_presets):
    pass
```

Tasks:

- iterate over all TSV files,
- generate multiple voice versions,
- create one folder per generated sample,
- write `audio.wav`,
- write `score.tsv`,
- log generation parameters.

中文：对每个 score 生成多个声音版本，形成 `syntheticdataset/`。

---

### Step 11: Validate dataset / 检查数据集

Function:

```python
def validate_generated_pair(audio_path, score_path):
    pass
```

Checks:

- file exists,
- audio duration is long enough,
- score times are inside audio duration,
- waveform is not silent,
- waveform is not clipped,
- sample rate is correct,
- no NaN or Inf values.

Optional:

- estimate f0 and compare against score pitch,
- plot spectrogram with note overlays.

中文：检查 WAV 是否静音、爆音、长度不够、采样率错误、和 score 不对齐。

---

### Step 12: Train organizer model / 训练主办方模型

Use the organizer-provided training scripts.

Rules:

- train only on synthetic data,
- do not use real singing data for training,
- do not redesign the model architecture,
- save the final `.ckpt`.

中文：训练时只用 synthetic data。真实歌声只能用于 evaluation，不能用于训练。

---

### Step 13: Evaluate and iterate / 评估并迭代

Loop:

```text
generate syntheticdataset
    -> train model
    -> evaluate
    -> inspect failure cases
    -> adjust synthesis parameters
    -> regenerate
    -> retrain
```

Possible metric interpretation:

- If onset score is bad: attack may be too slow or noisy.
- If offset score is bad: release or reverb may be too long.
- If pitch score is bad: vibrato or pitch drift may be too strong.

中文：根据分数迭代。如果 onset 差，检查 attack；如果 offset 差，检查 release/reverb；如果 pitch 差，检查 vibrato。

---

## 10. Required-by-us MVP features / 我们自己定义的 MVP 必须功能

These are required for our planned MVP, but they are not all official challenge requirements. The official requirement is to generate singing from score annotations and submit the generation code plus trained weights/checkpoint.
  
这些是我们自己为了完成 MVP 定义的必须功能，不代表全部都是主办方硬性要求。主办方硬性要求是：从 score annotations 生成 singing，并提交生成代码和训练好的 weights/checkpoint。

- [ ] TSV parser.
- [ ] MIDI-to-Hz conversion.
- [ ] Basic vocal-like note synthesis.
- [ ] Envelope control.
- [ ] Simple vowel/formant shaping.
- [ ] Controlled vibrato.
- [ ] Optional breathiness.
- [ ] WAV export.
- [ ] Batch generation into `syntheticdataset/`.
- [ ] Generation parameter logging.
- [ ] Dataset validation.
- [ ] Training with organizer code.
- [ ] Final `.ckpt` checkpoint.

中文：

- [ ] 读取 TSV。
- [ ] MIDI 转 Hz。
- [ ] 生成基础人声-like 音符。
- [ ] 控制音量包络。
- [ ] 加简单元音/formant。
- [ ] 加可控 vibrato。
- [ ] 可选 breathiness。
- [ ] 输出 WAV。
- [ ] 批量生成 `syntheticdataset/`。
- [ ] 记录生成参数。
- [ ] 检查数据质量。
- [ ] 用主办方代码训练。
- [ ] 输出最终 `.ckpt`。

---

## 11. Optimization ideas if time allows / 有时间再做的优化

These are optional ideas. Do not treat them as required unless the MVP is already working end-to-end.
  
这些是可选优化。只有在 MVP 全流程已经跑通之后才考虑，不是硬性要求。

### Data diversity / 数据多样性

- Multiple vowels: `ah`, `ee`, `oo`, `oh`, `uh`.
- Multiple synthetic singers: low, high, bright, dark, nasal, breathy.
- Randomized vibrato.
- Controlled pitch drift.
- Phrase-level loudness dynamics.
- Slight timing humanization within a safe range.

### More realistic singing / 更真实的人声

- Better source-filter synthesis.
- Better formant filters.
- Legato transitions.
- Portamento/slides.
- Consonant-like attacks.
- Light room reverb.

### Robustness / 泛化能力

- Mild noise augmentation.
- Mild EQ variation.
- Soft compression.
- Light accompaniment only if allowed and only if it does not hide the vocal.

### Evaluation tools / 评估工具

- Spectrogram visualization with score overlays.
- Automatic f0 sanity check.
- Clean vs augmented dataset comparison.
- Per-score validation report.

---

## 12. Risks and rules / 风险和规则

### Main risks

1. Generated audio does not align with TSV.
2. Attack is too slow, causing unclear onset.
3. Release or reverb is too long, causing unclear offset.
4. Vibrato is too strong, causing pitch ambiguity.
5. Sound is too synthetic, so the model fails on real singing.
6. Sound is realistic but uncontrolled, so labels become wrong.

### Design rules

- Label accuracy first, realism second.
- Generate multiple controlled variations instead of one perfect voice.
- Keep augmentations label-preserving.
- Train early and often.
- Use validation metrics to decide what to change.

中文：

- 标签准确第一，真实感第二。
- 不要只生成一种声音，要生成多种受控版本。
- 所有增强都不能明显破坏 onset / offset / pitch。
- 尽早训练，尽早看分数。
- 根据 validation 结果调整，不要凭感觉乱改。

---

## 13. Development timeline / 开发时间安排

This timeline is a practical hackathon plan, not an official schedule from the organizer.
  
这个时间安排是我们自己的 hackathon 实施计划，不是主办方官方时间表。

### Friday night / 周五晚上

Goal: make the full pipeline concept clear and run the simplest TSV-to-WAV baseline.

Tasks:

- Understand official repository.
- Confirm score format.
- Implement TSV parser.
- Implement MIDI-to-Hz.
- Generate simple voice-like audio.
- Export first WAV.

中文目标：先跑通最简单的 TSV 到 WAV。

---

### Saturday morning / 周六上午

Goal: build dataset generation.

Tasks:

- Add formant shaping.
- Add envelope.
- Add vibrato preset.
- Batch generate `syntheticdataset/`.
- Validate generated audio-score pairs.

中文目标：完成数据批量生成和检查。

---

### Saturday afternoon / 周六下午

Goal: train and evaluate.

Tasks:

- Run organizer training code.
- Produce first `.ckpt`.
- Run evaluation/inference.
- Inspect errors.

中文目标：训练出第一个 checkpoint 并看效果。

---

### Saturday evening / 周六晚上

Goal: improve synthetic data.

Tasks:

- Add more voice presets.
- Add controlled augmentation.
- Compare clean dataset vs diverse dataset.
- Retrain if time allows.

中文目标：增加数据多样性，提高真实数据泛化。

---

### Sunday morning / 周日上午

Goal: freeze final submission.

Tasks:

- Stop adding risky features.
- Keep the best checkpoint.
- Clean reproduction instructions.
- Prepare short pitch/demo explanation.
- Backup generated examples and checkpoint.

中文目标：冻结最终版本，不再大改。

---

## 14. Team roles / 团队分工建议

These roles are suggestions for team coordination.
  
这些分工只是团队协作建议。

### Role 1: Synthesis pipeline

- TSV parser.
- MIDI-to-Hz.
- Voice synthesis.
- Formant/vibrato/envelope.
- WAV export.

### Role 2: Dataset and training

- Build `syntheticdataset/`.
- Validate data.
- Run organizer training code.
- Manage checkpoints.
- Compare metrics.

### Role 3: Evaluation and presentation

- Listen to generated audio.
- Plot examples.
- Prepare demo audio.
- Explain project logic.
- Prepare final pitch.

中文：

- 角色 1：负责合成器核心。
- 角色 2：负责数据集、训练、checkpoint。
- 角色 3：负责评估、可视化和展示。

---

## 15. Demo script / 展示脚本

### English

1. **Problem**: Real singing transcription data is expensive because audio must be manually annotated with precise onset, offset, and pitch.
2. **Idea**: Instead of recording and labeling real singers, we generate synthetic singing directly from existing note annotations.
3. **Our system**: Given a score TSV, our generator renders a vocal-like WAV while preserving the labels.
4. **Training**: We train the organizer-provided transcription model only on our synthetic data.
5. **Evaluation**: The final test checks whether the model can transcribe real singing.
6. **Key design**: We optimize not only for realistic sound, but for label-preserving diversity.

### 中文

1. **问题**：真实歌声转谱数据很贵，因为需要人工精确标注 onset、offset 和 pitch。
2. **想法**：我们不录真人歌声，而是直接根据已有音符标注生成合成歌声。
3. **我们的系统**：输入 score TSV，输出标签对齐的 vocal-like WAV。
4. **训练**：用我们的 synthetic data 训练主办方提供的 transcription model。
5. **评估**：最终看这个模型能不能识别真实歌声。
6. **关键设计**：我们不只追求好听，而是追求“标签准确 + 数据多样”。

---

## 16. Final one-sentence pitch / 一句话 Pitch

### English

We generate diverse, label-preserving synthetic vocal performances from note annotations, then train a singing transcription model to recover onset, offset, and pitch from real singing audio.

### 中文

我们从音符标注生成多样化但保持标签准确的合成歌声，再用这些数据训练歌声转谱模型，让模型能够从真实歌声中识别 onset、offset 和 pitch。
