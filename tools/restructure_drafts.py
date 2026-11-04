# -*- coding: utf-8 -*-
"""Remap the ja/en drafts to the new 37-slide structure and insert the new sections."""
import re, sys

MAP = {1:1,2:2,3:3,4:4,5:5, 7:8,8:9,9:10,10:11,11:12,12:13,13:14, 15:15, 17:18,18:19,19:20,20:21,21:22,22:23,23:24,
       24:25, 26:29,27:28,28:30,29:31,30:32,31:33,32:34, 33:36,34:37}
DROP = {6,14,16,25}

NEW = {'ja': {}, 'en': {}}
J = NEW['ja']; E = NEW['en']

J[6] = """## スライド6 SimFoundry この発表での立ち位置：Real2Sim

- 入力は実世界の動画1本と、評価または学習したいポリシー
- VLM の仕事は物体の検出、質量や摩擦の推定、別の配置と別のタスクの提案
- ポリシーは Sim の中で「評価される側」か「学習される側」。VLM は Sim を作る側

ノート: SimFoundry の立ち位置を、冒頭の枠組みで確認します。3つの領域のうち Real2Sim です。入力は実世界の動画1本と、評価または学習したいポリシーです。VLM と視覚基盤モデルの仕事は、動画から物体を見つけて 3D にし、質量や摩擦を見積もり、さらに別の配置や別のタスクを提案することです。つまり VLM はポリシーを動かすのではなく、ポリシーを試す場を作ります。ポリシーは Sim の中で評価される側、あるいは Sim のデータで学習される側です。後の2本と違って VLM が実行時に関わらないので、遅延の問題がないことも特徴です。
"""
E[6] = """## Slide 6 SimFoundry Where it sits in this talk: Real2Sim

- Input: one real-world video, plus the policy you want to evaluate or train
- The VLM's job: detect objects, estimate mass and friction, propose new layouts and tasks
- The policy is what gets evaluated or trained inside the sim; the VLM builds the sim

Notes: Let me place SimFoundry in the framework from the introduction. Of the three areas, this is Real2Sim. The input is a single real-world video plus the policy you want to evaluate or train. The job of the VLM and the vision foundation models is to find the objects in the video, turn them into 3D, estimate mass and friction, and propose alternative layouts and tasks. In other words, the VLM does not drive the policy; it builds the arena in which the policy is tested. The policy is what gets evaluated in the sim, or trained on sim data. Unlike the next two papers, the VLM is not involved at execution time, so there is no latency issue.
"""

J[7] = """## スライド7 SimFoundry 何が新しいか：複製で終わらず、変種まで自動で作る

- 既存の Real2Sim の多くは、実シーンの複製（Digital Twin）を1つ作って終わり
- SimFoundry は複製から物体・配置・タスクの変種（Digital Cousins）を自動で作る
- 1つの実シーンから、評価用の忠実な Sim と学習用の多様な Sim の両方が得られる

ノート: 何が新しいかを一枚にまとめます。実世界からシミュレーションを作る研究はこれまでにもあり、多くは写真や動画から実シーンの複製、Digital Twin を1つ作るところまででした。複製は忠実なので評価には向きますが、1シーン分の学習データしか作れません。SimFoundry は複製を出発点にして、物体の形を変えた版、配置を変えた版、別のタスクを課した版を VLM に提案させて自動で作ります。これが Digital Cousins です。その結果、1つの実シーンから評価用の忠実な Sim と、学習用の多様な Sim の両方が得られます。論文の表1にある既存システムとの比較でも、評価・学習・多様化を全部備えるのは SimFoundry だけです。
"""
E[7] = """## Slide 7 SimFoundry What is new: not just a copy, but automatic variants

- Most real-to-sim work stops at one reconstructed copy of the scene (digital twin)
- SimFoundry automatically generates object, layout and task variants (digital cousins)
- One real scene yields both a faithful sim for evaluation and diverse sims for training

Notes: Here is what is new, on one slide. Building simulations from the real world is not new, but most prior work stops at one faithful copy of the scene, the digital twin. A twin is faithful, so it suits evaluation, but it gives training data for one scene only. SimFoundry starts from the twin and asks a VLM to propose versions with different object shapes, different layouts and different tasks, and builds them automatically. These are the digital cousins. As a result, one real scene yields both a faithful sim for evaluation and diverse sims for training. In the paper's Table 1, SimFoundry is the only system that covers evaluation, training and diversification together.
"""

J[10] = """## スライド10 SimFoundry 手法①：動画1本から複製シーンを作る4ステップ

- ① 動画から1フレームを選び、深度を推定して点群にする
- ② VLM が物体を見つけ、SAM で1つずつ切り抜く。切り抜いた物は塗りつぶして次へ
- ③ 切り抜き画像から 3D メッシュを作り、質量や摩擦を VLM に答えさせる
- ④ 物理 Sim に並べ、めり込みを解消して安定させる

ノート: 再構成の手順を4ステップに噛み砕きます。1つ目、動画から代表の1フレームを選び、深度推定で点群にします。これで机の面と物の位置関係が分かります。2つ目、VLM に「この画像に何があるか」を答えさせ、SAM 3 で物体を1つずつ切り抜きます。切り抜いた物体は画像から塗りつぶして消し、残りの物体を繰り返し探します。3つ目、切り抜いた画像1枚から 2D から 3D の生成モデルでメッシュを作り、点群に合わせて位置と向きを決めます。引き出しや扉は別のモジュールで関節を付けます。質量や摩擦は VLM に常識で答えさせます。4つ目、物理シミュレータに並べ、物同士のめり込みを解消して安定させ、IsaacLab などに書き出します。各ステップは既製の基盤モデルを呼んでいるだけなので、より良いモデルが出れば差し替えられます。
"""
E[10] = """## Slide 10 SimFoundry Method 1: four steps from a video to a reconstructed scene

- ① Pick one frame from the video, estimate depth, build a point cloud
- ② A VLM finds the objects; SAM cuts them out one by one, inpainting each away
- ③ Generate a 3D mesh from each crop; ask the VLM for mass and friction
- ④ Place everything in a physics sim and resolve penetrations

Notes: Let me break the reconstruction into four steps. First, pick a representative frame from the video and estimate depth to get a point cloud; this gives the table plane and where things are. Second, ask a VLM what is in the image, and cut the objects out one at a time with SAM 3; each cut-out object is inpainted away so the remaining ones can be found in turn. Third, from each single crop, a 2D-to-3D generative model produces a mesh, which is aligned to the point cloud; drawers and doors get joints from a separate module, and the VLM answers mass and friction from common sense. Fourth, everything is placed in a physics simulator, penetrations are resolved, and the scene is exported to IsaacLab and others. Each step just calls an off-the-shelf foundation model, so better models can be swapped in.
"""

J[11] = """## スライド11 SimFoundry 手法②：複製から3種類の変種を作る

- 物体の変種：切り抜き画像を少し変えて 3D を作り直す（形の違うマグなど）
- 配置の変種：VLM が「上に置く」「右に置く」などの関係を書き換える
- タスクの変種：VLM が「この机でできる別のタスク」を提案し、デモを自動生成

ノート: 変種の作り方です。物体の変種は、切り抜いた画像を画像生成で少し変えてから 3D を作り直します。マグなら形や取っ手やテクスチャが違うマグになり、機能は同じです。配置の変種は、VLM に「上に置く」「右に置く」のような物同士の関係を書き換えさせます。単なる位置のノイズではなく、意味のある別の配置になり、邪魔になる物も追加できます。タスクの変種は、VLM にその机でできる別のタスクを提案させ、目標の記述に変換して、既存のデモ生成手法で実演を自動で作ります。この3つで、1つの実シーンから物体・配置・タスクの多様性を持つ大量の学習データが得られます。
"""
E[11] = """## Slide 11 SimFoundry Method 2: three kinds of variants from the twin

- Object variants: perturb the crop and regenerate the 3D mesh (a mug of a different shape)
- Layout variants: the VLM rewrites relations such as "on top of" and "right of"
- Task variants: the VLM proposes other tasks feasible on this table; demos are generated

Notes: Now the variants. Object cousins perturb the cropped image with an image model and regenerate the 3D mesh, giving a mug with a different shape, handle or texture but the same function. Scene cousins have the VLM rewrite relations between objects such as on-top-of or right-of, producing meaningful new layouts rather than position noise; distractors can be added too. Task cousins have the VLM propose other tasks that are feasible on this table, convert them to goal specifications, and generate demonstrations with existing data-generation methods. Together these turn one real scene into a large training set that is diverse in objects, layouts and tasks.
"""

J[16] = """## スライド16 Code-as-Monitor この発表での立ち位置：失敗検出

- 入力はタスクの指示、カメラ画像、そして実行中のポリシー（開ループでよい）
- VLM の仕事は、守るべき条件を文章で書き、それを判定するコードを書くこと
- ポリシーはそのまま動く。コードが横で見張り、条件を破ったら止めて再計画させる

ノート: Code-as-Monitor の立ち位置です。3つの領域のうち失敗検出です。入力はタスクの指示とカメラ画像、そして実行中のポリシーで、ポリシーは開ループのものでも構いません。VLM の仕事は、守るべき条件を文章で書き、それを判定するコードを書くことです。ポリシー自体はそのまま動き、コードが横で見張ります。条件が破られたら即座にポリシーを止め、理由を返して再計画させます。つまり VLM はポリシーの中身に触らず、外側に監視役を置きます。
"""
E[16] = """## Slide 16 Code-as-Monitor Where it sits in this talk: failure detection

- Input: the task instruction, camera images, and the running policy (open-loop is fine)
- The VLM's job: write the conditions to keep, then write code that checks them
- The policy runs as is; the code watches alongside and stops it to re-plan when a condition breaks

Notes: Here is where Code-as-Monitor sits: failure detection. The input is the task instruction, camera images and the running policy, which may be open-loop. The VLM's job is to write the conditions that must hold, and then to write code that checks them. The policy itself runs unchanged while the code watches alongside it; when a condition is violated the policy is stopped immediately and the reason is returned for re-planning. So the VLM never touches the policy; it places a monitor outside it.
"""

J[17] = """## スライド17 Code-as-Monitor 何が新しいか：VLM に毎回聞かず、コードに見張らせる

- 既存は「失敗したか」を VLM に画像で問う。遅く、1枚の画像では 3D の関係が分からない
- 本手法はサブゴールの最初に VLM が判定コードを書き、以後はコードが毎フレーム検査する
- 失敗の予兆（鍋の傾き）も数値で捉えられるので、起きる前に止められる

ノート: 何が新しいかです。既存の失敗検出は、失敗したかを VLM に画像で問う形でした。上の段のように毎フレーム問うと遅く、1枚の画像からでは 3D の関係が分からないので誤判定が増えます。中の段のようにサブゴールの完了時だけ問うと、失敗の予兆が出ても完了まで気づきません。本手法は下の段で、サブゴールの最初に1回だけ VLM に判定コードを書かせ、以後はそのコードが毎フレーム、追跡した点の座標を検査します。コードは数値で判定するので、鍋が傾き始めたというような予兆も捉えられ、失敗が起きる前に止められます。VLM の呼び出しは1回なので速く、幻覚の影響も受けにくくなります。
"""
E[17] = """## Slide 17 Code-as-Monitor What is new: let code watch instead of asking the VLM every time

- Prior work asks the VLM "did it fail?" with images: slow, and a single image hides 3D relations
- Here the VLM writes checking code once per subgoal; the code then checks every frame
- Early signs such as a tilting pan show up as numbers, so failures are stopped before they happen

Notes: Here is what is new. Prior failure detection asks a VLM, with images, whether the task has failed. Asking every frame, as in the top row, is slow, and 3D relations are hard to read from a single image, so misjudgments increase. Asking only when a subgoal completes, as in the middle row, misses the early signs until the end. This method, in the bottom row, has the VLM write checking code once at the start of a subgoal, after which the code checks the coordinates of tracked points every frame. Because the code judges with numbers, it also catches early signs such as the pan starting to tilt, and stops the policy before the failure happens. With a single VLM call it is fast and less exposed to hallucination.
"""

J[18] = """## スライド18 Code-as-Monitor 手法①：「鍋を運ぶ」例で見る3ステップ

- ① VLM が守るべき条件を文章で書く：「鍋は水平を保つ」「パンは鍋の中に留まる」
- ② 条件に関係する部分を点・線・面にして画像に描く：鍋の面は3つの赤い点
- ③ VLM が点を使う判定コードを書く：面の傾きが 15° を超えたら「失敗」と返す

ノート: 手法を「パンの入った鍋をコンロへ運ぶ」という例で3ステップに噛み砕きます。1つ目、VLM がタスクの指示と画像から、次のサブゴールと守るべき条件を文章で書きます。実行中に守る条件は「鍋の取っ手を持ち続ける」「パンは鍋の中に留まる」「鍋は水平を保つ」、完了時に満たす条件は「鍋がコンロの真上にある」です。2つ目、各条件に関係する部分を点・線・面に抽象化して画像に描き込みます。鍋の面なら縁の3つの赤い点、パンなら緑の点、コンロなら青い点です。3つ目、その描き込んだ画像を見せて、VLM に点の座標を使う判定コードを書かせます。例では3点から面の法線を計算し、鉛直との角度が 15 度を超えたら「鍋が水平でない」という理由付きで失敗を返します。あとは点を追跡しながらこのコードを毎フレーム動かすだけです。
"""
E[18] = """## Slide 18 Code-as-Monitor Method 1: three steps on the "carry the pan" example

- ① The VLM writes the conditions in words: "the pan stays level", "the bread stays in the pan"
- ② The relevant parts become points, lines and surfaces drawn on the image: the pan surface is three red points
- ③ The VLM writes checking code over those points: if the surface tilts more than 15°, return "failure"

Notes: Let me break the method into three steps using the example of carrying a pan with bread to the stove. First, from the instruction and the images, the VLM writes the next subgoal and the conditions to keep, in words. During execution: keep grasping the handle, the bread stays in the pan, the pan stays level. Upon completion: the pan is directly above the stove. Second, the parts relevant to each condition are abstracted into points, lines and surfaces and drawn on the image: three red points on the rim for the pan surface, a green point for the bread, a blue point for the stove. Third, shown these annotated images, the VLM writes checking code over the point coordinates. In the example it computes the surface normal from the three points and, if the angle to vertical exceeds 15 degrees, returns a failure with the reason "the pan is not level". After that the code simply runs every frame on the tracked points.
"""

J[26] = """## スライド26 VLS この発表での立ち位置：推論時の誘導

- 入力はカメラ画像と指示、そして凍結した拡散／フローマッチングのポリシー
- VLM の仕事は「良い行動」を点数にする報酬関数をコードで書くこと
- ポリシーが行動を生成する途中で報酬の勾配を足し、少しずつ曲げる。学習はしない

ノート: VLS の立ち位置です。3つの領域のうち推論時の誘導です。入力はカメラ画像と指示、そして凍結した拡散またはフローマッチングのポリシーです。VLM の仕事は、今の状況で何が良い行動かを点数にする報酬関数を、コードとして書くことです。ポリシーはノイズから行動を少しずつ作っていきますが、その途中で報酬の勾配を足して、行動を報酬の高い側へ少しずつ曲げます。ポリシーの重みは一切変えず、学習もしません。Code-as-Monitor が実行の外側で見張るのに対し、VLS は生成の内側に手を入れる、という違いがあります。
"""
E[26] = """## Slide 26 VLS Where it sits in this talk: inference-time steering

- Input: camera images and the instruction, plus a frozen diffusion or flow-matching policy
- The VLM's job: write, as code, a reward function that scores "good" actions
- While the policy generates an action, reward gradients are added to bend it; nothing is trained

Notes: Here is where VLS sits: inference-time steering. The input is the camera images and the instruction, plus a frozen diffusion or flow-matching policy. The VLM's job is to write, as code, a reward function that scores how good an action is in the current situation. The policy builds its action gradually from noise, and during that process the reward gradient is added so the action bends toward higher reward. The policy weights are never changed and nothing is trained. Where Code-as-Monitor watches from outside the execution, VLS reaches inside the generation.
"""

J[27] = """## スライド27 VLS 何が新しいか：候補を選ぶのではなく、生成の途中で曲げる

- 既存は VLM や人が候補の中から選ぶ。候補に良い行動がなければ選べない
- 本手法は VLM が書いた報酬の勾配で、候補そのものを報酬の高い側へ動かす
- 勾配で動かし、報酬で選別する2段構え。ポリシーの重みは触らない

ノート: 何が新しいかを図で説明します。横軸は行動、たとえば手先の横位置で、青い山が学習済みポリシーの分布、橙の線が VLM の書いた報酬、灰色が壁です。(a) 誘導なしでは、候補はポリシーの山、つまり学習時に多かった行動に集まり、壁にぶつかります。既存の手法の多くは、この候補の中から VLM や人や価値関数で良いものを選びますが、候補の中に良い行動がなければ選べません。(b) 本手法は報酬の勾配を候補に足すので、候補そのものが報酬の高い側へ動きます。(c) さらに報酬の高い候補を複製し、低い候補を間引く選別を組み合わせます。勾配で動かし、報酬で選別する2段構えで、ポリシーの重みは一切触りません。
"""
E[27] = """## Slide 27 VLS What is new: bend the generation instead of picking among candidates

- Prior work lets a VLM or a human pick among candidates; if no candidate is good, nothing can be picked
- Here the gradient of a VLM-written reward moves the candidates themselves toward higher reward
- Two stages: move by gradient, then select by reward. The policy weights are untouched

Notes: Here is what is new, as a diagram. The horizontal axis is the action, say the lateral hand position; the blue hill is the pretrained policy's distribution, the orange curve is the VLM-written reward, and grey is the wall. In (a), without steering, candidates gather at the policy's hill, the actions that were common in training, and hit the wall. Most prior methods pick the best of these candidates with a VLM, a human or a value function, but if no candidate is good there is nothing to pick. In (b), this method adds the reward gradient to the candidates, so the candidates themselves move toward higher reward. In (c) it also duplicates high-reward candidates and prunes low ones. Move by gradient, then select by reward, with the policy weights untouched.
"""

J[28] = """## スライド28 VLS 手法①：「チーズをかごに入れる」例で見る3ステップ

- ① 画像から関係する物の 3D 点を取り出し、番号を振る：チーズ、かご、ほかの物
- ② VLM が報酬関数を書く：「行動の軌道がかご（点 2）に近いほど高得点」
- ③ ポリシーのノイズ除去の各ステップで報酬の勾配を足し、軌道をかご側へずらす

ノート: 手法を「チーズをかごに入れる」という例で3ステップに噛み砕きます。1つ目、画像から関係する物を VLM に挙げさせ、SAM で切り抜き、DINOv2 の特徴と深度で 3D の点にして番号を振ります。チーズ、かご、周りの物がそれぞれ番号付きの点になります。2つ目、VLM にその番号を使って報酬関数を PyTorch のコードで書かせます。図の例では「行動の軌道と点2、つまりかごとの距離の二乗にマイナスを付けた値」で、近いほど高得点です。微分できる演算だけで書かせるので、行動に対する勾配が取れます。3つ目、ポリシーがノイズから行動を作る各ステップで、この報酬の勾配を足します。軌道が少しずつかご側へずれ、最後にはかごに届く行動になります。VLM はコードを書くだけで、勾配の計算には関わりません。
"""
E[28] = """## Slide 28 VLS Method 1: three steps on the "put the cheese in the basket" example

- ① Extract 3D points of the relevant objects from the image and number them: cheese, basket, others
- ② The VLM writes a reward: "the closer the action trajectory is to the basket (point 2), the higher"
- ③ At every denoising step, add the reward gradient so the trajectory shifts toward the basket

Notes: Let me break the method into three steps on the example of putting the cheese in the basket. First, the VLM names the relevant objects, SAM cuts them out, and DINOv2 features plus depth turn them into numbered 3D points: the cheese, the basket and the surrounding objects each get a number. Second, the VLM writes a reward function in PyTorch using those numbers. In the figure it is the negative squared distance between the action trajectory and point 2, the basket, so closer is better. It is restricted to differentiable operations, so we can take the gradient with respect to the actions. Third, at every step where the policy builds its action from noise, this reward gradient is added. The trajectory shifts a little toward the basket each step and ends up reaching it. The VLM only writes the code; it plays no part in computing the gradient.
"""

J[35] = """## スライド35 Insights 3本の対応表：VLM に何をさせ、誰が実行するか

- 3本とも VLM は「コードや構造」を書くだけで、ロボットを直接は動かさない
- 違いは、書いたものを使う場所。Sim の構築、実行の監視、生成の誘導
- VLM を呼ぶ頻度が実機での遅延を決める。SimFoundry は実行時に呼ばない

ノート: 3本を同じ表で並べます。入力はどれもカメラ画像と指示ですが、VLM が書き出すものが違います。SimFoundry は物体のラベルと物性、配置とタスクの提案、Code-as-Monitor は制約文と判定コード、VLS は報酬関数のコードです。それを使うのは、SimFoundry ではシミュレータ、Code-as-Monitor では実行中の監視プロセス、VLS ではポリシーのノイズ除去ループです。VLM を呼ぶ頻度は、SimFoundry が配備前だけ、Code-as-Monitor がサブゴールごとに1回、VLS が段階の切り替えごとで、これがそのまま実機での遅延の差になります。3本とも VLM はコードや構造を書くだけで、ロボットを直接は動かさない、という共通点が見えてきます。
"""
E[35] = """## Slide 35 Insights Side by side: what the VLM writes and who runs it

- In all three, the VLM only writes code or structure; it never drives the robot directly
- The difference is where the output is used: building the sim, monitoring execution, steering generation
- How often the VLM is called sets the real-robot latency; SimFoundry never calls it at run time

Notes: Let me put the three papers in one table. The inputs are all camera images and an instruction, but what the VLM writes differs: SimFoundry gets object labels, physical properties and proposals for layouts and tasks; Code-as-Monitor gets constraint sentences and checking code; VLS gets reward-function code. Who uses it also differs: the simulator for SimFoundry, the monitoring process during execution for Code-as-Monitor, and the policy's denoising loop for VLS. The VLM is called only before deployment in SimFoundry, once per subgoal in Code-as-Monitor, and at each stage switch in VLS, which maps directly onto the real-robot latency. What they share is that the VLM only writes code or structure and never drives the robot directly.
"""

# --- bullet / head tweaks for remapped slides ---------------------------------
TWEAK = {
 'ja': {
   13: ("- 13タスクの Sim データで π0.5 を微調整し、未学習タスクでも 29%", "- 再構成の忠実度は F1 0.81〜0.92、1物体あたり約5分。卓上シーンが前提"),
   29: ("## スライド29 VLS 問題設定：生成過程に報酬の勾配を足す", "## スライド29 VLS 手法②：仕組み。生成過程に報酬の勾配を足す"),
   30: ("## スライド30 VLS 手法：報酬で誘導する生成と閉ループ制御", "## スライド30 VLS 手法③：ループの詳細と閉ループ制御"),
   19: ("## スライド19 Code-as-Monitor 手法：制約要素とその切り出し", "## スライド19 Code-as-Monitor 手法②：なぜ点・線・面にするのか"),
   20: ("## スライド20 Code-as-Monitor 手法：監視コードの生成と実行", "## スライド20 Code-as-Monitor 手法③：監視コードの中身と実行"),
 },
 'en': {
   13: ("- π0.5 fine-tuned on 13 sim tasks: 29% on held-out tasks", "- Reconstruction fidelity: F1 0.81-0.92, about 5 min per object; tabletop scenes only"),
   29: ("## Slide 29 VLS Problem setting: reward gradients in generation", "## Slide 29 VLS Method 2: how reward gradients enter the generation"),
   30: ("## Slide 30 VLS Method: reward-guided generation and control", "## Slide 30 VLS Method 3: the loop in detail and closed-loop control"),
   19: ("## Slide 19 Code-as-Monitor Method: constraint elements", "## Slide 19 Code-as-Monitor Method 2: why points, lines and surfaces"),
   20: ("## Slide 20 Code-as-Monitor Method: generating and running monitor code", "## Slide 20 Code-as-Monitor Method 3: inside the monitor code"),
 },
}
# extra notes to append to slide 13 (fidelity result merged)
NOTE13 = {
 'ja': " 再構成の品質も見ておきます。12シーンでの幾何評価では全自動で F1 スコアが 0.81 から 0.92 で、SAM3D の 0.66 から 0.71 を上回ります。1物体あたり約5分で、3分の手作業を足すと F1 は 0.93 から 0.99 まで上がります。制約は卓上シーンが前提であることと、各基盤モデルの失敗をそのまま引き継ぐことです。",
 'en': " A word on reconstruction quality: on a geometric evaluation over 12 scenes the fully automatic pipeline reaches F1 of 0.81 to 0.92, above SAM3D's 0.66 to 0.71, at about five minutes per object, and three minutes of manual tuning raises F1 to 0.93 to 0.99. The limitations are the tabletop assumption and inheriting the failures of each foundation model.",
}


def restructure(lang):
    path = f'{lang}/draft_{lang}.md'
    s = open(path, encoding='utf-8').read()
    head_re = re.compile(r'^## (?:スライド ?|Slide )(\d+) (.*)$', re.M)
    parts = head_re.split(s)
    preamble = parts[0]
    sections = {}
    for i in range(1, len(parts), 3):
        n = int(parts[i]); title = parts[i + 1]; body = parts[i + 2]
        sections[n] = (title, body)
    out = {}
    for n, (title, body) in sections.items():
        if n in DROP:
            continue
        m = MAP[n]
        text = (f'## スライド{m} ' if lang == 'ja' else f'## Slide {m} ') + f'{title}{body}'
        if lang == 'ja':
            text = text.replace(f'## スライド{m} ', f'## スライド{m} ')
        out[m] = text
    for n, text in NEW[lang].items():
        out[n] = text + '\n'
    # tweaks
    for n, (a, b) in TWEAK[lang].items():
        assert a in out[n], (lang, n, a)
        out[n] = out[n].replace(a, b)
    out[13] = out[13].rstrip('\n') + NOTE13[lang] + '\n\n'
    # renumber old video slide 29/31 notes refer nothing numeric; fine
    body = ''.join(out[k] for k in sorted(out))
    # normalise ja header spacing: '## スライド6 ...' style used by parser (no space between スライド and number)
    body = re.sub(r'^## スライド (\d+) ', r'## スライド\1 ', body, flags=re.M)
    open(path, 'w', encoding='utf-8').write(preamble + body)
    print(lang, sorted(out))


for lang in ('ja', 'en'):
    restructure(lang)
