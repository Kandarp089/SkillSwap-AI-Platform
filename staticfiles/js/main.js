/* ==========================================================================
   SkillSwap AI - Interactive Core JavaScript Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSkillSearch();
    initCounterAnimations();
});

/* Theme Management */
function initTheme() {
    const savedTheme = localStorage.getItem('skillswap-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('skillswap-theme', newTheme);
    updateThemeIcon(newTheme);
    showToast(`Switched to ${newTheme} mode`, 'info');
}

function updateThemeIcon(theme) {
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.innerHTML = theme === 'dark' 
            ? '<i class="bi bi-sun-fill text-warning"></i>' 
            : '<i class="bi bi-moon-stars-fill text-primary"></i>';
    }
}

/* Toast Notifications */
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container-custom';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-custom toast-${type}`;
    
    let icon = 'bi-check-circle-fill text-success';
    if (type === 'info') icon = 'bi-info-circle-fill text-cyan';
    if (type === 'error') icon = 'bi-exclamation-triangle-fill text-danger';

    toast.innerHTML = `
        <i class="bi ${icon} fs-5"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/* Interactive AI Match Calculator Widget */
function calculateHomeAIMatch() {
    const offerSkill = document.getElementById('matchOfferSkill');
    const learnSkill = document.getElementById('matchLearnSkill');
    const resultBox = document.getElementById('aiMatchResult');
    const scoreText = document.getElementById('aiMatchScoreText');
    const progressBar = document.getElementById('aiMatchProgressBar');

    if (!offerSkill || !learnSkill || !resultBox) return;

    if (offerSkill.value === learnSkill.value) {
        showToast('Please select different skills to offer and learn!', 'error');
        return;
    }

    // Generate dynamic realistic score based on string hashes
    const hash = (offerSkill.value + learnSkill.value).length * 17;
    const score = 82 + (hash % 17); // 82% to 98%

    resultBox.classList.remove('d-none');
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    let currentScore = 0;
    const interval = setInterval(() => {
        currentScore += 2;
        if (currentScore >= score) {
            currentScore = score;
            clearInterval(interval);
        }
        scoreText.innerText = `${currentScore}%`;
        progressBar.style.width = `${currentScore}%`;
    }, 30);

    showToast(`AI Match computed: ${score}% Compatibility!`, 'success');
}

/* Live Skill Search Filter */
function initSkillSearch() {
    const searchInput = document.getElementById('skillSearchInput');
    if (!searchInput) return;

    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.skill-card-item');

        cards.forEach(card => {
            const title = card.getAttribute('data-skill-name')?.toLowerCase() || '';
            const category = card.getAttribute('data-skill-category')?.toLowerCase() || '';
            const teacher = card.getAttribute('data-teacher-name')?.toLowerCase() || '';

            if (title.includes(query) || category.includes(query) || teacher.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

function filterByCategory(category) {
    const cards = document.querySelectorAll('.skill-card-item');
    const pills = document.querySelectorAll('.category-pill-btn');

    pills.forEach(p => p.classList.remove('active', 'btn-neon-primary'));

    cards.forEach(card => {
        const cardCat = card.getAttribute('data-skill-category')?.toLowerCase() || '';
        if (category === 'all' || cardCat.includes(category.toLowerCase())) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/* Swap Request Modal Handler */
function openSwapModal(skillTitle, teacherName, username = '') {
    const modalTitle = document.getElementById('swapModalSkillTitle');
    const modalTeacher = document.getElementById('swapModalTeacher');
    const hiddenSkill = document.getElementById('hiddenRequestedSkill');
    const hiddenUsername = document.getElementById('hiddenReceiverUsername');
    const modalElement = document.getElementById('swapRequestModal');

    if (modalTitle) modalTitle.innerText = skillTitle;
    if (modalTeacher) modalTeacher.innerText = teacherName;
    if (hiddenSkill) hiddenSkill.value = skillTitle;
    if (hiddenUsername) hiddenUsername.value = username || teacherName;

    if (modalElement && window.bootstrap) {
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();
    } else {
        showToast(`Opening request form for ${teacherName}...`, 'info');
    }
}

/* Number Counter Animation */
function initCounterAnimations() {
    const counters = document.querySelectorAll('.stat-counter');
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        let count = 0;
        const speed = target / 50;
        const updateCount = () => {
            count += speed;
            if (count < target) {
                counter.innerText = Math.ceil(count).toLocaleString();
                setTimeout(updateCount, 30);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };
        updateCount();
    });
}
