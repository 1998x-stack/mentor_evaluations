/**
 * Mentor Detail Page Logic
 */

let mentorData = null;
let radarChart = null;
let displayedEvaluations = 10;
let currentFilter = 'all';

/**
 * Initialize page
 */
async function init() {
    try {
        // Get mentor ID from URL
        const mentorId = getURLParameter('id');
        if (!mentorId) {
            window.location.href = 'index.html';
            return;
        }

        // Load mentor detail
        mentorData = await loadMentorDetail(mentorId);

        // Update page
        updateHeader();
        updateStats();
        initializeRadarChart();
        renderEvaluations();
        generateSuggestions();

        // Setup event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Error initializing page:', error);
        showError('加载导师数据失败，请返回重试');
    }
}

/**
 * Update page header
 */
function updateHeader() {
    document.title = `${mentorData.name} - ${mentorData.school}`;

    document.getElementById('mentorName').textContent = mentorData.name;
    document.getElementById('mentorSchool').textContent = mentorData.school;
    document.getElementById('mentorDept').textContent = mentorData.department || '未知院系';

    const score = mentorData.totalScore;
    document.getElementById('overallScore').textContent = formatScore(score);
    document.getElementById('scoreLabel').textContent = getScoreLabel(score);
    document.getElementById('evaluationCount').textContent = `${mentorData.evaluationCount} 条评价`;

    // Update breadcrumb
    document.getElementById('mentorBreadcrumb').textContent = mentorData.name;
    document.getElementById('schoolBreadcrumb').textContent = mentorData.school;
    document.getElementById('schoolBreadcrumb').href = `mentors.html?school=${encodeURIComponent(mentorData.school)}`;

    // Back button
    document.getElementById('backToMentors').href = `mentors.html?school=${encodeURIComponent(mentorData.school)}`;
}

/**
 * Update statistics
 */
function updateStats() {
    document.getElementById('statTotalEval').textContent = formatNumber(mentorData.evaluationCount);
    document.getElementById('statDimensions').textContent = Object.keys(mentorData.dimensionScores).length;
    document.getElementById('statOverallScore').textContent = formatScore(mentorData.totalScore);
}

/**
 * Initialize radar chart
 */
function initializeRadarChart() {
    const canvas = document.getElementById('radarChart');
    canvas.setAttribute('data-radar-chart', 'true');

    const dimensionScores = mentorData.dimensionScores;

    if (Object.keys(dimensionScores).length === 0) {
        canvas.parentElement.innerHTML = '<div class="loading">暂无维度评分数据</div>';
        return;
    }

    const labels = Object.keys(dimensionScores);
    const values = Object.values(dimensionScores);

    // Create radar chart
    radarChart = new RadarChart(canvas, {
        radius: 120,
        levels: 5,
        maxValue: 10
    });

    canvas.radarChart = radarChart;
    radarChart.setData(labels, values);

    // Render legend
    renderDimensionLegend(dimensionScores);
}

/**
 * Render dimension legend
 */
function renderDimensionLegend(dimensionScores) {
    const legend = document.getElementById('dimensionLegend');

    legend.innerHTML = Object.entries(dimensionScores)
        .map(([name, score]) => `
            <div class="legend-item">
                <span class="legend-label">${escapeHtml(name)}</span>
                <span class="legend-score" style="color: ${getScoreColor(score)}">
                    ${formatScore(score)}
                </span>
            </div>
        `).join('');
}

/**
 * Render evaluations
 */
function renderEvaluations() {
    const evaluations = mentorData.evaluations;

    if (!evaluations || evaluations.length === 0) {
        document.getElementById('evaluationsList').innerHTML =
            '<div class="loading">暂无评价数据</div>';
        return;
    }

    // Filter evaluations
    let filtered = filterEvaluations(evaluations, currentFilter);

    // Show limited number
    const toShow = filtered.slice(0, displayedEvaluations);

    const html = toShow.map(eval => {
        const dimensionsHtml = Object.entries(eval.dimensions || {})
            .map(([name, content]) => `
                <div class="eval-dimension-tag">
                    <span class="eval-dimension-name">${escapeHtml(name)}:</span>
                    <span class="eval-dimension-content">${escapeHtml(content)}</span>
                </div>
            `).join('');

        return `
            <div class="evaluation-item">
                <div class="evaluation-comment">${escapeHtml(eval.comment)}</div>
                ${dimensionsHtml ? `<div class="evaluation-dimensions">${dimensionsHtml}</div>` : ''}
            </div>
        `;
    }).join('');

    document.getElementById('evaluationsList').innerHTML = html;

    // Show "Show More" button if needed
    const showMoreContainer = document.getElementById('showMoreContainer');
    if (filtered.length > displayedEvaluations) {
        showMoreContainer.style.display = 'block';
        document.getElementById('showMoreBtn').textContent =
            `查看更多评价 (${filtered.length - displayedEvaluations} 条)`;
    } else {
        showMoreContainer.style.display = 'none';
    }
}

/**
 * Filter evaluations by sentiment
 */
function filterEvaluations(evaluations, filter) {
    if (filter === 'all') return evaluations;

    return evaluations.filter(eval => {
        const comment = eval.comment.toLowerCase();

        const positiveKeywords = ['好', '优秀', '不错', '负责', '认真', '支持'];
        const negativeKeywords = ['差', '不好', '糟糕', '压榨', '延期', '苛刻'];

        const positiveCount = positiveKeywords.filter(k => comment.includes(k)).length;
        const negativeCount = negativeKeywords.filter(k => comment.includes(k)).length;

        if (filter === 'positive') {
            return positiveCount > negativeCount;
        } else if (filter === 'negative') {
            return negativeCount > positiveCount;
        }

        return true;
    });
}

/**
 * Generate suggestions based on data
 */
function generateSuggestions() {
    const score = mentorData.totalScore;
    const dimensionScores = mentorData.dimensionScores;

    let suggestions = [];

    // Overall assessment
    if (score >= 7) {
        suggestions.push({
            title: '✅ 综合评价较好',
            text: `该导师综合评分为 ${formatScore(score)} 分，整体评价较为正面。`
        });
    } else if (score >= 5) {
        suggestions.push({
            title: '⚠️ 综合评价一般',
            text: `该导师综合评分为 ${formatScore(score)} 分，建议进一步了解具体情况。`
        });
    } else {
        suggestions.push({
            title: '❌ 综合评价较差',
            text: `该导师综合评分为 ${formatScore(score)} 分，评价相对负面，请谨慎选择。`
        });
    }

    // Dimension analysis
    const lowScoreDimensions = Object.entries(dimensionScores)
        .filter(([_, score]) => score < 5)
        .map(([name]) => name);

    const highScoreDimensions = Object.entries(dimensionScores)
        .filter(([_, score]) => score >= 7)
        .map(([name]) => name);

    if (highScoreDimensions.length > 0) {
        suggestions.push({
            title: '👍 优势维度',
            text: `在 ${highScoreDimensions.join('、')} 方面表现较好。`
        });
    }

    if (lowScoreDimensions.length > 0) {
        suggestions.push({
            title: '⚠️ 关注点',
            text: `在 ${lowScoreDimensions.join('、')} 方面评价较低，建议重点关注。`
        });
    }

    // Sample size
    if (mentorData.evaluationCount < 5) {
        suggestions.push({
            title: '📊 样本提示',
            text: `该导师评价数量较少（${mentorData.evaluationCount} 条），数据可能不够全面，建议结合其他渠道了解。`
        });
    }

    // Render suggestions
    const html = suggestions.map(s => `
        <div class="suggestion-section">
            <div class="suggestion-title">${s.title}</div>
            <div class="suggestion-text">${s.text}</div>
        </div>
    `).join('');

    const finalHtml = html + `
        <div class="suggestion-highlight">
            💡 <strong>建议：</strong>本系统评价仅供参考，建议结合多方信息（师兄师姐、学院官网等）综合判断，做出最适合自己的选择。
        </div>
    `;

    document.getElementById('suggestionsContent').innerHTML = finalHtml;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Filter buttons
    document.querySelectorAll('.evaluations-card .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentFilter = btn.dataset.filter;

            // Update active state
            document.querySelectorAll('.evaluations-card .filter-btn').forEach(b => {
                b.classList.toggle('active', b === btn);
            });

            // Reset display count and re-render
            displayedEvaluations = 10;
            renderEvaluations();
        });
    });

    // Show more button
    document.getElementById('showMoreBtn').addEventListener('click', () => {
        displayedEvaluations += 10;
        renderEvaluations();
    });
}

/**
 * Escape HTML
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
