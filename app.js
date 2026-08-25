// app.js

const API_BASE = 'http://127.0.0.1:5000/api';
let students = [];
let charts = {}; // Store chart instances to destroy them before re-rendering

// Global Chart Defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Outfit', sans-serif";
const gridConfig = { color: 'rgba(255, 255, 255, 0.04)' };

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await fetchStudents();
});

// -----------------------------------------
// DATA FETCHING & CRUD
// -----------------------------------------
async function fetchStudents() {
    try {
        const response = await fetch(`${API_BASE}/students`);
        if (!response.ok) throw new Error('Failed to fetch students');
        const data = await response.json();
        
        // Map backend data to frontend model
        students = data.map(s => {
            // Frontend prediction calculation (for UI demonstration purposes if not provided by backend)
            let predictedScore = 0;
            const gpa = s.Midterm_Marks ? s.Midterm_Marks : 70;
            const att = s.Attendance ? s.Attendance : 80;
            predictedScore += (gpa / 100) * 30; // 30%
            predictedScore += (att / 100) * 20; // 20%
            predictedScore += (Math.min(s.Study_Hours || 10, 30) / 30) * 15; // 15%
            predictedScore += ((s.Assignments_Completed || 80) / 100) * 15; // 15%
            predictedScore += ((s.Quiz_Score || 70) / 100) * 20; // 20%
            
            // Normalize to 100 scale
            predictedScore = (predictedScore * 100).toFixed(1);
            
            let riskLevel = 'Low';
            if (predictedScore < 40) riskLevel = 'Critical';
            else if (predictedScore < 55) riskLevel = 'High';
            else if (predictedScore < 70) riskLevel = 'Medium';

            return {
                id: s.Student_ID,
                name: `Student ${s.Student_ID}`, // The dataset doesn't have names, so we generate one
                gpa: (gpa / 25).toFixed(2), // Convert 100 scale to 4.0 scale approx
                attendance: att,
                studyHours: s.Study_Hours || 0,
                assignments: s.Assignments_Completed || 0,
                predictedScore: predictedScore,
                riskLevel: riskLevel,
                raw: s
            };
        });

        updateDashboard();
    } catch (error) {
        console.error('Error fetching data:', error);
        // Fallback dummy data if backend is not running
        if (students.length === 0) {
            students = generateDummyStudents(20);
            updateDashboard();
        }
    }
}

async function saveStudent(data, mode) {
    const method = mode === 'edit' ? 'PUT' : 'POST';
    const url = mode === 'edit' ? `${API_BASE}/students/${data.Student_ID}` : `${API_BASE}/students`;
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to save student');
        
        closeModal();
        await fetchStudents(); // Refresh data
    } catch (error) {
        console.error('Error saving student:', error);
        alert('Could not connect to backend. Data will be saved locally for this session.');
        
        // Fallback for local session if backend fails
        if (mode === 'add') {
            students.push(mapLocalData(data));
        } else {
            const idx = students.findIndex(s => s.id === data.Student_ID);
            if (idx > -1) students[idx] = mapLocalData(data);
        }
        closeModal();
        updateDashboard();
    }
}

async function deleteStudent(id) {
    if (!confirm(`Are you sure you want to delete student ${id}?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/students/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete student');
        await fetchStudents();
    } catch (error) {
        console.error('Error deleting student:', error);
        // Fallback for local session
        students = students.filter(s => s.id !== id);
        updateDashboard();
    }
}

function mapLocalData(payload) {
    return {
        id: payload.Student_ID,
        name: `Student ${payload.Student_ID}`,
        gpa: (payload.Midterm_Marks / 25).toFixed(2),
        attendance: payload.Attendance,
        studyHours: payload.Study_Hours,
        assignments: payload.Assignments_Completed,
        predictedScore: 75.0,
        riskLevel: 'Low',
        raw: payload
    };
}

// -----------------------------------------
// DATASET UPLOAD
// -----------------------------------------
async function uploadDataset(file) {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Failed to upload dataset');
        const data = await response.json();
        alert(`Success: ${data.message}. Loaded ${data.rows} rows.`);
        await fetchStudents();
    } catch (error) {
        console.error('Error uploading dataset:', error);
        alert('Failed to upload dataset. Check the console for details.');
    }
}

// -----------------------------------------
// DASHBOARD UPDATES
// -----------------------------------------
function updateDashboard() {
    updateKPIs();
    populateTable(students);
    
    // Destroy existing charts before re-rendering
    Object.values(charts).forEach(chart => chart.destroy());
    
    charts.performance = initPerformanceChart();
    charts.grade = initGradeChart();
    charts.radar = initRadarChart();
    charts.scatter = initScatterChart();
}

function updateKPIs() {
    document.querySelector('#kpi-total .kpi-value').textContent = students.length;
    
    const avgGpa = students.reduce((sum, s) => sum + parseFloat(s.gpa), 0) / (students.length || 1);
    document.querySelector('#kpi-gpa .kpi-value').textContent = avgGpa.toFixed(2);
    
    const riskCount = students.filter(s => s.riskLevel === 'High' || s.riskLevel === 'Critical').length;
    document.getElementById('riskCount').textContent = riskCount;
    
    // Update live clock
    const clock = document.getElementById('liveClock');
    if (clock) {
        const now = new Date();
        clock.textContent = now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}

// -----------------------------------------
// MODAL LOGIC
// -----------------------------------------
const modal = document.getElementById('studentModal');
const form = document.getElementById('studentForm');

function openModal(mode, studentId = null) {
    document.getElementById('formMode').value = mode;
    const title = document.getElementById('modalTitle');
    
    if (mode === 'edit') {
        title.textContent = 'Edit Student';
        const student = students.find(s => s.id === studentId);
        if (student) {
            document.getElementById('studentId').value = student.id;
            document.getElementById('studentId').readOnly = true; // Can't edit ID
            document.getElementById('studentName').value = student.name;
            document.getElementById('studentGpa').value = student.raw.Midterm_Marks || (student.gpa * 25);
            document.getElementById('studentAttendance').value = student.attendance;
            document.getElementById('studentStudyHours').value = student.studyHours;
            document.getElementById('studentAssignments').value = student.assignments;
        }
    } else {
        title.textContent = 'Add Student';
        form.reset();
        document.getElementById('studentId').readOnly = false;
        document.getElementById('studentId').value = `STU${Math.floor(Math.random() * 9000) + 1000}`;
    }
    
    modal.showModal();
}

function closeModal() {
    modal.close();
    form.reset();
}

// -----------------------------------------
// VIEW MODAL LOGIC
// -----------------------------------------
const viewModal = document.getElementById('viewStudentModal');

function openViewModal(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;

    const detailsContainer = document.getElementById('viewStudentDetails');
    detailsContainer.innerHTML = ''; // Clear previous

    const fields = [
        { label: 'Student ID', value: student.id },
        { label: 'Name', value: student.name },
        { label: 'Gender', value: student.raw.Gender || 'Unknown' },
        { label: 'Age', value: student.raw.Age || 'Unknown' },
        { label: 'Class', value: student.raw.Class || 'Unknown' },
        { label: 'Attendance', value: `${student.attendance}%` },
        { label: 'Study Hours', value: student.studyHours },
        { label: 'Assignments (%)', value: student.assignments },
        { label: 'Quiz Score', value: student.raw.Quiz_Score || 'Unknown' },
        { label: 'Midterm Marks', value: student.raw.Midterm_Marks || 'Unknown' },
        { label: 'Final Exam Marks', value: student.raw.Final_Exam_Marks || 'Unknown' },
        { label: 'Internet Access', value: student.raw.Internet_Access || 'Unknown' },
        { label: 'Parental Education', value: student.raw.Parental_Education || 'Unknown' },
        { label: 'Extra Curricular', value: student.raw.Extra_Curricular || 'Unknown' },
        { label: 'Sleep Hours', value: student.raw.Sleep_Hours || 'Unknown' },
        { label: 'Previous Grade', value: student.raw.Previous_Grade || 'Unknown' },
        { label: 'Predicted Performance', value: student.raw.Performance || 'Unknown' }
    ];

    fields.forEach(field => {
        const group = document.createElement('div');
        group.className = 'form-group';
        group.innerHTML = `
            <label>${field.label}</label>
            <input type="text" value="${field.value}" readonly style="background: var(--bg); border: 1px dashed var(--border-2); color: var(--text-2);">
        `;
        detailsContainer.appendChild(group);
    });

    viewModal.showModal();
}

function closeViewModal() {
    viewModal.close();
}

// -----------------------------------------
// EVENT LISTENERS
// -----------------------------------------
function setupEventListeners() {
    // Modal buttons
    document.getElementById('addStudentBtn').addEventListener('click', () => openModal('add'));
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    document.getElementById('cancelModalBtn').addEventListener('click', closeModal);
    
    // View Modal buttons
    document.getElementById('closeViewModalBtn').addEventListener('click', closeViewModal);
    document.getElementById('doneViewModalBtn').addEventListener('click', closeViewModal);

    // Upload Dataset
    const uploadInput = document.getElementById('uploadDatasetInput');
    const uploadBtn = document.getElementById('uploadDatasetBtn');
    if (uploadBtn && uploadInput) {
        uploadBtn.addEventListener('click', () => uploadInput.click());
        uploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) uploadDataset(file);
            e.target.value = ''; // Reset
        });
    }

    document.getElementById('saveStudentBtn').addEventListener('click', (e) => {
        e.preventDefault();
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const mode = document.getElementById('formMode').value;
        const payload = {
            Student_ID: document.getElementById('studentId').value,
            Midterm_Marks: parseFloat(document.getElementById('studentGpa').value),
            Attendance: parseFloat(document.getElementById('studentAttendance').value),
            Study_Hours: parseFloat(document.getElementById('studentStudyHours').value),
            Assignments_Completed: parseFloat(document.getElementById('studentAssignments').value)
        };
        
        saveStudent(payload, mode);
    });

    // Search filter
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = students.filter(s => 
                s.name.toLowerCase().includes(term) || 
                s.id.toLowerCase().includes(term)
            );
            populateTable(filtered);
        });
    }

    // Topbar Actions
    document.getElementById('filterBtn')?.addEventListener('click', () => alert('Filter logic will go here.'));
    document.getElementById('notifBtn')?.addEventListener('click', () => alert('You have no new notifications.'));
    document.getElementById('exportBtn')?.addEventListener('click', () => alert('Exporting data as CSV...'));

    // Chart Filters
    document.querySelectorAll('.card-actions .pill-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active from siblings
            Array.from(e.target.parentElement.children).forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            // Logic to update chart data could go here
        });
    });

    // Table controls
    let sortAsc = false;
    document.getElementById('sortByRisk')?.addEventListener('click', (e) => {
        sortAsc = !sortAsc;
        e.target.textContent = sortAsc ? 'Sort: Risk ↑' : 'Sort: Risk ↓';
        const sorted = [...students].sort((a, b) => sortAsc ? a.predictedScore - b.predictedScore : b.predictedScore - a.predictedScore);
        populateTable(sorted);
    });

    document.getElementById('viewAll')?.addEventListener('click', () => {
        populateTable(students); // View all instead of top 15
    });

    // Sidebar Navigation
    const navItems = document.querySelectorAll('.sb-nav .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            navItems.forEach(nav => nav.classList.remove('active'));
            const target = e.target.closest('.nav-item');
            if (target) target.classList.add('active');
        });
    });

    // Mobile Sidebar Toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sbOverlay');
    const sbToggle = document.getElementById('sbToggle');

    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.add('mobile-open');
            overlay.classList.add('show');
        });
    }
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('show');
        });
    }
    if (sbToggle) {
        sbToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            document.getElementById('mainContent').classList.toggle('sidebar-collapsed');
        });
    }
}

// -----------------------------------------
// TABLE
// -----------------------------------------
function populateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    // Sort by risk (highest risk first)
    const sortedData = [...data].sort((a, b) => a.predictedScore - b.predictedScore).slice(0, 15);
    
    sortedData.forEach(student => {
        const tr = document.createElement('tr');
        const riskClass = `badge-${student.riskLevel.toLowerCase()}`;
        
        tr.innerHTML = `
            <td>
                <div class="student-cell">
                    <img src="https://ui-avatars.com/api/?name=${student.name.replace(' ', '+')}&background=random&color=fff" class="student-avatar" alt="Avatar">
                    <strong>${student.name}</strong>
                </div>
            </td>
            <td>${student.id}</td>
            <td>
                <div class="gpa-bar-wrap">
                    <span>${student.gpa}</span>
                    <div class="gpa-bar"><div class="gpa-fill" style="width: ${(student.gpa/4)*100}%"></div></div>
                </div>
            </td>
            <td>${student.attendance}%</td>
            <td><span class="badge ${riskClass}">${student.riskLevel}</span></td>
            <td><strong style="font-family:'JetBrains Mono',monospace">${student.predictedScore}</strong></td>
            <td>
                <button class="tbl-action" style="background:rgba(16,185,129,0.1);color:#10b981;border-color:rgba(16,185,129,0.2)" onclick="openViewModal('${student.id}')">View</button>
                <button class="tbl-action" onclick="openModal('edit', '${student.id}')">Edit</button>
                <button class="tbl-action" style="background:rgba(244,63,94,0.1);color:#f43f5e;border-color:rgba(244,63,94,0.2)" onclick="deleteStudent('${student.id}')">Del</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// -----------------------------------------
// CHARTS (Simplified initialization)
// -----------------------------------------
function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    const gradient1 = ctx.createLinearGradient(0, 0, 0, 400);
    gradient1.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
    gradient1.addColorStop(1, 'rgba(99, 102, 241, 0.0)');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'],
            datasets: [{
                label: 'Current Cohort',
                data: [75, 78, 80, 79, 82, 85, 84, Math.max(50, students.length ? students[0].predictedScore : 86)],
                borderColor: '#6366f1',
                backgroundColor: gradient1,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { grid: gridConfig, min: 50, max: 100 }, x: { grid: gridConfig } },
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleColor: '#fff', bodyColor: '#cbd5e1' }
            }
        }
    });
}

function initGradeChart() {
    const ctx = document.getElementById('gradeChart').getContext('2d');
    
    // Calculate grade distribution from students array
    let a=0, b=0, c=0, d=0, f=0;
    students.forEach(s => {
        const gpa = parseFloat(s.gpa);
        if (gpa >= 3.5) a++;
        else if (gpa >= 3.0) b++;
        else if (gpa >= 2.0) c++;
        else if (gpa >= 1.0) d++;
        else f++;
    });

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['A (3.5-4.0)', 'B (3.0-3.4)', 'C (2.0-2.9)', 'D (1.0-1.9)', 'F (<1.0)'],
            datasets: [{
                data: [a, b, c, d, f].map(v => v === 0 ? 1 : v), // Fallback if 0
                backgroundColor: ['#10b981', '#6366f1', '#f59e0b', '#ef4444', '#8b5cf6'],
                borderWidth: 0, hoverOffset: 4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom' } } }
    });
}

function initRadarChart() {
    const ctx = document.getElementById('subjectRadarChart').getContext('2d');
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Math', 'Physics', 'Chem', 'English', 'CS', 'Bio'],
            datasets: [
                { label: 'Top Performers', data: [95, 92, 88, 94, 98, 90], backgroundColor: 'rgba(99,102,241,0.2)', borderColor: '#6366f1', pointBackgroundColor: '#6366f1' },
                { label: 'Class Average', data: [72, 68, 75, 82, 70, 76], backgroundColor: 'rgba(255,255,255,0.05)', borderColor: '#94a3b8', pointBackgroundColor: '#94a3b8' }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { r: { angleLines: { color: 'rgba(255,255,255,0.1)' }, grid: { color: 'rgba(255,255,255,0.1)' }, pointLabels: { color: '#e2e8f0' }, ticks: { display: false } } },
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function initScatterChart() {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    const datasets = [
        { label: 'Low Risk', data: students.filter(s => s.riskLevel === 'Low').map(s => ({x: s.attendance, y: s.gpa, name: s.name})), backgroundColor: '#10b981' },
        { label: 'Medium Risk', data: students.filter(s => s.riskLevel === 'Medium').map(s => ({x: s.attendance, y: s.gpa, name: s.name})), backgroundColor: '#f59e0b' },
        { label: 'High/Critical Risk', data: students.filter(s => s.riskLevel === 'High' || s.riskLevel === 'Critical').map(s => ({x: s.attendance, y: s.gpa, name: s.name})), backgroundColor: '#ef4444' }
    ];

    return new Chart(ctx, {
        type: 'scatter',
        data: { datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { x: { title: { display: true, text: 'Attendance (%)', color: '#94a3b8' }, grid: gridConfig }, y: { title: { display: true, text: 'GPA', color: '#94a3b8' }, grid: gridConfig } },
            plugins: { tooltip: { callbacks: { label: (ctx) => `${ctx.raw.name}: Att ${ctx.raw.x}%, GPA ${ctx.raw.y}` } } }
        }
    });
}

// -----------------------------------------
// DUMMY DATA GENERATOR (Fallback)
// -----------------------------------------
function generateDummyStudents(count) {
    const students = [];
    for (let i = 0; i < count; i++) {
        const gpa = (Math.random() * (4.0 - 1.5) + 1.5).toFixed(2);
        const attendance = Math.floor(Math.random() * (100 - 40 + 1) + 40);
        let predictedScore = ((gpa / 4.0) * 50) + ((attendance / 100) * 50);
        
        let riskLevel = 'Low';
        if (predictedScore < 40) riskLevel = 'Critical';
        else if (predictedScore < 55) riskLevel = 'High';
        else if (predictedScore < 70) riskLevel = 'Medium';

        students.push({
            id: `STU${1000 + i}`,
            name: `Student ${1000 + i}`,
            gpa: gpa,
            attendance: attendance,
            predictedScore: predictedScore.toFixed(1),
            riskLevel: riskLevel,
            raw: { Midterm_Marks: gpa * 25 }
        });
    }
    return students;
}
