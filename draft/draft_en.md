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

## Slide 6 SimFoundry Where it sits in this talk: Real2Sim

- Input: one real-world video, plus the policy you want to evaluate or train
- The VLM's job: detect objects, estimate mass and friction, propose new layouts and tasks
- The policy is what gets evaluated or trained inside the sim; the VLM builds the sim

Notes: Let me place SimFoundry in the framework from the introduction. Of the three areas, this is Real2Sim. The input is a single real-world video plus the policy you want to evaluate or train. The job of the VLM and the vision foundation models is to find the objects in the video, turn them into 3D, estimate mass and friction, and propose alternative layouts and tasks. In other words, the VLM does not drive the policy; it builds the arena in which the policy is tested. The policy is what gets evaluated in the sim, or trained on sim data. Unlike the next two papers, the VLM is not involved at execution time, so there is no latency issue.

## Slide 7 SimFoundry What is new: automatic variants, not just a copy

- Most real-to-sim work stops at one copy of the scene (digital twin)
- SimFoundry adds object, layout and task variants (digital cousins) automatically
- One scene gives a faithful sim for evaluation and diverse sims for training

Notes: Here is what is new, on one slide. Building simulations from the real world is not new, but most prior work stops at one faithful copy of the scene, the digital twin. A twin is faithful, so it suits evaluation, but it gives training data for one scene only. SimFoundry starts from the twin and asks a VLM to propose versions with different object shapes, different layouts and different tasks, and builds them automatically. These are the digital cousins. As a result, one real scene yields both a faithful sim for evaluation and diverse sims for training. In the paper's Table 1, SimFoundry is the only system that covers evaluation, training and diversification together.

## Slide 8 SimFoundry Overview: from a reconstructed scene to variants

- Input: one video. Output: a scene in a physics sim (digital twin)
- From the twin, generate unlimited variants (digital cousins)
- Uses: sim evaluation of real policies, and sim-to-real training

Notes: Here is the overview. The input is a single video of a real scene and the output is an interactive scene in a physics simulator, which the paper calls a digital twin. From the twin, SimFoundry generates an unlimited number of variants that preserve the task-relevant affordances, called digital cousins, along three axes: objects, layouts and tasks. The resulting environments serve both purposes shown by the arrows: evaluating real-world policies in simulation, and training policies in simulation that transfer to the real robot.

## Slide 9 SimFoundry Reconstruction examples (video)

- Left: a dining room. Right: a toy table. Both from a single video
- Each object mesh is generated from one image crop, fully automatically
- About 5 minutes per object, no manual annotation

Notes: Let's look at reconstruction examples. On the left is a dining room and on the right a table with toys, both reconstructed from a single real video. The first half shows the real scene and the second half the reconstruction in simulation. Each object's 3D mesh is generated automatically from a single image crop, and you can see that the shapes and the layout match the real scene. No manual annotation is needed and it takes about five minutes per object. These reconstructed scenes are what we later use for evaluation and for generating training data.

## Slide 10 SimFoundry Method 1: four steps from video to scene

- ① Pick one frame from the video, estimate depth, build a point cloud
- ② A VLM names the objects; SAM cuts them out one by one
- ③ Generate a 3D mesh from each crop; ask the VLM for mass and friction
- ④ Place everything in a physics sim and resolve penetrations

Notes: Let me break the reconstruction into four steps. First, pick a representative frame from the video and estimate depth to get a point cloud; this gives the table plane and where things are. Second, ask a VLM what is in the image, and cut the objects out one at a time with SAM 3; each cut-out object is inpainted away so the remaining ones can be found in turn. Third, from each single crop, a 2D-to-3D generative model produces a mesh, which is aligned to the point cloud; drawers and doors get joints from a separate module, and the VLM answers mass and friction from common sense. Fourth, everything is placed in a physics simulator, penetrations are resolved, and the scene is exported to IsaacLab and others. Each step just calls an off-the-shelf foundation model, so better models can be swapped in.

## Slide 11 SimFoundry Method 2: three kinds of variants

- Object variants: perturb the crop, regenerate the mesh (a different mug)
- Layout variants: the VLM rewrites relations such as "on top of"
- Task variants: the VLM proposes other tasks; demos are generated

Notes: Now the variants. Object cousins perturb the cropped image with an image model and regenerate the 3D mesh, giving a mug with a different shape, handle or texture but the same function. Scene cousins have the VLM rewrite relations between objects such as on-top-of or right-of, producing meaningful new layouts rather than position noise; distractors can be added too. Task cousins have the VLM propose other tasks that are feasible on this table, convert them to goal specifications, and generate demonstrations with existing data-generation methods. Together these turn one real scene into a large training set that is diverse in objects, layouts and tasks.

## Slide 12 SimFoundry Result 1: sim evaluation predicts real performance

- 7 tasks × 5 policies, evaluated in sim and on the real robots
- Mean Pearson r = 0.911, MMRV = 0.018 (almost no rank flips)
- r is 0.59 above PolaRiS, with no fine-tuning of the policies

Notes: The first result is real-to-sim evaluation. Seven tasks on two real setups, a single-arm Franka in the DROID setup and a bimanual YAM, with five policies: π0, π0.5, GR00T N1.6, N1.7 and DreamZero, evaluated both in simulation and on the real robots. In the scatter plot, SimFoundry's blue markers lie close to the diagonal, with a mean Pearson correlation of 0.911 and a mean maximum rank violation of 0.018. The orange markers of the baseline PolaRiS are scattered, and the correlation gap is more than 0.59. Moreover, PolaRiS lightly fine-tunes the policies on its simulation data, while SimFoundry evaluates the policies zero-shot. Evaluating at the sub-task level raises the correlation from 0.90 to 0.95 and tells you which stage of a task is weak.

## Slide 13 SimFoundry Result 2: sim-to-real transfer and variants

- Sim-only training reaches 99-100% zero-shot on the real robots
- Object / scene / task cousins raise real success by +17 / +21 / +40%
- Reconstruction fidelity: F1 0.81-0.92, about 5 min per object; tabletop scenes only

Notes: The second result is sim-to-real training. Policies trained only on SimFoundry data transfer zero-shot to the real robots, reaching 99% on Pot on Stove with YAM and 100% on Stack Dishware with DROID. On YAM this is a flow-matching policy trained from scratch; on DROID the π0.5 DROID checkpoint is fine-tuned on sim demonstrations. The figure shows the effect of the variants. In panel A, object cousins improve robustness to unseen objects, a 50-point gain on unseen Pot on Stove objects. In panel B, scene cousins improve layout generalization: 16% on cousin layouts where the twin-only policy gets 0%, and up to 28 points even on the twin layout. In panel C, with the total number of demos fixed, replacing some target-task demos with related-task demos actually raises success on the target task, by 60 points on Throw Away Trash. Fine-tuning π0.5 on multi-task data from 13 tasks gives 29% on held-out tasks and up to 18% improvement in the real world. A word on reconstruction quality: on a geometric evaluation over 12 scenes the fully automatic pipeline reaches F1 of 0.81 to 0.92, above SAM3D's 0.66 to 0.71, at about five minutes per object, and three minutes of manual tuning raises F1 to 0.93 to 0.99. The limitations are the tabletop assumption and inheriting the failures of each foundation model.

## Slide 14 SimFoundry Real-robot demo (video): sim-trained policies

- Left: bimanual policy trained in sim (YAM). Middle: same policy, real robot
- Right: objects never seen in training, thanks to object cousins
- Pot on Stove reaches 99% on the real robot

Notes: Here are policies trained in simulation running on the real robot. On the left is the bimanual YAM policy trained inside simulation, and in the middle the same policy executed on the real robot without any fine-tuning. On the right it runs on objects that were not in the training set, which is where object cousins in the training data pay off. On the Pot on Stove task the real-world success rate was 99%.

## Slide 15 Papers (highlight paper 2)

Notes: The second paper is Code-as-Monitor, from CVPR 2025. In one sentence, it unifies reactive failure detection and proactive failure prevention as checking whether constraints are satisfied, and monitors them in real time with VLM-generated code. Three things to remember: unifying reactive and proactive detection, constraint elements that abstract objects into points, lines and surfaces, and calling the VLM only once per subgoal.

## Slide 16 Code-as-Monitor Where it sits in this talk: failure detection

- Input: task instruction, camera images, and the running (open-loop) policy
- The VLM's job: write the conditions to keep, then code that checks them
- The policy runs as is; the code watches and stops it to re-plan on a violation

Notes: Here is where Code-as-Monitor sits: failure detection. The input is the task instruction, camera images and the running policy, which may be open-loop. The VLM's job is to write the conditions that must hold, and then to write code that checks them. The policy itself runs unchanged while the code watches alongside it; when a condition is violated the policy is stopped immediately and the reason is returned for re-planning. So the VLM never touches the policy; it places a monitor outside it.

## Slide 17 Code-as-Monitor What is new: let code do the watching

- Prior work asks the VLM "did it fail?" with images: slow, weak in 3D
- Here the VLM writes checking code once; the code then checks every frame
- Early signs (a tilting pan) show up as numbers, so failures are stopped early

Notes: Here is what is new. Prior failure detection asks a VLM, with images, whether the task has failed. Asking every frame, as in the top row, is slow, and 3D relations are hard to read from a single image, so misjudgments increase. Asking only when a subgoal completes, as in the middle row, misses the early signs until the end. This method, in the bottom row, has the VLM write checking code once at the start of a subgoal, after which the code checks the coordinates of tracked points every frame. Because the code judges with numbers, it also catches early signs such as the pan starting to tilt, and stops the policy before the failure happens. With a single VLM call it is fast and less exposed to hallucination.

## Slide 18 Code-as-Monitor Method 1: three steps on "carry the pan"

- ① The VLM writes the conditions: "the pan stays level", "the bread stays in the pan"
- ② Relevant parts become points, lines, surfaces on the image: the pan surface is 3 red points
- ③ The VLM writes code over those points: tilt over 15° returns "failure"

Notes: Let me break the method into three steps using the example of carrying a pan with bread to the stove. First, from the instruction and the images, the VLM writes the next subgoal and the conditions to keep, in words. During execution: keep grasping the handle, the bread stays in the pan, the pan stays level. Upon completion: the pan is directly above the stove. Second, the parts relevant to each condition are abstracted into points, lines and surfaces and drawn on the image: three red points on the rim for the pan surface, a green point for the bread, a blue point for the stove. Third, shown these annotated images, the VLM writes checking code over the point coordinates. In the example it computes the surface normal from the three points and, if the angle to vertical exceeds 15 degrees, returns a failure with the reason "the pan is not level". After that the code simply runs every frame on the tracked points.

## Slide 19 Code-as-Monitor Method 2: why points, lines and surfaces

- Objects and parts become points, lines, surfaces: easy to track
- ConSeg (LISA + LoRA) segments the relevant part from the constraint text
- Training data: BridgeData V2 auto-annotated by GPT-4o (10,181 traj.)

Notes: The other core idea is the constraint element. Objects or parts relevant to a constraint are abstracted into compact geometric elements such as points, lines and surfaces. For "the pan should remain horizontal", the pan surface becomes three points and the code just computes the angle between its normal and the z axis. Irrelevant details such as texture are discarded, which makes tracking easy and generalizes to unseen objects and scenes. The pipeline segments instance and part masks from the constraint text, projects them to a 3D point cloud using depth, voxelizes and clusters them according to the element type, and connects the points into elements, which are then annotated onto the multi-view images with numbers. The segmentation model is called ConSeg. It is built on LISA, keeping the LLaVA and SAM encoder and decoder frozen and training LoRA parameters, and outputs the mask and element type directly from the constraint text. The training data comes from BridgeData V2: GPT-4o generates subgoals, constraints and object-part associations, Grounded SAM and Semantic SAM produce the masks, and the result is manually checked, giving 10,181 trajectories and 219,356 images.

## Slide 20 Code-as-Monitor Method 3: inside the monitor code

- Input: 3D element positions and history. Output: (bool, reason)
- Thresholds from a knowledge base or the VLM; every branch is tested
- On a violation: stop the policy, return the reason, re-plan

Notes: Here is the monitor code in practice. GPT-4o receives the annotated multi-view images, the next subgoal and the constraints, and writes a function that takes the 3D positions of the elements. The code computes angles and distances with NumPy and returns a boolean indicating failure plus a string explaining why. In the example, if the angle between the pan surface normal and the z axis exceeds 15 degrees, it returns "the pan surface is not horizontal". Because the history of positions is also an input, precise conditions such as "move 2 cm" or "rotate 180 degrees" can be monitored, which VQA-style methods cannot do. Thresholds come from a knowledge base for common tasks and from the VLM's knowledge for unseen ones. Right after generation, the code is run on the current state so that every if-else branch is exercised, and it is regenerated on any error. During execution the elements are tracked and the code evaluated; when it returns False the policy stops immediately and the reason goes back to the VLM for re-planning.

## Slide 21 Code-as-Monitor Sim demo (video): monitoring under disturbances

- Left: stacking under placement noise. CaM restacks before collapse
- Middle: DoReMi queries the VLM repeatedly and misjudges more often
- Right: sweep half the blocks (count points), pour tea (surface tilt)

Notes: Let's watch the monitoring in simulation. On the left is block stacking in CLIPort with placement noise. Because the block positions are tracked as points, the method detects when the stack is about to collapse and restacks before moving on. In the middle is the baseline DoReMi, which keeps querying the VLM with images; 3D understanding from a single image is coarse, so misjudgments increase. On the right is the task of sweeping exactly half of the blocks, where counting the points inside the region lets the policy stop at the right moment. In OmniGibson's pour-tea task, the tilt of the teapot surface is monitored to catch a spill before it happens.

## Slide 22 Code-as-Monitor Result 1: simulation

- CLIPort: 76.7% → 88.3% under disturbances; Sweep Half 16.7 → 75.0%
- OmniGibson: only CaM catches surface tilt; time −35%, tokens −52%
- RLBench: 91.3% → 97.1% on unseen articulated and tool-use tasks

Notes: Simulation results. Three simulators with different robots, end-effectors and policies, with disturbances injected to induce failures. In CLIPort block stacking under strong disturbances, a 0.3 drop probability and 3 cm placement noise, the baseline DoReMi reaches 76.7% while this method reaches 88.3%. DoReMi, which repeatedly asks the VLM, has coarse 3D understanding from single images and misjudges more. On sweeping half the blocks, counting element points raises success from 16.7% to 75%. In OmniGibson, with point-, line- and surface-level disturbances, only this method could detect the surface-level disturbance in pouring tea. Since code is generated once per subgoal, execution time drops by 34.8% and token usage by 52.2%. On RLBench, even on articulated-object and tool-use tasks absent from the training data, success rises from ARP's 91.3% to 97.1%, showing generalization.

## Slide 23 Code-as-Monitor Real-robot demo (video): closing the loop

- Left: "clear everything except the animals". Moved objects are retargeted
- Right: "grasp animals nearest to the fruits first". Moving them reorders
- The grasp model stays open-loop; the monitor code triggers re-planning

Notes: Real-robot demos. The robot is a UR5 with a Leap Hand, and the grasp generation model DexGraspNet 2.0 is used as an open-loop policy. On the left, the task is to clear everything except the animals; when a person moves an object or takes it out of the hand, the tracked points update the target and execution continues. On the right, the task is to grasp the animals in order of distance to the fruits; when a person moves the horse or the pear, the distances are recomputed and the grasp order changes. In both cases the monitor code detects the failure or the change and triggers re-planning, so the open-loop policy behaves as a closed-loop system.

## Slide 24 Code-as-Monitor Result 2: real robot and ablation

- CaM on an open-loop grasp policy: over 90% under disturbances
- Long-horizon reasoning task: DoReMi 0% vs. CaM 90%
- Ablation: multi-view, segmentation, point connection (65% → 40-55%)

Notes: The real robot is a UR5 with a Leap Hand, and the policy is the open-loop grasp model DexGraspNet 2.0; the segmentation model is the base model without any simulator fine-tuning. Under disturbances, moving the object during grasping or removing it during transport, and across four object types including deformable and transparent ones, the method exceeds 90%, about 20 points above DoReMi, with shorter execution time. On the cluttered long-horizon task "grasp the animals from nearest to the fruits", moving the horse or the pear changes the order; the method monitors the distances and switches targets, reaching 90% where DoReMi gets 0%. The open-loop policy effectively becomes closed-loop. In the ablation, removing multi-view drops success from 65% to 40%, replacing constraint-aware segmentation with DINOv2 semantic points gives 42.5%, and removing point connection gives 55%, so each component matters; on the real robot, not forming elements drops success from 60% to 20%. Stated limitations are VLM hallucination, difficulty with force-related failures that involve no displacement, and no handling of other modalities such as sound or liquids.

## Slide 25 Papers (highlight paper 3)

Notes: The third paper is VLS. In one sentence, it is a training-free framework that steers the sampling process of a frozen diffusion or flow-matching policy at inference time with differentiable rewards written by a VLM. Three things to remember: adding reward gradients to the generation process, having the VLM write the reward function as a program, and combining gradient-based refinement with reward-based candidate selection.

## Slide 26 VLS Where it sits in this talk: inference-time steering

- Input: camera images and the instruction, plus a frozen diffusion / flow policy
- The VLM's job: write, as code, a reward function that scores "good" actions
- While the policy generates an action, reward gradients bend it; nothing is trained

Notes: Here is where VLS sits: inference-time steering. The input is the camera images and the instruction, plus a frozen diffusion or flow-matching policy. The VLM's job is to write, as code, a reward function that scores how good an action is in the current situation. The policy builds its action gradually from noise, and during that process the reward gradient is added so the action bends toward higher reward. The policy weights are never changed and nothing is trained. Where Code-as-Monitor watches from outside the execution, VLS reaches inside the generation.

## Slide 27 VLS What is new: bend the generation, do not just pick

- Prior work picks among candidates; if no candidate is good, nothing can be picked
- Here the reward gradient moves the candidates themselves toward higher reward
- Two stages: move by gradient, then select by reward; weights untouched

Notes: Here is what is new, as a diagram. The horizontal axis is the action, say the lateral hand position; the blue hill is the pretrained policy's distribution, the orange curve is the VLM-written reward, and grey is the wall. In (a), without steering, candidates gather at the policy's hill, the actions that were common in training, and hit the wall. Most prior methods pick the best of these candidates with a VLM, a human or a value function, but if no candidate is good there is nothing to pick. In (b), this method adds the reward gradient to the candidates, so the candidates themselves move toward higher reward. In (c) it also duplicates high-reward candidates and prunes low ones. Move by gradient, then select by reward, with the policy weights untouched.

## Slide 28 VLS Method 1: three steps on "cheese in the basket"

- ① Extract numbered 3D points of the relevant objects: cheese, basket, others
- ② The VLM writes a reward: closer to the basket (point 2) scores higher
- ③ At every denoising step, add the reward gradient; the trajectory shifts to the basket

Notes: Let me break the method into three steps on the example of putting the cheese in the basket. First, the VLM names the relevant objects, SAM cuts them out, and DINOv2 features plus depth turn them into numbered 3D points: the cheese, the basket and the surrounding objects each get a number. Second, the VLM writes a reward function in PyTorch using those numbers. In the figure it is the negative squared distance between the action trajectory and point 2, the basket, so closer is better. It is restricted to differentiable operations, so we can take the gradient with respect to the actions. Third, at every step where the policy builds its action from noise, this reward gradient is added. The trajectory shifts a little toward the basket each step and ends up reaching it. The VLM only writes the code; it plays no part in computing the gradient.

## Slide 29 VLS Method 2: how the gradient enters generation

- Inject a gradient g into the frozen policy's denoising (classifier guidance)
- Hard part: the new condition has spatial and semantic structure
- Have the VLM write a differentiable surrogate score R as a program

Notes: The problem setting. The denoising process of the frozen base policy is steered by adding the gradient g of the log-likelihood of the new condition, in the form of classifier guidance known from image generation. For diffusion, the gradient scaled by a guidance strength lambda is added to the noise prediction; for flow matching, to the velocity field. The hard part is modeling g. A real-world condition is not a class label; it has spatial and semantic constraint structure, and the guidance must give dense, informative gradients with respect to the action trajectory. Existing steering methods use a learned value function, a learned dynamics model, or let humans or VLMs select among candidates, with respective issues: bias toward the critic's preferences, model error and cost, and discrete sparse signals. VLS instead has the VLM write the differentiable surrogate score R as a program, obtaining dense gradients without training.

## Slide 30 VLS Method 3: loop details and closed-loop control

- Repulsion keeps candidates diverse; reward gradients are applied repeatedly
- Candidates are resampled by reward weights; high-reward ones are duplicated
- Guidance strength λ adapts to the reward; stages switch with hysteresis

Notes: Inside the denoising loop. A batch of B action candidates is initialized, and in the early steps a repulsive force between candidates is added as a gradient to prevent premature collapse to a narrow mode of the base policy. Then the reward gradient of stage s is injected to refine the candidates; for diffusion policies there are four inner updates per step, in the spirit of MCMC. In addition, a gradient-free selection step follows Feynman-Kac steering: the exponential of the reward becomes a particle weight, the candidates are resampled according to the weights, high-reward candidates are duplicated and constraint-violating ones are pruned. In the closed-loop control, the guidance strength lambda is adapted from the reward relative to the first chunk of the stage: strong when the deviation is large, weak near completion so the base policy dominates. Stage switching uses a Schmitt-trigger-style hysteresis with two thresholds that decide to advance, maintain or reinforce, avoiding oscillation and premature transitions. On a switch, the VLM interprets the outcome and selects the next reward function.

## Slide 31 VLS Sim demo (video): with and without steering

- Left: LIBERO-PRO with moved objects. Frozen π0.5 fails; with VLS it succeeds
- Right: "avoid the wall". An unseen instruction, satisfied via reward gradients
- Numbered points: VLM-selected keypoints; rewards are distances to them

Notes: Here are videos of the same policy with and without steering. On the left is LIBERO-PRO with the object positions changed; the frozen π0.5 fails as is, but succeeds once VLS is added. The numbered points on screen are the keypoints chosen by the VLM, and the reward function is written in terms of distances to them. On the right the instruction is "put the red cube on the green patch while avoiding the wall", which does not appear in training. The base policy hits the wall, while the reward gradient corrects the trajectory so that it goes around the wall.

## Slide 32 VLS Result 1: simulation (LIBERO-PRO / CALVIN)

- LIBERO-PRO: frozen π0.5 + VLS, 23.7% → 36.8% (+13 pt)
- CALVIN: 94% on movable objects (7.4×), 87% on articulated parts (9.6×)
- Ablation: no gradient guidance → 17%; selection and repulsion add efficiency

Notes: Simulation results. LIBERO-PRO adds object-position and task-specification perturbations to LIBERO; OpenVLA and π0 are near 0%, and even the LeRobot π0.5 gets 23.7%. Adding VLS to that frozen π0.5 raises it to 36.8%, a 13-point gain. The authors' interpretation is that post-training on robot data entangles the VLM backbone's spatial reasoning with the training context. On CALVIN with a Diffusion Policy base, VLS reaches 94% on movable objects, 7.4 times the base, and 87% on articulated parts, 9.6 times, outperforming DynaGuide and ITPS by 15 to 25 points. In the ablation, removing gradient guidance collapses success to 17%, so dense, trajectory-differentiable guidance is the main driver; reward-based resampling and repulsion matter less for success but improve episode length and stability. The bottom right shows scaling with the number of samples: more samples help, but inference time exceeds 1.2 seconds, a compute-performance trade-off.

## Slide 33 VLS Real-robot demo (video): steering on a Franka

- Left: in-distribution, "put the banana on the green plate"
- Middle: an unseen object, a mug instead of the banana (0% → 40%)
- Right: plates swapped, same instruction; the policy follows

Notes: Real-robot demos on a Franka with a frozen π0.5 base. On the left is an in-distribution task: put the banana on the green plate. In the middle the banana is replaced by a mug the policy has never seen; the frozen policy gets 0%, and with VLS it succeeds in 40% of trials. On the right the plates are swapped while the instruction stays the same, and the policy follows the new positions. The overlay in the top left shows the guidance strength and the reward, and you can see the guidance weaken as the stage nears completion.

## Slide 34 VLS Result 2: real robot and limitations

- In-distribution: pick-and-place tasks go from 50% to 69% (+19 pt)
- Under shifts: unseen mug 0% → 40%, average 42% → 69%
- Limitation: latency, about 1 second per action chunk

Notes: The real robot is a Franka Emika with a frozen π0.5. The in-distribution tasks are placing an orange on the instructed plate, and, with a banana added, selecting both the object and the plate; average success rises from 50% to 69%, a 19-point gain. The out-of-distribution variants replace the plate with an unseen yellow one, swap the plate positions, and replace the banana with an unseen mug. The baseline degrades sharply, to 0% on the mug, while VLS gets 40% there and 69% on average versus 42%. The main limitation is inference overhead from batch sampling, repeated refinement and resampling, about one second per chunk in Figure 4; progress-aware reward generation and efficiency are listed as future work.

## Slide 35 Insights Side by side: what the VLM writes, who runs it

- In all three, the VLM only writes code or structure; it never drives the robot directly
- The difference is where the output is used: sim building, monitoring, steering
- VLM call frequency sets real-robot latency; SimFoundry never calls it at run time

Notes: Let me put the three papers in one table. The inputs are all camera images and an instruction, but what the VLM writes differs: SimFoundry gets object labels, physical properties and proposals for layouts and tasks; Code-as-Monitor gets constraint sentences and checking code; VLS gets reward-function code. Who uses it also differs: the simulator for SimFoundry, the monitoring process during execution for Code-as-Monitor, and the policy's denoising loop for VLS. The VLM is called only before deployment in SimFoundry, once per subgoal in Code-as-Monitor, and at each stage switch in VLS, which maps directly onto the real-robot latency. What they share is that the VLM only writes code or structure and never drives the robot directly.

## Slide 36 Insights Summary: three ways to use VLM capabilities

- All three use the VLM around the policy: build sims, monitor execution, steer generation
- SimFoundry: VLM spatial understanding copies real scenes into sim for eval and data
- Code-as-Monitor and VLS share a pattern: VLM-written geometry + code, as monitor or reward
- My view: all improve with base models; issues are latency and VLM errors; reuse sim-verified code

Notes: To summarize. What the three papers share is that they use the VLM around the policy rather than as the policy. SimFoundry uses the VLM's spatial understanding to copy a real scene into simulation and produce evaluation and training data. Code-as-Monitor and VLS both have the VLM write geometric elements and the code that uses them; Code-as-Monitor uses that code as a monitor condition to check execution, VLS uses it as a reward to steer generation. I think the same code could serve both as a monitor at execution time and as a guide at generation time. As ASPIRE showed at the start, methods that have the model write code improve as the base model improves, and I expect these three to improve the same way. The shared issues are latency and VLM errors: VLS takes about a second per chunk, and Code-as-Monitor calls the VLM once per subgoal. From my own research perspective, if reward and monitor code verified in simulation were accumulated as an asset and only reused on the real robot, we could reduce both the dependence on the VLM at inference time and the latency.

## Slide 37 Insights My own work: steering + monitoring

- Recently I have been testing VLS-style steering combined with CaM-style monitoring
- VLM-written code both steers generation and monitors execution
- Videos: LIBERO examples; the right panel shows the VLM judgment and monitor log

Notes: Finally, a brief look at my own work. I have recently been testing a method that combines VLS-style reward steering with Code-as-Monitor-style monitor code, which is exactly the idea from the summary: VLM-written code used both to steer generation and to monitor execution. The videos show examples on LIBERO-Goal and LIBERO-Object, with the VLM's judgment and the monitor log on the right. It is still work in progress, but the early results are interesting, so please talk to me afterwards if you are curious. Thank you for your attention. I am happy to take questions.
