/**
 * Mentors Page Logic
 */

let allMentors = [];
let currentSchool = '';
let currentSort = 'evaluationCount';

/**
 * Initialize page
 */
async function init() {
    try {
        // Get school name from URL
        currentSchool = getURLParameter('school');
        if (!currentSchool) {
            window.location.href = 'index.html';
            return;
        }

        // Update page with school name
        document.getElementById('schoolName').textContent = currentSchool;
        document.getElementById('schoolHeaderTitle').textContent = currentSchool;
        document.title = `${currentSchool} - 导师列表`;

        // Load mentors for this school
        const mentorsBySchool = await loadMentorsBySchool();
        allMentors = mentorsBySchool[currentSchool] || [];

        if (allMentors.length === 0) {
            showError('该学校暂无导师数据');
            document.getElementById('mentorsGrid').innerHTML =
                '<div class="loading">该学校暂无导师数据</div>';
            return;
        }

        // Update stats
        updateStats(allMentors);

        // Render mentors
        renderMentors(allMentors);

        // Setup event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Error initializing page:', error);
        showError('加载数据失败，请刷新页面重试');
    }
}

/**
 * Update statistics
 */
function updateStats(mentors) {
    const totalScore = mentors.reduce((sum, m) => sum + m.totalScore, 0);
    const avgScore = totalScore / mentors.length;

    document.getElementById('mentorCount').textContent = formatNumber(mentors.length);
    document.getElementById('avgScore').textContent = formatScore(avgScore);
}

/**
 * Render mentors grid
 */
function renderMentors(mentors) {
    const grid = document.getElementById('mentorsGrid');

    if (mentors.length === 0) {
        grid.innerHTML = '<div class="loading">未找到匹配的导师</div>';
        return;
    }

    grid.innerHTML = mentors.map(mentor => {
        const dimensionTags = Object.entries(mentor.dimensionScores || {})
            .slice(0, 3)  // Show first 3 dimensions
            .map(([name, score]) => `
                <div class="dimension-tag">
                    <span class="dimension-tag-name">${escapeHtml(name)}</span>
                    <span class="dimension-tag-score">${formatScore(score)}</span>
                </div>
            `).join('');

        return `
            <a href="mentor-detail.html?id=${encodeURIComponent(mentor.id)}" class="mentor-card">
                <div class="mentor-card-header">
                    <div class="mentor-info">
                        <h3>${escapeHtml(mentor.name)}</h3>
                        <div class="mentor-department">${escapeHtml(mentor.department || '未知院系')}</div>
                    </div>
                    <div class="mentor-score-badge">
                        <div>${formatScore(mentor.totalScore)}</div>
                        <div class="score-label">${getScoreLabel(mentor.totalScore)}</div>
                    </div>
                </div>

                ${dimensionTags ? `<div class="dimension-preview">${dimensionTags}</div>` : ''}

                <div class="mentor-stats">
                    <div class="mentor-stat">
                        <div class="mentor-stat-value">${formatNumber(mentor.evaluationCount)}</div>
                        <div class="mentor-stat-label">评价数</div>
                    </div>
                    <div class="mentor-stat">
                        <div class="mentor-stat-value">${Object.keys(mentor.dimensionScores || {}).length}</div>
                        <div class="mentor-stat-label">维度</div>
                    </div>
                </div>
            </a>
        `;
    }).join('');
}

/**
 * Sort mentors
 */
function sortMentors(mentors, sortBy) {
    const sorted = [...mentors];

    switch (sortBy) {
        case 'evaluationCount':
            sorted.sort((a, b) => b.evaluationCount - a.evaluationCount);
            break;
        case 'totalScore':
            sorted.sort((a, b) => b.totalScore - a.totalScore);
            break;
        case 'name':
            sorted.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
            break;
    }

    return sorted;
}

/**
 * Filter mentors by search query
 */
function filterMentors(mentors, query) {
    if (!query) return mentors;

    const lowerQuery = query.toLowerCase();
    return mentors.filter(mentor =>
        mentor.name.toLowerCase().includes(lowerQuery) ||
        (mentor.department && mentor.department.toLowerCase().includes(lowerQuery))
    );
}

/**
 * Handle search
 */
const handleSearch = debounce((event) => {
    const query = event.target.value.trim();
    const filtered = filterMentors(allMentors, query);
    const sorted = sortMentors(filtered, currentSort);
    renderMentors(sorted);
}, 300);

/**
 * Handle sort change
 */
function handleSortChange(sortBy) {
    currentSort = sortBy;

    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.sort === sortBy);
    });

    // Re-render with new sort
    const searchQuery = document.getElementById('searchInput').value.trim();
    const filtered = filterMentors(allMentors, searchQuery);
    const sorted = sortMentors(filtered, sortBy);
    renderMentors(sorted);
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', handleSearch);

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            handleSortChange(btn.dataset.sort);
        });
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
