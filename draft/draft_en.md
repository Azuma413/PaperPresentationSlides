# Three Ways to Use VLMs in Robot Learning

Real2Sim ・ Failure Detection ・ Inference-Time Steering

Notes: Good afternoon, everyone. Today I will present three papers from the perspective of "how can we bring the capabilities of today's VLMs into robot learning?" With foundation models such as GPT-6 Astra, manipulation benchmarks are starting to be solved. At the same time, using a VLM directly as the policy is still weak at precise and contact-rich manipulation. So I picked one paper from each of three areas where a VLM is combined with a pretrained policy: Real2Sim, failure detection, and inference-time steering.

## Slide 2 Background: VLMs are starting to solve benchmarks

- GPT-6 Astra (OpenAI, Sep. 2026): strong spatial reasoning; drives robots by code
- ASPIRE (NVIDIA GEAR): discovers skills as code; 99% on 80 LIBERO-Pro tasks
- Stronger base models score higher (GPT-6 Luna 15%, Claude Opus 5.5 99%)

Notes: First, some background. GPT-6 Astra, released by OpenAI in September 2026, has been described as a step change in spatial reasoning. Using it to write code that drives a robot directly has become common, and the left figure shows a case where it planned and solved a bimanual spatial-constraint puzzle. On the right is ASPIRE from NVIDIA GEAR. A coding agent writes robot skills as code, inspects failures, revises the code, and grows a library of reusable skills. Version 1.0, released in October, reaches 99% success on the 80 LIBERO-Pro tasks. The right figure shows success on 10 tasks: the stronger the base model, the higher the success, from 15% with GPT-6 Luna to 99% with Claude Opus 5.5. Simulation benchmarks are starting to be solved by VLM-centric methods.

## Slide 3 Background: How to use VLMs in robot learning

- VLMs as the policy are still weak at precise, bimanual tasks (RoboDojo 22.5%)
- Instead: keep a pretrained policy and use the VLM around it
- Today: one paper each from Real2Sim, failure detection, and steering

Notes: So how should we use these capabilities in robot learning? There are evaluations that use the VLM directly as a policy, but they report 22.5% on RoboDojo and 11.1% on LIBERO-GeoMotion with geometric constraints, and precise, contact-rich and bimanual manipulation remains weak. There is a gap between semantic reasoning and physical execution. This motivates combining the VLM with a pretrained policy such as a VLA or a diffusion policy, and using the VLM's spatial understanding, reasoning and code generation around the policy. Today I split this into three areas. The first is Real2Sim, which uses the VLM's spatial understanding to copy a real scene into simulation for evaluation and training data. The second is failure detection, where VLM-written monitor code detects and prevents failures during execution. The third is inference-time steering, where VLM-written reward functions steer the action generation of a pretrained policy. I will present one paper for each, in this order.

## Slide 4 Papers (all three)

Notes: These are the three papers. The first is SimFoundry from NVIDIA, Stanford and Georgia Tech, which turns a single real-world video into a simulation environment for policy evaluation and training. The second is Code-as-Monitor from Beihang University, Peking University, BAAI and Galbot, published at CVPR 2025, which detects and prevents robot failures in real time with VLM-generated code. The third is VLS from the University of Washington and AI2, which steers a frozen generative policy at inference time with VLM-written rewards. I will go through them in the order Real2Sim, failure detection, steering.

## Slide 5 Papers (highlight paper 1)

Notes: Let's start with SimFoundry. In one sentence, it is a modular system that automatically builds a simulation environment usable for both evaluation and training from a single real-world video. Three things to remember: it reconstructs a real scene in simulation, it generates many affordance-preserving variants of that reconstruction, and the result serves both sim evaluation of real-world policies and sim-to-real transfer of policies trained in simulation.

## Slide 6 SimFoundry Overview 1: Real2Sim

- Builds a physics-sim scene automatically from one real-world video
- VLM: detects objects, estimates mass and friction, proposes layouts/tasks
- The policy is evaluated in that sim, or trained on data generated in it

Notes: SimFoundry belongs to the first of the three areas, Real2Sim. The input is a single real-world video plus the policy you want to evaluate or train. The VLM and vision foundation models find the objects in the video, turn them into 3D, estimate mass and friction, and propose alternative layouts and tasks. In other words, the VLM does not drive the policy; it builds the arena in which the policy is tested. The policy is what gets evaluated in the sim, or trained on sim data. Unlike the next two papers, the VLM is not involved at execution time, so there is no latency issue.

## Slide 7 SimFoundry Overview 2: what SimFoundry is

- Input: one video. Output: a physics-sim replica of the scene (the twin)
- Then unlimited variants of objects, layouts and tasks (digital cousins)
- Two uses: evaluate real policies in sim; train in sim, deploy on the robot

Notes: Here is the overview. The input is a single video of a real scene and the output is an interactive scene in a physics simulator, which the paper calls a digital twin. From the twin, SimFoundry generates an unlimited number of variants with different object shapes, layouts and tasks, called digital cousins. The environments serve two purposes, shown by the arrows: evaluating real-world policies in simulation, and training policies in simulation that transfer to the real robot.

## Slide 8 SimFoundry Overview 3: vs. prior real-to-sim systems

- Prior systems each do one thing (train in sim, evaluate in sim, or auto-build)
- SimFoundry does all three in one pipeline, with articulated objects and two arms
- Only SimFoundry makes variants on all three axes: objects, layouts, tasks

Notes: How does it differ from prior real-to-sim systems? The table is Table 1 of the paper, comparing existing systems feature by feature. Some support sim-to-real training, some real-to-sim evaluation, some automatic scene construction, but most specialize in one. SimFoundry covers all three in a single pipeline and also handles articulated objects such as drawers and bimanual robots. And the last three rows show that only SimFoundry generates variants along all three axes: objects, layouts and tasks.

## Slide 9 SimFoundry Method 1: four steps from a video to a twin

- ① Depth Anything 3 estimates depth, giving a point cloud and the table plane
- ② Gemini 3 Pro lists the objects; SAM 3 cuts out each one
- ③ Hunyuan3D turns each crop into a mesh; FoundationPose aligns its pose
- ④ CoACD collision shapes; Gemini sets mass and friction; PyBullet stabilizes

Notes: The four reconstruction steps. Each step calls an off-the-shelf foundation model, and the models are interchangeable. First, Depth Anything 3 is run on the first frame of the video to estimate depth and build a point cloud; SAM 3 finds the table plane to align with the simulator frame. Second, Gemini 3 Pro lists the objects in the image and SAM 3 cuts out a mask for each one; each cut-out object is removed from the image and depth by inpainting, and the remaining objects are found in turn. Third, each crop is upsampled with Gemini's image model and turned into a mesh by Hunyuan3D 2.1 or TRELLIS.2, and FoundationPose aligns its position and orientation to the point cloud. For drawers and doors, Gemini names the movable parts and joint types, and an Articulate-Anything-style module adds the joints. Fourth, CoACD builds collision geometry, Gemini assigns mass and friction from common sense, PyBullet resolves penetrations to a stable configuration, and the scene is exported to IsaacLab or OmniGibson.

## Slide 10 SimFoundry Method 2: making the three kinds of variants

- Objects: Gemini edits each part (handle, lid) in the image; the mesh is rebuilt
- Layouts: pick an anchor object; place the rest by relations (LeftOf, OnTop)
- Tasks: Gemini reads the scene and object list; writes goals with OnTop / Inside

Notes: How the variants are made. For object cousins, Gemini first decomposes the object into functional parts such as handle, lid and body, then proposes changes per part along geometry, structure and appearance, for example "make the handle thicker" or "remove the lid". An image-editing model applies the change to the crop, Hunyuan3D regenerates the mesh, and Gemini checks that the result is plausible, discarding odd ones. For scene cousins, an anchor object is chosen and relations such as LeftOf, RightOf, OnTop and Inside are sampled for the other objects, giving meaningful new layouts rather than position noise; distractor objects can also be added. For task cousins, Gemini receives the simulated scene image, the list of manipulable objects and the robot constraints, and writes goal states with predicates such as OnTop and Inside. The output is directly usable for demonstration generation.

## Slide 11 SimFoundry Method 3: evaluation and training protocol

- Evaluation: 25 start poses per task from a 5×5 grid, matched in sim and real
- Metrics: Pearson r of success rates, and how often policy rankings flip (MMRV)
- Training: 10-15 human demos → MimicGen → fine-tune π0.5, or train a flow policy

Notes: How the sim is used. For real-to-sim evaluation, each task samples 25 object start positions from a 5-by-5 grid, and the same distribution is used in sim and on the real robot. Each rollout scores 0 or 1, and per-policy success rates are compared across sim and real. Two metrics are used: Pearson's r for the linear correlation of success rates, and MMRV for how often the ranking of policies in sim disagrees with the real ranking. For sim-to-real training, a human first collects 10 to 15 teleoperated demos, MimicGen multiplies them while randomizing materials and camera poses, and the data is used to fine-tune the DROID checkpoints of π0 and π0.5, or, on YAM, to train a flow-matching policy from scratch. Checkpoints are evaluated periodically in sim and the best one is deployed on the real robot.

## Slide 12 SimFoundry Result 1: sim evaluation predicts real success

- 7 tasks × 5 policies, evaluated in sim and on the real robots
- Mean Pearson r = 0.911, MMRV = 0.018 (almost no rank flips)
- r is 0.59 above PolaRiS, with no fine-tuning of the policies

Notes: The first result is real-to-sim evaluation. Seven tasks on two real setups, a single-arm Franka in the DROID setup and a bimanual YAM, with five policies: π0, π0.5, GR00T N1.6, N1.7 and DreamZero, evaluated both in simulation and on the real robots. In the scatter plot, SimFoundry's blue markers lie close to the diagonal, with a mean Pearson correlation of 0.911 and a mean maximum rank violation of 0.018. The orange markers of the baseline PolaRiS are scattered, and the correlation gap is more than 0.59. Moreover, PolaRiS lightly fine-tunes the policies on its simulation data, while SimFoundry evaluates the policies zero-shot. Evaluating at the sub-task level raises the correlation from 0.90 to 0.95 and tells you which stage of a task is weak.

## Slide 13 SimFoundry Result 2: sim-to-real transfer and variants

- Sim-only training reaches 99-100% zero-shot on the real robots
- Object / scene / task variants: real success +17 / +21 / +40%
- π0.5 fine-tuned on 13 sim tasks: 29% on held-out tasks

Notes: The second result is sim-to-real training. Policies trained only on SimFoundry data transfer zero-shot to the real robots, reaching 99% on Pot on Stove with YAM and 100% on Stack Dishware with DROID. The figure shows the effect of the variants. In panel A, object cousins improve robustness to unseen objects, a 50-point gain on unseen Pot on Stove objects. In panel B, scene cousins improve layout generalization: 16% on cousin layouts where the twin-only policy gets 0%, and up to 28 points even on the twin layout. In panel C, with the total number of demos fixed, replacing some target-task demos with related-task demos actually raises success on the target task, by 60 points on Throw Away Trash. Fine-tuning π0.5 on multi-task data from 13 tasks gives 29% on held-out tasks and up to 18% improvement in the real world.

## Slide 14 SimFoundry Result 2: real-robot demo (video)

- Left: bimanual policy trained in sim (YAM). Middle: same policy on real
- Right: objects never seen in training, thanks to object cousins
- Pot on Stove reaches 99% on the real robot

Notes: Here are policies trained in simulation running on the real robot. On the left is the bimanual YAM policy trained inside simulation, and in the middle the same policy executed on the real robot without any fine-tuning. On the right it runs on objects that were not in the training set, which is where object cousins in the training data pay off. On the Pot on Stove task the real-world success rate was 99%.

## Slide 15 SimFoundry Result 3: reconstruction quality (video)

- Zero-shot F1 of 0.81-0.92 on 12 scenes (SAM3D: 0.66-0.71)
- About 5 minutes per object; 3 minutes of tuning raises F1 to 0.93-0.99
- Limits: tabletop scenes only; inherits each foundation model's failures

Notes: Finally, the quality of the reconstruction itself. The videos show a dining room on the left and a toy table on the right; the first half is the real scene and the second half the reconstruction in simulation. The bottle shape, the spatula pose and even small items such as a cookie come out as individual meshes. On a geometric evaluation over 12 scenes, the fully automatic pipeline reaches F1 scores of 0.81 to 0.92, above SAM3D's 0.66 to 0.71. Reconstruction takes about five minutes per object, and three minutes of manual tuning per object raises F1 to 0.93 to 0.99. The stated limitations are the tabletop assumption and inheriting the failure modes of each underlying foundation model.

## Slide 16 Papers (highlight paper 2)

Notes: The second paper is Code-as-Monitor, from CVPR 2025. In one sentence, it unifies reactive failure detection and proactive failure prevention as checking whether constraints are satisfied, and monitors them in real time with VLM-generated code. Three things to remember: unifying reactive and proactive detection, constraint elements that abstract objects into points, lines and surfaces, and calling the VLM only once per subgoal.

## Slide 17 Code-as-Monitor Overview 1: failure detection

- Runs beside an (open-loop) policy, watches for failure signs, and stops it
- Per subgoal, the VLM writes conditions to keep and the code to check them
- On a violation, the policy stops and the reason goes to the VLM to re-plan

Notes: Code-as-Monitor is the failure-detection area. The input is the task instruction, camera images and the running policy, which may be open-loop. For each subgoal the VLM writes the conditions that must hold and the code that checks them. The policy itself runs unchanged while the code watches alongside it; when a condition is violated the policy is stopped immediately and the reason is returned to the VLM for re-planning. The VLM never touches the policy; it places a monitor outside it.

## Slide 18 Code-as-Monitor Overview 2: what Code-as-Monitor is

- Reactive: detect a failure after it happens. Example: the lobster fell out
- Proactive: catch the early sign and prevent it. Example: the pan tilts
- Both become checks of whether constraints hold, run by VLM-written code

Notes: Here is the overview. Failure detection has two modes. Reactive detection identifies a failure after it occurs: in panel (a) the lobster jumps out of the pan and the robot detects that it fell. Proactive detection prevents foreseeable failures: in panel (b) the robot detects that the pan is tilting and corrects it before anything falls. The method treats both uniformly as checking whether constraints such as "the pan is level" and "the lobster is in the pan" hold, and runs that check with code written by a VLM. As panel (c) shows, combined with an open-loop policy it becomes a closed-loop system that copes with human interference in cluttered scenes.

## Slide 19 Code-as-Monitor Overview 3: vs. prior failure detection

- Prior work asks the VLM "did it fail?" from images: slow, and misreads 3D
- Asking only when a subgoal completes misses the early signs
- Here the VLM is called once to write code; that code checks every frame

Notes: How it differs from prior failure detection. Most prior work shows a VLM images and asks whether the task failed. Asking every frame, as in the top row, is slow, and 3D relations are misread from a single image, so misjudgments increase. Asking only when a subgoal completes, as in the middle row, misses the early signs until the end. This method, in the bottom row, has the VLM write checking code once at the start of a subgoal, after which the code checks the coordinates of tracked points every frame as numbers. It catches early signs such as the pan starting to tilt and stops the policy before the failure happens. With a single VLM call it is fast and less exposed to hallucination.

## Slide 20 Code-as-Monitor Method 1: the overall flow

- Constraint Generator: GPT-4o writes the subgoal plus during/upon constraints
- Constraint Painter: relevant parts → points, lines, surfaces on multi-view images
- Constraint Monitor: GPT-4o writes check code; runs each frame on tracked points

Notes: Let me follow the overall flow on the figure's example of carrying a pan with bread to the stove. There are three modules. The Constraint Generator, GPT-4o, takes the task instruction, the previous subgoal, the previous failure reason and multi-view images, and writes the next subgoal, "move the pan above the stove", with constraints of two kinds: during execution, keep grasping the handle, the bread stays in the pan, the pan stays level; upon completion, the pan is directly above the stove. The Constraint Painter abstracts the parts relevant to each constraint into points, lines and surfaces and draws them, numbered, on the multi-view images: three red points for the pan surface, a green point for the bread, a blue point for the stove. The Constraint Monitor gives these annotated images and the constraints to GPT-4o, which writes the checking code. During execution CoTracker tracks the points and the code runs every frame on their coordinates. When the pan tilts and the code returns False, the policy stops, the reason goes back to the Generator, and the task is re-planned.

## Slide 21 Code-as-Monitor Method 2: building the constraint elements

- ConSeg (LoRA-tuned LISA) outputs object and part masks from the constraint text
- Masks become 3D points via depth; key points picked per element type, then linked
- Training data: 10,181 BridgeData V2 trajectories auto-annotated with GPT-4o

Notes: How the points, lines and surfaces are made. The input is a constraint sentence such as "the pan should remain horizontal; segment the relevant part" together with the image. A segmentation model called ConSeg returns the object mask, the part mask and the element type, here a surface. ConSeg is built on LISA, keeping the LLaVA and SAM encoder and decoder frozen and training LoRA parameters. The masks are projected to a 3D point cloud with depth, voxelized according to the element type, and representative points are chosen: three for a surface, two for a line, one for a point. The points are connected into an element and drawn, numbered, on the multi-view images. The training data is 10,181 BridgeData V2 trajectories for which GPT-4o wrote subgoals, constraints and object-part associations, with masks from Grounded SAM and Semantic SAM, checked by hand. Because appearance and texture are discarded and only geometry remains, tracking is easy and the elements generalize to unseen objects.

## Slide 22 Code-as-Monitor Method 3: generating and running monitor code

- Input: the elements' 3D coordinates and history. Output: (failed?, reason)
- Example: pan normal from 3 points; tilt over 15° → "the pan is not level"
- All branches tested at generation; errors → regenerate. One VLM call per subgoal

Notes: Inside the monitor code. GPT-4o writes a function that takes the 3D coordinates of the elements and their history. In the example it forms two vectors from the pan's three points, computes the normal, and if the angle to vertical exceeds the 15-degree threshold it returns False with the reason "the pan surface is not horizontal, the angle is N degrees". Because the history is also an input, precise conditions such as "move 2 cm" or "rotate 180 degrees" can be monitored. Thresholds come from a knowledge base for common tasks and from the VLM for unseen ones. Right after generation the code is run on the current state so that every if-else branch is exercised, and it is regenerated on any error. As the flow on the right shows, the VLM is called only once at the start of a subgoal; afterwards CoTracker tracks the points, the code is evaluated every frame, and when it returns False the policy stops and the task is re-planned.

## Slide 23 Code-as-Monitor Result 1: sim (CLIPort / OmniGibson / RLBench)

- CLIPort: 76.7% → 88.3% under disturbances; Sweep Half 16.7 → 75.0%
- OmniGibson: only CaM catches surface tilt; time −35%, tokens −52%
- RLBench: 91.3% → 97.1% on unseen articulated and tool-use tasks

Notes: Simulation results. Three simulators with different robots, end-effectors and policies, with disturbances injected to induce failures. In CLIPort block stacking under strong disturbances, a 0.3 drop probability and 3 cm placement noise, the baseline DoReMi reaches 76.7% while this method reaches 88.3%. DoReMi, which repeatedly asks the VLM, has coarse 3D understanding from single images and misjudges more. On sweeping half the blocks, counting element points raises success from 16.7% to 75%. In OmniGibson, with point-, line- and surface-level disturbances, only this method could detect the surface-level disturbance in pouring tea. Since code is generated once per subgoal, execution time drops by 34.8% and token usage by 52.2%. On RLBench, even on articulated-object and tool-use tasks absent from the training data, success rises from ARP's 91.3% to 97.1%, showing generalization.

## Slide 24 Code-as-Monitor Result 1: sim demo (video)

- Left: stacking under placement noise. CaM restacks before collapse
- Middle: DoReMi queries the VLM repeatedly and misjudges more often
- Right: sweep half the blocks (count points), pour tea (surface tilt)

Notes: Let's watch the monitoring in simulation. On the left is block stacking in CLIPort with placement noise. Because the block positions are tracked as points, the method detects when the stack is about to collapse and restacks before moving on. In the middle is the baseline DoReMi, which keeps querying the VLM with images; 3D understanding from a single image is coarse, so misjudgments increase. On the right is the task of sweeping exactly half of the blocks, where counting the points inside the region lets the policy stop at the right moment. In OmniGibson's pour-tea task, the tilt of the teapot surface is monitored to catch a spill before it happens.

## Slide 25 Code-as-Monitor Result 2: real robot (UR5 + Leap Hand) and ablation

- CaM on an open-loop grasp policy: over 90% under disturbances
- Long-horizon reasoning task: DoReMi 0% vs. CaM 90%
- Ablation: multi-view, segmentation, point connection (65% → 40-55%)

Notes: The real robot is a UR5 with a Leap Hand, and the policy is the open-loop grasp model DexGraspNet 2.0; the segmentation model is the base model without any simulator fine-tuning. Under disturbances, moving the object during grasping or removing it during transport, and across four object types including deformable and transparent ones, the method exceeds 90%, about 20 points above DoReMi, with shorter execution time. On the cluttered long-horizon task "grasp the animals from nearest to the fruits", moving the horse or the pear changes the order; the method monitors the distances and switches targets, reaching 90% where DoReMi gets 0%. The open-loop policy effectively becomes closed-loop. In the ablation, removing multi-view drops success from 65% to 40%, replacing constraint-aware segmentation with DINOv2 semantic points gives 42.5%, and removing point connection gives 55%, so each component matters; on the real robot, not forming elements drops success from 60% to 20%. Stated limitations are VLM hallucination, difficulty with force-related failures that involve no displacement, and no handling of other modalities such as sound or liquids.

## Slide 26 Code-as-Monitor Result 2: real-robot demo (video)

- Left: "clear everything except the animals". Moved objects are retargeted
- Right: "grasp animals nearest to the fruits first". Moving them reorders
- The grasp model stays open-loop; the monitor code triggers re-planning

Notes: Real-robot demos. The robot is a UR5 with a Leap Hand, and the grasp generation model DexGraspNet 2.0 is used as an open-loop policy. On the left, the task is to clear everything except the animals; when a person moves an object or takes it out of the hand, the tracked points update the target and execution continues. On the right, the task is to grasp the animals in order of distance to the fruits; when a person moves the horse or the pear, the distances are recomputed and the grasp order changes. In both cases the monitor code detects the failure or the change and triggers re-planning, so the open-loop policy behaves as a closed-loop system.

## Slide 27 Papers (highlight paper 3)

Notes: The third paper is VLS. In one sentence, it is a training-free framework that steers the sampling process of a frozen diffusion or flow-matching policy at inference time with differentiable rewards written by a VLM. Three things to remember: adding reward gradients to the generation process, having the VLM write the reward function as a program, and combining gradient-based refinement with reward-based candidate selection.

## Slide 28 VLS Overview 1: inference-time steering

- Bends the action while a frozen diffusion / flow policy is generating it
- The VLM writes a reward, as code, that scores how good an action is now
- No weights change, nothing is trained; the VLM writes rewards, not actions

Notes: VLS is the inference-time steering area. The input is the camera images and the instruction, plus a frozen diffusion or flow-matching policy. The VLM writes, as code, a reward function that scores how good an action is in the current situation. The policy builds its action gradually from noise, and during that process the reward gradient is added so the action bends toward higher reward. The policy weights are never changed and nothing is trained. Where Code-as-Monitor watches from outside the execution, VLS reaches inside the generation.

## Slide 29 VLS Overview 2: what VLS is

- Pretrained policies break under small shifts: layout, obstacles, wording
- Not a missing skill; actions are bound to the training layout and wording
- No retraining: VLS steers generation with a VLM-written reward's gradient

Notes: Here is the overview. Policies trained with diffusion or flow matching perform well under the training conditions but fail when an object is moved, an obstacle appears or the instruction changes slightly. The authors argue that this is not a lack of skill; action generation is tightly coupled to the training-time spatial configurations and task specifications. As the figure shows, the pretrained policy behaves in a fixed way in-distribution and cannot handle new objects, scenes or instructions. VLS does not retrain or fine-tune; it corrects the generation process with the gradient of a VLM-written reward function so that the actions fit the new conditions.

## Slide 30 VLS Overview 3: vs. prior steering methods

- Prior work picks among candidates; if none is good, nothing can be picked
- Steering with a learned value/dynamics model inherits that model's errors
- VLS moves candidates by the reward gradient, then selects; no training

Notes: How it differs from prior steering methods, as a diagram. The horizontal axis is the action, say the lateral hand position; the blue hill is the pretrained policy's distribution, the orange curve is the VLM-written reward, and grey is the wall. In (a), without steering, candidates gather at the policy's hill, the actions that were common in training, and hit the wall. Most prior methods pick the best of these candidates with a VLM or a human, but if no candidate is good there is nothing to pick. Methods that steer with a learned value function or dynamics model exist too, but the policy is pulled by that model's errors and preferences. In (b), VLS adds the reward gradient to the candidates, so the candidates themselves move toward higher reward. In (c) it also duplicates high-reward candidates and prunes low ones. The reward is written on the spot by the VLM, so no extra training is needed.

## Slide 31 VLS Method 1: the overall flow

- ① Keypoints: the VLM names objects; SAM, DINOv2, depth → numbered 3D points
- ② Rewards: the VLM writes a differentiable PyTorch reward for each task stage
- ③ Guided generation: the reward gradient is added at every denoising step

Notes: Let me follow the overall flow on the figure. The input is an RGB-D image and the instruction, here "pick the cheese in the basket". First, keypoint extraction: the VLM names the task-relevant objects, SAM gives masks, DINOv2 features plus depth give a 3D point cloud that is clustered into a set of numbered 3D keypoints, numbered 0 to 4 in the figure. Second, reward generation: the VLM splits the task into stages and, for each stage, writes a reward function over the keypoints and the action sequence as PyTorch code. The allowed operations are restricted to differentiable ones such as distances and dot products, so the gradient with respect to the actions exists. The VLM itself stays outside the computation graph; gradients flow through the generated function. Third, guided generation: at every step where the frozen base policy, π0.5 or Diffusion Policy in the experiments, builds its action from noise, the reward gradient is added. The VLM also decides when to switch stages.

## Slide 32 VLS Method 2: how the reward steers generation

- Classifier guidance: add λ × the reward gradient ∇R to the velocity field
- Batch of candidates: repulsion (RBF), gradient refinement, resampling (FK)
- λ adapts to reward progress; stages switch with a hysteresis threshold

Notes: The steering mechanism. The equation has the same form as classifier guidance in image generation: for flow matching the gradient of the reward R with respect to the action, scaled by λ, is added to the velocity field; for diffusion, to the noise prediction. The implementation keeps a batch of B action candidates. In the early steps an RBF repulsion between candidates spreads them out, preventing premature collapse to a narrow mode of the base policy. Then the reward gradient is added at every step to refine them; diffusion policies use four updates per step. In addition, following Feynman-Kac steering, the exponential of the reward becomes a weight, the candidates are resampled, high-reward ones are duplicated and low ones pruned. For closed-loop control, λ is set from the reward relative to the first chunk of the stage: strong when the deviation is large, weaker near completion so the base policy dominates. Stage switching uses a hysteresis with two thresholds to avoid oscillation near the boundary, and on a switch the VLM looks at the outcome and selects the next reward function.

## Slide 33 VLS Method 3: example "put the cheese in the basket"

- ① Cheese, basket and nearby objects → numbered 3D points (basket = point 2)
- ② VLM-written reward: −(distance from trajectory to point 2)²; closer is better
- ③ Adding the gradient at each denoising step pulls the trajectory to the basket

Notes: The same flow on the concrete example of putting the cheese in the basket. First, the cheese, the basket and the surrounding objects become numbered 3D points; the basket is point 2. Second, the reward for stage 1 written by the VLM is the code in the middle: it takes the coordinates of point 2, computes the distance to every point of the action trajectory, and returns the negative sum of squared distances. A trajectory closer to the basket scores higher, and since it uses only torch operations the gradient exists. Third, the figure on the right shows how the candidate trajectories change step by step: they start scattered as the base policy proposes them, spread by repulsion, are corrected by the gradient and resampled, and end up as a trajectory that reaches the basket.

## Slide 34 VLS Result 1: simulation (LIBERO-PRO / CALVIN)

- LIBERO-PRO: frozen π0.5 + VLS, 23.7% → 36.8% (+13 pt)
- CALVIN: movable objects 94% (7.4×), articulated parts 87% (9.6×)
- Ablation: no gradient → 17%; resampling / repulsion add efficiency

Notes: Simulation results. LIBERO-PRO adds object-position and task-specification perturbations to LIBERO; OpenVLA and π0 are near 0%, and even the LeRobot π0.5 gets 23.7%. Adding VLS to that frozen π0.5 raises it to 36.8%, a 13-point gain. The authors' interpretation is that post-training on robot data entangles the VLM backbone's spatial reasoning with the training context. On CALVIN with a Diffusion Policy base, VLS reaches 94% on movable objects, 7.4 times the base, and 87% on articulated parts, 9.6 times, outperforming DynaGuide and ITPS by 15 to 25 points. In the ablation, removing gradient guidance collapses success to 17%, so dense, trajectory-differentiable guidance is the main driver; reward-based resampling and repulsion matter less for success but improve episode length and stability. The bottom right shows scaling with the number of samples: more samples help, but inference time exceeds 1.2 seconds, a compute-performance trade-off.

## Slide 35 VLS Result 1: sim demo (video)

- Left: LIBERO-PRO, objects moved. Frozen π0.5 fails; with VLS it succeeds
- Right: "avoid the wall", an unseen instruction met via the reward gradient
- Numbered points: VLM-selected keypoints; rewards are distances to them

Notes: Here are videos of the same policy with and without steering. On the left is LIBERO-PRO with the object positions changed; the frozen π0.5 fails as is, but succeeds once VLS is added. The numbered points on screen are the keypoints chosen by the VLM, and the reward function is written in terms of distances to them. On the right the instruction is "put the red cube on the green patch while avoiding the wall", which does not appear in training. The base policy hits the wall, while the reward gradient corrects the trajectory so that it goes around the wall.

## Slide 36 VLS Result 2: real robot (Franka) and limitations

- In-distribution: pick-and-place tasks go from 50% to 69% (+19 pt)
- Under shifts: unseen mug 0% → 40%, average 42% → 69%
- Limitation: latency, about 1 second per action chunk

Notes: The real robot is a Franka Emika with a frozen π0.5. The in-distribution tasks are placing an orange on the instructed plate, and, with a banana added, selecting both the object and the plate; average success rises from 50% to 69%, a 19-point gain. The out-of-distribution variants replace the plate with an unseen yellow one, swap the plate positions, and replace the banana with an unseen mug. The baseline degrades sharply, to 0% on the mug, while VLS gets 40% there and 69% on average versus 42%. The main limitation is inference overhead from batch sampling, repeated refinement and resampling, about one second per chunk in Figure 4; progress-aware reward generation and efficiency are listed as future work.

## Slide 37 VLS Result 2: real-robot demo (video)

- Left: in-distribution, "put the banana on the green plate"
- Middle: an unseen object, a mug instead of the banana (0% → 40%)
- Right: plates swapped, same instruction; the policy follows

Notes: Real-robot demos on a Franka with a frozen π0.5 base. On the left is an in-distribution task: put the banana on the green plate. In the middle the banana is replaced by a mug the policy has never seen; the frozen policy gets 0%, and with VLS it succeeds in 40% of trials. On the right the plates are swapped while the instruction stays the same, and the policy follows the new positions. The overlay in the top left shows the guidance strength and the reward, and you can see the guidance weaken as the stage nears completion.

## Slide 38 Insights Summary: where the VLM output enters the policy

- Where the VLM output enters: training data, a stop condition, the generation objective
- Deeper intervention: more direct effect, but more inference cost and VLM-error impact
- CaM and VLS both lift objects to 3D points and let the VLM write code on them: shareable
- SimFoundry's variants are a testbed for such inference-time mechanisms under shift

Notes: To summarize. The three papers differ in where the VLM output enters the policy. SimFoundry feeds the training data, Code-as-Monitor supplies the condition that stops execution, and VLS supplies the objective of action generation. As the table shows, the deeper the entry point, the more direct the effect: VLS changes the success rate of a frozen policy on the spot, but the inference cost and the impact of VLM errors grow too. SimFoundry uses no VLM at run time, so there is no impact, and Code-as-Monitor keeps it to one call per subgoal. A second observation is that Code-as-Monitor and VLS both turn objects into 3D points and have the VLM write code over them, as a checking condition in one case and as a reward in the other. The same points and the same code could serve both monitoring and steering, which leads to my own work on the last slide. And SimFoundry's variants are a place to test such inference-time mechanisms at scale under distribution shift. As ASPIRE showed, methods that have the model write code improve as base models improve, so I expect all three to keep gaining.

## Slide 39 Insights My own work: steering + monitoring

- Lately I have been combining VLS-style steering with CaM-style monitoring
- VLM-written code both steers generation and monitors execution
- Videos from LIBERO; the right panel is the VLM judgment and monitor log

Notes: Finally, a brief look at my own work. I have recently been testing a method that combines VLS-style reward steering with Code-as-Monitor-style monitor code, which is exactly the idea from the summary: VLM-written code used both to steer generation and to monitor execution. The videos show examples on LIBERO-Goal and LIBERO-Object, with the VLM's judgment and the monitor log on the right. It is still work in progress, but the early results are interesting, so please talk to me afterwards if you are curious. Thank you for your attention. I am happy to take questions.
