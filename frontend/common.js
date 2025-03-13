// 共通JavaScript機能

// スクロールアニメーション
document.addEventListener('DOMContentLoaded', function() {
    // スクロール時の要素表示アニメーション
    const scrollRevealElements = document.querySelectorAll('.scroll-reveal');
    
    function checkScroll() {
        scrollRevealElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight * 0.85) {
                element.classList.add('revealed');
            }
        });
    }
    
    // 初期チェック
    checkScroll();
    
    // スクロール時にチェック
    window.addEventListener('scroll', checkScroll);
    
    // 言語切替機能
    const languageSelector = document.querySelector('select');
    if (languageSelector) {
        languageSelector.addEventListener('change', function() {
            const lang = this.value;
            // 言語に応じたURLにリダイレクト
            if (lang === 'ja') {
                // 現在のページ
            } else if (lang === 'en') {
                window.location.href = window.location.pathname.replace('.html', '.en.html');
            } else if (lang === 'zh') {
                window.location.href = window.location.pathname.replace('.html', '.zh-CN.html');
            } else if (lang === 'ko') {
                window.location.href = window.location.pathname.replace('.html', '.ko.html');
            }
        });
    }
    
    // スムーズスクロール
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // ヘッダーの高さを考慮
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // モバイルメニュー
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('nav ul');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
});

// ダークモード切替
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    
    // 設定を保存
    const isDarkMode = !document.body.classList.contains('light-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// ダークモード設定の読み込み
function loadDarkModePreference() {
    const savedDarkMode = localStorage.getItem('darkMode');
    
    if (savedDarkMode === 'false') {
        document.body.classList.add('light-mode');
    }
}

// ページ読み込み時にダークモード設定を適用
loadDarkModePreference();