# Three Ways to Use VLMs in Robot Learning

Real2Sim ・ Failure Detection ・ Inference-Time Steering

Notes: Good afternoon, everyone. Today I will present three papers from the perspective of "how can we bring the capabilities of today's VLMs into robot learning?" With foundation models such as GPT-6 Astra, manipulation benchmarks are starting to be solved. At the same time, using a VLM directly as the policy is still weak at precise and contact-rich manipulation. So I picked one paper from each of three areas where a VLM is combined with a pretrained policy: Real2Sim, failure detection, and inference-time steering.

## Slide 2 Background: VLMs are starting to solve benchmarks

- GPT-6 Astra (OpenAI, Sep. 2026): a step change in spatial reasoning, drives robots via code
- ASPIRE (NVIDIA GEAR): an agent discovers skills as code; v1.0 hits 99% on 80 LIBERO-Pro tasks
- Stronger base models give higher success (GPT-6 Luna 15%, Claude Opus 5.5 99%)

Notes: First, some background. GPT-6 Astra, released by OpenAI in September 2026, has been described as a step change in spatial reasoning. Using it to write code that drives a robot directly has become common, and the left figure shows a case where it planned and solved a bimanual spatial-constraint puzzle. On the right is ASPIRE from NVIDIA GEAR. A coding agent writes robot skills as code, inspects failures, revises the code, and grows a library of reusable skills. Version 1.0, released in October, reaches 99% success on the 80 LIBERO-Pro tasks. The right figure shows success on 10 tasks: the stronger the base model, the higher the success, from 15% with GPT-6 Luna to 99% with Claude Opus 5.5. Simulation benchmarks are starting to be solved by VLM-centric methods.

## Slide 3 Background: how to use VLMs in robot learning

- As a policy, VLMs are still weak at precise and bimanual manipulation (RoboDojo 22.5%)
- Instead: keep a pretrained policy and use the VLM around it
- Today: one paper each from Real2Sim, failure detection, and steering

Notes: So how should we use these capabilities in robot learning? There are evaluations that use the VLM directly as a policy, but they report 22.5% on RoboDojo and 11.1% on LIBERO-GeoMotion with geometric constraints, and precise, contact-rich and bimanual manipulation remains weak. There is a gap between semantic reasoning and physical execution. This motivates combining the VLM with a pretrained policy such as a VLA or a diffusion policy, and using the VLM's spatial understanding, reasoning and code generation around the policy. Today I split this into three areas. The first is Real2Sim, which uses the VLM's spatial understanding to copy a real scene into simulation for evaluation and training data. The second is failure detection, where VLM-written monitor code detects and prevents failures during execution. The third is inference-time steering, where VLM-written reward functions steer the action generation of a pretrained policy. I will present one paper for each, in this order.

## Slide 4 Papers (all three)

Notes: These are the three papers. The first is SimFoundry from NVIDIA, Stanford and Georgia Tech, which turns a single real-world video into a simulation environment for policy evaluation and training. The second is Code-as-Monitor from Beihang University, Peking University, BAAI and Galbot, published at CVPR 2025, which detects and prevents robot failures in real time with VLM-generated code. The third is VLS from the University of Washington and AI2, which steers a frozen generative policy at inference time with VLM-written rewards. I will go through them in the order Real2Sim, failure detection, steering.

## Slide 5 Papers (highlight paper 1)

Notes: Let's start with SimFoundry. In one sentence, it is a modular system that automatically builds a simulation environment usable for both evaluation and training from a single real-world video. Three things to remember: it reconstructs a real scene in simulation, it generates many affordance-preserving variants of that reconstruction, and the result serves both sim evaluation of real-world policies and sim-to-real transfer of policies trained in simulation.

## Slide 6 SimFoundry Background: real-world evaluation does not scale

- Sim is cheap to scale, and sim evaluation correlates with real performance
- Building sim scenes that match the real world by hand is the bottleneck
- Existing systems lack evaluation, training, or diversification

Notes: Background. Training a robot foundation model needs large-scale teleoperation data, and evaluating one rigorously needs thousands of real-world trials. Simulation has become the alternative: demonstrations can be generated automatically, and simulation evaluations have been shown to correlate with real-world performance. The bottleneck is building simulation scenes that match the real world by hand. The table compares existing real-to-sim systems. Some support sim-to-real training, some support real-to-sim evaluation, and some build scenes automatically, but none provides all of them while also diversifying objects, layouts and tasks. SimFoundry aims to cover all of this in one pipeline.

## Slide 7 SimFoundry Overview: from a reconstructed scene to variants

- Input: one video. Output: a scene in a physics sim (digital twin)
- From the twin, generate unlimited variants (digital cousins)
- Uses: sim evaluation of real policies, and sim-to-real training

Notes: Here is the overview. The input is a single video of a real scene and the output is an interactive scene in a physics simulator, which the paper calls a digital twin. From the twin, SimFoundry generates an unlimited number of variants that preserve the task-relevant affordances, called digital cousins, along three axes: objects, layouts and tasks. The resulting environments serve both purposes shown by the arrows: evaluating real-world policies in simulation, and training policies in simulation that transfer to the real robot.

## Slide 8 SimFoundry Reconstruction examples (video)

- Left: a dining room. Right: a toy table. Both from a single video
- Each object mesh is generated from one image crop, fully automatically
- About 5 minutes per object, no manual annotation

Notes: Let's look at reconstruction examples. On the left is a dining room and on the right a table with toys, both reconstructed from a single real video. The first half shows the real scene and the second half the reconstruction in simulation. Each object's 3D mesh is generated automatically from a single image crop, and you can see that the shapes and the layout match the real scene. No manual annotation is needed and it takes about five minutes per object. These reconstructed scenes are what we later use for evaluation and for generating training data.

## Slide 9 SimFoundry Method: building the twin from a video

- Extraction: depth, VLM object detection, SAM 3 one object at a time
- Generation: 2D-to-3D mesh, pose alignment, joints, physical properties
- Every module is swappable; the background can use 3DGS

Notes: The reconstruction pipeline. In the extraction stage, a representative frame is chosen, a depth model produces a point cloud, a VLM detects the objects, and SAM 3 segments them one at a time, inpainting each away until no foreground remains. In the generation stage, each object crop is upsampled and turned into a 3D mesh, aligned to the scene with FoundationPose, and articulated objects such as drawers get joints from a separate module. CoACD produces collision geometry and a VLM assigns physical parameters such as mass and friction. Finally, PyBullet resolves penetrations to get a stable configuration, and the scene is exported to IsaacLab and similar simulators. Every module is replaceable, so better foundation models can be dropped in as they appear. The background can also be reconstructed with 3D Gaussian Splatting.

## Slide 10 SimFoundry Method: three kinds of variants

- Object cousins: perturb the image, regenerate the mesh (same function)
- Scene cousins: a VLM edits spatial predicates (OnTop, ...)
- Task cousins: a VLM proposes tasks; demos are generated automatically

Notes: Now the variants. Object cousins perturb the object image in image space and regenerate the 3D mesh, producing objects with different shapes and textures but the same function. Scene cousins let a VLM edit spatial predicates such as OnTop and RightOf, giving meaningful alternative layouts rather than position noise; distractor objects can be added as well. Task cousins ask a VLM to propose other feasible tasks from the objects and affordances in the scene, convert them into BDDL goal specifications, and generate demonstrations with MimicGen-style methods. In this way one real scene yields a large amount of training data that is diverse in objects, layouts and tasks.

## Slide 11 SimFoundry Result 1: sim evaluation predicts real performance

- 7 tasks × 5 policies, evaluated in sim and on the real robots
- Mean Pearson r = 0.911, MMRV = 0.018 (almost no rank flips)
- r is 0.59 above PolaRiS, with no fine-tuning of the policies

Notes: The first result is real-to-sim evaluation. Seven tasks on two real setups, a single-arm Franka in the DROID setup and a bimanual YAM, with five policies: π0, π0.5, GR00T N1.6, N1.7 and DreamZero, evaluated both in simulation and on the real robots. In the scatter plot, SimFoundry's blue markers lie close to the diagonal, with a mean Pearson correlation of 0.911 and a mean maximum rank violation of 0.018. The orange markers of the baseline PolaRiS are scattered, and the correlation gap is more than 0.59. Moreover, PolaRiS lightly fine-tunes the policies on its simulation data, while SimFoundry evaluates the policies zero-shot. Evaluating at the sub-task level raises the correlation from 0.90 to 0.95 and tells you which stage of a task is weak.

## Slide 12 SimFoundry Result 2: sim-to-real transfer and variants

- Sim-only training reaches 99-100% zero-shot on the real robots
- Object / scene / task cousins raise real success by +17 / +21 / +40%
- π0.5 fine-tuned on 13 sim tasks: 29% on held-out tasks

Notes: The second result is sim-to-real training. Policies trained only on SimFoundry data transfer zero-shot to the real robots, reaching 99% on Pot on Stove with YAM and 100% on Stack Dishware with DROID. On YAM this is a flow-matching policy trained from scratch; on DROID the π0.5 DROID checkpoint is fine-tuned on sim demonstrations. The figure shows the effect of the variants. In panel A, object cousins improve robustness to unseen objects, a 50-point gain on unseen Pot on Stove objects. In panel B, scene cousins improve layout generalization: 16% on cousin layouts where the twin-only policy gets 0%, and up to 28 points even on the twin layout. In panel C, with the total number of demos fixed, replacing some target-task demos with related-task demos actually raises success on the target task, by 60 points on Throw Away Trash. Fine-tuning π0.5 on multi-task data from 13 tasks gives 29% on held-out tasks and up to 18% improvement in the real world.

## Slide 13 SimFoundry Real-robot demo (video): sim-trained policies

- Left: bimanual policy trained in sim (YAM). Middle: same policy, real robot
- Right: objects never seen in training, thanks to object cousins
- Pot on Stove reaches 99% on the real robot

Notes: Here are policies trained in simulation running on the real robot. On the left is the bimanual YAM policy trained inside simulation, and in the middle the same policy executed on the real robot without any fine-tuning. On the right it runs on objects that were not in the training set, which is where object cousins in the training data pay off. On the Pot on Stove task the real-world success rate was 99%.

## Slide 14 SimFoundry Result 3: reconstruction quality and cost

- Zero-shot F1 of 0.81-0.92 (SAM3D: 0.66-0.71)
- About 5 min per object; 3 min of tuning raises F1 to 0.93-0.99
- Limits: tabletop scenes; inherits each foundation model's failures

Notes: Finally, an analysis of the system itself. On a geometric evaluation over 12 scenes, the fully automatic pipeline reaches F1 scores of 0.81 to 0.92, above SAM3D's 0.66 to 0.71. Reconstruction takes about five minutes per object, and three minutes of manual tuning per object raises F1 to 0.93 to 0.99, so fidelity can be traded for effort on demand. In the figure the top row is the real scene, the middle the digital twin and the bottom a digital cousin; shapes and layouts change while the task semantics are preserved. The stated limitations are the tabletop assumption and inheriting the failure modes of each underlying foundation model.

## Slide 15 Papers (highlight paper 2)

Notes: The second paper is Code-as-Monitor, from CVPR 2025. In one sentence, it unifies reactive failure detection and proactive failure prevention as checking whether constraints are satisfied, and monitors them in real time with VLM-generated code. Three things to remember: unifying reactive and proactive detection, constraint elements that abstract objects into points, lines and surfaces, and calling the VLM only once per subgoal.

## Slide 16 Code-as-Monitor Background: reactive and proactive detection

- Reactive: detect a failure after it happens (the lobster fell out)
- Proactive: prevent a foreseeable failure (fix the tilted pan)
- VQA-style detection is slow and weak in 3D; proactive is unexplored

Notes: Background. There are two modes of failure detection. Reactive detection identifies a failure after it occurs: in panel (a) the lobster jumps out of the pan and the robot detects that it fell. Proactive detection prevents foreseeable failures: in panel (b) the robot detects that the pan is tilting and corrects it before anything falls, which needs real-time, precise monitoring. Existing work mostly asks an LLM or VLM about failures as a visual question-answering problem, which is slow and computationally expensive, and spatio-temporal 3D understanding from a single image is coarse. Proactive detection is largely unexplored and limited to predefined failures. Code-as-Monitor aims to do both, for open-set failures, in real time. As panel (c) shows, combining it with an open-loop policy yields a closed-loop system.

## Slide 17 Code-as-Monitor Method: overview

- Reactive and proactive detection unified as constraint checking
- The VLM writes constraints, paints elements, then writes monitor code
- VLM called once per subgoal; the code monitors every frame after that

Notes: Here is the overall framework. The key formulation is to unify reactive and proactive detection as checking whether constraints are satisfied. First, a VLM, GPT-4o, takes the task instruction, the previous subgoal, failure feedback and multi-view observations, and generates the next subgoal and two kinds of textual constraints: constraints to maintain during execution, such as "the bread must remain in the pan" and "the pan should remain horizontal", and constraints to satisfy upon completion, such as "the pan is directly above the stove". The former correspond to proactive detection and the latter to reactive detection. Next, each constraint is mapped onto the images as constraint elements, and those annotated images are used as visual prompts to have the VLM write monitor code. The VLM is called only once at the start of each subgoal; during execution the elements are tracked with CoTracker and the code is simply evaluated, so it runs in real time. If a constraint is violated, the policy stops immediately and the reason is fed back for re-planning.

## Slide 18 Code-as-Monitor Method: constraint elements

- Objects and parts become points, lines, surfaces: easy to track
- ConSeg (LISA + LoRA) segments the relevant part from the constraint text
- Training data: BridgeData V2 auto-annotated by GPT-4o (10,181 traj.)

Notes: The other core idea is the constraint element. Objects or parts relevant to a constraint are abstracted into compact geometric elements such as points, lines and surfaces. For "the pan should remain horizontal", the pan surface becomes three points and the code just computes the angle between its normal and the z axis. Irrelevant details such as texture are discarded, which makes tracking easy and generalizes to unseen objects and scenes. The pipeline segments instance and part masks from the constraint text, projects them to a 3D point cloud using depth, voxelizes and clusters them according to the element type, and connects the points into elements, which are then annotated onto the multi-view images with numbers. The segmentation model is called ConSeg. It is built on LISA, keeping the LLaVA and SAM encoder and decoder frozen and training LoRA parameters, and outputs the mask and element type directly from the constraint text. The training data comes from BridgeData V2: GPT-4o generates subgoals, constraints and object-part associations, Grounded SAM and Semantic SAM produce the masks, and the result is manually checked, giving 10,181 trajectories and 219,356 images.

## Slide 19 Code-as-Monitor Method: generating and running monitor code

- Input: 3D element positions and history. Output: (bool, reason)
- Thresholds from a knowledge base or the VLM; every branch is tested
- On a violation: stop the policy, return the reason, re-plan

Notes: Here is the monitor code in practice. GPT-4o receives the annotated multi-view images, the next subgoal and the constraints, and writes a function that takes the 3D positions of the elements. The code computes angles and distances with NumPy and returns a boolean indicating failure plus a string explaining why. In the example, if the angle between the pan surface normal and the z axis exceeds 15 degrees, it returns "the pan surface is not horizontal". Because the history of positions is also an input, precise conditions such as "move 2 cm" or "rotate 180 degrees" can be monitored, which VQA-style methods cannot do. Thresholds come from a knowledge base for common tasks and from the VLM's knowledge for unseen ones. Right after generation, the code is run on the current state so that every if-else branch is exercised, and it is regenerated on any error. During execution the elements are tracked and the code evaluated; when it returns False the policy stops immediately and the reason goes back to the VLM for re-planning.

## Slide 20 Code-as-Monitor Sim demo (video): monitoring under disturbances

- Left: stacking under placement noise. CaM restacks before collapse
- Middle: DoReMi queries the VLM repeatedly and misjudges more often
- Right: sweep half the blocks (count points), pour tea (surface tilt)

Notes: Let's watch the monitoring in simulation. On the left is block stacking in CLIPort with placement noise. Because the block positions are tracked as points, the method detects when the stack is about to collapse and restacks before moving on. In the middle is the baseline DoReMi, which keeps querying the VLM with images; 3D understanding from a single image is coarse, so misjudgments increase. On the right is the task of sweeping exactly half of the blocks, where counting the points inside the region lets the policy stop at the right moment. In OmniGibson's pour-tea task, the tilt of the teapot surface is monitored to catch a spill before it happens.

## Slide 21 Code-as-Monitor Result 1: simulation

- CLIPort: 76.7% → 88.3% under disturbances; Sweep Half 16.7 → 75.0%
- OmniGibson: only CaM catches surface tilt; time −35%, tokens −52%
- RLBench: 91.3% → 97.1% on unseen articulated and tool-use tasks

Notes: Simulation results. Three simulators with different robots, end-effectors and policies, with disturbances injected to induce failures. In CLIPort block stacking under strong disturbances, a 0.3 drop probability and 3 cm placement noise, the baseline DoReMi reaches 76.7% while this method reaches 88.3%. DoReMi, which repeatedly asks the VLM, has coarse 3D understanding from single images and misjudges more. On sweeping half the blocks, counting element points raises success from 16.7% to 75%. In OmniGibson, with point-, line- and surface-level disturbances, only this method could detect the surface-level disturbance in pouring tea. Since code is generated once per subgoal, execution time drops by 34.8% and token usage by 52.2%. On RLBench, even on articulated-object and tool-use tasks absent from the training data, success rises from ARP's 91.3% to 97.1%, showing generalization.

## Slide 22 Code-as-Monitor Real-robot demo (video): closing the loop

- Left: "clear everything except the animals". Moved objects are retargeted
- Right: "grasp animals nearest to the fruits first". Moving them reorders
- The grasp model stays open-loop; the monitor code triggers re-planning

Notes: Real-robot demos. The robot is a UR5 with a Leap Hand, and the grasp generation model DexGraspNet 2.0 is used as an open-loop policy. On the left, the task is to clear everything except the animals; when a person moves an object or takes it out of the hand, the tracked points update the target and execution continues. On the right, the task is to grasp the animals in order of distance to the fruits; when a person moves the horse or the pear, the distances are recomputed and the grasp order changes. In both cases the monitor code detects the failure or the change and triggers re-planning, so the open-loop policy behaves as a closed-loop system.

## Slide 23 Code-as-Monitor Result 2: real robot and ablation

- CaM on an open-loop grasp policy: over 90% under disturbances
- Long-horizon reasoning task: DoReMi 0% vs. CaM 90%
- Ablation: multi-view, segmentation, point connection (65% → 40-55%)

Notes: The real robot is a UR5 with a Leap Hand, and the policy is the open-loop grasp model DexGraspNet 2.0; the segmentation model is the base model without any simulator fine-tuning. Under disturbances, moving the object during grasping or removing it during transport, and across four object types including deformable and transparent ones, the method exceeds 90%, about 20 points above DoReMi, with shorter execution time. On the cluttered long-horizon task "grasp the animals from nearest to the fruits", moving the horse or the pear changes the order; the method monitors the distances and switches targets, reaching 90% where DoReMi gets 0%. The open-loop policy effectively becomes closed-loop. In the ablation, removing multi-view drops success from 65% to 40%, replacing constraint-aware segmentation with DINOv2 semantic points gives 42.5%, and removing point connection gives 55%, so each component matters; on the real robot, not forming elements drops success from 60% to 20%. Stated limitations are VLM hallucination, difficulty with force-related failures that involve no displacement, and no handling of other modalities such as sound or liquids.

## Slide 24 Papers (highlight paper 3)

Notes: The third paper is VLS. In one sentence, it is a training-free framework that steers the sampling process of a frozen diffusion or flow-matching policy at inference time with differentiable rewards written by a VLM. Three things to remember: adding reward gradients to the generation process, having the VLM write the reward function as a program, and combining gradient-based refinement with reward-based candidate selection.

## Slide 25 VLS Background: why generative policies fail

- Diffusion and flow-matching policies perform well in-distribution
- The skills exist but are tied to training-time layouts and instructions
- Retraining is costly. The real problem is inference-time control

Notes: Background. Imitation-learned diffusion and flow-matching policies perform well in the conditions they were trained in, but they fail under mild changes: the same task near an obstacle, on a shifted support surface, or with light clutter. The authors argue that this is not a lack of motor skill; action generation is tightly coupled to the training-time spatial configurations and task specifications. As the figure shows, a pretrained policy behaves in a fixed way in-distribution, but cannot handle new objects, scenes or instructions. Retraining or fine-tuning is costly and conceptually misaligned, since the behaviors already exist. VLS therefore treats this as an inference-time control problem.

## Slide 26 VLS Problem setting: reward gradients in generation

- Inject a gradient g into the frozen policy's denoising (classifier guidance)
- Hard part: the new condition has spatial and semantic structure
- Have the VLM write a differentiable surrogate score R as a program

Notes: The problem setting. The denoising process of the frozen base policy is steered by adding the gradient g of the log-likelihood of the new condition, in the form of classifier guidance known from image generation. For diffusion, the gradient scaled by a guidance strength lambda is added to the noise prediction; for flow matching, to the velocity field. The hard part is modeling g. A real-world condition is not a class label; it has spatial and semantic constraint structure, and the guidance must give dense, informative gradients with respect to the action trajectory. Existing steering methods use a learned value function, a learned dynamics model, or let humans or VLMs select among candidates, with respective issues: bias toward the critic's preferences, model error and cost, and discrete sparse signals. VLS instead has the VLM write the differentiable surrogate score R as a program, obtaining dense gradients without training.

## Slide 27 VLS Method: pipeline

- ① Keypoints: SAM, DINOv2 and depth give a 3D keypoint set P
- ② Rewards: the VLM writes stage-wise rewards as PyTorch functions
- ③ Guided generation: reward gradients refine; reward progress switches stages

Notes: The VLS pipeline has three components. The first is keypoint extraction: from the RGB-D observation and the instruction, a VLM identifies the task-relevant objects, SAM gives masks, DINOv2 gives dense features, and depth lifts them to a 3D point cloud that is clustered into a set of task-relevant 3D keypoints P. The new condition is thus compressed into a geometric scaffold. The second is reward generation: the VLM decomposes the task into S stages and, for each stage, writes a reward function over the keypoints and the action sequence using differentiable PyTorch tensor operations, for example the negative squared distance to a target keypoint. The VLM itself stays outside the computation graph; gradients flow through the generated function. The third is the reward-guided denoising loop with closed-loop stage switching, which I explain on the next slide.

## Slide 28 VLS Method: reward-guided generation and control

- Repulsion keeps candidates diverse; reward gradients are applied repeatedly
- Candidates are resampled by reward weights; high-reward ones are duplicated
- Guidance strength λ adapts to the reward; stages switch with hysteresis

Notes: Inside the denoising loop. A batch of B action candidates is initialized, and in the early steps a repulsive force between candidates is added as a gradient to prevent premature collapse to a narrow mode of the base policy. Then the reward gradient of stage s is injected to refine the candidates; for diffusion policies there are four inner updates per step, in the spirit of MCMC. In addition, a gradient-free selection step follows Feynman-Kac steering: the exponential of the reward becomes a particle weight, the candidates are resampled according to the weights, high-reward candidates are duplicated and constraint-violating ones are pruned. In the closed-loop control, the guidance strength lambda is adapted from the reward relative to the first chunk of the stage: strong when the deviation is large, weak near completion so the base policy dominates. Stage switching uses a Schmitt-trigger-style hysteresis with two thresholds that decide to advance, maintain or reinforce, avoiding oscillation and premature transitions. On a switch, the VLM interprets the outcome and selects the next reward function.

## Slide 29 VLS Sim demo (video): with and without steering

- Left: LIBERO-PRO with moved objects. Frozen π0.5 fails; with VLS it succeeds
- Right: "avoid the wall". An unseen instruction, satisfied via reward gradients
- Numbered points: VLM-selected keypoints; rewards are distances to them

Notes: Here are videos of the same policy with and without steering. On the left is LIBERO-PRO with the object positions changed; the frozen π0.5 fails as is, but succeeds once VLS is added. The numbered points on screen are the keypoints chosen by the VLM, and the reward function is written in terms of distances to them. On the right the instruction is "put the red cube on the green patch while avoiding the wall", which does not appear in training. The base policy hits the wall, while the reward gradient corrects the trajectory so that it goes around the wall.

## Slide 30 VLS Result 1: simulation (LIBERO-PRO / CALVIN)

- LIBERO-PRO: frozen π0.5 + VLS, 23.7% → 36.8% (+13 pt)
- CALVIN: 94% on movable objects (7.4×), 87% on articulated parts (9.6×)
- Ablation: no gradient guidance → 17%; selection and repulsion add efficiency

Notes: Simulation results. LIBERO-PRO adds object-position and task-specification perturbations to LIBERO; OpenVLA and π0 are near 0%, and even the LeRobot π0.5 gets 23.7%. Adding VLS to that frozen π0.5 raises it to 36.8%, a 13-point gain. The authors' interpretation is that post-training on robot data entangles the VLM backbone's spatial reasoning with the training context. On CALVIN with a Diffusion Policy base, VLS reaches 94% on movable objects, 7.4 times the base, and 87% on articulated parts, 9.6 times, outperforming DynaGuide and ITPS by 15 to 25 points. In the ablation, removing gradient guidance collapses success to 17%, so dense, trajectory-differentiable guidance is the main driver; reward-based resampling and repulsion matter less for success but improve episode length and stability. The bottom right shows scaling with the number of samples: more samples help, but inference time exceeds 1.2 seconds, a compute-performance trade-off.

## Slide 31 VLS Real-robot demo (video): steering on a Franka

- Left: in-distribution, "put the banana on the green plate"
- Middle: an unseen object, a mug instead of the banana (0% → 40%)
- Right: plates swapped, same instruction; the policy follows

Notes: Real-robot demos on a Franka with a frozen π0.5 base. On the left is an in-distribution task: put the banana on the green plate. In the middle the banana is replaced by a mug the policy has never seen; the frozen policy gets 0%, and with VLS it succeeds in 40% of trials. On the right the plates are swapped while the instruction stays the same, and the policy follows the new positions. The overlay in the top left shows the guidance strength and the reward, and you can see the guidance weaken as the stage nears completion.

## Slide 32 VLS Result 2: real robot and limitations

- In-distribution: pick-and-place tasks go from 50% to 69% (+19 pt)
- Under shifts: unseen mug 0% → 40%, average 42% → 69%
- Limitation: latency, about 1 second per action chunk

Notes: The real robot is a Franka Emika with a frozen π0.5. The in-distribution tasks are placing an orange on the instructed plate, and, with a banana added, selecting both the object and the plate; average success rises from 50% to 69%, a 19-point gain. The out-of-distribution variants replace the plate with an unseen yellow one, swap the plate positions, and replace the banana with an unseen mug. The baseline degrades sharply, to 0% on the mug, while VLS gets 40% there and 69% on average versus 42%. The main limitation is inference overhead from batch sampling, repeated refinement and resampling, about one second per chunk in Figure 4; progress-aware reward generation and efficiency are listed as future work.

## Slide 33 Insights Summary: three ways to use VLM capabilities

- All three use the VLM around the policy: build sims, monitor execution, steer generation
- SimFoundry: VLM spatial understanding copies real scenes into sim for eval and data
- Code-as-Monitor and VLS share a pattern: VLM-written geometry + code, as monitor or reward
- My view: all improve with base models; issues are latency and VLM errors; reuse sim-verified code

Notes: To summarize. What the three papers share is that they use the VLM around the policy rather than as the policy. SimFoundry uses the VLM's spatial understanding to copy a real scene into simulation and produce evaluation and training data. Code-as-Monitor and VLS both have the VLM write geometric elements and the code that uses them; Code-as-Monitor uses that code as a monitor condition to check execution, VLS uses it as a reward to steer generation. I think the same code could serve both as a monitor at execution time and as a guide at generation time. As ASPIRE showed at the start, methods that have the model write code improve as the base model improves, and I expect these three to improve the same way. The shared issues are latency and VLM errors: VLS takes about a second per chunk, and Code-as-Monitor calls the VLM once per subgoal. From my own research perspective, if reward and monitor code verified in simulation were accumulated as an asset and only reused on the real robot, we could reduce both the dependence on the VLM at inference time and the latency.

## Slide 34 Insights My own work: steering + monitoring

- Recently I have been testing VLS-style steering combined with CaM-style monitoring
- VLM-written code both steers generation and monitors execution
- Videos: LIBERO examples; the right panel shows the VLM judgment and monitor log

Notes: Finally, a brief look at my own work. I have recently been testing a method that combines VLS-style reward steering with Code-as-Monitor-style monitor code, which is exactly the idea from the summary: VLM-written code used both to steer generation and to monitor execution. The videos show examples on LIBERO-Goal and LIBERO-Object, with the VLM's judgment and the monitor log on the right. It is still work in progress, but the early results are interesting, so please talk to me afterwards if you are curious. Thank you for your attention. I am happy to take questions.
