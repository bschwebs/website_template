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