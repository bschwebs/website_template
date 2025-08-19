/**
 * Main JavaScript functionality for Japan's History blog
 * Handles social sharing and clipboard operations
 */

/**
 * Copy text to clipboard with visual feedback
 * @param {string} url - The URL to copy to clipboard
 * @param {HTMLElement} button - The button element that triggered the copy
 */
function copyToClipboard(url, button) {
    // Try modern clipboard API first
    navigator.clipboard.writeText(url).then(function() {
        updateButtonSuccess(button);
    }).catch(function(err) {
        console.error('Failed to copy with clipboard API: ', err);
        // Fallback for older browsers
        fallbackCopyToClipboard(url, button);
    });
}

/**
 * Update button appearance for successful copy operation
 * @param {HTMLElement} button - The button to update
 */
function updateButtonSuccess(button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
    button.classList.remove('btn-outline-secondary');
    button.classList.add('btn-success');
    
    // Reset after 2 seconds
    setTimeout(function() {
        button.innerHTML = originalHTML;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-secondary');
    }, 2000);
}

/**
 * Fallback copy method for older browsers
 * @param {string} url - The URL to copy
 * @param {HTMLElement} button - The button element
 */
function fallbackCopyToClipboard(url, button) {
    const textArea = document.createElement('textarea');
    textArea.value = url;
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
        updateButtonSuccess(button);
    } catch (err) {
        console.error('Fallback copy failed: ', err);
    }
    
    document.body.removeChild(textArea);
}

/**
 * Initialize loading animations and intersection observers
 */
function initializeLoadingAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                // Stop observing once animated
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.observe-fade, .observe-slide-left, .observe-slide-right');
    animatedElements.forEach((el) => observer.observe(el));
}

/**
 * Add staggered animation classes to grid items
 */
function addStaggeredAnimations() {
    const gridItems = document.querySelectorAll('.post-card, .card');
    gridItems.forEach((item, index) => {
        if (index < 6) {
            item.classList.add(`stagger-${index + 1}`, 'fade-in');
        }
    });
}

/**
 * Create skeleton loading placeholders
 */
function createSkeletonLoader(container, count = 6) {
    container.innerHTML = '';
    
    for (let i = 0; i < count; i++) {
        const skeletonCard = document.createElement('div');
        skeletonCard.className = 'col-md-6 col-lg-4';
        skeletonCard.innerHTML = `
            <div class="skeleton-card">
                <div class="skeleton-image"></div>
                <div class="skeleton-content">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-text"></div>
                    <div class="skeleton-text"></div>
                    <div class="skeleton-text"></div>
                    <div class="skeleton-button"></div>
                </div>
            </div>
        `;
        container.appendChild(skeletonCard);
    }
}

/**
 * Simulate loading and reveal content
 */
function simulateContentLoading() {
    const contentContainers = document.querySelectorAll('.content-container');
    
    contentContainers.forEach((container, index) => {
        setTimeout(() => {
            container.classList.add('loaded');
        }, 100 * (index + 1));
    });
}

/**
 * Enhanced image loading with fade-in effect
 */
function enhanceImageLoading() {
    const images = document.querySelectorAll('img[data-src], img:not([data-loaded])');
    
    images.forEach((img) => {
        if (img.complete) {
            img.classList.add('image-loaded');
            img.setAttribute('data-loaded', 'true');
        } else {
            img.addEventListener('load', () => {
                img.classList.add('image-loaded');
                img.setAttribute('data-loaded', 'true');
            });
        }
    });
}

/**
 * Add search loading animation
 */
function addSearchLoading() {
    const searchForm = document.querySelector('form[action*="search"]');
    const searchInput = searchForm?.querySelector('input[name="query"]');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchInput.classList.add('search-loading');
            
            searchTimeout = setTimeout(() => {
                searchInput.classList.remove('search-loading');
            }, 1000);
        });
    }
}

/**
 * Page transition animation
 */
function addPageTransition() {
    // Create page transition element
    const pageTransition = document.createElement('div');
    pageTransition.className = 'page-transition';
    document.body.appendChild(pageTransition);
    
    // Add loading animation to internal links
    const internalLinks = document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]');
    
    internalLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            // Skip if it's a download link or external
            if (link.download || link.target === '_blank') return;
            
            // Skip if it's a dropdown toggle (has dropdown-toggle class or data-bs-toggle attribute)
            if (link.classList.contains('dropdown-toggle') || 
                link.getAttribute('data-bs-toggle') === 'dropdown' ||
                link.getAttribute('role') === 'button') return;
            
            pageTransition.classList.add('loading');
            
            // Remove loading class after navigation
            setTimeout(() => {
                pageTransition.classList.remove('loading');
            }, 500);
        });
    });
}

/**
 * Enhanced post card hover effects
 */
function enhancePostCards() {
    const postCards = document.querySelectorAll('.post-card');
    
    postCards.forEach((card) => {
        card.classList.add('post-card-enhanced');
        
        // Add enhanced hover effects
        card.addEventListener('mouseenter', () => {
            card.style.zIndex = '2';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.zIndex = '1';
        });
    });
}

/**
 * Loading state management
 */
class LoadingManager {
    constructor() {
        this.loadingStates = new Set();
    }
    
    show(id) {
        this.loadingStates.add(id);
        this.updateUI();
    }
    
    hide(id) {
        this.loadingStates.delete(id);
        this.updateUI();
    }
    
    updateUI() {
        const isLoading = this.loadingStates.size > 0;
        document.body.classList.toggle('loading', isLoading);
    }
    
    showSpinner(element) {
        if (!element.querySelector('.loading-spinner-small')) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner-small';
            element.prepend(spinner);
        }
    }
    
    hideSpinner(element) {
        const spinner = element.querySelector('.loading-spinner-small');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Global loading manager
const loadingManager = new LoadingManager();

/**
 * Enhanced Card Layout System
 */
class CardLayoutManager {
    constructor() {
        this.categoryColors = {
            'history': 'category-history',
            'culture': 'category-culture', 
            'art': 'category-art',
            'politics': 'category-politics',
            'society': 'category-society',
            'technology': 'category-technology'
        };
    }
    
    /**
     * Calculate reading time for content
     */
    calculateReadingTime(content) {
        const wordsPerMinute = 200;
        const words = content.trim().split(/\s+/).length;
        const minutes = Math.ceil(words / wordsPerMinute);
        return minutes;
    }
    
    /**
     * Get category color class
     */
    getCategoryColorClass(categoryName) {
        const normalizedName = categoryName.toLowerCase().replace(/\s+/g, '');
        return this.categoryColors[normalizedName] || 'category-default';
    }
    
    /**
     * Create enhanced card element
     */
    createEnhancedCard(post) {
        const readingTime = this.calculateReadingTime(post.content || post.excerpt || '');
        const categoryClass = this.getCategoryColorClass(post.category || 'default');
        
        return `
            <div class="post-card-dynamic observe-fade" data-post-id="${post.id}">
                <div class="card-image">
                    ${post.image_filename ? 
                        `<img src="/static/uploads/${post.image_filename}" alt="${post.title}" loading="lazy">` :
                        '<div class="card-gradient-overlay"></div>'
                    }
                    <div class="category-badge ${categoryClass}">
                        ${post.category || 'Article'}
                    </div>
                    <div class="reading-time">
                        <i class="fas fa-clock"></i> ${readingTime} min
                    </div>
                </div>
                
                <div class="card-content-enhanced">
                    <h3 class="card-title-enhanced">${post.title}</h3>
                    <p class="card-excerpt">${post.excerpt || this.truncateContent(post.content, 120)}</p>
                    
                    ${post.tags && post.tags.length > 0 ? `
                        <div class="card-tags">
                            ${post.tags.slice(0, 3).map(tag => 
                                `<span class="card-tag">${tag}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="card-meta">
                        <span class="card-date">
                            <i class="fas fa-calendar"></i> ${this.formatDate(post.created_at)}
                        </span>
                    </div>
                </div>
                
                <div class="card-actions">
                    <a href="/posts/${post.slug || post.id}" class="action-btn action-btn-primary">
                        <i class="fas fa-arrow-right"></i> Read Article
                    </a>
                    <button class="action-btn" onclick="sharePost('${post.title}', '/posts/${post.slug || post.id}')">
                        <i class="fas fa-share"></i> Share
                    </button>
                    <button class="action-btn" onclick="toggleBookmark(${post.id})">
                        <i class="far fa-bookmark"></i> Save
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Truncate content with smart word boundaries
     */
    truncateContent(content, maxLength) {
        if (!content || content.length <= maxLength) return content || '';
        
        const truncated = content.substring(0, maxLength);
        const lastSpace = truncated.lastIndexOf(' ');
        return (lastSpace > 0 ? truncated.substring(0, lastSpace) : truncated) + '...';
    }
    
    /**
     * Format date for display
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    }
    
    /**
     * Initialize enhanced grid layout
     */
    initializeEnhancedGrid() {
        const gridContainers = document.querySelectorAll('#posts-grid, #articles-grid');
        
        gridContainers.forEach(container => {
            container.classList.add('posts-grid-enhanced');
            this.addCardVariations(container);
        });
    }
    
    /**
     * Add size variations to cards for visual interest (disabled for consistent sizing)
     */
    addCardVariations(container) {
        // Disabled for consistent card sizing
        // All cards will now have the same height
        return;
        
        /* const cards = container.querySelectorAll('.post-card-dynamic');
        const variations = ['card-size-small', 'card-size-medium', 'card-size-large'];
        
        cards.forEach((card, index) => {
            // Add size variation based on content length and position
            const contentLength = card.querySelector('.card-excerpt')?.textContent.length || 0;
            let sizeClass;
            
            if (index % 7 === 0) {
                sizeClass = 'card-size-xl';
            } else if (contentLength > 150) {
                sizeClass = 'card-size-large';
            } else if (contentLength > 100) {
                sizeClass = 'card-size-medium';
            } else {
                sizeClass = 'card-size-small';
            }
            
            card.classList.add(sizeClass);
        }); */
    }
    
    /**
     * Create skeleton cards for loading states
     */
    createSkeletonCards(container, count = 6) {
        const skeletonHTML = Array.from({length: count}, (_, i) => `
            <div class="card-skeleton-enhanced observe-fade stagger-${(i % 6) + 1}">
                <div class="skeleton-image"></div>
                <div class="skeleton-content">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-lines">
                        <div class="skeleton-line"></div>
                        <div class="skeleton-line"></div>
                        <div class="skeleton-line"></div>
                    </div>
                    <div class="skeleton-meta"></div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = skeletonHTML;
        container.classList.add('posts-grid-enhanced');
    }
}

// Global card layout manager
const cardLayoutManager = new CardLayoutManager();

/**
 * Seamless Pagination Manager
 * Handles AJAX pagination without page refreshes
 */
class PaginationManager {
    constructor() {
        this.isLoading = false;
        this.currentPage = 1;
        this.totalPages = 1;
        this.baseUrl = window.location.pathname;
        this.postsContainer = null;
        this.paginationInfo = null;
        this.paginationButtons = null;
        
        this.init();
    }
    
    init() {
        // Find pagination elements on page load
        this.postsContainer = document.getElementById('posts-grid');
        this.paginationInfo = document.querySelector('.d-flex.align-items-center .text-muted');
        this.paginationButtons = document.querySelector('.btn-group[role="group"]');
        
        if (!this.postsContainer) return;
        
        // Get initial page info from pagination display
        this.extractCurrentPageInfo();
        
        // Initialize pagination event listeners
        this.initializePaginationListeners();
    }
    
    extractCurrentPageInfo() {
        if (this.paginationInfo) {
            const pageText = this.paginationInfo.textContent;
            const match = pageText.match(/Page (\d+) of (\d+)/);
            if (match) {
                this.currentPage = parseInt(match[1]);
                this.totalPages = parseInt(match[2]);
            }
        }
    }
    
    initializePaginationListeners() {
        if (!this.paginationButtons) return;
        
        // Get all pagination links
        const paginationLinks = this.paginationButtons.querySelectorAll('a[href*="page="]');
        
        paginationLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                if (this.isLoading) return;
                
                const url = new URL(link.href);
                const newPage = parseInt(url.searchParams.get('page'));
                
                if (newPage && newPage !== this.currentPage) {
                    this.loadPage(newPage);
                }
            });
        });
    }
    
    async loadPage(pageNumber) {
        if (this.isLoading || pageNumber < 1 || pageNumber > this.totalPages) return;
        
        this.isLoading = true;
        
        try {
            // Show loading state
            this.showLoadingState();
            
            // Fetch new content
            const url = new URL(window.location);
            url.searchParams.set('page', pageNumber);
            
            // Preserve per_page parameter if responsive pagination is active
            if (window.responsivePaginationManager) {
                const currentPerPage = window.responsivePaginationManager.currentPerPage;
                url.searchParams.set('per_page', currentPerPage);
            }
            
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error('Failed to fetch page');
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract new posts content
            const newPostsGrid = doc.getElementById('posts-grid');
            const newPaginationInfo = doc.querySelector('.d-flex.align-items-center .text-muted');
            const newPaginationButtons = doc.querySelector('.btn-group[role="group"]');
            
            if (newPostsGrid) {
                // Smooth transition
                await this.transitionToNewContent(newPostsGrid.innerHTML);
                
                // Update pagination controls
                this.updatePaginationControls(newPaginationInfo, newPaginationButtons, pageNumber);
                
                // Update browser URL without reload
                window.history.pushState(
                    { page: pageNumber }, 
                    '', 
                    url.toString()
                );
                
                // Re-initialize animations for new content
                this.reinitializeAnimations();
            }
            
        } catch (error) {
            console.error('Pagination error:', error);
            // Fallback to traditional navigation  
            window.location.href = url;
        } finally {
            this.isLoading = false;
        }
    }
    
    showLoadingState() {
        if (!this.postsContainer) return;
        
        // Add loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'pagination-loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading new articles...</p>
            </div>
        `;
        
        this.postsContainer.style.position = 'relative';
        this.postsContainer.appendChild(loadingOverlay);
        
        // Disable pagination buttons
        if (this.paginationButtons) {
            this.paginationButtons.querySelectorAll('a, button').forEach(btn => {
                btn.style.pointerEvents = 'none';
                btn.style.opacity = '0.6';
            });
        }
    }
    
    async transitionToNewContent(newHTML) {
        if (!this.postsContainer) return;
        
        // Fade out current content
        this.postsContainer.style.transition = 'opacity 0.3s ease';
        this.postsContainer.style.opacity = '0';
        
        // Wait for fade out
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Update content
        this.postsContainer.innerHTML = newHTML;
        
        // Remove loading overlay if it exists
        const loadingOverlay = this.postsContainer.querySelector('.pagination-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
        
        // Fade in new content
        this.postsContainer.style.opacity = '1';
        
        // Reset container styles
        setTimeout(() => {
            this.postsContainer.style.transition = '';
            this.postsContainer.style.position = '';
        }, 300);
    }
    
    updatePaginationControls(newPaginationInfo, newPaginationButtons, newPage) {
        this.currentPage = newPage;
        
        // Update pagination info text
        if (this.paginationInfo && newPaginationInfo) {
            this.paginationInfo.textContent = newPaginationInfo.textContent;
        }
        
        // Update pagination buttons
        if (this.paginationButtons && newPaginationButtons) {
            this.paginationButtons.innerHTML = newPaginationButtons.innerHTML;
            
            // Re-enable buttons
            this.paginationButtons.querySelectorAll('a, button').forEach(btn => {
                btn.style.pointerEvents = '';
                btn.style.opacity = '';
            });
            
            // Re-attach event listeners
            this.initializePaginationListeners();
        }
    }
    
    reinitializeAnimations() {
        // Re-run intersection observer for new elements
        const newAnimatedElements = this.postsContainer.querySelectorAll('.observe-fade, .observe-slide-left, .observe-slide-right');
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        newAnimatedElements.forEach((el) => observer.observe(el));
        
        // Enhance new post cards
        if (typeof enhancePostCards === 'function') {
            enhancePostCards();
        }
    }
}

// Initialize pagination manager
let paginationManager;

/**
 * Share post functionality
 */
function sharePost(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: window.location.origin + url
        });
    } else {
        // Fallback to clipboard
        navigator.clipboard.writeText(window.location.origin + url).then(() => {
            showToast('Link copied to clipboard!');
        });
    }
}

/**
 * Toggle bookmark functionality
 */
function toggleBookmark(postId) {
    const bookmarks = JSON.parse(localStorage.getItem('bookmarks') || '[]');
    const isBookmarked = bookmarks.includes(postId);
    
    if (isBookmarked) {
        const index = bookmarks.indexOf(postId);
        bookmarks.splice(index, 1);
        showToast('Removed from bookmarks');
    } else {
        bookmarks.push(postId);
        showToast('Added to bookmarks');
    }
    
    localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
    updateBookmarkIcons();
}

/**
 * Update bookmark icons based on saved state
 */
function updateBookmarkIcons() {
    const bookmarks = JSON.parse(localStorage.getItem('bookmarks') || '[]');
    
    document.querySelectorAll('[onclick*="toggleBookmark"]').forEach(btn => {
        const postId = parseInt(btn.getAttribute('onclick').match(/\d+/)[0]);
        const icon = btn.querySelector('i');
        
        if (bookmarks.includes(postId)) {
            icon.className = 'fas fa-bookmark';
            btn.setAttribute('title', 'Remove from bookmarks');
        } else {
            icon.className = 'far fa-bookmark';
            btn.setAttribute('title', 'Add to bookmarks');
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message) {
    // Remove existing toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create new toast
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--accent-copper);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Initialize jumbotron shine effect
 */
function initializeJumbotronEffects() {
    const jumbotron = document.querySelector('.jumbotron');
    if (jumbotron) {
        jumbotron.classList.add('jumbotron-enhanced');
    }
}

/**
 * Lazy loading implementation for images
 */
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('image-loading');
                    img.classList.add('image-loaded');
                    imageObserver.unobserve(img);
                }
            });
        });

        const images = document.querySelectorAll('img[data-src]');
        images.forEach((img) => {
            img.classList.add('image-loading');
            imageObserver.observe(img);
        });
    }
}

/**
 * Responsive Pagination Manager
 * Automatically adjusts posts per page based on screen size
 */
class ResponsivePaginationManager {
    constructor() {
        this.currentPerPage = this.getOptimalPerPage();
        this.isHomePage = window.location.pathname === '/';
        
        this.init();
    }
    
    init() {
        if (!this.isHomePage) return;
        
        // Set initial per_page based on screen size
        this.adjustPaginationForScreenSize();
        
        // Listen for screen size changes
        window.addEventListener('resize', () => {
            this.handleScreenSizeChange();
        });
        
        // Handle initial page load with current screen size
        this.handleInitialLoad();
    }
    
    getOptimalPerPage() {
        const width = window.innerWidth;
        
        // Mobile: 1 column - show 2 cards (2 rows, clean stacking)
        if (width < 768) return 2;
        
        // Small tablet: 2 columns - show 2 cards (1 row, perfectly filled) 
        if (width >= 768 && width < 850) return 2;
        
        // Large tablet/Desktop: Can comfortably handle 3 cards with good spacing
        return 3;
    }
    
    adjustPaginationForScreenSize() {
        const optimalPerPage = this.getOptimalPerPage();
        
        if (optimalPerPage !== this.currentPerPage) {
            this.currentPerPage = optimalPerPage;
            this.updatePaginationIfNeeded();
        }
    }
    
    handleScreenSizeChange() {
        // Debounce resize events
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.adjustPaginationForScreenSize();
        }, 250);
    }
    
    handleInitialLoad() {
        // Check if we need to redirect with correct per_page parameter
        const urlParams = new URLSearchParams(window.location.search);
        const currentPerPage = parseInt(urlParams.get('per_page')) || 3;
        const optimalPerPage = this.getOptimalPerPage();
        
        // Redirect if per_page doesn't match optimal for current screen size
        if (currentPerPage !== optimalPerPage) {
            console.log(`Screen size requires per_page=${optimalPerPage}, but current is ${currentPerPage}. Redirecting...`);
            this.redirectWithPerPage(optimalPerPage);
        }
    }
    
    updatePaginationIfNeeded() {
        // Update pagination links if they exist
        const paginationLinks = document.querySelectorAll('a[href*="page="]');
        
        paginationLinks.forEach(link => {
            const url = new URL(link.href);
            url.searchParams.set('per_page', this.currentPerPage);
            link.href = url.toString();
        });
    }
    
    redirectWithPerPage(perPage) {
        const urlParams = new URLSearchParams(window.location.search);
        const currentPage = parseInt(urlParams.get('page')) || 1;
        
        // Calculate if we need to adjust the current page number
        const currentPerPage = parseInt(urlParams.get('per_page')) || 3;
        
        // If we're changing per_page, we might need to recalculate which page to show
        // For now, just go to page 1 with the new per_page to avoid complexity
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('per_page', perPage);
        
        // Only redirect to page 1 if we're not already there or per_page is different
        if (currentPage > 1 || currentPerPage !== perPage) {
            newUrl.searchParams.set('page', 1);
        }
        
        // Only redirect if URL actually changed
        if (newUrl.toString() !== window.location.toString()) {
            window.location.href = newUrl.toString();
        }
    }
    
    getCurrentBreakpoint() {
        const width = window.innerWidth;
        if (width < 768) return 'mobile';
        if (width < 1200) return 'medium';
        return 'desktop';
    }
}

// Global responsive pagination manager
let responsivePaginationManager;

/**
 * Instant Search Manager
 * Handles live search suggestions and quick results
 */
class InstantSearchManager {
    constructor() {
        this.searchInputs = [];
        this.suggestionDropdowns = [];
        this.debounceTimeout = null;
        this.currentRequest = null;
        this.isVisible = false;
        
        this.init();
    }
    
    init() {
        // Find all search inputs
        this.searchInputs = document.querySelectorAll('input[name="query"]');
        
        this.searchInputs.forEach((input, index) => {
            this.initializeSearchInput(input, index);
        });
    }
    
    initializeSearchInput(input, index) {
        // Create suggestion dropdown for this input
        const dropdown = this.createSuggestionDropdown(input, index);
        this.suggestionDropdowns[index] = dropdown;
        
        // Add event listeners
        input.addEventListener('input', (e) => {
            this.handleSearchInput(e, index);
        });
        
        input.addEventListener('focus', (e) => {
            const query = e.target.value.trim();
            if (query.length >= 2) {
                this.handleSearchInput(e, index);
            }
        });
        
        input.addEventListener('blur', (e) => {
            // Delay hiding to allow click on suggestions
            setTimeout(() => {
                this.hideSuggestions(index);
            }, 150);
        });
        
        // Handle keyboard navigation
        input.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e, index);
        });
    }
    
    createSuggestionDropdown(input, index) {
        const dropdown = document.createElement('div');
        dropdown.className = 'search-suggestions-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-height: 400px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;
        
        // Position relative to input
        const container = input.closest('.input-group') || input.parentElement;
        container.style.position = 'relative';
        container.appendChild(dropdown);
        
        return dropdown;
    }
    
    handleSearchInput(event, index) {
        const query = event.target.value.trim();
        
        // Clear previous timeout
        clearTimeout(this.debounceTimeout);
        
        if (query.length < 2) {
            this.hideSuggestions(index);
            return;
        }
        
        // Debounce the search
        this.debounceTimeout = setTimeout(() => {
            this.fetchSuggestions(query, index);
        }, 300);
    }
    
    async fetchSuggestions(query, index) {
        try {
            // Cancel previous request
            if (this.currentRequest) {
                this.currentRequest.abort();
            }
            
            // Create new request
            const controller = new AbortController();
            this.currentRequest = controller;
            
            const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`, {
                signal: controller.signal,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error('Failed to fetch suggestions');
            
            const data = await response.json();
            this.displaySuggestions(data.suggestions, index, query);
            
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Search suggestions error:', error);
            }
        }
    }
    
    displaySuggestions(suggestions, index, query) {
        const dropdown = this.suggestionDropdowns[index];
        if (!dropdown) return;
        
        if (suggestions.length === 0) {
            dropdown.innerHTML = `
                <div class="search-suggestion-item" style="padding: 12px; color: #666; text-align: center;">
                    No suggestions found
                </div>
            `;
        } else {
            dropdown.innerHTML = suggestions.map(suggestion => {
                const highlightedTitle = this.highlightMatch(suggestion.title, query);
                
                if (suggestion.type === 'post') {
                    return `
                        <div class="search-suggestion-item post-suggestion" data-url="${suggestion.url}" style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; align-items: center;">
                            <div style="flex: 1;">
                                <div style="font-weight: 500; color: #333; margin-bottom: 4px;">
                                    <i class="fas fa-file-alt" style="color: var(--accent-copper); margin-right: 6px;"></i>
                                    ${highlightedTitle}
                                </div>
                                ${suggestion.excerpt ? `<div style="font-size: 0.85rem; color: #666; line-height: 1.3;">${suggestion.excerpt}</div>` : ''}
                                ${suggestion.category ? `<div style="font-size: 0.75rem; color: var(--accent-copper); margin-top: 4px;">${suggestion.category}</div>` : ''}
                            </div>
                        </div>
                    `;
                } else {
                    return `
                        <div class="search-suggestion-item tag-suggestion" data-url="${suggestion.url}" style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; align-items: center;">
                            <div style="flex: 1;">
                                <div style="font-weight: 500; color: #333;">
                                    <i class="fas fa-tag" style="color: var(--accent-copper); margin-right: 6px;"></i>
                                    ${highlightedTitle}
                                </div>
                                <div style="font-size: 0.85rem; color: #666;">${suggestion.description}</div>
                            </div>
                        </div>
                    `;
                }
            }).join('');
        }
        
        // Add click handlers
        dropdown.querySelectorAll('.search-suggestion-item[data-url]').forEach(item => {
            item.addEventListener('click', () => {
                window.location.href = item.dataset.url;
            });
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = '#f8f9fa';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = '';
            });
        });
        
        this.showSuggestions(index);
    }
    
    highlightMatch(text, query) {
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark style="background: #fff3cd; padding: 1px 2px;">$1</mark>');
    }
    
    showSuggestions(index) {
        const dropdown = this.suggestionDropdowns[index];
        if (dropdown) {
            dropdown.style.display = 'block';
            this.isVisible = true;
        }
    }
    
    hideSuggestions(index) {
        const dropdown = this.suggestionDropdowns[index];
        if (dropdown) {
            dropdown.style.display = 'none';
            this.isVisible = false;
        }
    }
    
    handleKeyboardNavigation(event, index) {
        const dropdown = this.suggestionDropdowns[index];
        if (!dropdown || !this.isVisible) return;
        
        const items = dropdown.querySelectorAll('.search-suggestion-item[data-url]');
        if (items.length === 0) return;
        
        const currentActive = dropdown.querySelector('.search-suggestion-item.active');
        let newActiveIndex = -1;
        
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            newActiveIndex = currentActive ? Array.from(items).indexOf(currentActive) + 1 : 0;
            if (newActiveIndex >= items.length) newActiveIndex = 0;
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            newActiveIndex = currentActive ? Array.from(items).indexOf(currentActive) - 1 : items.length - 1;
            if (newActiveIndex < 0) newActiveIndex = items.length - 1;
        } else if (event.key === 'Enter' && currentActive) {
            event.preventDefault();
            window.location.href = currentActive.dataset.url;
            return;
        } else if (event.key === 'Escape') {
            this.hideSuggestions(index);
            return;
        }
        
        // Update active state
        items.forEach(item => item.classList.remove('active'));
        if (newActiveIndex >= 0 && items[newActiveIndex]) {
            items[newActiveIndex].classList.add('active');
            items[newActiveIndex].style.backgroundColor = '#e3f2fd';
        }
    }
}

// Global instant search manager
let instantSearchManager;

/**
 * Recently Viewed Posts Manager
 * Tracks and displays recently viewed posts using localStorage
 */
class RecentlyViewedManager {
    constructor() {
        this.storageKey = 'recentlyViewedPosts';
        this.maxItems = 5;
        this.sidebarSelector = '#recently-viewed-sidebar';
        this.init();
    }
    
    init() {
        // Track current post if we're on a post page
        this.trackCurrentPost();
        
        // Create and display sidebar
        this.createSidebar();
        this.updateSidebar();
    }
    
    trackCurrentPost() {
        // Check if we're on a post page (primary method)
        const postMeta = document.querySelector('meta[property="og:type"][content="article"]');
        let postData = null;
        
        if (postMeta) {
            // Get post information from meta tags
            const postTitle = document.querySelector('meta[property="og:title"]')?.content;
            const postUrl = document.querySelector('meta[property="og:url"]')?.content || window.location.href;
            const postImage = document.querySelector('meta[property="og:image"]')?.content;
            const postDescription = document.querySelector('meta[property="og:description"]')?.content;
            
            if (postTitle && postUrl) {
                postData = {
                    title: postTitle,
                    url: postUrl,
                    image: postImage,
                    description: postDescription,
                    viewedAt: new Date().toISOString(),
                    id: this.generatePostId(postUrl)
                };
            }
        } else {
            // Fallback method: detect post pages by URL pattern or page structure
            const isPostPage = window.location.pathname.match(/\/posts\/[^\/]+$/);
            if (isPostPage) {
                const pageTitle = document.title;
                const h1Element = document.querySelector('h1');
                const imgElement = document.querySelector('article img, .post-content img');
                const excerptElement = document.querySelector('.post-content p');
                
                if (pageTitle && h1Element) {
                    postData = {
                        title: h1Element.textContent.trim(),
                        url: window.location.href,
                        image: imgElement?.src,
                        description: excerptElement?.textContent.substring(0, 200),
                        viewedAt: new Date().toISOString(),
                        id: this.generatePostId(window.location.href)
                    };
                }
            }
        }
        
        if (postData) {
            this.addToRecentlyViewed(postData);
        }
    }
    
    generatePostId(url) {
        // Extract post ID from URL pattern /posts/123 or /posts/slug
        const matches = url.match(/\/posts\/([^\/\?]+)/);
        return matches ? matches[1] : url;
    }
    
    addToRecentlyViewed(postData) {
        let recentPosts = this.getRecentlyViewed();
        
        // Remove if already exists (to update position)
        recentPosts = recentPosts.filter(post => post.id !== postData.id);
        
        // Add to beginning
        recentPosts.unshift(postData);
        
        // Limit to max items
        recentPosts = recentPosts.slice(0, this.maxItems);
        
        // Save to localStorage
        localStorage.setItem(this.storageKey, JSON.stringify(recentPosts));
        
        // Update sidebar if it exists
        this.updateSidebar();
    }
    
    getRecentlyViewed() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error reading recently viewed posts:', error);
            return [];
        }
    }
    
    createSidebar() {
        // Check if sidebar already exists
        if (document.querySelector(this.sidebarSelector)) return;
        
        // Show sidebar on all non-admin pages
        const isAdminPage = window.location.pathname.startsWith('/admin');
        const isEditPage = window.location.pathname.includes('/edit') || window.location.pathname.includes('/create');
        
        // Don't show on admin pages or editing pages
        if (isAdminPage || isEditPage) return;
        
        // Create sidebar HTML
        const sidebarHtml = `
            <div id="recently-viewed-sidebar" class="recently-viewed-sidebar">
                <div class="sidebar-header">
                    <h5 class="sidebar-title">
                        <i class="fas fa-history"></i>
                        Recently Viewed
                    </h5>
                    <button class="sidebar-close" onclick="recentlyViewedManager.hideSidebar()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="sidebar-content" id="recently-viewed-content">
                    <!-- Content will be populated by updateSidebar() -->
                </div>
                <div class="sidebar-toggle" onclick="recentlyViewedManager.toggleSidebar()">
                    <i class="fas fa-history"></i>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.insertAdjacentHTML('beforeend', sidebarHtml);
        
        // Add entrance animation
        setTimeout(() => {
            const sidebar = document.querySelector(this.sidebarSelector);
            if (sidebar) {
                sidebar.style.transition = 'right 0.3s ease';
            }
        }, 100);
    }
    
    updateSidebar() {
        const sidebar = document.querySelector(this.sidebarSelector);
        const content = document.getElementById('recently-viewed-content');
        
        if (!sidebar || !content) return;
        
        const recentPosts = this.getRecentlyViewed();
        
        if (recentPosts.length === 0) {
            content.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-book-open"></i>
                    <p>No recent articles</p>
                </div>
            `;
            return;
        }
        
        content.innerHTML = recentPosts.map(post => `
            <div class="recent-post-item" onclick="window.location.href='${post.url}'">
                <div class="recent-post-image">
                    ${post.image ? 
                        `<img src="${post.image}" alt="${post.title}" loading="lazy">` :
                        `<div class="placeholder-image"><i class="fas fa-file-alt"></i></div>`
                    }
                </div>
                <div class="recent-post-content">
                    <h6 class="recent-post-title">${this.truncateText(post.title, 50)}</h6>
                    <p class="recent-post-time">${this.formatTime(post.viewedAt)}</p>
                </div>
            </div>
        `).join('');
    }
    
    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }
    
    toggleSidebar() {
        const sidebar = document.querySelector(this.sidebarSelector);
        if (sidebar) {
            sidebar.classList.toggle('sidebar-open');
        }
    }
    
    showSidebar() {
        const sidebar = document.querySelector(this.sidebarSelector);
        if (sidebar) {
            sidebar.classList.add('sidebar-open');
        }
    }
    
    hideSidebar() {
        const sidebar = document.querySelector(this.sidebarSelector);
        if (sidebar) {
            sidebar.classList.remove('sidebar-open');
        }
    }
    
    clearHistory() {
        localStorage.removeItem(this.storageKey);
        this.updateSidebar();
        showToast('Recently viewed history cleared');
    }
}

// Global recently viewed manager
let recentlyViewedManager;

// Initialize any additional functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Japan\'s History blog initialized with loading animations');
    
    // Initialize all loading animations and effects
    setTimeout(() => {
        initializeLoadingAnimations();
        addStaggeredAnimations();
        enhanceImageLoading();
        addSearchLoading();
        addPageTransition();
        enhancePostCards();
        
        // Initialize instant search
        instantSearchManager = new InstantSearchManager();
        
        // Initialize recently viewed posts
        recentlyViewedManager = new RecentlyViewedManager();
        
        // Initialize responsive pagination (handles screen size-based per_page)
        responsivePaginationManager = new ResponsivePaginationManager();
        window.responsivePaginationManager = responsivePaginationManager;
        
        // Initialize seamless pagination
        paginationManager = new PaginationManager();
        
        // Handle browser back/forward navigation
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.page && paginationManager) {
                paginationManager.loadPage(event.state.page);
            }
        });
        initializeJumbotronEffects();
        initializeLazyLoading();
        
        // Initialize enhanced card layout
        cardLayoutManager.initializeEnhancedGrid();
        updateBookmarkIcons();
        
        // Simulate content loading for demo
        simulateContentLoading();
    }, 100);
    
    // Add content containers class to main content areas
    const mainContent = document.querySelector('main .container');
    if (mainContent) {
        mainContent.classList.add('content-container');
    }
});