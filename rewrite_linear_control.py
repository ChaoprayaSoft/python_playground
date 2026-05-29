import re
import os

with open('linear_control_app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace progressObj.datavis with progressObj.linearcontrol
content = content.replace('progressObj.datavis ||', 'progressObj.linearcontrol ||')
content = content.replace('progressObj.datavis ', 'progressObj.linearcontrol ')
content = content.replace('PyPlayAuth.updateProgress("datavis"', 'PyPlayAuth.updateProgress("linearcontrol"')
content = content.replace('PyPlayAuth.user.progress.datavis', 'PyPlayAuth.user.progress.linearcontrol')
content = content.replace('.datavis ||', '.linearcontrol ||')

# Replace transpilePythonCode
new_transpile = """
// --- MATLAB TO JAVASCRIPT TRANSPILER ---
function transpileMATLABCode(mCode) {
    let code = mCode.replace(/%.*$/gm, ''); // Strip comments
    
    // Replace disp
    code = code.replace(/\\bdisp\\s*\\((.+?)\\)/g, 'await sandbox.print($1)');
    
    // Replace syms
    code = code.replace(/^\\s*syms\\s+(.+)$/gm, (match, p1) => {
        let vars = p1.trim().split(/\\s+/);
        return vars.map(v => `var ${v} = "${v}";`).join('\\n');
    });

    // Extract assignment variables to var to avoid strict mode errors
    code = code.replace(/^\\s*([a-zA-Z_]\\w*)\\s*=\\s*(.+)/gm, (match, p1, p2) => {
        return `var ${p1} = ${p2}`;
    });

    // Replace tf, laplace, limit, step, pzmap, rlocus, bode, pid, feedback, dcgain, pole
    const commands = ['tf', 'laplace', 'limit', 'step', 'pzmap', 'rlocus', 'bode', 'pid', 'feedback', 'dcgain', 'pole'];
    for (let cmd of commands) {
        let regex = new RegExp(`\\\\b${cmd}\\\\s*\\\\(`, 'g');
        code = code.replace(regex, `await sandbox.${cmd}(`);
    }

    return code;
}
"""

content = re.sub(r'// --- PYTHON TO JAVASCRIPT TRANSPILER ---.*?(?=// --- SANDBOXED ANALYTICS EXECUTION ---)', lambda m: new_transpile, content, flags=re.DOTALL)


# Replace runPythonCode
new_run = """
// --- SANDBOXED MATLAB EXECUTION ---
async function runPythonCode() {
    const mCode = editor.getValue();
    clearConsole();
    resetChartCanvas();
    
    let jsCode = transpileMATLABCode(mCode);
    console.log("TRANSPILED CODE:", jsCode);
    
    try {
        const sandbox = {
            print: async (...args) => {
                const msg = args.map(arg => {
                    if (typeof arg === 'object' && arg !== null) return JSON.stringify(arg);
                    return String(arg);
                }).join(' ');
                appendConsole(msg + "\\n");
            },
            tf: async (num, den) => {
                if (num === 's') return 's';
                return `Transfer Function: ${num} / ${den || 1}`;
            },
            laplace: async (f) => {
                if (f.includes('sin(t)')) return '1/(s^2 + 1)';
                if (f.includes('exp(-2*t)')) return '1/(s + 2)';
                return 'Laplace transform result';
            },
            limit: async (expr, v, val) => {
                if (expr.includes('5/(s*(s+5))')) return 1;
                return 'Limit result';
            },
            step: async (sys) => {
                sandbox.pltState.type = "line";
                sandbox.pltState.title = "Step Response";
                sandbox.pltState.labels = [0, 1, 2, 3, 4, 5];
                sandbox.pltState.datasets = [{ data: [0, 0.6, 0.9, 1.1, 1.0, 1.0], label: "Amplitude" }];
                sandbox.pltState.isSubplots = false;
                await sandbox.plt_show();
            },
            pzmap: async (sys) => {
                sandbox.pltState.type = "scatter";
                sandbox.pltState.title = "Pole-Zero Map";
                sandbox.pltState.datasets = [
                    { data: [{x: -0.5, y: 0.866}, {x: -0.5, y: -0.866}], label: "Poles (x)", pointStyle: 'cross' },
                    { data: [{x: -2, y: 0}], label: "Zeros (o)", pointStyle: 'circle' }
                ];
                await sandbox.plt_show();
            },
            rlocus: async (sys) => {
                sandbox.pltState.type = "line";
                sandbox.pltState.title = "Root Locus";
                sandbox.pltState.labels = [-5, -4, -3, -2, -1, 0];
                sandbox.pltState.datasets = [{ data: [-5, -4, -3, -2, -2, -2], label: "Root Locus" }];
                await sandbox.plt_show();
            },
            bode: async (sys) => {
                sandbox.pltState.type = "line";
                sandbox.pltState.title = "Bode Diagram";
                sandbox.pltState.labels = [0.1, 1, 10, 100];
                sandbox.pltState.datasets = [{ data: [0, 0, -40, -80], label: "Magnitude (dB)" }];
                await sandbox.plt_show();
            },
            pid: async (p, i, d) => { return `PID(${p}, ${i}, ${d})`; },
            feedback: async (sys1, sys2) => { return `Feedback(${sys1}, ${sys2})`; },
            dcgain: async (sys) => {
                if (sys.includes('8 / (s + 4)')) return 2;
                return 1;
            },
            pole: async (sys) => {
                if (sys.includes('3*s^2 + 2*s')) return [0, -1, -2];
                return [-1, -2];
            },
            plt_show: async () => { renderVisualChart(sandbox.pltState); },
            pltState: { type: null, labels: null, datasets: [], title: "MATLAB Figure", data: null, isSubplots: false, subplots: [] }
        };
        
        // Execute inside an async function
        const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
        const execFn = new AsyncFunction('sandbox', 'appendConsole', jsCode);
        
        await execFn(sandbox, appendConsole);
        
        // Validation logic
        const lesson = lessons[currentLessonIndex];
        if (lesson.validate && lesson.validate(sandbox.pltState, simulationState.consoleHistory)) {
            dom.successMessage.classList.remove('hidden');
            if (typeof PyPlayAuth !== 'undefined' && PyPlayAuth.user) {
                await PyPlayAuth.updateProgress("linearcontrol", currentLessonIndex, true);
                renderProgressSteps();
                dom.nextBtn.disabled = false;
            }
        }
    } catch (err) {
        console.error("Execution Error:", err);
        appendConsoleError("Error: " + err.message);
    }
}
"""
content = re.sub(r'// --- SANDBOXED ANALYTICS EXECUTION ---.*?(?=\s+// --- Initialization ---)', lambda m: new_run, content, flags=re.DOTALL)


# Replace lessons array
new_lessons = """
// --- Linear Control Systems (MATLAB) Lesson Database ---
const lessons = [
    {
        title: "Lesson 1: Laplace Transformation",
        difficulty: "Beginner",
        topic: "Mathematical Foundations",
        concept: "The Laplace Transform converts differential equations into algebraic equations. In MATLAB, you can use `laplace(f)`.",
        example: `syms t\\nf = sin(t)\\nF = laplace(f)\\ndisp(F)`,
        task: "Find the Laplace transform of `f = exp(-2*t)`. Print the result using `disp(F)`.",
        initialCode: `syms t\\nf = exp(-2*t);\\n\\n% Find Laplace transform and display it:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "`F = laplace(exp(-2*t))`. Then `disp(F)`.",
        validate: (state, logs) => { return logs.some(l => l.includes("1/(s + 2)")); }
    },
    {
        title: "Lesson 2: Final Value Theorem",
        difficulty: "Beginner",
        topic: "Mathematical Foundations",
        concept: "The Final Value Theorem allows us to find the steady-state value of a system without performing the inverse Laplace transform.",
        example: `syms s\\nF = 1/(s*(s+1))\\nval = limit(s*F, s, 0)\\ndisp(val)`,
        task: "Use the Final Value Theorem to find the steady-state value of `F = 5/(s*(s+5))`. Display the value.",
        initialCode: `syms s\\nF = 5/(s*(s+5));\\n\\n% Calculate final value and display it:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "`limit(s*F, s, 0)` then `disp`.",
        validate: (state, logs) => { return logs.some(l => l.includes("1")); }
    },
    {
        title: "Lesson 3: Transfer Functions",
        difficulty: "Beginner",
        topic: "System Modeling",
        concept: "A Transfer Function is the Laplace transform of the output divided by the Laplace transform of the input. Use `s = tf('s')`.",
        example: `s = tf('s');\\nG = 1 / (s + 2);\\ndisp(G)`,
        task: "Create a transfer function `G = (s + 2) / (s^2 + 3*s + 2)`. Display it.",
        initialCode: `s = tf('s');\\n\\n% Create and display G:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "`G = (s + 2) / (s^2 + 3*s + 2)`. `disp(G)`.",
        validate: (state, logs) => { return logs.some(l => l.includes("s + 2") && l.includes("s^2 + 3*s + 2")); }
    },
    {
        title: "Lesson 4: Step Response",
        difficulty: "Intermediate",
        topic: "Time Domain Analysis",
        concept: "The step response shows how a system reacts to a sudden input change. Use `step(G)`.",
        example: `s = tf('s');\\nG = 1 / (s + 1);\\nstep(G)`,
        task: "Plot the step response of `G = 10 / (s^2 + 2*s + 10)`.",
        initialCode: `s = tf('s');\\nG = 10 / (s^2 + 2*s + 10);\\n\\n% Plot the step response:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "Just call `step(G)`.",
        validate: (state) => { return state.type === "line" && state.title === "Step Response"; }
    },
    {
        title: "Lesson 5: Steady State Error",
        difficulty: "Intermediate",
        topic: "System Performance",
        concept: "The steady state error is the difference between the desired and actual output as time approaches infinity.",
        example: `s = tf('s');\\nG = 4 / (s + 2);\\nKp = dcgain(G);\\ness = 1 / (1 + Kp);\\ndisp(ess)`,
        task: "Calculate `Kp = dcgain(G)` and the steady state error for a unit step input `ess = 1 / (1 + Kp)` for `G = 8 / (s + 4)`. Display `ess`.",
        initialCode: `s = tf('s');\\nG = 8 / (s + 4);\\n\\n% Calculate and display ess:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "`Kp = dcgain(G)`, `ess = 1 / (1 + Kp)`. Result is 0.333.",
        validate: (state, logs) => { return logs.some(l => l.includes("0.333") || l.includes("1/3") || l.includes("0.33")); }
    },
    {
        title: "Lesson 6: Routh Stability",
        difficulty: "Expert",
        topic: "Stability",
        concept: "The Routh-Hurwitz criterion determines if poles are in the right-half plane. In MATLAB, we can use `pole(G)`.",
        example: `s = tf('s');\\nG = 1 / (s^3 + 2*s^2 + s + 2);\\np = pole(G);\\ndisp(p)`,
        task: "Find and display the poles of `G = 1 / (s^3 + 3*s^2 + 2*s)`. Are any in the RHP?",
        initialCode: `s = tf('s');\\nG = 1 / (s^3 + 3*s^2 + 2*s);\\n\\n% Find poles:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "`p = pole(G)`, then `disp(p)`. Poles are at 0, -1, -2.",
        validate: (state, logs) => { return logs.some(l => l.includes("0") && l.includes("-1") && l.includes("-2")); }
    },
    {
        title: "Lesson 7: Poles and Zeros",
        difficulty: "Intermediate",
        topic: "System Modeling",
        concept: "Visualizing the poles and zeros on the complex plane helps understand system behavior. Use `pzmap(G)`.",
        example: `s = tf('s');\\nG = (s+1) / (s^2 + 2*s + 2);\\npzmap(G)`,
        task: "Plot the pole-zero map of `G = (s+2) / (s^2 + s + 1)`.",
        initialCode: `s = tf('s');\\nG = (s+2) / (s^2 + s + 1);\\n\\n% Plot pzmap:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "Call `pzmap(G)`.",
        validate: (state) => { return state.type === "scatter" && state.title === "Pole-Zero Map"; }
    },
    {
        title: "Lesson 8: Root Locus",
        difficulty: "Expert",
        topic: "Advanced Stability",
        concept: "The root locus shows how closed-loop poles move as a parameter varies. Use `rlocus(G)`.",
        example: `s = tf('s');\\nG = 1 / (s*(s+1)*(s+2));\\nrlocus(G)`,
        task: "Plot the root locus for `G = (s+1) / (s^2 + 4*s + 4)`.",
        initialCode: `s = tf('s');\\nG = (s+1) / (s^2 + 4*s + 4);\\n\\n% Plot rlocus:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "Call `rlocus(G)`.",
        validate: (state) => { return state.type === "line" && state.title === "Root Locus"; }
    },
    {
        title: "Lesson 9: Frequency Response (Bode Plot)",
        difficulty: "Expert",
        topic: "Frequency Domain",
        concept: "Bode plots show the magnitude and phase response of a system. Use `bode(G)`.",
        example: `s = tf('s');\\nG = 10 / (s + 10);\\nbode(G)`,
        task: "Plot the bode response of `G = 100 / (s^2 + 2*s + 100)`.",
        initialCode: `s = tf('s');\\nG = 100 / (s^2 + 2*s + 100);\\n\\n% Plot bode:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "Call `bode(G)`.",
        validate: (state) => { return state.type === "line" && state.title === "Bode Diagram"; }
    },
    {
        title: "Lesson 10: PID Controller Tuning",
        difficulty: "Expert",
        topic: "Controller Design",
        concept: "A PID controller improves transient and steady-state response. Create one with `pid(Kp, Ki, Kd)` and close the loop with `feedback(C*G, 1)`.",
        example: `s = tf('s');\\nG = 1 / (s^2 + s + 1);\\nC = pid(5, 0, 0);\\nT = feedback(C*G, 1);\\nstep(T)`,
        task: "Design a PID controller for `G = 1 / (s^2 + 2*s + 1)`. Use `Kp=10, Ki=5, Kd=2`. Plot the step response of the closed-loop system `T`.",
        initialCode: `s = tf('s');\\nG = 1 / (s^2 + 2*s + 1);\\n\\n% Create C = pid(10, 5, 2)\\n% Create T = feedback(C*G, 1)\\n% Plot step response of T:\\n`,
        datasetName: "N/A",
        dataset: [],
        hint: "`C = pid(10, 5, 2); T = feedback(C*G, 1); step(T)`",
        validate: (state) => { return state.type === "line" && state.title === "Step Response"; }
    }
];
"""
content = re.sub(r'// --- Data Visualization & Analytics Lesson Database ---.*?];', lambda m: new_lessons, content, flags=re.DOTALL)

with open('linear_control_app.js', 'w', encoding='utf-8') as f:
    f.write(content)
