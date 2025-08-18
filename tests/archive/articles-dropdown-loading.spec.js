const { test, expect } = require('@playwright/test');

test.describe('Articles Dropdown Loading Bar Investigation', () => {
  test('should investigate loading bar behavior when clicking articles dropdown', async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot before clicking
    await page.screenshot({ path: 'tests/screenshots/before-dropdown-click.png' });
    
    // Look for the articles dropdown toggle button
    const articlesDropdown = page.locator('a.nav-link.dropdown-toggle[href*="articles"]');
    await expect(articlesDropdown).toBeVisible();
    
    // Check if there's already a page transition element
    const existingPageTransition = page.locator('.page-transition');
    const hasPageTransition = await existingPageTransition.count();
    console.log(`Page transition elements found: ${hasPageTransition}`);
    
    // Set up listeners for any loading indicators
    const loadingBarPromise = page.waitForSelector('.page-transition.loading', { timeout: 2000 }).catch(() => null);
    const loadingOverlayPromise = page.waitForSelector('.loading-overlay', { timeout: 2000 }).catch(() => null);
    
    // Click the articles dropdown toggle
    await articlesDropdown.click();
    
    // Wait a moment to see if loading appears
    await page.waitForTimeout(100);
    
    // Take screenshot right after click
    await page.screenshot({ path: 'tests/screenshots/after-dropdown-click.png' });
    
    // Check if loading bar appeared
    const loadingBar = await loadingBarPromise;
    const loadingOverlay = await loadingOverlayPromise;
    
    if (loadingBar) {
      console.log('✓ Loading bar (.page-transition.loading) appeared');
      await page.screenshot({ path: 'tests/screenshots/loading-bar-visible.png' });
      
      // Get the loading bar styles
      const styles = await page.evaluate(() => {
        const element = document.querySelector('.page-transition.loading');
        if (element) {
          const computed = getComputedStyle(element);
          return {
            position: computed.position,
            top: computed.top,
            left: computed.left,
            width: computed.width,
            height: computed.height,
            background: computed.background,
            zIndex: computed.zIndex,
            transform: computed.transform,
            transformOrigin: computed.transformOrigin
          };
        }
        return null;
      });
      console.log('Loading bar styles:', styles);
    } else {
      console.log('✗ No loading bar (.page-transition.loading) appeared');
    }
    
    if (loadingOverlay) {
      console.log('✓ Loading overlay appeared');
    } else {
      console.log('✗ No loading overlay appeared');
    }
    
    // Wait for dropdown to open
    await page.waitForSelector('.dropdown-menu.show', { timeout: 2000 });
    
    // Take screenshot with dropdown open
    await page.screenshot({ path: 'tests/screenshots/dropdown-opened.png' });
    
    // Check if dropdown is properly opened
    const dropdown = page.locator('.dropdown-menu.show');
    await expect(dropdown).toBeVisible();
    
    // Look for any elements inside the dropdown that might trigger loading
    const dropdownLinks = page.locator('.dropdown-menu.show a');
    const linkCount = await dropdownLinks.count();
    console.log(`Dropdown contains ${linkCount} links`);
    
    // Test clicking on a dropdown link to see if it triggers loading
    if (linkCount > 0) {
      const firstLink = dropdownLinks.first();
      const href = await firstLink.getAttribute('href');
      console.log(`Testing click on first dropdown link: ${href}`);
      
      // Set up loading detection again
      const linkLoadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 2000 }).catch(() => null);
      
      // Click the first dropdown link
      await firstLink.click();
      
      // Check if loading appeared
      const linkLoading = await linkLoadingPromise;
      if (linkLoading) {
        console.log('✓ Loading bar appeared when clicking dropdown link');
        await page.screenshot({ path: 'tests/screenshots/dropdown-link-loading.png' });
      } else {
        console.log('✗ No loading bar when clicking dropdown link');
      }
    }
    
    // Analyze the JavaScript functions responsible for loading
    const jsAnalysis = await page.evaluate(() => {
      const results = {
        hasAddPageTransition: typeof addPageTransition === 'function',
        hasPageTransitionElement: !!document.querySelector('.page-transition'),
        internalLinksCount: document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]').length,
        dropdownLinksWithListeners: 0
      };
      
      // Check if dropdown links have click listeners
      const dropdownLinks = document.querySelectorAll('.dropdown-menu a');
      dropdownLinks.forEach(link => {
        const listeners = getEventListeners ? getEventListeners(link) : null;
        if (listeners && listeners.click && listeners.click.length > 0) {
          results.dropdownLinksWithListeners++;
        }
      });
      
      return results;
    });
    
    console.log('JavaScript analysis:', jsAnalysis);
    
    // Final screenshot
    await page.screenshot({ path: 'tests/screenshots/final-state.png' });
  });
  
  test('should analyze page transition element creation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Execute the JavaScript analysis
    const analysis = await page.evaluate(() => {
      // Check if addPageTransition function exists and what it does
      if (typeof addPageTransition === 'function') {
        // Let's see the function source
        const functionSource = addPageTransition.toString();
        
        // Check for existing page transition element
        const existingTransition = document.querySelector('.page-transition');
        
        // Check how many internal links exist
        const internalLinks = document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]');
        
        return {
          hasFunction: true,
          functionSource: functionSource,
          hasExistingTransition: !!existingTransition,
          internalLinksCount: internalLinks.length,
          articlesDropdownExists: !!document.querySelector('a.nav-link.dropdown-toggle[href*="articles"]'),
          articlesDropdownIsInternal: true // since it's href="/articles"
        };
      }
      
      return { hasFunction: false };
    });
    
    console.log('Page transition analysis:', JSON.stringify(analysis, null, 2));
    
    expect(analysis.hasFunction).toBe(true);
    expect(analysis.articlesDropdownExists).toBe(true);
  });
});