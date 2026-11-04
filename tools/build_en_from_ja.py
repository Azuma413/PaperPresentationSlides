# -*- coding: utf-8 -*-
"""Build the English deck from the (user-edited) Japanese deck by replacing text per paragraph,
keeping run formatting (bold labels, red highlights), swapping Japanese chart images for the
English versions, and installing English speaker notes.
usage: python3 build_en_from_ja.py <ja_noshrink.pptx> <out_en.pptx>
"""
import sys, re, json, copy
S = '/tmp/claude-0/-home-user-PaperPresentationSlides/b16a4cd5-a6b6-52ff-a060-bdd5dfede159/scratchpad'
sys.path.insert(0, S)
from pptx import Presentation
from pptx.util import Emu
from cites import iter_frames

IN, OUT = sys.argv[1], sys.argv[2]
P = Presentation(IN)
jp = lambda t: re.search(r'[぀-ヿ一-鿿（）：]', t) is not None

TR = {
 'VLMのRobot Learningへの応用': 'Applications of VLMs to Robot Learning',
 # 2
 'Code as Policy (CaP) の再注目': 'Code as Policy (CaP) is back in focus',
 'GPT-6 Astra（OpenAI、2026年9月）は空間推論が向上し、コードでロボットを直接動かす': 'GPT-6 Astra (OpenAI, Sep. 2026): better spatial reasoning; drives robots directly with code',
 'ASPIRE（NVIDIA GEAR）はスキルをコードとして自動発見。LIBERO-Pro [Zhou+ 2025] 80 タスクで 99%': ['ASPIRE (NVIDIA GEAR) discovers skills as code; 80 LIBERO-Pro [Zhou+ 2025] tasks at ', '99%'],
 '基盤モデルが強いほど成功率が上がる（GPT-6 Luna 15%、Claude Opus 5.5 99%）': ['Stronger base models score higher (GPT-6 Luna 15%, Claude Opus 5.5 ', '99%', ')'],
 # 3
 'VLM の能力をロボット学習にどう使うか': 'How to use VLM capabilities in robot learning',
 'Code as Policyは精密な操作や両腕の協調がまだ弱い（RoboDojo [2026] 22.5%）': 'Code as Policy is still weak at precise and bimanual manipulation (RoboDojo [2026]: 22.5%)',
 'VLM の空間理解・推論・コード生成能力をRobot Learningに使いたい': 'We want to use VLM spatial understanding, reasoning and code generation in robot learning',
 '→Real2Sim、失敗検出、推論時の誘導の3領域から1本ずつ論文を紹介': '→ One paper each from Real2Sim, failure detection and inference-time steering',
 'VLM（空間理解 ・ 推論 ・ コード生成）': 'VLM (spatial understanding, reasoning, code generation)',
 '動画から Sim を作り、評価と学習データに使う': 'Build a sim from a video; use it for evaluation and training data',
 '② 失敗検出': '② Failure detection',
 '③ 推論時の誘導': '③ Inference-time steering',
 '監視コードで実行中の失敗を検知し予防する': 'Detect and prevent failures during execution with monitor code',
 '報酬関数でポリシーの行動生成を誘導する': "Steer the policy's action generation with a reward function",
 '学習済みポリシー（π0.5 / Diffusion Policy / GR00T …）': 'Pretrained policy (π0.5 / Diffusion Policy / GR00T …)',
 '学習済みポリシー': 'Pretrained policy',
 'VLM の能力をロボット学習に活かす3つの道': 'Three Ways to Use VLMs in Robot Learning',
 # 6
 '概要：SimFoundry': 'Overview: SimFoundry',
 '1本の動画から物理 Sim 上のDigital Twinを作成': 'Builds a digital twin in a physics sim from one video',
 '単に複製するだけでなく，物体・配置・タスクを変えたDigital Cousinsを生成': 'Beyond the copy, generates digital cousins with changed objects, layouts and tasks',
 '→実機ポリシーの Sim 評価と、Sim で学習したポリシーの実機転移に利用': '→ Used to evaluate real policies in sim and to transfer sim-trained policies to the robot',
 'VLM の役割': 'Role of the VLM',
 '物体の検出、質量・摩擦の推定、別の配置やタスクの提案': 'Detect objects, estimate mass and friction, propose other layouts and tasks',
 '→シミュレータのシーン構築とデモの自動生成': '→ Scene construction in the simulator and automatic demo generation',
 'ポリシーとの関係': 'Relation to the policy',
 'VLMを用いて作成したSimで評価・学習': 'Evaluated and trained in the VLM-built sim',
 # 7
 '概要：先行研究との差分': 'Overview: difference from prior work',
 '先行研究は「Sim で学習」「Sim で評価」「自動構築」のどれかに特化': 'Prior systems specialize in one of: training in sim, evaluation in sim, automatic construction',
 'SimFoundry は1つのパイプラインで3つを満たす': 'SimFoundry covers all three in one pipeline',
 '物体・配置・タスクの3軸で，似たような別シーン (Digital Cousins) を作れる': 'Generates similar but different scenes (digital cousins) along objects, layouts and tasks',
 '既存の Real2Sim': 'Prior real-to-sim',
 '構築': 'Build', '手作業・半自動': 'manual / semi-automatic', '動画1本から全自動': 'fully automatic from one video',
 '出力': 'Output', '複製シーン1つ': 'one twin scene', 'Twin ＋ 物体・配置・タスクの Cousins': 'twin + object / layout / task cousins',
 '用途': 'Use', '評価か学習のどちらか': 'evaluation or training', '評価と学習の両方': 'both evaluation and training',
 # 8
 '手法：動画からDigital Twinを作るステップ': 'Method: steps from a video to a digital twin',
 '① Depth Anything 3 [Lin+ 2025] で深度を推定し、点群と床面を得る': '① Depth Anything 3 [Lin+ 2025] estimates depth → point cloud and table plane',
 '② Gemini 3 Pro が物体を列挙し、SAM 3 [Carion+ 2025] で1つずつ切り抜く': '② Gemini 3 Pro lists the objects; SAM 3 [Carion+ 2025] cuts out each one',
 '③ Hunyuan3D [2025] でメッシュ化し、FoundationPose [Wen+ 2024] で姿勢合わせ': '③ Hunyuan3D [2025] builds the mesh; FoundationPose [Wen+ 2024] aligns its pose',
 '④ CoACD [Wei+ 2022] で衝突形状、Gemini が質量・摩擦を推定。PyBullet で安定化': '④ CoACD [Wei+ 2022] collision shapes; Gemini sets mass and friction; PyBullet stabilizes',
 '① 深度 → 点群': '① Depth → point cloud', '② 物体の切り抜き': '② Cut out each object', 'Gemini 3 Pro で列挙、SAM 3 でマスク': 'Gemini 3 Pro lists, SAM 3 masks',
 '③ メッシュ化と姿勢合わせ': '③ Mesh + pose', '④ 物性と安定化': '④ Properties + stabilization', 'CoACD, Gemini（質量・摩擦）, PyBullet → IsaacLab': 'CoACD, Gemini (mass, friction), PyBullet → IsaacLab',
 # 9
 '手法：Digital Cousinsの作り方': ['Method: how ', 'digital cousins', ' are made'],
 '物体：Gemini が部品（取っ手・蓋など）ごとに変更案を出し、画像を編集して 3D 化し直す': ['Objects', ': Gemini proposes edits per part (handle, lid, …); the image is edited and re-meshed'],
 '配置：基準の物体に対する相対的な位置関係を他の物体に割り当てて置き直す': ['Layouts', ': other objects are re-placed by relations to an anchor object'],
 'タスク：Gemini にシーン画像と物体一覧を渡し、OnTop / Inside などの述語でタスク目標を書かせる': ['Tasks', ': Gemini reads the scene and object list; writes goals with OnTop / Inside'],
 # 10
 '実験設定': 'Experimental setup',
 '評価：物体の初期位置を 5×5 の格子から 25 通り選び、Sim と実機で同じ分布にそろえる': ['Evaluation', ': 25 start positions per object from a 5×5 grid, the same distribution in sim and real'],
 '評価指標：成功率の相関（Pearson r）と、ポリシー順位の入れ替わり（MMRV）を評価': ['Metrics', ': correlation of success rates (Pearson r) and rank flips between policies (MMRV)'],
 '学習：デモ 10〜15 本 → MimicGen [Mandlekar+ 2023] で拡張 → π0.5 / Flow Policy': ['Training', ': 10-15 demos → MimicGen [Mandlekar+ 2023] augmentation → π0.5 / flow policy'],
 'Fig. J.1 in Ranawaka et al., 2026：Stack Dishware の初期位置グリッド。各物体 25 点から毎回サンプル': 'Fig. J.1 in Ranawaka et al., 2026: start-position grid for Stack Dishware; each object is sampled from 25 points',
 '評価（実機ポリシーを Sim で）': 'Evaluation (real policies in sim)', '学習（Sim のデータで実機へ）': 'Training (sim data → real robot)',
 'ロボット': 'Robots', 'DROID（Franka 1本腕）、YAM（両腕）': 'DROID (one Franka arm), YAM (two arms)', '同じ 2 種': 'the same two',
 'ポリシー': 'Policies', 'ゼロショット：π0, π0.5, GR00T N1.6 / N1.7, DreamZero': 'Zero-shot: π0, π0.5, GR00T N1.6 / N1.7, DreamZero',
 '微調整：π0, π0.5, GR00T N1.6（実機デモ 50 本）': 'Fine-tuned: π0, π0.5, GR00T N1.6 (50 real demos)',
 'DROID：π0 / π0.5 を微調整': 'DROID: fine-tune π0 / π0.5', 'YAM：Flow Matching をゼロから学習': 'YAM: flow matching from scratch',
 'タスク': 'Tasks', 'ゼロショット 4 + 微調整 3 の計 7': '4 zero-shot + 3 fine-tuned = 7', 'Pot on Stove など 3 + 13 タスク': '3 + 13 tasks, e.g. Pot on Stove',
 'データ': 'Data', 'タスクごとに 25 試行（右図の位置から）': '25 trials per task (positions as in the grid)',
 'テレオペ 10〜15 本 → MimicGen → 材質・カメラをランダム化': '10-15 teleop demos → MimicGen → material / camera randomization',
 # 11
 '結果：再構成の品質': 'Result: reconstruction quality',
 '12シーンでゼロショットの F1 は 0.81〜0.92（SAM3D [SAM 3D Team 2025] は 0.66〜0.71）': 'Zero-shot F1 of 0.81-0.92 on 12 scenes (SAM3D [SAM 3D Team 2025]: 0.66-0.71)',
 '1物体あたり約5分。3分の手作業調整を足すと F1 は 0.93〜0.99': 'About 5 minutes per object; 3 minutes of manual tuning raises F1 to 0.93-0.99',
 'Limitation: 卓上シーン前提．基盤モデルの性能依存': 'Limitation: tabletop scenes only; depends on the foundation models',
 '家のダイニング：実世界 → 複製シーン': 'Dining room: real → reconstructed', 'おもちゃの机：実世界 → 複製シーン': 'Toy table: real → reconstructed',
 '▶ 前半が実世界、後半が Sim。瓶の形やへらの向きまで一致する': ['▶ ', 'First half real, second half sim; bottle shape and spatula pose match'],
 '▶ 小さな物（クッキー、にんじん）も個別のメッシュになる': ['▶ ', 'Small items (cookie, carrot) become individual meshes'],
 # 12
 '結果：Sim性能と実機性能の相関': 'Result: sim vs. real correlation',
 '7タスク × 5ポリシーを Sim と実機の両方で評価': '7 tasks × 5 policies evaluated both in sim and on the real robots',
 '平均 Pearson r = 0.911、MMRV = 0.018（順位の逆転がほぼない）': 'Mean Pearson r = 0.911, MMRV = 0.018 (almost no rank flips)',
 'サブタスク単位の評価': 'Sub-task evaluation', '長期タスクの弱い段階も分かる': 'Shows the weak stage of long tasks',
 'モデルの得意・不得意も見える': 'Reveals model strengths', 'GR00T N1.7 は精密な把持に強い': 'GR00T N1.7: precise grasping', 'π0.5 は言語の追従に強い': 'π0.5: language following',
 # 13
 '結果：実機への転移と Digital Cousins の効果 [1/2]': 'Result: sim-to-real transfer and digital cousins [1/2]',
 'ゼロショットSim2RealでSR 99〜100%': 'Zero-shot sim-to-real: SR 99-100%',
 '物体・配置・タスクのDigital Cousinsで実機の成功率が最大40%向上': 'Object / layout / task cousins raise real success by up to 40%',
 '13タスクの Sim データで π0.5 を微調整し、未学習タスクでもSR 29%': 'π0.5 fine-tuned on 13 sim tasks: SR 29% on unseen tasks',
 'Fig. 5 in Ranawaka et al., 2026   A: 物体の Cousins は未知の物体に効く   B: 配置の Cousins は新しい配置に効く   C: 関連タスクのデモが目標タスクを押し上げる': 'Fig. 5 in Ranawaka et al., 2026   A: object cousins help on unseen objects   B: layout cousins help on new layouts   C: demos of related tasks lift the target task',
 # 14
 '結果：実機への転移と Digital Cousins の効果 [2/2]': 'Result: sim-to-real transfer and digital cousins [2/2]',
 '左は Sim で学習した両腕ポリシー（YAM）。中は同じポリシーを実機で実行': 'Left: bimanual policy trained in sim (YAM). Middle: the same policy on the real robot',
 '右は未知の物体での実行。物体の Digital Cousins を学習に混ぜた効果': 'Right: an unseen object, thanks to object cousins mixed into training',
 'Pot on Stove は実機で成功率 99%': 'Pot on Stove reaches 99% on the real robot',
 'Sim で学習（YAM、両腕）': 'Trained in sim (YAM, bimanual)', '同じポリシーを実機で実行': 'Same policy on the real robot', '未知の物体で実行': 'Unseen object',
 '▶ 複製シーンの中で鍋をコンロへ運ぶ': ['▶ ', 'Carries the pot to the stove inside the twin'],
 '▶ 微調整なしで実機でも同じ動き': ['▶ ', 'Same motion on the real robot, no fine-tuning'],
 '▶ 学習にない黄色いボウルでも掴める': ['▶ ', 'Grasps a yellow bowl never seen in training'],
 # 16
 '概要：Code-as-Monitor': 'Overview: Code-as-Monitor',
 'タスクのサブゴールごとに，VLM が守るべき条件とそれを監視するコードを書く': 'Per subgoal, the VLM writes the conditions to keep and the monitor code',
 'ポリシー実行中に，生成したコードが失敗の兆候を監視': 'While the policy runs, the generated code watches for signs of failure',
 '→条件が破られたらポリシーを止めて再計画': '→ If a condition is violated, stop the policy and re-plan',
 '守るべき条件を文章で書き、それを判定するコードを書く': 'Write the conditions to keep as text, and the code that checks them',
 '→実行中の監視プロセス。点を追跡し、コードを毎フレーム実行する': '→ A monitor process: tracks points and runs the code every frame',
 'そのまま動く。条件を破ったら止められ、再計画を受ける': 'Runs unchanged; stopped and re-planned when a condition breaks',
 # 17
 '概要：既存の失敗検出手法との違い': 'Overview: difference from prior failure detection',
 '既存研究では，VLM に画像を見せて失敗したかを問うため，判定が遅い': 'Prior work shows the VLM an image and asks whether it failed, so detection is slow',
 'CaMは先にVLM にmonitorコードを書かせ、以後はコードが毎フレーム検査する': 'CaM has the VLM write monitor code first; the code then checks every frame',
 '事後検知（Reactive）': 'Reactive detection', '失敗が起きた後に検知。例：ロブスターが落ちた': 'After the failure, e.g. the lobster fell out',
 '事前予防（Proactive）': 'Proactive prevention', '兆候を捉えて防ぐ。例：鍋が傾いたので直す': 'Catch the sign, e.g. the pan tilts, so level it',
 # 18
 '手法：全体の流れ': 'Method: overall flow',
 'Constraint Generator：VLMがサブゴールと、その実行中・完了時の制約条件を書く': ['Constraint Generator', ': VLM writes the subgoal and its constraints (during / upon completion)'],
 'Constraint Painter：タスクに関係する部位を点・線・面として画像に描き込む': ['Constraint Painter', ': relevant parts drawn on the images as points, lines, surfaces'],
 'Constraint Monitor：VLMがmonitorコードを書き、点を追跡しながら実行': ['Constraint Monitor', ': VLM writes monitor code, run while tracking the points'],
 # 19
 '手法：制約要素の作り方': 'Method: building the constraint elements',
 '制約条件から ConSegが物体と部位のマスクを生成': 'ConSeg produces object and part masks from the constraint text',
 '深度情報を用いてマスクを3D 点群にし、要素の種類（点・線・面）に応じて点群を連結': 'Masks → 3D points via depth, connected by element type (point / line / surface)',
 'BridgeData V2 [Walke+ 2023] の 10,181 軌道を GPT-4o で自動注釈して学習': 'Trained on 10,181 BridgeData V2 [Walke+ 2023] trajectories auto-annotated with GPT-4o',
 # 20
 '手法：monitorコードの生成・実行': 'Method: generating and running the monitor code',
 '制約要素の 3D 座標とその履歴を入力に受け取り，角度や距離に基づき，成否とその理由を返す': "Input: the elements' 3D coordinates and history. Output: (failed?, reason)",
 '例：鍋の3点の制約要素から法線を求め、傾きが 15°を超えたら「鍋が水平でない」と返す': ['Example', ': normal from the pan\'s 3 points; tilt over 15° returns "the pan is not level"'],
 '生成直後に全分岐をテストし、エラーなら再生成': 'Every branch is tested right after generation; errors trigger regeneration',
 'サブゴールの開始時に VLM を1回呼ぶ': 'Call the VLM once at the start of a subgoal', '要素を追跡する（CoTracker [Karaev+ 2024]）': 'Track the elements (CoTracker [Karaev+ 2024])',
 'コードを毎フレーム評価する': 'Evaluate the code every frame', 'False なら停止し、理由を付けて再計画': 'On False: stop, return the reason, re-plan',
 # 21
 '結果：Simulation実験 [1/2]': 'Result: simulation [1/2]',
 '設定：点・線・面の3種類の外乱で失敗を誘発し、成功率・実行時間・token 数を比較': ['Setup', ': point / line / surface disturbances induce failures; compare success, time and tokens'],
 '成功率：外乱を強くするほど差が開く。積み木積み（落下 p = 0.3）は 21.7% → 88.3%': ['Success', ': the gap widens with stronger disturbance; stacking (drop p = 0.3) 21.7% → 88.3%'],
 '効率：VLM に毎回問う DoReMi [Guo+ 2023] より実行時間 −34.8%、token −52.2%': ['Efficiency', ': time −34.8% and tokens −52.2% vs. DoReMi [Guo+ 2023] (VLM queried every step)'],
 'Data from Table 1, 2 in Zhou et al., 2025 (OmniGibson [Li+ 2022]).  ReKep [Huang+ 2024]：監視なしのポリシー、DoReMi [Guo+ 2023]：VLM に画像で問い続ける比較手法。Inner Monologue [Huang+ 2022]：サブゴール完了時だけ問う比較手法': 'Data from Table 1, 2 in Zhou et al., 2025 (OmniGibson [Li+ 2022]).  ReKep [Huang+ 2024]: policy without a monitor; DoReMi [Guo+ 2023]: baseline that keeps querying the VLM with images; Inner Monologue [Huang+ 2022]: baseline that asks only when a subgoal completes',
 # 22
 '結果： Simulation実験 [2/2]': 'Result: simulation [2/2]',
 'CaM: 配置に外乱を加えても、本手法は崩れる前に検知して積み直す': 'CaM: even with placement disturbance, it detects before collapse and restacks',
 'DoReMi [Guo+ 2023]: VLM に画像で問い続けるため誤判定が増える': 'DoReMi [Guo+ 2023]: keeps asking the VLM with images, so misjudgments increase',
 '積み木積み：本手法': 'Stacking: CaM', '積み木積み：DoReMi': 'Stacking: DoReMi', 'お茶注ぎ（面の傾き）': 'Pour tea (surface tilt)',
 '▶ 積み木の位置を点で追跡。ずれたら積み直してから次へ': ['▶ ', 'Block positions tracked as points; restacks after a shift'],
 '▶ VLM に毎回問うため、積めているのに失敗と誤判定してやり直す': ['▶ ', 'Asks the VLM each time; misjudges a good stack and redoes it'],
 '▶ ポットの面の傾きを監視し、傾けすぎを止める': ['▶ ', 'Watches the teapot surface; stops over-tilting'],
 # 23
 '結果：実機実験・アブレーション [1/2]': 'Result: real robot and ablation [1/2]',
 'ポリシーに本手法を適用すると、OOD下でもSR 90% 超': 'With CaM on the policy, SR stays above 90% under OOD disturbances',
 '推論が要る長期タスクでは DoReMi [Guo+ 2023] 0% に対しCaM 90%': ['Long-horizon reasoning task: DoReMi [Guo+ 2023] 0% vs. ', 'CaM 90%'],
 'Ablation：多視点・部位分割・点の連結を外すと 65% → 40〜55%': ['Ablation', ': drop multi-view, segmentation or linking → 65% to 40-55%'],
 # 24
 '結果：実機実験・アブレーション [2/2]': 'Result: real robot and ablation [2/2]',
 '左：「動物以外を片付ける」。人が物を動かしても目標を更新して続行': ['Left', ': "clear everything except the animals". Moved objects are retargeted'],
 '右：「果物に近い順に動物を掴む」。馬や梨を動かされると順番を変える': ['Right', ': "grasp animals nearest to the fruits first". Moving them reorders the targets'],
 '把持生成モデルは開ループのまま。監視コードが失敗を検知し、再計画を促す': 'Open-loop grasp model; the monitor code catches failures and re-plans',
 '動物以外を片付ける': 'Clear all except animals', '果物に近い順に動物を掴む': 'Grasp animals nearest to fruits first',
 '0:01 人がぬいぐるみとカップを動かす ': '0:01 a person moves the toy and the cup', '→ 追跡点で目標を更新': '→ target updated from tracked points',
 '0:18 掴んだぬいぐるみを人が抜き取る': '0:18 the toy is pulled out of the hand', '→ 検知して掴み直す': '→ detected, re-grasped',
 '0:03 人が馬を動かす': '0:03 a person moves the horse', '→ 牛が最も近くなり、目標が牛に変わる': '→ the cow is now nearest; target switches',
 '0:14 人が梨を動かす': '0:14 the pear is moved', '→ 距離を再計算し、再び馬へ': '→ distances recomputed; back to the horse',
 # 26
 '概要：VLS': 'Overview: VLS',
 'Diffusion / Flow Policyの行動生成に途中に介入してactionを修正': "Intervenes inside a diffusion / flow policy's action generation to correct the action",
 'VLM はより望ましい行動へ誘導するための微分可能な報酬関数をコードで書く': 'The VLM writes, as code, a differentiable reward that steers toward better actions',
 'Policyは再学習せず、VLM が書いた報酬の勾配でActionをガイダンスする': 'No retraining: the action is guided by the gradient of the VLM-written reward',
 '段階ごとの報酬関数を、微分可能な PyTorch のコードとして書く': 'Write a reward per stage as differentiable PyTorch code',
 '→ポリシーのノイズ除去ループ。各ステップで報酬の勾配を足す': "→ The policy's denoising loop: the reward gradient is added at every step",
 '重みは変えない。生成の途中で行動が少しずつ曲げられる': 'Weights unchanged; the action is bent gradually during generation',
 # 27
 '概要：既存手法との違い': 'Overview: difference from prior methods',
 '既存の推論時誘導は，「候補から選ぶ」か「学習済みモデルの勾配で誘導する」の 2 系統': "Prior methods either pick among candidates or follow a learned model's gradient",
 'VLS は追加の学習なしに候補そのものを動かせる点が異なる（下表）': 'VLS differs in moving the candidates themselves, with no extra training (table)',
 '代表例': 'Examples', 'どう誘導するか': 'How it steers', '弱点': 'Weakness',
 '候補から選ぶ': 'Pick among candidates', '（Test-Time Compute 系）': '(test-time compute)',
 'ポリシーが出した候補を VLM・人・検証器が選ぶ': "A VLM, a person or a verifier picks one of the policy's candidates",
 '候補に良い行動がなければ選べない': 'If no candidate is good, nothing can be picked',
 '学習済みモデルの勾配で誘導': "Steer with a learned model's gradient",
 '価値関数やダイナミクスモデルの勾配でノイズ除去を誘導': 'Gradients of a value or dynamics model guide the denoising',
 '補助モデルの学習が要り、その誤差や好みに引きずられる': 'Needs an extra model; its errors and preferences leak in',
 '本論文 [Liu+ 2026]': 'This paper [Liu+ 2026]',
 'VLM が書いた報酬の勾配で候補そのものを動かし、報酬で選別': 'The gradient of a VLM-written reward moves the candidates; reward-based resampling',
 '追加学習は不要。VLM の誤りは報酬に直結': 'No extra training; VLM mistakes go straight into the reward',
 # 28
 'キーポイント抽出：VLM が物体を挙げ、SAM と深度で番号付きの 3D 点にする': ['Keypoint extraction', ': the VLM names objects; SAM + depth make numbered 3D points'],
 '報酬生成：VLM が段階ごとの報酬を PyTorch の微分可能な関数で書く': ['Reward generation', ': the VLM writes a differentiable PyTorch reward per stage'],
 '誘導付き生成：凍結ポリシーのノイズ除去の各ステップに勾配を足す': ['Guided generation', ': the reward gradient is added at every denoising step'],
 # 29
 '手法：報酬で誘導する仕組み': 'Method: how the reward steers generation',
 'Classifier guidanceで誘導（速度場に報酬の勾配 ∇R を λ 倍して足す）': 'Classifier guidance: λ × the reward gradient ∇R is added to the velocity field',
 '候補行動をバッチ生成し、斥力で広げ（RBF）、勾配で補正し、報酬の重みでResampling': 'Candidate batch: repulsion (RBF), gradient refinement, reward resampling',
 '誘導の強さ λ は報酬の進捗で調整': 'The strength λ adapts to reward progress',
 '候補を引き離す斥力（RBF）': 'Repulsion between candidates (RBF)', '報酬で重み付けした選別（FK）': 'Reward-weighted resampling (FK)', '誘導の強さ λ の調整': 'Adaptive guidance strength λ',
 # 30
 '具体例：チーズをかごに入れる': 'Example: "put the cheese in the basket"',
 '画像からチーズ、かご、周りの物を 3D 点にして番号を振る': 'Cheese, basket and nearby objects become numbered 3D points',
 'かごに近いほど高得点となるようVLM が報酬を記述': 'The VLM writes a reward that is higher the closer to the basket',
 'ノイズ除去の各ステップで勾配を足すと、軌道がかご側へずれていく': 'Each step adds the gradient; the trajectory drifts toward the basket',
 '① 3D の点を取り出す': '① Extract 3D keypoints', '② VLM が報酬をコードで書く': '② VLM writes the reward as code',
 '軌道と点 2 の距離の二乗にマイナス': 'negative squared distance to point 2', '③ 各ステップで勾配を足す': '③ Add the gradient every step',
 '初期候補 → 斥力 → 補正 → 選別': 'init → repulsion → refine → resample', 'かご = 点 2': 'basket = point 2',
 # 31
 '結果： Simulation実験 [1/2]': 'Result: simulation [1/2]',
 '設定：LIBERO-PRO [Zhou+ 2025] と CALVIN [Mees+ 2022]。学習時と条件を変えて評価': ['Setup', ': LIBERO-PRO [Zhou+ 2025] and CALVIN [Mees+ 2022] under shifted conditions'],
 'LIBERO-PRO：凍結 π0.5 + VLS で平均 23.7% → 36.8%。物体の変更では 10.5% → 41%': ['LIBERO-PRO', ': frozen π0.5 + VLS, mean 23.7% → 36.8%; objects changed 10.5% → 41%'],
 'CALVIN：可動物体 94%、関節物体 87%（DynaGuide [Du+ 2025] より +15〜25 pt）': ['CALVIN', ': movable 94%, articulated 87% (+15-25 pt over DynaGuide [Du+ 2025])'],
 'Fig. 3 in Liu et al., 2026：CALVIN で既存の誘導手法と比較': 'Fig. 3 in Liu et al., 2026: CALVIN, vs. prior steering methods',
 'Fig. 4 (left) in Liu et al., 2026（勾配なしで 17%）': 'Fig. 4 (left) in Liu et al., 2026 (no gradient: 17%)',
 # 32
 '左：LIBERO-PRO で物体の位置を変更。凍結 π0.5 は失敗、VLS を付けると成功': ['Left', ': LIBERO-PRO with moved objects. Frozen π0.5 fails; with VLS it succeeds'],
 '右：「壁を避けてキューブを置く」。学習にない指示でも報酬の勾配で壁を避ける': ['Right', ': "avoid the wall": an unseen instruction, met via the reward gradient'],
 '数字付きの点が VLM の選んだキーポイント。報酬はこの点との距離': 'Numbered points are the VLM-selected keypoints; the reward is the distance to them',
 'LIBERO-PRO：π0.5（失敗）': 'LIBERO-PRO: π0.5 (fail)', 'LIBERO-PRO：+VLS（成功）': 'LIBERO-PRO: +VLS (success)',
 '壁を避ける：ベース（失敗）': 'Avoid the wall: base (fail)', '壁を避ける：+VLS（成功）': 'Avoid the wall: +VLS (success)',
 '▶ 学習時の位置へ向かい、空振りする': ['▶ ', 'Reaches for the training-time spot and misses'],
 '▶ 数字付きの点が目標。報酬で補正される': ['▶ ', 'Numbered points are the target; corrected by the reward'],
 '▶ 「壁を避けて」を知らず、壁にぶつかる': ['▶ ', 'Does not know "avoid the wall"; hits it'],
 '▶ 壁から遠いほど高報酬 → 迂回する': ['▶ ', 'Reward grows away from the wall → detours'],
 # 33
 '結果：実機実験 [1/2]': 'Result: real robot [1/2]',
 '学習時と同じ条件では物体選択と配置のタスクで 50% → 69%（+19 pt）': ['In-distribution pick-and-place tasks: ', '50% → 69%', ' (+19 pt)'],
 '条件を変えても安定。未知のマグでは 0% → 40%、平均 42% → 69%': 'Stable under shifts: unseen mug 0% → 40%, average 42% → 69%',
 '限界は推論の遅さ。1チャンクの生成に約1秒かかる': 'Limitation: latency, about 1 second per action chunk',
 # 34
 '結果②：実機実験 [2/2]': 'Result: real robot [2/2]',
 '左：学習時と同じ条件。「バナナを緑の皿に置く」': ['Left', ': in-distribution, "put the banana on the green plate"'],
 '中：未知の物体。バナナの代わりにマグを置く（0% → 40%）': ['Middle', ': an unseen object, a mug instead of the banana (0% → 40%)'],
 '右：皿の位置を入れ替えた場合。指示は同じまま、位置の変化に追従する': ['Right', ': plates swapped; same instruction, the policy follows the new positions'],
 '同じ条件：バナナを緑の皿に': 'In-distribution: banana on green plate', '未知の物体：マグを皿に': 'Unseen object: mug on plate', '皿の位置を入れ替え': 'Plates swapped',
 '▶ 左上の Guide が誘導の有無、Sig_Str が強さ。仕上げで弱まる': ['▶ ', 'Top-left: Guide = on/off, Sig_Str = strength; it weakens near the end'],
 '▶ 学習にないマグでも、点との距離で報酬が書けるので掴める': ['▶ ', 'A mug never seen in training; distance-to-point rewards still work'],
 '▶ 指示は同じ。皿の位置を点で取り直すだけで追従する': ['▶ ', 'Same instruction; re-extracted plate points are enough to follow'],
 # 35
 'まとめ：VLM の出力をポリシーのどこに入れるか': 'Summary: where the VLM output enters the policy',
 '3本とも VLM が書いたものをポリシーの外側から入れる。違いは入れる場所': 'All three add VLM output from outside the policy; the difference is where',
 'CaM と VLS は同じ 3D 点とコードを共有でき、SimFoundry はそれを大量に試す場になる': 'CaM and VLS can share points and code; SimFoundry is the testbed at scale',
 'VLM が書くもの': 'What the VLM writes', 'Digital Twin と Digital Cousins': 'Digital twin and cousins', '制約と監視コード': 'Constraints + monitor code', '報酬関数': 'Reward function',
 '入れ先': 'Where it goes', '学習データ': 'Training data', '実行の停止条件': 'Stop condition at run time', '行動生成の目的関数': 'Objective of generation',
 '効果': 'Effect', 'Sim 評価 r = 0.91、実機 +40%': 'Sim eval r = 0.91; real +40%', '外乱下 +28.7 pt、時間 −31.8%': '+28.7 pt under disturbance; time −31.8%', 'LIBERO-PRO +13 pt、実機 +19 pt': 'LIBERO-PRO +13 pt; real +19 pt',
 # 36
 '自分の取り組み：誘導と監視の組み合わせ': 'My own work: steering + monitoring',
 '最近、VLS の誘導と Code-as-Monitor の監視を組み合わせた手法を検証中': 'Lately I have been testing VLS-style steering combined with CaM-style monitoring',
 'VLM が書いたコードを生成時の誘導と実行時の監視の両方に使う': 'VLM-written code both steers generation and monitors execution',
 '動画は LIBERO [Liu+ 2023] での例。右側が VLM の判定と監視コードのログ': 'Videos: LIBERO [Liu+ 2023]; right panel = VLM judgment and monitor log',
 'LIBERO-Goal：誘導 + 監視': 'LIBERO-Goal: steering + monitoring', 'LIBERO-Object：誘導 + 監視': 'LIBERO-Object: steering + monitoring',
}


def run_key(r):
    f = r.font
    col = str(f.color.rgb) if (f.color is not None and f.color.type is not None) else None
    return (bool(f.bold), col, f.font_size_pt if False else (f.size.pt if f.size else None), bool(f.italic))


missing = set(); mismatch = []
for si, slide in enumerate(P.slides, 1):
    for tf in iter_frames(slide):
        for para in tf.paragraphs:
            runs = [r for r in para.runs]
            full = ''.join(r.text for r in runs)
            if not jp(full):
                continue
            key = full
            if key not in TR:
                missing.add((si, full)); continue
            en = TR[key]
            # segments of identical formatting
            segs = []  # list of [key, [runs]]
            for r in runs:
                if not r.text:
                    continue
                k = run_key(r)
                if segs and segs[-1][0] == k:
                    segs[-1][1].append(r)
                else:
                    segs.append([k, [r]])
            if isinstance(en, str):
                if len(segs) > 1:
                    mismatch.append((si, full[:40], 'str for %d segs' % len(segs)))
                for i, (k, rs) in enumerate(segs):
                    rs[0].text = en if i == 0 else ''
                    for r in rs[1:]:
                        r.text = ''
            else:
                if len(en) != len(segs):
                    mismatch.append((si, full[:40], 'list %d vs segs %d' % (len(en), len(segs))))
                    rs0 = segs[0][1]
                    rs0[0].text = ''.join(en)
                    for r in runs[1:]:
                        if r is not rs0[0]: r.text = ''
                    continue
                for (k, rs), e in zip(segs, en):
                    rs[0].text = e
                    for r in rs[1:]:
                        r.text = ''

# ---------------- swap Japanese chart images for English ones
import glob, os
ja_imgs = {}
for f in glob.glob(S + '/diag/*_ja.png'):
    ja_imgs[open(f, 'rb').read()] = f.replace('_ja.png', '_en.png')
swapped = 0
for slide in P.slides:
    for sh in list(slide.shapes):
        if sh.shape_type == 13:
            try:
                blob = sh.image.blob
            except Exception:
                continue
            if blob in ja_imgs:
                x, y, w, h = sh.left, sh.top, sh.width, sh.height
                el = sh._element; parent = el.getparent(); idx = parent.index(el)
                parent.remove(el)
                pic = slide.shapes.add_picture(ja_imgs[blob], x, y, width=w, height=h)
                parent.remove(pic._element); parent.insert(idx, pic._element)
                swapped += 1

# ---------------- English speaker notes from the earlier English draft
def parse(s, tag):
    d = {}; cur = None
    for line in s.split('\n'):
        m = re.match(r'^## (?:スライド|Slide)\s*(\d+)', line)
        if m: cur = int(m.group(1))
        elif line.startswith(tag) and cur: d[cur] = line[len(tag):].strip()
    return d
jn = parse(open(S + '/ja/draft_ja.md').read(), 'ノート:')
enn = parse(open(S + '/en/draft_en.md').read(), 'Notes:')
notes_set = 0; notes_miss = []
for si, slide in enumerate(P.slides, 1):
    if not slide.has_notes_slide:
        continue
    t = slide.notes_slide.notes_text_frame.text.replace('[J] ', '', 1).strip()
    hit = [k for k, v in jn.items() if v == t]
    if si == 1:
        m1 = re.search(r'^Notes: (.*)$', open(S + '/en/draft_en.md').read(), re.M)
        slide.notes_slide.notes_text_frame.text = '[E] ' + m1.group(1); notes_set += 1; continue
    if hit and hit[0] in enn:
        slide.notes_slide.notes_text_frame.text = '[E] ' + enn[hit[0]]
        notes_set += 1
    else:
        notes_miss.append(si)

P.save(OUT)
print('saved', OUT, 'slides', len(P.slides), 'images swapped', swapped, 'notes set', notes_set, 'notes missing', notes_miss)
for m in sorted(missing): print('MISSING TR:', m)
for m in mismatch: print('MISMATCH:', m)
