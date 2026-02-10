/**
 * Schools Page Logic
 */

let allSchools = [];
let currentSort = 'mentorCount';

/**
 * Initialize page
 */
async function init() {
    try {
        // Load metadata and update stats
        const metadata = await loadMetadata();
        updateStats(metadata);

        // Load schools
        allSchools = await loadSchools();
        renderSchools(allSchools);

        // Setup event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Error initializing page:', error);
        showError('加载数据失败，请刷新页面重试');
    }
}

/**
 * Update statistics in hero section
 */
function updateStats(metadata) {
    document.getElementById('totalSchools').textContent = formatNumber(metadata.totalSchools);
    document.getElementById('totalMentors').textContent = formatNumber(metadata.totalMentors);
    document.getElementById('totalEvaluations').textContent = formatNumber(metadata.totalEvaluations);
}

/**
 * Render schools grid
 */
function renderSchools(schools) {
    const grid = document.getElementById('schoolsGrid');

    if (schools.length === 0) {
        grid.innerHTML = '<div class="loading">未找到匹配的学校</div>';
        return;
    }

    grid.innerHTML = schools.map(school => `
        <a href="mentors.html?school=${encodeURIComponent(school.name)}" class="school-card">
            <div class="school-card-header">
                <div>
                    <h3 class="school-name">${escapeHtml(school.name)}</h3>
                </div>
                <div class="school-score">${formatScore(school.averageScore)}分</div>
            </div>
            <div class="school-stats">
                <div class="school-stat">
                    <div class="school-stat-value">${formatNumber(school.mentorCount)}</div>
                    <div class="school-stat-label">导师</div>
                </div>
                <div class="school-stat">
                    <div class="school-stat-value">${formatNumber(school.evaluationCount)}</div>
                    <div class="school-stat-label">评价</div>
                </div>
                <div class="school-stat">
                    <div class="school-stat-value">${formatNumber(school.departmentCount)}</div>
                    <div class="school-stat-label">院系</div>
                </div>
            </div>
        </a>
    `).join('');
}

/**
 * Sort schools
 */
function sortSchools(schools, sortBy) {
    const sorted = [...schools];

    switch (sortBy) {
        case 'mentorCount':
            sorted.sort((a, b) => b.mentorCount - a.mentorCount);
            break;
        case 'averageScore':
            sorted.sort((a, b) => b.averageScore - a.averageScore);
            break;
        case 'name':
            sorted.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
            break;
    }

    return sorted;
}

/**
 * Filter schools by search query
 */
function filterSchools(schools, query) {
    if (!query) return schools;

    const lowerQuery = query.toLowerCase();
    return schools.filter(school =>
        school.name.toLowerCase().includes(lowerQuery)
    );
}

/**
 * Handle search
 */
const handleSearch = debounce((event) => {
    const query = event.target.value.trim();
    const filtered = filterSchools(allSchools, query);
    const sorted = sortSchools(filtered, currentSort);
    renderSchools(sorted);
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
    const filtered = filterSchools(allSchools, searchQuery);
    const sorted = sortSchools(filtered, sortBy);
    renderSchools(sorted);
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

    // About button
    document.getElementById('aboutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        alert('导师评价系统\n\n本系统收集并展示导师评价数据，帮助学生做出更明智的选择。\n\n数据来源：真实学生评价\n评价维度：导师能力、经费情况、学生补助、师生关系、工作时间、毕业去向');
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
