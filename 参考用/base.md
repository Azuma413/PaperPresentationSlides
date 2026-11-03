# VLA Models Survey: Presentation Script & Slide Plan
## 論文紹介発表 原稿とスライド構成案

**Target duration / 想定時間:** 25–30 minutes
**Total slides / スライド総数:** 30 slides

### 構成 (Structure)
| Section | Slides | Pages |
|---|---|---|
| Title & Background | 1–4 | 4 slides |
| Paper 1 — UniT | 5–12 | 8 slides |
| Paper 2 — LaST-R1 | 13–22 | 10 slides |
| Paper 3 — Streaming Flow Policy | 23–30 | 8 slides |
| **Total** | | **30 slides** |

> ※ Conclusionスライドは削除し、Paper 2 (LaST-R1) を8枚→10枚に拡張して、原論文の重要な追加情報（pre-training datasets、Latent representation ablation、Adaptive reasoning length analysis、Action-to-vision attention など）を盛り込みました。

---

## Slide 1 — Title Slide

### Layout / レイアウト
- **Title (large, centered):** A Survey of Recent Advances in Vision–Language–Action Models
- **Subtitle:** Encoder, VLM, and Action Model Perspectives
- **Presenter:** Kaneyoshi Hiratsuka
- **Date / 日付:** (発表日)
- **Background image:** Fig. 1 from the resume placed faintly behind, or a single robot manipulation image

### Talking script — English
> Good afternoon, everyone. Today I will present a survey of three recent papers on Vision–Language–Action models, or VLAs, which are quickly becoming the standard architecture for general-purpose robotic manipulation. Rather than picking three random papers, I have selected one paper for each of the three structural components of a VLA — the encoder, the vision–language model, and the action model — so that we can see how the field is progressing along all three axes at once.

### Talking script — 日本語
> 皆さん、こんにちは。本日は、汎用ロボットマニピュレーションの標準アーキテクチャになりつつある「Vision–Language–Action（VLA）モデル」に関する最新の3本の論文を紹介します。3本の選び方には意図があって、VLAを構成する3つのモジュール — エンコーダ、Vision–Language Model（VLM）、Action Model — それぞれを代表する論文を1本ずつ選びました。これにより、VLA分野が3つの軸で同時にどう進化しているかを俯瞰できる構成になっています。

---

## Slide 2 — What is a VLA Model?

### Layout / レイアウト
- **Title:** What is a Vision–Language–Action (VLA) Model?
- **Center:** A simplified pipeline diagram:
  `[Camera image] + [Language instruction "Pick up the apple"] → [Neural Network] → [Robot actions]`
- **Right side bullets (concise):**
  - Inputs: images + natural language
  - Output: continuous robot actions
  - Goal: generalize across objects, scenes, instructions
- **Bottom:** Representative examples — *OpenVLA, π₀, GR00T*

### Talking script — English
> Let me first clarify what a VLA model is. A VLA takes two inputs — visual observations from the robot's cameras, and a natural-language instruction such as "pick up the apple and place it in the basket" — and directly outputs continuous robot actions, all within a single neural architecture. The dream is to do for robots what large language models did for text: train one big model on diverse data, and have it generalize across objects, environments, and instructions. Representative examples include OpenVLA, π-zero, and NVIDIA's GR00T family.

### Talking script — 日本語
> まずVLAモデルとは何かを簡単に説明します。VLAは2種類の入力を受け取ります。ひとつはロボットカメラからの画像、もうひとつは「リンゴを取ってかごに入れて」のような自然言語の指示です。これを単一のニューラルネットワークに通して、連続値のロボット動作を直接出力します。LLMが「テキストを大量に学習させればあらゆるタスクに汎化する」という発想だったのと同じように、VLAでは「多様なロボットデータで大きなモデルを学習すれば、物体・環境・指示に対して汎化するはず」というのが目標です。代表例としてOpenVLA、π-zero、そしてNVIDIAのGR00Tシリーズが挙げられます。

---

## Slide 3 — Three Building Blocks of a VLA

### Layout / レイアウト
- **Title:** A VLA = Encoder + VLM + Action Model
- **Center figure:** Fig. 1 from the resume (the GR00T-style architecture with three colored regions: Encoder / VLM / Action Decoder)
- **Annotations on the figure** (with arrows pointing to each block):
  - 🟦 **Encoder:** Raw observations → compact representation
  - 🟩 **VLM:** "What to do" — semantic & causal reasoning
  - 🟧 **Action Model:** "How to move" — continuous trajectories
- **Bottom caption:** "Each of the three papers we will discuss targets exactly one of these blocks."

### Talking script — English
> A modern VLA can be decomposed into three building blocks, and this decomposition is the key to today's talk. The Encoder turns raw pixels and proprioceptive states into compact representations. The VLM, which is essentially a vision–language model backbone, performs the high-level semantic reasoning — it decides *what* to do. And finally, the Action Model converts those high-level decisions into smooth, continuous trajectories that the robot's motors can actually execute — it decides *how* to move. The three papers I will present each target exactly one of these blocks, which is why I think they tell a connected story.

### Talking script — 日本語
> 現代のVLAは大きく3つのブロックに分解できます。これが本日の発表の骨格になります。まずEncoderは、生のピクセルや関節角度などの観測値を、コンパクトな表現に変換します。次にVLMは、いわばVision–Languageモデルのバックボーンで、「何をすべきか」という高レベルの意味的・因果的な推論を担当します。最後にAction Modelが、その高レベルの決定を、ロボットモータが実際に追従できる滑らかな連続軌道に変換する、つまり「どう動くか」を決めます。本日紹介する3本の論文は、ちょうどこの3つのブロックを1つずつターゲットにしているので、ばらばらの論文紹介ではなく、ひとつの繋がった物語として聞いていただけると思います。

---

## Slide 4 — Three Challenges & Today's Three Papers

### Layout / レイアウト
- **Title:** Three Open Challenges → Three Papers
- **Three-column table:**

| Component | Open Challenge | Today's Paper |
|---|---|---|
| 🟦 Encoder | Robot data is scarce; how to leverage human video? | **UniT** (Chen et al.) |
| 🟩 VLM | How to translate "thinking in language" into "thinking in the body"? | **LaST-R1** (Chen et al., 2026) |
| 🟧 Action Model | Diffusion/flow policies are expressive but slow | **Streaming Flow Policy** (Jiang et al.) |

- **Bottom takeaway:** "Three complementary contributions toward practical, general-purpose VLA."

### Talking script — English
> Despite rapid progress, the three components each face a hard open problem. On the Encoder side, robot demonstration data is orders of magnitude scarcer than the text used to train LLMs — how do we leverage abundant human video instead? On the VLM side, chain-of-thought reasoning works for text, but how do we extend "thinking in language" to "thinking in the body" with closed-loop physical control? And on the Action Model side, diffusion and flow-matching policies are very expressive, but they suffer from high inference latency. Each of the three papers we will see today tackles exactly one of these challenges: UniT for the encoder, LaST-R1 for the VLM, and Streaming Flow Policy for the action model.

### Talking script — 日本語
> 急速な進歩にもかかわらず、3つのコンポーネントにはそれぞれ大きな未解決問題があります。Encoder側では、ロボットの実演データはLLMの学習に使われるテキストに比べて何桁も少ない。じゃあ大量に手に入る人間の動画データをどう活用するか、という問題です。VLM側では、テキストではChain-of-Thoughtが効きますが、これを「身体で考える」、つまり閉ループの物理制御に拡張するにはどうするか。そしてAction Model側では、Diffusionやflow matchingベースのポリシーは表現力は高いものの、推論レイテンシが大きいという問題があります。本日紹介する3本は、ちょうどこの3つの課題に1対1で対応しています。エンコーダのUniT、VLMのLaST-R1、Action ModelのStreaming Flow Policyです。

---

# === PAPER 1: UniT (Slides 5–12) ===

## Slide 5 — Paper 1: UniT Overview

### Layout / レイアウト
- **Section divider style** (clear visual break)
- **Title:** Paper 1 — UniT
- **Subtitle:** Toward a Unified Physical Language for Human-to-Humanoid Policy Learning and World Modeling
- **Authors:** Chen et al.
- **One-line summary box:** *"A latent action tokenizer that bridges humans and humanoids by anchoring on visual outcomes."*
- **Three keywords (large):** *Visual Anchoring · Cross-Reconstruction · Embodiment-Agnostic*

### Talking script — English
> Let's start with the first paper, UniT. The one-line summary is: UniT introduces a latent action tokenizer that bridges humans and humanoids by *anchoring* on visual outcomes. Three keywords to keep in mind: visual anchoring, cross-reconstruction, and embodiment-agnostic.

### Talking script — 日本語
> では、1本目のUniTから始めます。1行で言うと、「人間とヒューマノイドの動きを、視覚的な結果に錨を下ろすことで橋渡しする潜在アクション・トークナイザ」です。覚えていただきたいキーワードは3つ、Visual Anchoring（視覚への錨）、Cross-Reconstruction（相互再構成）、Embodiment-Agnostic（身体性に依らない表現）です。

---

## Slide 6 — Background: Robot Data is Scarce

### Layout / レイアウト
- **Title:** Why look at humans? Robot data is scarce.
- **Left: bar chart (visual)**
  - LLM training tokens: 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 (10+ trillion)
  - Robot trajectories: 🟧 (~millions, dramatically shorter)
- **Right:**
  - ✅ Egocentric human videos = abundant, rich physical priors
  - ❌ But: humans ≠ humanoids (DoF, control modes, action params differ)
  - ❌ Classical fix: IK-based retargeting → labor-intensive, physically inconsistent
- **Bottom:** "Solution direction: *learn a shared latent action space.*"

### Talking script — English
> Why is this paper looking at humans at all? Because LLMs were trained on tens of trillions of tokens, while robot demonstration datasets contain at most a few million trajectories. The gap is enormous. Egocentric human videos, on the other hand, can be collected at massive scale and they contain rich physical interaction priors — exactly what we need. The problem is that humans and humanoids differ in degrees of freedom, control modes, and action parameterization. The classical fix is inverse-kinematics retargeting, but that is case-by-case, labor-intensive, and often physically inconsistent. So the recent direction is to absorb embodiment differences at the *representation* level, by learning a shared latent action space.

### Talking script — 日本語
> なぜわざわざ人間に目を向けるのか。LLMが何十兆トークンも学習しているのに対して、ロボットの実演データはせいぜい数百万軌道です。スケールが何桁も違います。一方、一人称視点の人間の動画は大量に集められて、しかも物理的な相互作用のリッチな事前知識を含んでいる。まさに欲しいものなんです。問題は、人間とヒューマノイドでは自由度、制御モード、行動パラメータがどれも違うこと。古典的な解決策はIKによるリターゲティングですが、ケースバイケースで手間がかかり、物理的に矛盾することも多い。そこで最近の方向性は、身体性の違いを「表現のレベル」で吸収しよう、つまり共有の潜在アクション空間を学習しようというものです。

---

## Slide 7 — Existing Latent Action Paradigms (and their flaws)

### Layout / レイアウト
- **Title:** Existing approaches & their limitations
- **Main visual:** Fig. 2 from the resume (the four-panel comparison: action-only / vision-only / decoupled / UniT)
- **Annotation under each panel:**
  - (a) Action-only → ❌ no visual grounding, distribution shift
  - (b) Vision-only → ❌ entangled with lighting/textures, loses motor precision
  - (c) Decoupled V+A → ❌ disjoint vocabularies, no shared structure
  - (d) **UniT (Ours)** → ✅ mutually reconstructed, vision as universal anchor

### Talking script — English
> The authors of UniT classify existing latent-action methods into three categories, shown in panels (a), (b), and (c). Action-only methods tokenize only the actions, but without any visual grounding they are vulnerable to distribution shift. Vision-only methods avoid the kinematic mismatch but tend to entangle low-level appearance confounders such as lighting and texture, which hurts motor precision. Decoupled vision–action methods tokenize the two modalities separately, but the two vocabularies end up disjoint and fail to capture shared physical structure. UniT, in panel (d), takes a different stance: vision and action are *mutually reconstructed*, with vision serving as the universal anchor across embodiments.

### Talking script — 日本語
> UniTの著者らは、既存の潜在アクション手法を3つに分類しています。図の(a)(b)(c)です。(a)Action-only法はアクションだけをトークン化しますが、視覚的な接地がないため分布シフトに弱い。(b)Vision-only法は運動学のミスマッチは回避できるものの、照明やテクスチャといった見た目の余計な要因が絡んでしまい、モータ精度が落ちる。(c)Decoupled法は視覚とアクションを別々にトークン化しますが、語彙が分離してしまい、両者に共通する物理構造を捉えられない。これに対してUniTは(d)、視覚とアクションを「相互に再構成しあう」というスタンスを取ります。視覚を、身体性をまたぐ普遍的な錨として使うのが要です。

---

## Slide 8 — UniT Architecture

### Layout / レイアウト
- **Title:** UniT Architecture: Three encoders, one shared codebook
- **Main visual:** Fig. 3 from the resume (the tri-branch encoder + RQ-VAE + dual decoders)
- **Annotations:**
  - **Visual branch** (input: DINOv2 features of o_t, o_{t+k}) → inverse-dynamics latent
  - **Action branch** (input: state s_t, action chunk a_{t:t+k}) → motor-control latent
  - **Fusion branch** (V + A) → visuo-motor latent
  - All three → quantized via shared **RQ-VAE codebook** → **Unified Latent Action tokens**
  - Decoded by: shared **vision decoder** + embodiment-specific **action decoder**

### Talking script — English
> Now the architecture. UniT takes as input an observation pair at times t and t+k, the current robot state, and the action chunk between them. Three parallel transformer encoders process this information. The visual branch consumes frozen DINOv2 features and behaves like an inverse-dynamics model — it asks "what action explains this visual transition?". The action branch encodes the state and action chunk through embodiment-specific MLPs and a shared transformer to produce a motor-control latent. The fusion branch combines both modalities. The continuous outputs of all three branches are then quantized into a *shared* discrete codebook using a Residual Quantization VAE, producing what the authors call Unified Latent Action tokens. Every quantized token is then decoded both by a shared visual decoder and by an embodiment-specific action decoder.

### Talking script — 日本語
> アーキテクチャを見ていきます。UniTは、時刻tとt+kの観測ペア、現在のロボット状態、その間のアクションチャンクを入力にします。これを3つの並列なTransformerエンコーダで処理します。Visual branchは、凍結されたDINOv2の特徴量を入力に取り、逆動力学モデルのように振る舞います。つまり「この見た目の変化を説明するアクションは何か?」を考えるブランチです。Action branchは、状態とアクションチャンクを身体性ごとのMLPと共有Transformerに通して、モータ制御の潜在表現を作ります。Fusion branchは両方を統合する役目です。3つのブランチの連続的な出力を、Residual Quantization VAEで「共有の」離散コードブックに量子化します。これが論文の言うUnified Latent Actionトークンです。そして各量子化トークンを、共有のVisual Decoderと、身体性ごとのAction Decoderの両方でデコードします。

---

## Slide 9 — Cross-Reconstruction: The Key Idea

### Layout / レイアウト
- **Title:** The key idea: *Cross-Reconstruction*
- **Center: equation box** (large, readable):

$$\mathcal{L} = \sum_{i \in \{v, a, m\}} \left[ \lambda_v \mathcal{L}_{\cos}(\hat{f}^{(i)}_{t+k}, f_{t+k}) + \lambda_a \mathcal{L}_{\text{act}}(\hat{a}^{(i)}_{t:t+k}, a_{t:t+k}) \right] + \mathcal{L}_{\text{RQ}}$$

- **Two boxes below the equation:**
  - 📦 **Action features → predict visual outcome:** kinematics anchored to pixel-space consequences
  - 📦 **Visual features → reconstruct action:** strips away appearance noise (lighting, texture)
- **Punchline (highlighted):**
  *"What survives the bottleneck = embodiment-agnostic physical intent."*

### Talking script — English
> Here is the heart of the paper, and it is conceptually elegant. Look at the loss. For *every* branch — visual, action, and fusion — both decoders are used. That means: action features are required to predict the future visual outcome, and visual features are required to reconstruct the action. Why does this work? Forcing action features to predict visual consequences anchors heterogeneous kinematics to the same pixel-space outcomes, so a human arm motion and a humanoid arm motion that produce the same visual effect end up at the same token. Conversely, requiring visual features to reconstruct actions strips away appearance noise that has no motor counterpart — lighting and texture cannot help reconstruct an action, so they are filtered out. What survives this two-way bottleneck is precisely the intersection: an embodiment-agnostic physical intent.

### Talking script — 日本語
> ここがこの論文のいちばん美しいアイデアです。損失関数を見てください。Visual、Action、Fusionのどのブランチに対しても、両方のデコーダで再構成させているんです。つまり、アクションの特徴量から将来の視覚的結果を予測させ、視覚の特徴量からアクションを再構成させる。なぜこれが効くのか。アクション特徴量に視覚的結果を予測させることで、異なる身体性の運動学が同じピクセル空間の結果に錨付けされる。同じ視覚的効果を生む人間の腕の動きとヒューマノイドの腕の動きが、同じトークンに対応するようになる。逆方向に、視覚特徴量からアクションを再構成させると、運動とは無関係な見た目のノイズが排除されます。照明やテクスチャはアクションの再構成に役立たないので、ボトルネックで自動的に削ぎ落とされるわけです。この双方向のボトルネックを生き残るものこそが、まさに2つのモダリティの「交差」、つまり身体性に依らない物理的意図というわけです。

---

## Slide 10 — Downstream Use: VLA-UniT & WM-UniT

### Layout / レイアウト
- **Title:** Two downstream paradigms
- **Two-column layout:**

| **VLA-UniT** (policy) | **WM-UniT** (world model) |
|---|---|
| Built on GR00T n1.5 + Qwen2.5-VL backbone | Built on NVIDIA Cosmos Predict 2.5 |
| VLM predicts **UniT tokens** from image + instruction | Continuous **pre-quantization** features as conditioning |
| Lightweight flow-matching head → embodiment-specific actions | Replaces raw action conditioning |

- **Bottom:** Same token vocabulary serves both policy and world model.

### Talking script — English
> The authors deploy UniT in two downstream paradigms. The first, VLA-UniT, is a policy. It is built on the GR00T n1.5 architecture with a Qwen2.5-VL backbone. The VLM takes the image and language instruction and predicts UniT tokens — the same tokens we just trained — and a lightweight flow-matching head turns those tokens into embodiment-specific continuous actions. The second, WM-UniT, is a world model. It uses the *continuous, pre-quantization* features of UniT as the conditioning signal for the Cosmos Predict 2.5 video generator, replacing raw action conditioning. The clean message here is that one tokenizer simultaneously serves both the action side and the world-modeling side.

### Talking script — 日本語
> UniTトークンの使い道は2つ用意されています。1つ目のVLA-UniTはポリシーで、GR00T n1.5アーキテクチャ上にQwen2.5-VLバックボーンを載せた構成です。VLMが画像と言語指示からUniTトークン、つまりさっき学習したのと同じトークンを予測し、軽量なflow-matchingヘッドがそのトークンを身体性ごとの連続アクションに変換します。2つ目のWM-UniTはワールドモデルで、UniTの「量子化前の」連続特徴量を、Cosmos Predict 2.5という動画生成モデルの条件付け信号として使います。生のアクションで条件付けるのを置き換えるわけです。要するに、ひとつのトークナイザがポリシーとワールドモデルの両方を同時に支えるという、きれいなメッセージになっています。

---

## Slide 11 — Results: Simulation & Few-Shot

### Layout / レイアウト
- **Title:** Results in simulation: substantial gains, especially in low-data
- **Left: simple bar chart (RoboCasa GR1, average success rate):**
  - GR00T-Qwen2.5 (no UniT): **47.8%**
  - VLA-UniT (full data): **66.7%** ⬆ **+18.9 pts**
  - VLA-UniT (10% data, few-shot): **45.5%** (≈ full-data baselines)
- **Right: short bullet points:**
  - Outperforms UWM, Diffusion Policy, FLARE, GR00T-N1.6, π-Qwen3, FAST-Qwen3, OFT-Qwen3
  - Co-training with EgoDex: in-dist. **+3.3 pts**, OOD **34.7% → 38.5%**
- **Takeaway box:** "UniT helps most where data is scarce or OOD — exactly where we need it."

### Talking script — English
> Let's look at simulation results on the RoboCasa GR1 benchmark, which covers 24 tabletop tasks. With full data, VLA-UniT reaches 66.7% average success rate, compared with 47.8% for the same architecture without UniT token prediction. That's an 18.9-point improvement that directly quantifies the contribution of UniT as a learning objective. The few-shot result is perhaps even more impressive: with only 10% of the training data, VLA-UniT still reaches 45.5%, essentially matching baselines trained on the full dataset. And co-training with the EgoDex human video dataset further raises out-of-distribution success from 34.7% to 38.5%. The takeaway is that UniT helps most precisely where we need help — in low-data and OOD settings.

### Talking script — 日本語
> シミュレーション結果を見ます。RoboCasa GR1という24個のタスクからなるベンチマークです。フルデータ条件で、VLA-UniTは平均成功率66.7%。UniTトークン予測なしの同アーキテクチャ(GR00T-Qwen2.5)は47.8%なので、18.9ポイントの差です。これはまさに「UniTを学習目的に加えた効果」が定量化されたものと言えます。さらに印象的なのはfew-shot条件で、訓練データの10%しか使わなくても45.5%に達して、フルデータの他のベースラインとほぼ並びます。EgoDexという人間動画データセットとの共学習でOOD成功率も34.7%→38.5%に上がっています。一番嬉しい性質は、まさに「データが少ない・分布外」という困った場面で最も効くことです。

---

## Slide 12 — Results: Real-World & World Modeling

### Layout / レイアウト
- **Title:** Real robot + emergent behaviors
- **Left (real-world robot, IRON-R01 humanoid):**
  - Pick & Place: **78%** success
  - Bimanual Pouring: **75%** success
  - Unseen **Stacking** (human-augmented): **60%** — emergent waist rotation, head turning
- **Right (world modeling on DROID):**
  - UniT-conditioned > raw-action / action-only-latent on PSNR, SSIM, LPIPS, FVD, **EPE**
  - Cross-embodiment study (Gemini-3-Pro judge): WM-UniT wins on semantic / temporal / geometric axes
- **Takeaway:** "Same token vocabulary transfers across **embodiments** *and* across **policy ↔ world model**."

### Talking script — English
> Moving to real-world experiments on the IRON-R01 humanoid. VLA-UniT reaches 78% on Pick & Place and 75% on bimanual pouring, well above the GR00T baseline. The most exciting result is on an unseen Stacking task: only the variant co-trained on human videos succeeds, at 60%, and the authors observe emergent whole-body behaviors like waist rotation and head turning — behaviors that were never demonstrated by the humanoid itself, only by humans. On the world-modeling side, UniT-conditioned generation on DROID beats both raw-action conditioning and action-only-latent conditioning across all standard video-quality metrics — PSNR, SSIM, LPIPS, FVD — and especially on the endpoint controllability metric EPE. So the same token vocabulary transfers both across embodiments and across the policy–versus–world-model boundary, which is exactly what you want from a "unified physical language".

### Talking script — 日本語
> 実機実験はIRON-R01ヒューマノイドで行われています。VLA-UniTはPick & Placeで78%、両腕の注ぐタスクで75%と、GR00Tベースラインを大きく上回っています。特に面白いのは未学習のStackingタスクで、人間の動画と共学習したバリアントだけが60%成功し、しかも腰の回転や頭の向きを変えるといった、ヒューマノイド自身は実演されていない、人間からしか観測できなかった全身協調動作が「創発」しています。ワールドモデル側では、DROIDデータセット上のUniT条件付き生成が、生アクション条件付けやアクションのみの潜在条件付けを、PSNR、SSIM、LPIPS、FVDといった標準動画品質指標で全勝、特にコントローラビリティ指標EPEで大差で勝っています。つまり、同じトークン語彙が「身体性をまたぐ転移」と「ポリシー↔ワールドモデルをまたぐ転移」の両方で機能している。まさに著者らの言う「統一された物理言語」の名にふさわしい結果と言えます。

---

# === PAPER 2: LaST-R1 (Slides 13–22, 10 slides) ===

## Slide 13 — Paper 2: LaST-R1 Overview

### Layout / レイアウト
- **Section divider style**
- **Title:** Paper 2 — LaST-R1
- **Subtitle:** Reinforcing Robotic Manipulation via Adaptive Physical Latent Reasoning
- **Authors:** Chen, Liu, Yan, Han et al. (CUHK + PKU + Simplexity Robotics, 2026)
- **Project page:** https://siriyep.github.io/last-r1/
- **One-line summary:** *"The first RL post-training framework that jointly optimizes latent reasoning AND action generation."*
- **Three keywords:** *Latent CoT · LAPO (PPO on latents) · Adaptive Reasoning Length*

### Talking script — English
> Now we move to Paper 2: LaST-R1. The one-line summary is that this is the first reinforcement-learning post-training framework specifically designed for VLA models that *reason before acting*. It jointly optimizes the latent reasoning process and the action generation. The three keywords here are Latent Chain-of-Thought, LAPO — which stands for Latent-to-Action Policy Optimization — and adaptive reasoning length. This paper is a collaboration between CUHK, Peking University, and Simplexity Robotics.

### Talking script — 日本語
> 続いて2本目、LaST-R1です。1行で言うと、「行動前に推論する」タイプのVLAモデルに対する、初の強化学習ベースのPost-trainingフレームワークです。潜在的な推論プロセスとアクション生成を同時最適化します。キーワードは3つ、Latent Chain-of-Thought（潜在的な思考連鎖）、LAPO（Latent-to-Action Policy Optimizationの略）、そして適応的推論長です。著者は香港中文大学、北京大学、Simplexity Roboticsの共同研究です。

---

## Slide 14 — Background: Vanilla VLA RL vs LaST-R1

### Layout / レイアウト
- **Title:** What is missing in existing VLA RL?
- **Main visual:** Fig. 1 (a) vs (b) from the LaST-R1 paper, side-by-side
  - **(a) Vanilla VLA RL:** observation → Action-Only Policy → Action Generation → Reward → RL update (only actions)
  - **(b) LaST-R1 + LAPO:** observation → Adaptive Latent CoT → Action Generation → Reward → RL updates **both latents and actions**
- **Side notes:**
  - "Latent reasoning" = high-dim feature-space deliberation (NOT natural-language CoT)
  - Existing RL: optimizes only the **action space**, bypasses internal reasoning
  - LaST-R1: lets reward signals **directly shape the reasoning space too**

### Talking script — English
> Why do we need this paper? Look at the figure. Panel (a) shows vanilla VLA RL: the model produces actions, the environment gives a reward, and RL updates only the action policy. The internal reasoning, if any exists, is completely bypassed. Panel (b) shows LaST-R1's approach: the model first does latent reasoning, then produces actions, and crucially the reward signal flows back to update *both* the latent reasoning and the action generation. Let me clarify the term: "latent reasoning" here is deliberation in a high-dimensional feature space, not in natural language tokens. It is analogous to chain-of-thought in LLMs, but it is tightly coupled with action generation and carries denser physical information.

### Talking script — 日本語
> なぜこの論文が必要か。図を見てください。(a)が従来のVLA RLで、モデルがアクションを出し、環境が報酬を返し、RLでアクションポリシーだけを更新する。仮に内部推論があっても、そこは完全にスキップされてしまう。(b)がLaST-R1のアプローチで、モデルがまず潜在的に推論し、それからアクションを生成する。そして決定的に重要なのは、報酬信号が潜在推論とアクション生成の「両方」に逆伝播する点です。用語の整理として、ここで言う「潜在推論」は自然言語トークンではなく高次元な特徴空間での思考のこと。LLMのChain-of-Thoughtの類似物ですが、アクション生成と密結合していて、より密な物理情報を運ぶ点が違います。

---

## Slide 15 — LaST-R1 VLA Architecture

### Layout / レイアウト
- **Title:** Architecture: Latent reasoning → parallel action decoding
- **Main visual:** Fig. 2(a) from the LaST-R1 paper (Visual Encoder → DINOv3 latent GT → LLM Backbone → latent embeddings → action tokens)
- **Pipeline annotations:**
  1. Image + instruction → **Qwen3-VL-4B** + SigLIP2-Large encoder (visual emb. ∈ ℝ^{N_v×2560})
  2. LLM backbone **autoregressively** emits a sequence of **latent reasoning embeddings**
  3. Terminated by `<latent_end>` token
  4. **Parallel** action decoding (single forward pass, action chunk H=8)
  5. Value head (4-layer MLP, shared backbone) for advantage estimation
- **Side panel — Hybrid Attention Mask (Fig. 7):**
  - 🔻 Vision+Text+Latent: **causal mask** (autoregressive)
  - 🔁 `<Latent_end>` + Action tokens: **bidirectional mask** (parallel)

### Talking script — English
> The architecture is built on Qwen3-VL-4B with a SigLIP2-Large visual encoder. Given the image and instruction, the backbone first autoregressively produces a sequence of latent reasoning embeddings — these are continuous vectors, not language tokens. The sequence is terminated by a special `<latent_end>` token. Then comes a nice design choice: continuous actions are produced in *parallel* with bidirectional attention in a single forward pass. The chunk size is 8, yielding 56 action tokens per chunk. A 4-layer MLP value head sharing the same backbone is used for advantage estimation. The key technical trick that makes this efficient is a custom hybrid attention mask: causal for the vision-text-latent prefix, and bidirectional for the action tokens. So you get the autoregressive reasoning capability of an LLM and the parallel decoding speed for actions, in one model.

### Talking script — 日本語
> アーキテクチャはQwen3-VL-4BにSigLIP2-Largeの視覚エンコーダを載せた構成です。画像と指示が与えられると、バックボーンがまず一連の「潜在推論埋め込み」を自己回帰的に生成します。これは言語トークンではなく連続ベクトル。そして`<latent_end>`トークンで終端します。ここからが綺麗な設計で、連続アクションは双方向アテンションで「並列に」、1回のforward passで生成します。チャンクサイズは8で、計56個のアクショントークンが並列出力されます。アドバンテージ推定にはバックボーン共有の4層MLPのvalue headを使用。これを効率的にしている技術的トリックがハイブリッドアテンションマスクで、Vision+Text+Latentの部分は因果(causal)マスクで自己回帰、`<latent_end>`以降のアクショントークンは双方向(bidirectional)マスクで並列、という設計になっています。LLMの自己回帰的推論能力とアクションの並列デコード速度を、1つのモデルで両立しているわけです。

---

## Slide 16 — Latent Targets: Why DINOv3 <CLS>?

### Layout / レイアウト
- **Title:** What should the latent embeddings target?
- **Main idea (highlighted):** Latent reasoning targets = **⟨CLS⟩ token of DINOv3** with channel-wise top-k selection (k = 2560)
- **Why this choice?**
  - 🔧 Precomputed **offline** → **zero extra inference cost**
  - 🌍 DINOv3 = SOTA vision foundation model → rich semantic + spatial prior
  - 🎯 Top-k selection retains the most salient channels, matches VLA hidden size
- **Ablation visual (Fig. 4a):**
  - Global Pooling: 96.8%
  - Convolution: 98.4%
  - Q-Former: 97.2%
  - **DINOv3 ⟨CLS⟩ top-k (Ours): 99.8%** ✅

### Talking script — English
> One subtle but important design decision: what should the latent embeddings actually predict? Prior methods use average pooling of the VLA's own visual features, or learnable Q-Former queries. The authors instead use the ⟨CLS⟩ token of DINOv3 — a state-of-the-art vision foundation model — and apply top-k channel selection with k equals 2560, which conveniently matches the VLA's hidden size. The critical engineering benefit is that these targets are precomputed *offline*, so there is zero extra inference cost at deployment. The ablation in Figure 4(a) directly compares this choice: global pooling gives 96.8%, convolution 98.4%, Q-Former 97.2%, and DINOv3 with top-k selection achieves 99.8%. The DINOv3 representation wins by 1.4 to 3 points over the alternatives, validating that leveraging a powerful pretrained foundation model is better than learning the latent target from scratch.

### Talking script — 日本語
> 細かいけれど重要な設計判断を一つ。「潜在埋め込みは具体的に何を予測するのか」という問いです。先行手法はVLA自身の視覚特徴を平均プーリングしたり、Q-Formerの学習可能クエリで集約したりしていました。本論文はそれに代えて、最新の視覚基盤モデルDINOv3の⟨CLS⟩トークンを使い、チャネル方向にtop-k(k=2560)で選択する。kはVLAの隠れ次元と一致するように選ばれています。エンジニアリング上の最大のメリットは、これらのターゲットを「オフラインで事前計算」できる点で、推論時の追加コストがゼロになる。図4(a)のablationで設計選択が直接比較されていて、Global Pooling 96.8%、Convolution 98.4%、Q-Former 97.2%、DINOv3 + top-k(本論文) 99.8%。代替案より1.4〜3ポイント差で勝っていて、強力な事前学習済み基盤モデルを使う方が、ゼロから潜在ターゲットを学習させるより良いことが実証されています。

---

## Slide 17 — LAPO: PPO on Latents + Actions

### Layout / レイアウト
- **Title:** LAPO — Latent-to-Action Policy Optimization
- **Two equations side by side:**
  - **Action ratio (categorical):**
    $r^a_t(\theta) = \exp(\log \pi_\theta(C_t) - \log \pi_{\theta_{\text{old}}}(C_t))$
  - **Latent ratio (closed form from isotropic Gaussian):**
    $r^z_t(\theta) = \exp\!\left(-\frac{1}{2\sigma^2} \sum_{i=1}^{N_z} \|z^{\text{old}}_{t,i} - z^\theta_{t,i}\|^2 \right)$
- **Derivation hint (small):** old policy mean = $z^{\text{old}}_t$, so $\pi_{\theta_{\text{old}}}(z^{\text{old}}_t) =$ const → normalization cancels.
- **Clipped surrogate loss (joint over latent + action):**
  $\mathcal{L}_{\text{policy}}(\theta) = -\mathbb{E}_t \sum_{k\in\{z,a\}} \min(r^k_t \hat{A}_t, \text{clip}(r^k_t, 1-\epsilon_{\min}, 1+\epsilon_{\max}) \hat{A}_t)$
- **Total loss:** $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{action}} + \lambda_1 \mathcal{L}_{\text{latent}} + \lambda_2 \mathcal{L}_{\text{value}}$
- **Optimal weights (ablation):** $\lambda_1=0.1, \lambda_2=1, \lambda_3=0.1$ → **99.8%**

### Talking script — English
> The core contribution is LAPO, which is essentially PPO but treating latent embeddings as implicit decision variables alongside actions. For discrete actions, the standard categorical importance ratio is used. For the *continuous* latent embeddings, LAPO approximates the rollout distribution by an isotropic Gaussian centered at the current policy output. The derivation is elegant: since the old policy's mean is by definition the sampled latent itself, the old policy's density evaluated at its own sample is just the normalization constant — which cancels with the numerator's normalization. What's left is a clean closed-form ratio: exponential of negative-half-sigma-squared times the sum of squared latent distances. The clipped surrogate loss is then formed jointly over both ratios, with advantages from Generalized Advantage Estimation. Intuitively, when advantage is positive, the optimization pulls the current policy's latent embeddings toward the "good-reasoning" manifold that produced successful trajectories. The authors do an ablation on the weighting coefficients and find lambda-1=0.1, lambda-2=1, lambda-3=0.1 to be optimal.

### Talking script — 日本語
> LaST-R1の中核がLAPOで、PPOのアクションに並んで「潜在埋め込みも暗黙の決定変数」として扱う点が新しい。離散アクションには標準のカテゴリカル重要度比を使います。連続な潜在埋め込みに対しては、ロールアウト分布を「現在のポリシー出力を中心とする等方Gaussian」で近似します。導出が綺麗で、旧ポリシーの平均は定義上「サンプリングされた潜在変数そのもの」なので、旧ポリシーの密度をその自分自身のサンプルで評価すると単に正規化定数になり、分子の正規化と相殺される。結果として、−1/(2σ²)×潜在距離の二乗和、を指数の肩に乗せたきれいな閉形式になります。Clipped Surrogate Lossを両方の比に対して同時に構成し、アドバンテージはGAEで計算する。直感的には、アドバンテージが正のとき、潜在埋め込みが「成功軌道を生んだ良い推論の多様体」に引き寄せられる。著者らは損失重みのablationもしていて、λ₁=0.1, λ₂=1, λ₃=0.1が最適とのこと。

---

## Slide 18 — Adaptive Latent CoT: How long to think?

### Layout / レイアウト
- **Title:** Adaptive Latent CoT — variable reasoning length
- **Schematic on the left:**
  - Max length $N_{\max} = 8$
  - $M$ candidate exit positions (best: **M = 4**)
  - Inference exit rule: emit `<latent_end>` when $p \geq 0.99$
- **Right: equation**

$$p_m = \frac{\exp(l_m / \beta)}{\sum_{i=1}^M \exp(l_i / \beta)}, \quad m \sim \text{Categorical}(p_1, \dots, p_M)$$

- **Below: ablation on M (Fig. 4c):**
  - M=1: 98.4% (fixed length)
  - M=2: 99.2%
  - **M=4: 99.8% ← best**
  - M=8: 99.0% (too much flexibility → instability)
- **Transition-token loss:** $\mathcal{L}_{\text{end}}$ added with weight $\lambda_3$

### Talking script — English
> One more piece — the adaptive latent CoT mechanism. Not every state needs the same amount of deliberation; trivial steps should be fast, hard steps should think longer. So the model is allowed to vary its reasoning horizon. Within a maximum length of 8, the special `<latent_end>` token can only be emitted at M predefined candidate positions. At inference, the model exits as soon as the exit probability exceeds 0.99. During RL rollouts, candidate lengths are sampled from a temperature-controlled categorical distribution, and a separate transition-token loss encourages the model to learn *when* to exit. The ablation in Figure 4(c) is interesting: M=1 is fixed-length at 98.4%, M=4 gives the best 99.8%, but M=8 — allowing exit after every single latent token — actually drops back to 99.0%. So too much flexibility hurts, and a moderately constrained M=4 is the sweet spot between flexibility and optimization stability.

### Talking script — 日本語
> もうひとつ、適応的なLatent CoT機構があります。全ての状態が同じ深さの思考を必要とするわけではなくて、簡単な場面はサッと、難しい場面はじっくり考えたい。そこでモデルが推論長を可変にできるようにしてあります。最大長は8、`<latent_end>`はあらかじめ決まったM個の位置でしか出せない。推論時は、終了確率が0.99を超えたら即座に抜けます。RLロールアウト中は、候補長を温度付きカテゴリカル分布からサンプリングし、終了トークン専用の損失も加える。図4(c)のablationが面白くて、M=1（固定長）で98.4%、M=4が最良の99.8%、ところがM=8（毎ステップ抜けられる）にすると99.0%まで戻ってしまう。つまり「柔軟性を与えすぎても駄目」で、M=4が柔軟性と最適化安定性のスイートスポット、ということです。

---

## Slide 19 — Results: LIBERO Simulation (Main Table)

### Layout / レイアウト
- **Title:** Near-perfect LIBERO with only one-shot SFT warm-up
- **Compact table (Table 1 from paper) showing top entries only:**

| Method | Paradigm | Spatial | Object | Goal | Long | **Avg** |
|---|---|---|---|---|---|---|
| OpenVLA-OFT | SFT | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 |
| π₀.₅ | SFT | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| SimpleVLA-RL | RL | 98.2 | 98.7 | 98.8 | 91.7 | 96.9 |
| RLinf-GRPO | RL | 98.9 | 99.7 | 98.3 | 93.6 | 97.6 |
| πRL | RL | 99.6 | 100.0 | 99.6 | 94.0 | 98.3 |
| **LaST-R1 (Ours)** | **RL** | **99.8** | **100.0** | **100.0** | **99.8** | **99.9** |

- **Highlight:** LIBERO-Long: **99.8% vs 94.0%** (next-best RL) — **+5.8 points** on long-horizon!
- **Data regime:** Only **one-trajectory** SFT warm-up + online RL
- **Note:** Beats even **SFT baselines trained on full data**

### Talking script — English
> Now the main results. In simulation, LaST-R1 is evaluated on the LIBERO benchmark with four task suites — Spatial, Object, Goal, and Long — with ten tasks each. The data regime is intentionally harsh: only *one-shot* SFT warm-up per task, followed by online RL. Even so, LaST-R1 reaches 99.9% average success, ranking first on every suite. Notice the bottom block of the table: LaST-R1 beats SFT baselines like OpenVLA-OFT and π-zero-point-five even though they were trained on the *full* dataset of 50 trajectories per task. The advantage is most pronounced on LIBERO-Long, where LaST-R1 hits 99.8% versus 94.0% for the next-best RL baseline πRL — a 5.8-point gap on long-horizon tasks, where latent CoT really pays off.

### Talking script — 日本語
> 主結果に行きます。LIBEROベンチマークはSpatial、Object、Goal、Longの4スイート各10タスクで構成されます。データ条件はかなり厳しく、SFT warm-upは「ワンショット」、つまり各タスクで1軌道だけ使い、その後オンラインRLです。それでもLaST-R1は平均成功率99.9%、全スイートで1位。表の下段に注目すると、LaST-R1は各タスク50軌道のフルデータで訓練されたSFTベースライン（OpenVLA-OFTやπ₀.₅）すらも上回っています。差が最も顕著なのはLIBERO-Longで、LaST-R1の99.8%に対して次点のRLベースラインπRLは94.0%。長期視野タスクではLatent CoTの本領が発揮される、5.8ポイント差です。

---

## Slide 20 — Real-World Franka: Tasks & Results

### Layout / レイアウト
- **Title:** Real-world: Franka Research 3, 4 tasks (1 single-arm + 3 dual-arm)
- **Top: task strip (icons or thumbnails of Fig. 12)**
  - 1️⃣ Insert hexagon block (single-arm, precision insertion)
  - 2️⃣ Open bag zipper (dual-arm, deformable object)
  - 3️⃣ Wipe vase with sponge (dual-arm, curved trajectory)
  - 4️⃣ Open bottle cap (dual-arm, rotational manipulation)
- **Bottom: Table 2 — Main results vs π₀.₅:**

| Task | π₀.₅ (Full SFT 100 trajs) | LaST-R1 (SFT 30 + RL) |
|---|---|---|
| Insert hexagon block | 65 | 45 → **90** |
| Open bag zipper | 75 | 55 → **95** |
| Wipe vase with sponge | 75 | 65 → **95** |
| Open bottle cap | 70 | 45 → **95** |
| **Average** | **71.25%** | **52.5% → 93.75%** ⬆ +22.5pt |

- **Key efficiency:** Only **30 demos/task** + LoRA rank 32 (vs π₀.₅'s 100 trajs full SFT)

### Talking script — English
> The real-world experiments are on a Franka Research 3 platform, with four tasks shown across the top. A single-arm hexagon block insertion, and three dual-arm tasks: opening a bag zipper, wiping a vase with a sponge, and opening a bottle cap. Each tests a different physical skill — precision insertion, deformable-object manipulation, curved-trajectory contact, and coordinated rotational manipulation. The result table is striking. With only 30 trajectories per task for SFT warm-up — less than a third of the 100 trajectories that the full-SFT π-zero-point-five baseline uses — and updating only LoRA parameters of rank 32 during online RL, LaST-R1 goes from 52.5% to 93.75% average success rate, beating π-zero-point-five by 22.5 points. Particularly dramatic is the bottle cap task, which goes from 45% all the way to 95% after RL — a 50-point gain that signals the policy has learned to model the temporally evolving rotational dynamics.

### Talking script — 日本語
> 実機実験はFranka Research 3で、上段に並べた4タスクで行われています。単腕の六角形ブロック挿入と、両腕タスクが3つ：バッグのジッパー開け、スポンジで花瓶を拭く、ボトルキャップを開ける。それぞれ異なる物理スキルを試していて、精密挿入、変形物体の操作、曲面軌道での接触、協調的な回転操作です。下の表が衝撃的で、各タスク30軌道のSFT warm-up（フルSFTのπ₀.₅は100軌道なので3分の1未満）と、オンラインRLでLoRA rank 32のパラメータだけ更新する条件で、LaST-R1は52.5%→93.75%まで上昇し、π₀.₅を22.5ポイント上回ります。特に劇的なのがbottle capタスクで、45%→95%（+50ポイント）、これは時間発展する回転動力学をモデル化する能力を獲得した、と言えるレベルの伸びです。

---

## Slide 21 — Real-World Generalization Under Perturbations

### Layout / レイアウト
- **Title:** Robustness under unseen objects / backgrounds / lighting
- **Visual:** Image strip from Fig. 13 (4 tasks, each showing 3 perturbation cases with red bounding boxes)
- **Comparison table (Table 2 OOD columns, drop from original):**

| Method | Unseen-Object | -Background | -Lighting |
|---|---|---|---|
| π₀.₅ (Full SFT) | up to **−45%** | up to −15% | up to **−25%** |
| **LaST-R1** | within **−15%** | **−0% to −15%** | **−0% to −10%** |

- **Bottom box (highlighted):**
  - "π₀.₅ collapses; LaST-R1 stays robust."
  - "Near-zero degradation against background or lighting changes."

### Talking script — English
> Robustness is where the gap becomes most dramatic. The image strip at the top shows the same four tasks but under three kinds of perturbation: unseen objects, unseen backgrounds, and unseen lighting — highlighted in the red bounding boxes. The table summarizes the worst-case performance drops. The full-SFT π-zero-point-five baseline collapses, with up to a 45-point drop when interacting with unseen objects. LaST-R1, in contrast, stays within 15 points across the board, and shows nearly zero degradation against background or lighting changes. The authors argue that optimizing latent reasoning through environmental feedback intrinsically fortifies the model against environmental uncertainty — the policy is forced to learn transferable physical concepts, not just kinematic patterns.

### Talking script — 日本語
> ロバストネスでさらに差が広がります。上段の画像帯が同じ4タスクを3種類の摂動下で示したもので、未学習物体、未学習背景、未学習照明、それぞれ赤枠で強調されています。下の表が最悪値の性能低下をまとめたものです。フルSFTのπ₀.₅は崩壊していて、未学習物体で最大45ポイントも落ちる。一方LaST-R1は全条件で15ポイント以内に収まっていて、背景や照明変化に対してはほぼ無劣化。著者らの主張は、「環境フィードバックを通じて潜在推論を最適化することが、本質的に環境の不確実性に対する頑健性を生む」というもので、ポリシーが運動学パターンの暗記ではなく、転移可能な物理概念を学ばざるを得ない、という解釈です。

---

## Slide 22 — Deeper Analysis: What did the Policy Learn?

### Layout / レイアウト
- **Title:** What did the optimized policy actually learn? — Three findings
- **Three sub-panels:**

  **(1) Reasoning-length distribution (Fig. 9):**
  - Before RL: roughly uniform over {2, 4, 6, 8}
  - After LAPO: sharp peaks at **length 2 and 4** → learns to think *short*

  **(2) Execution episode length (Fig. 10):**
  - Spatial: Expert 109 / Before-RL 153 / **After-RL 102** ✅ beats expert
  - Object: 137 / 181 / **124** ✅
  - Goal: 106 / 176 / **104** ✅
  - Long: 205 / 396 / 235 (close to expert)

  **(3) Action-to-Vision attention (Fig. 16, Grad-CAM):**
  - Action-Only: diffuse, lags the gripper
  - LaST-R1: focused, anticipates target → after LAPO, attention dynamically shifts object → target

- **Takeaway (highlighted):**
  *"RL on latents = test-time scaling for robotics — shorter thinking, faster execution, better attention."*

### Talking script — English
> Three analyses that show what the optimized policy actually learned. First, the reasoning-length distribution shifts dramatically after LAPO: before RL, the lengths are roughly uniform over 2, 4, 6, 8 because the warm-up samples them uniformly, but after LAPO the distribution becomes sharply peaked at lengths 2 and 4. The policy learns to think *short*. Second, the actual execution episode length on Spatial, Object, and Goal drops *below* the scripted expert demonstrations — for example on LIBERO-Spatial the expert takes 109 steps, the pre-RL policy needs 153 because it wanders inefficiently, and the post-RL policy takes just 102 steps, beating the expert. Third, action-to-vision attention maps from Grad-CAM show that the LaST-R1 + LAPO policy develops focused, goal-directed visual attention that dynamically shifts from the manipulated object to the target receptacle. The takeaway is that RL on latents is effectively *test-time scaling for robotics* — adaptive thinking budgets, shorter execution, and better attention, all learned automatically from reward.

### Talking script — 日本語
> 最適化されたポリシーが実際に何を学んだのか、3つの分析を見ます。1つ目、推論長の分布がLAPO後に劇的に変化する。RL前は長さ2, 4, 6, 8にほぼ一様に分布している（warm-upで一様サンプリングするため）のが、LAPO後は長さ2と4にシャープなピークを持つ形に。ポリシーは「短く考える」ことを学習する。2つ目、実行ステップ数がSpatial、Object、Goalスイートでスクリプト化されたエキスパート実演を「下回る」。例えばLIBERO-Spatialではエキスパート109ステップ、RL前153ステップ（非効率に彷徨うので増える）、RL後102ステップで、エキスパートに勝っている。3つ目、Grad-CAMによるaction-to-vision attention mapsを見ると、LaST-R1 + LAPOは焦点が定まり目標指向的な視覚注意を持ち、しかも操作物体→目標容器へと動的にシフトする。総括すると、潜在空間でのRLは、ロボティクスの「test-time scaling」として機能していて、適応的な思考予算、短い実行、優れた注意、すべてが報酬から自動で学ばれている、ということです。

---

# === PAPER 3: Streaming Flow Policy (Slides 23–30, 8 slides) ===

## Slide 23 — Paper 3: Streaming Flow Policy Overview

### Layout / レイアウト
- **Section divider style**
- **Title:** Paper 3 — Streaming Flow Policy (SFP)
- **Subtitle:** Simplifying Diffusion/Flow-Matching Policies by Treating Action Trajectories as Flow Trajectories
- **Authors:** Jiang, Fang, Roy, Lozano-Pérez, Kaelbling, Ancha (MIT)
- **One-line summary:** *"Align flow time with execution time → stream actions on the fly, 10× faster."*
- **Three keywords:** *Action trajectory = Flow trajectory · Stabilizing velocity field · 4.5 ms latency*

### Talking script — English
> Last paper: Streaming Flow Policy, abbreviated SFP, from MIT. The one-line summary is that SFP redesigns flow-matching policies so that flow time *coincides* with execution time, allowing actions to be streamed to the robot on the fly, an order of magnitude faster than conventional diffusion policies. Three keywords: action trajectory equals flow trajectory, a stabilizing velocity field, and a 4.5-millisecond action latency.

### Talking script — 日本語
> 最後の論文は、MITのStreaming Flow Policy、略してSFPです。1行で言うと、Flow-matchingベースのポリシーを再設計して、「flow timeと実行時間を一致させる」ことで、アクションをロボットに流れるように送り出せるようにしたもの。従来のDiffusionポリシーより一桁速い。キーワードは3つ、Action trajectory = Flow trajectory、安定化付き速度場、そして4.5ミリ秒のアクション遅延です。

---

## Slide 24 — Background: Why Diffusion/Flow Policies?

### Layout / レイアウト
- **Title:** Why diffusion/flow policies? And why are they slow?
- **Top half (the good):**
  - 🎯 **Multi-modal action distributions** — many valid trajectories for one task
  - 📉 MSE-trained policies average over them → degenerate behaviors
- **Bottom half (the bad):**
  - ⏱️ Operate in **action-sequence space** $\mathcal{A}^T$
  - Start from pure Gaussian noise → must complete the full denoising loop
  - 🚫 Cannot stream actions to the robot until the loop finishes
  - Streaming Diffusion Policy (Høeg et al. 2024) partially fixes this, but requires a rolling buffer with increasing noise across the horizon

### Talking script — English
> First, why have diffusion- and flow-based policies become popular? Because they naturally represent multi-modal action distributions. For many manipulation tasks — say, picking up a cup — there are several equally valid trajectories. MSE-trained policies tend to average them into degenerate behaviors, while diffusion policies preserve the modes. But there is a real cost: conventional diffusion/flow policies operate in the *action-sequence* space, meaning the entire chunk of future actions, and they start sampling from pure Gaussian noise. So you discard a whole stack of intermediate trajectories during denoising, and worse, you cannot send any actions to the robot until the full loop completes. Streaming Diffusion Policy by Høeg et al. partially mitigates the latency by using a rolling buffer with increasing noise levels across the horizon, but it's a workaround rather than a fundamental fix.

### Talking script — 日本語
> まず、なぜDiffusion/Flowベースのポリシーが人気なのか。理由は、マルチモーダルなアクション分布を自然に表現できるからです。「コップを掴む」のようなタスクには、等しく妥当な軌道が複数存在する。MSE損失で訓練するとそれを平均化して変な行動になりますが、Diffusionポリシーはモードを保てる。しかし代償もあります。従来のDiffusion/Flowポリシーは、未来のアクションチャンク全体を含む「アクション系列空間」で動作していて、しかも純粋なGaussianノイズからサンプリングを始める。だからdenoising中の中間軌道を全部捨てる無駄が出るし、もっと深刻なことに、denoisingループが終わるまでロボットには1つのアクションも送れない。Streaming Diffusion Policy（Høegら, 2024）はrolling bufferを使って遅延を一部緩和しますが、これは回避策であって、根本的な解決ではありません。

---

## Slide 25 — Key Idea: Action Trajectory = Flow Trajectory

### Layout / レイアウト
- **Title:** Key idea: align *flow time* with *execution time*
- **Main visual:** Fig. 5 from the resume (left: conventional in $\mathcal{A}^T$; right: SFP in $\mathcal{A}$)
- **Annotations:**
  - **Left (conventional):** "Trajectory of trajectories" — vertical axis = diffusion time, horizontal = execution time. Must finish vertically before sending anything.
  - **Right (SFP):** Single action trajectory in $\mathcal{A}$, where **flow time = execution time**. Stream as you integrate!
- **Highlighted insight:** *"Don't sample trajectories — flow through one."*

### Talking script — English
> Here is the central idea, and it is beautifully simple. Look at the figure. On the left, the conventional diffusion/flow policy: the vertical axis is diffusion or flow time, the horizontal axis is execution time, and you need to climb all the way up the vertical axis — the full denoising loop — before any action can be sent. You are sampling a "trajectory of trajectories". On the right, the SFP picture: there is just *one* action trajectory in the action space, and flow time is aligned with execution time. As the ODE solver integrates forward in flow time, it is also moving forward in execution time, so every newly integrated action can be streamed directly to the robot. The slogan: don't sample trajectories — flow through one.

### Talking script — 日本語
> 中心アイデアはとてもシンプルで、図を見れば一目瞭然です。左が従来のDiffusion/Flowポリシー。縦軸がdiffusion timeまたはflow time、横軸が実行時間で、まず縦軸を最後まで登り切らないと、つまりdenoisingループを最後まで回さないと、ロボットには何も送れない。「軌道の軌道」をサンプリングしている状態ですね。右がSFP。アクション空間にあるのはたった1本のアクション軌道で、しかもflow timeが実行時間と一致しています。だからODE solverがflow timeで前に進むと、同時に実行時間でも前に進むので、新しく積分されたアクションはそのままロボットに流せる。スローガンは「軌道をサンプリングするな、1本を流れろ」。

---

## Slide 26 — Method: Stabilizing Velocity Field

### Layout / レイアウト
- **Title:** Method: stabilizing conditional velocity field
- **Top equation (velocity field):**

$$v_\xi(a, t) = \dot{\xi}(t) - k(a - \xi(t))$$

- **Annotations:**
  - $\dot{\xi}(t)$ → trajectory velocity along demo $\xi$
  - $-k(a - \xi(t))$ → **proportional stabilization** (pulls deviations back)
- **Bottom equation (per-timestep marginal):**

$$p_\xi(a \mid t) = \mathcal{N}(a \mid \xi(t),\, \sigma_0^2 e^{-2kt})$$

- **Geometric picture (right side):** A "Gaussian tube" around the demo trajectory whose width shrinks exponentially over time.
- **Note:** Initial $a_0 \sim \mathcal{N}(a_{\text{prev}}, \sigma_0^2)$ — start near the last executed action.

### Talking script — English
> The method, then. SFP models the policy as a history-conditioned velocity field on the action space. Crucially, the initial action is *not* sampled from pure Gaussian noise — it's sampled from a narrow Gaussian centered at the last executed action. So the flow starts close to where the robot already is. For each demonstration trajectory ξ, the authors analytically construct what they call a stabilizing conditional velocity field. The first term is just the velocity along the demonstration. The second term, minus k times (a - ξ(t)), is a proportional stabilization term — a simple P-controller that pulls deviations back toward the demonstration. The induced per-timestep marginal distribution turns out to be a Gaussian tube around the demonstration, whose width shrinks exponentially as e to the minus 2kt. This stabilization is motivated by prior theoretical results showing that low-level stabilizing controllers reduce distribution shift and tighten generalization bounds in imitation learning.

### Talking script — 日本語
> 手法に入ります。SFPでは、ポリシーを「履歴で条件付けされた、アクション空間上の速度場」としてモデル化します。決定的に違う点として、初期アクションを純粋なGaussianノイズではなく、「直前に実行したアクションを中心とする狭いGaussian」からサンプリングします。だからフローはロボットが今いる場所のすぐ近くから始まる。各実演軌道 ξ に対して、著者らは「安定化付きの条件速度場」を解析的に構成します。第1項は実演に沿った速度。第2項の $-k(a-\xi(t))$ は比例項で、要するにP制御で実演軌道に向かって偏差を引き戻す働きをします。これによって誘導される各時刻の周辺分布は、実演の周りのGaussianチューブ状の形になって、その幅が $e^{-2kt}$ で指数的に狭まっていく。この安定化は、模倣学習で低レベル安定化制御器が分布シフトを減らし、汎化バウンドを締めることが理論的に知られていることに動機づけられています。

---

## Slide 27 — Training & Inference

### Layout / レイアウト
- **Title:** Training & Inference
- **Top: Training (flow matching loss)**

$$\mathcal{L}_{\text{CFM}}(v, p_\mathcal{D}) = \mathbb{E}_{(h, \xi), t, a \sim p_\xi(a|t)} \left\| v(a, t \mid h) - v_\xi(a, t) \right\|_2^2$$

- 📌 *Flow-matching theorem guarantees marginal action distribution matches training data at every t — preserves multi-modality.*
- **Bottom: Inference**
  - $\sigma_0 \to 0$ → deterministic policy
  - ODE solver integrates autoregressively
  - Each newly integrated action → **streamed directly to controller**
  - For configuration-space tasks: can initialize from measured robot state (proprioception-based state imitation)

### Talking script — English
> Training is then standard conditional flow matching, regressing the network onto the analytical velocity field we just constructed. The flow-matching theorem guarantees that the minimizer's marginal action distribution at every time t matches the training distribution, which preserves multi-modality even when many demonstrations are aggregated. At inference, sigma-zero is set to zero so the policy behaves deterministically. An ODE solver autoregressively integrates the velocity field, and — this is the punchline — each newly computed action can be streamed directly to the robot controller without waiting for the full chunk to complete. There is also a nice option for tasks defined in robot configuration space: you can initialize the integration from the *measured* robot state, leveraging proprioception to reduce accumulated error. This is what the authors call "state imitation".

### Talking script — 日本語
> 訓練は標準的な条件付きflow matchingで、ニューラルネットを今構成した解析的な速度場に回帰させます。Flow-matching定理により、最適解の周辺アクション分布は各時刻tで訓練データの分布と一致することが保証されます。だから多数の実演を集約してもマルチモーダル性が保たれる。推論時は $\sigma_0$ を0にしてポリシーを決定的にします。ODE solverが速度場を自己回帰的に積分していき、ここが要ですが、新しく計算されたアクションをチャンク全体の完了を待たずに直接ロボット制御器にストリームできる。さらに、ロボットのconfiguration空間で定義されたタスクには便利な拡張があって、積分の初期値を「観測されたロボット状態」から始めることもできます。proprioceptionを使って累積誤差を減らすわけです。著者らはこれを「state imitation」と呼んでいます。

---

## Slide 28 — A Subtle Caveat (and why it's actually a feature)

### Layout / レイアウト
- **Title:** Caveat: marginals ≠ joint
- **Two-column layout:**
  - **Left (what SFP guarantees):**
    ✅ Marginal action distribution at every $t$ matches training data
  - **Right (what SFP does NOT guarantee):**
    ❌ Joint distribution over **entire trajectories**
- **Below (highlighted):**
  - *"For quasi-static manipulation, this is actually a feature, not a bug."*
  - The policy can compose new valid trajectories from segments of demos
  - **Local constraints** (joint limits, convex velocity constraints) are still provably respected

### Talking script — English
> There is one subtle caveat that I want to flag because the authors are very explicit about it. SFP matches the *marginal* action distribution at every timestep, but it does not necessarily match the *joint* distribution over entire trajectories. In other words, SFP might compose new trajectories by mixing segments from different demonstrations. The authors argue — and I find this convincing — that for quasi-static manipulation this is a *feature*, not a bug, because it lets the policy compose novel valid behaviors from training segments. They also prove that local constraints like joint limits and convex velocity constraints are still respected throughout. So you trade joint-distribution fidelity for additional compositional generality.

### Talking script — 日本語
> ひとつ細かいですが大事な留意点を共有します。著者らも明示しているところです。SFPが保証するのは「各時刻における周辺アクション分布の一致」であって、「軌道全体の同時分布の一致」ではない。言い換えると、SFPは複数の実演のセグメントを混ぜ合わせて新しい軌道を構成することがあります。著者らの主張は、準静的なマニピュレーションタスクではこれは「バグではなく特徴」だ、というもので、訓練データのセグメントから新しい妥当な行動を合成できるという利点になる。理論的には、関節限界や凸な速度制約といった局所的な制約は全区間で保たれることも証明されています。つまり、同時分布の忠実度を譲って、合成的な汎化を得ているという trade-off になっています。

---

## Slide 29 — Results: Simulation

### Layout / レイアウト
- **Title:** Simulation results: best in class, by far the fastest
- **Table-style comparison (compact):**

| Method | Push-T (state) avg/max | Square (RoboMimic) | Latency |
|---|---|---|---|
| DDPM-100 | 92.9% / 94.4% | — | **53.4 ms** |
| DDIM-10 | — | — | ~5 ms |
| Conv. Flow Policy | — | — | — |
| Streaming Diffusion | — | — | several× SFP |
| **SFP** | **95.1% / 96.0%** | **78.0% / 84.0%** | **4.5 ms** ⚡ |

- **Other tasks:** Push-T action mode 91.7% / 93.7% · Lift 100% · Can 98.4% / 100%
- **Ablation panel:** Remove stabilization (k=0): Square **78.0% → 53.2%** ← critical!

### Talking script — English
> Now the numbers. Push-T with state inputs: SFP averages 95.1% with max 96.0%, beating DDPM-100 at 92.9/94.4 and every other baseline. Action imitation: 91.7/93.7, again best. RoboMimic: 100% on Lift, 98.4 with max 100 on Can, and 78.0 with max 84.0 on Square — matching or beating every baseline. The critical number, though, is latency. SFP runs at 4.5 milliseconds per action, an order of magnitude faster than DDPM-100 at 53.4 ms, and several times faster than Streaming Diffusion Policy. The ablation also confirms the stabilization term matters: removing it (k equals zero) drops Square success from 78.0% all the way down to 53.2%. That P-controller term is not optional.

### Talking script — 日本語
> 数字を見ていきます。Push-T状態入力でSFPは平均95.1%、最大96.0%。DDPM-100の92.9/94.4%や他のベースラインを上回ります。アクション模倣で91.7/93.7、これも最高。RoboMimicではLift 100%、Can 98.4/100%、Square 78.0/84.0%と、すべてのベースラインと並ぶか上回る。一番効いている数字はレイテンシです。SFPは1アクションあたり4.5ミリ秒。DDPM-100の53.4msに対して一桁速く、Streaming Diffusion Policyに対しても数倍速い。Ablationからも、安定化項がやはり本質だとわかります。$k=0$ にするとSquareの成功率が78.0%→53.2%まで落ちる。あのP制御項はオプションではなく必須ということです。

---

## Slide 30 — Results: Real-World & Why It Feels Smoother

### Layout / レイアウト
- **Title:** Real-world: smoother, more uniform motion
- **Left: tasks (Franka Research 3 + RealSense D435f)**
  - Reach and pick an apple 🍎
  - Reorient a block 📦
- **Center: timing comparison schematic**
  - **Diffusion Policy execution:** stop-go pattern (long pauses while denoising)
    `🟦——————🟦——————🟦` (sparse, with gaps)
  - **SFP execution:** uniform stream of actions
    `🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧` (uniform)
- **Right takeaway box:**
  - "Same average latency would not be enough — *uniform emission* is the key."
  - "SFP feels smoother because it acts continuously, not in batches."

### Talking script — English
> The real-world experiments use a Franka Research 3 arm with a RealSense D435f camera, on two tasks: reaching and picking up an apple, and reorienting a block. Qualitatively, SFP produces noticeably smoother and faster motions than Diffusion Policy. And here is a subtle but important observation: the smoothness advantage does not come *only* from lower average latency. It comes from the fact that SFP emits actions at a *uniform* interval as the ODE integrates. Diffusion policies, in contrast, must complete the entire denoising loop before any action is sent, which produces a stop-and-go execution pattern even when the average latency looks similar. So evenly distributed action emission is itself a real advantage, beyond raw speed. And that wraps up the three papers. Thank you very much for listening — I'm happy to take questions.

### Talking script — 日本語
> 実機実験はFranka Research 3にRealSense D435fカメラを付けた構成で、リンゴを取りに行く・掴むタスクと、ブロックの再配置タスクの2つで行われています。定性的には、SFPはDiffusion Policyより明らかに滑らかで素早い動きをします。ここでひとつ、地味だけど大事な観察があります。滑らかさの優位性は「平均レイテンシが低いこと」だけから来ているわけではない。SFPはODEを積分している間、アクションを「一定の間隔で」出力し続ける。一方Diffusion系は、denoisingループが終わるまで一切アクションを送れないので、平均レイテンシが似ていてもstop-and-go型の挙動になってしまう。つまり「アクションを均等に出し続けられること」自体が、純粋な速度とは独立した実利上の利点になっているわけです。以上で3本の論文紹介を終わります。ご清聴ありがとうございました。質問をお受けします。

---

# 発表時間配分の目安 / Suggested Timing

| Section | Slides | Time |
|---|---|---|
| Background | 1–4 | ~4 min |
| Paper 1 (UniT) | 5–12 | ~7 min |
| Paper 2 (LaST-R1) | 13–22 | ~9–10 min |
| Paper 3 (SFP) | 23–30 | ~6–7 min |
| **Total (incl. Q&A buffer)** | **30** | **~26–30 min** |

# 図・素材リスト / Figures to prepare

1. **Slide 1, 2:** A robot manipulation hero image (optional, decorative)
2. **Slide 3:** Fig. 1 (VLA three-component architecture) — from resume page 1
3. **Slide 7:** Fig. 2 (four latent action paradigms) — from resume page 1/2
4. **Slide 8:** Fig. 3 (UniT architecture) — from resume page 2
5. **Slide 14:** Fig. 1 (a)(b) from LaST-R1 original paper (Vanilla VLA RL vs LaST-R1+LAPO)
6. **Slide 15:** Fig. 2(a) from LaST-R1 original paper (LaST-R1 VLA architecture); + Fig. 7 (Hybrid attention mask, optional small panel)
7. **Slide 16:** Fig. 4(a) from LaST-R1 paper — Latent representation ablation bar chart
8. **Slide 18:** Fig. 4(c) from LaST-R1 paper — Adaptive Latent Length ablation
9. **Slide 19:** Table 1 from LaST-R1 paper (LIBERO main table), summarised
10. **Slide 20:** Top — Fig. 12 task strip; Bottom — Table 2 main results
11. **Slide 21:** Fig. 13 perturbation strip + OOD numbers from Table 2
12. **Slide 22:** Three sub-figures — Fig. 9 (reasoning length distribution), Fig. 10 (episode length comparison), Fig. 16 (Action-to-Vision Grad-CAM)
13. **Slide 25:** Fig. 5 (conventional vs. SFP flow) — from resume page 4
14. **Slides 11, 19, 27, 29:** Bar charts / tables — render directly in Keynote/PowerPoint from the numbers in this script
15. **Slide 30:** Custom timing-pattern schematic showing stop-go vs uniform action emission

# プレゼン Tips

- 各スライドの英語と日本語の原稿は同じ内容を伝えていますので、好きな方を選んでください。バイリンガル発表の場合は、英語をメインにして日本語で要点だけ補足する、または逆、にすると20–30分に収まりやすいです。
- 数字（成功率、ms など）は強調して読み上げると印象に残りやすいです。スライドでも太字または色付けを推奨します。
- 図2、図3、図4、図5は本論文の核心なので、説明中は図を指しながら話すと効果的です。
- LaST-R1パートが10枚と長めなので、ペース管理に注意してください。Slide 16（DINOv3 latent target）、Slide 18（M=4 ablation）、Slide 22（reasoning length分析）の3枚は時間が足りなければ簡潔に流せます。逆に質疑応答で深掘りされやすい箇所でもあります。
- 最終スライド(30)で発表をきれいに締めるため、原稿末尾の「ご清聴ありがとうございました」を必ず読み上げてください。
- 各論文の冒頭スライド(5, 13, 23)はセクションディバイダとして視覚的に明確に区切ると、聴衆の注意がリセットされ理解しやすくなります。