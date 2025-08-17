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

// Initialize any additional functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here if needed
    console.log('Japan\'s History blog initialized');
});