import re

def patch_index():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_card = """
                <!-- Linear Control Systems -->
                <div class="glass-panel" style="display: flex; flex-direction: column; height: 100%; transition: all 0.3s; cursor: default;">
                    <div style="flex: 1;">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎛️</div>
                        <h3 style="font-size: 1.25rem; font-weight: 700; color: #fff; margin-bottom: 0.5rem;">Linear Control Systems</h3>
                        <p style="font-size: 0.9rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1rem;">Master control systems with MATLAB! Learn Transfer Functions, Root Locus, Bode Plots, and PID Tuning.</p>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                            <span class="badge badge-difficulty">Advanced</span>
                            <span class="badge" style="background: rgba(139, 92, 246, 0.2); color: #c4b5fd;">MATLAB</span>
                            <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7;">10 Lessons</span>
                        </div>
                    </div>
                    <a href="javascript:void(0)" onclick="startCourse('linear_control.html')" class="btn btn-primary" style="justify-content: center; width: 100%; margin-top: 1.5rem;">Start Course</a>
                </div>
    """
    
    # insert before robotics
    content = content.replace('<!-- Robotics -->', new_card + '\n                <!-- Robotics -->')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)


def patch_dashboard():
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    new_stat = """
                    <!-- Linear Control Systems -->
                    <div class="stat-card">
                        <div class="stat-icon" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">🎛️</div>
                        <div class="stat-info">
                            <div class="stat-label">Control Systems (MATLAB)</div>
                            <div class="stat-value" id="stat-linearcontrol-completed">0 / 10</div>
                        </div>
                    </div>
    """
    content = content.replace('<!-- Robotics Simulator -->', new_stat + '\n                    <!-- Robotics Simulator -->')

    new_badge = """
                        <div class="badge-card" id="badge-linearcontrol">
                            <div class="badge-icon" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 2px solid rgba(16, 185, 129, 0.3);">🎛️</div>
                            <h4 class="badge-title">CONTROL ENGINEER</h4>
                            <p class="badge-desc">Finished Linear Control Systems Course</p>
                        </div>
    """
    content = content.replace('<div class="badge-card" id="badge-robotics">', new_badge + '\n                        <div class="badge-card" id="badge-robotics">')
    
    js_update = """
            const lcProgress = user.progress.linearcontrol || { completed_lessons: [], completed: false };
            const lcCompletedCount = lcProgress.completed_lessons.length;
            document.getElementById('stat-linearcontrol-completed').textContent = `${lcCompletedCount} / 10`;

"""
    content = content.replace("const jsProgress = ", js_update + "            const jsProgress = ")

    js_badge_update = """
                document.getElementById('badge-linearcontrol').classList.add('earned');
            }
            if (user.progress.robotics && user.progress.robotics.completed) {
"""
    content = content.replace("if (user.progress.robotics && user.progress.robotics.completed) {", js_badge_update)

    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)


def patch_auth():
    with open('auth.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('robotics: { completed_lessons: [], completed: false }', 'robotics: { completed_lessons: [], completed: false },\n                linearcontrol: { completed_lessons: [], completed: false }')
    
    content = content.replace("else if (courseId === 'arduino' || courseId === 'datavis' || courseId === 'robotics') totalLessons = 10;", "else if (courseId === 'arduino' || courseId === 'datavis' || courseId === 'robotics' || courseId === 'linearcontrol') totalLessons = 10;")
    
    with open('auth.js', 'w', encoding='utf-8') as f:
        f.write(content)


def patch_admin():
    with open('admin.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('<option value="robotics">Completed Robotics</option>', '<option value="robotics">Completed Robotics</option>\n                            <option value="linearcontrol">Completed Control Systems</option>')
    
    with open('admin.html', 'w', encoding='utf-8') as f:
        f.write(content)

def patch_admin_app():
    with open('admin_app.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('robotics: 10', 'robotics: 10,\n        linearcontrol: 10')
    content = content.replace("robotics: '🤖'", "robotics: '🤖',\n        linearcontrol: '🎛️'")
    content = content.replace(" 'javascript', 'ai', 'robotics'", " 'javascript', 'ai', 'robotics', 'linearcontrol'")
    content = content.replace("if (courseId === 'cvcapstone') label = 'CVC';", "if (courseId === 'cvcapstone') label = 'CVC';\n                if (courseId === 'linearcontrol') label = 'CTRL';")
    
    with open('admin_app.js', 'w', encoding='utf-8') as f:
        f.write(content)

patch_index()
patch_dashboard()
patch_auth()
patch_admin()
patch_admin_app()
