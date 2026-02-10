/**
 * Common utilities for Mentor Evaluation System
 */

// API endpoints
const API = {
    METADATA: 'data/metadata.json',
    SCHOOLS: 'data/schools.json',
    MENTORS_BY_SCHOOL: 'data/mentors_by_school.json',
    getMentorDetail: (mentorId) => `data/mentors/${mentorId}.json`
};

// Cache for loaded data
const DataCache = {
    metadata: null,
    schools: null,
    mentorsBySchool: null
};

/**
 * Fetch JSON data with error handling
 */
async function fetchJSON(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${url}:`, error);
        throw error;
    }
}

/**
 * Load metadata
 */
async function loadMetadata() {
    if (DataCache.metadata) {
        return DataCache.metadata;
    }
    DataCache.metadata = await fetchJSON(API.METADATA);
    return DataCache.metadata;
}

/**
 * Load schools data
 */
async function loadSchools() {
    if (DataCache.schools) {
        return DataCache.schools;
    }
    DataCache.schools = await fetchJSON(API.SCHOOLS);
    return DataCache.schools;
}

/**
 * Load mentors by school
 */
async function loadMentorsBySchool() {
    if (DataCache.mentorsBySchool) {
        return DataCache.mentorsBySchool;
    }
    DataCache.mentorsBySchool = await fetchJSON(API.MENTORS_BY_SCHOOL);
    return DataCache.mentorsBySchool;
}

/**
 * Load individual mentor detail
 */
async function loadMentorDetail(mentorId) {
    return await fetchJSON(API.getMentorDetail(mentorId));
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toLocaleString('zh-CN');
}

/**
 * Format score to 1 decimal place
 */
function formatScore(score) {
    return score.toFixed(1);
}

/**
 * Get score color based on value
 */
function getScoreColor(score) {
    if (score >= 7) return '#34C759';  // Green
    if (score >= 5) return '#FF9500';  // Orange
    return '#FF3B30';  // Red
}

/**
 * Get score label based on value
 */
function getScoreLabel(score) {
    if (score >= 8) return '优秀';
    if (score >= 7) return '良好';
    if (score >= 5) return '一般';
    if (score >= 3) return '较差';
    return '很差';
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Get URL parameter
 */
function getURLParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

/**
 * Set URL parameter without reload
 */
function setURLParameter(name, value) {
    const url = new URL(window.location);
    url.searchParams.set(name, value);
    window.history.pushState({}, '', url);
}

/**
 * Show error message
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #FF3B30;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => errorDiv.remove(), 300);
    }, 3000);
}

/**
 * Show loading state
 */
function showLoading(element) {
    element.innerHTML = '<div class="loading">加载中...</div>';
}

/**
 * Animation helper
 */
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';

    let start = null;
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;

        element.style.opacity = Math.min(progress / duration, 1);

        if (progress < duration) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
