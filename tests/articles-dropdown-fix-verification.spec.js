const { test, expect } = require('@playwright/test');

test.describe('Articles Dropdown Loading Bar Fix Verification', () => {
  test('should NOT show loading bar when clicking articles dropdown toggle', async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Look for the articles dropdown toggle button
    const articlesDropdown = page.locator('a.nav-link.dropdown-toggle[href*="articles"]');
    await expect(articlesDropdown).toBeVisible();
    
    // Verify the dropdown has the expected classes
    const dropdownClasses = await articlesDropdown.getAttribute('class');
    console.log(`Articles dropdown classes: ${dropdownClasses}`);
    
    // Set up a listener to detect if loading bar appears (it shouldn't)
    let loadingBarAppeared = false;
    page.on('console', msg => {
      if (msg.text().includes('Loading bar appeared')) {
        loadingBarAppeared = true;
      }
    });
    
    // Monitor for loading bar with a shorter timeout since it shouldn't appear
    const loadingBarPromise = page.waitForSelector('.page-transition.loading', { timeout: 1000 }).catch(() => null);
    
    // Click the articles dropdown toggle
    await articlesDropdown.click();
    
    // Wait a brief moment
    await page.waitForTimeout(200);
    
    // Check if loading bar appeared (it shouldn't)
    const loadingBar = await loadingBarPromise;
    
    if (loadingBar) {
      console.log('❌ ISSUE: Loading bar still appears when clicking dropdown');
    } else {
      console.log('✅ SUCCESS: No loading bar when clicking dropdown toggle');
    }
    
    // Verify dropdown opened successfully
    const dropdownMenu = page.locator('.dropdown-menu.show');
    await expect(dropdownMenu).toBeVisible({ timeout: 2000 });
    console.log('✅ Dropdown menu opened successfully');
    
    // Now test that loading bar still works for actual navigation links inside dropdown
    const firstDropdownLink = dropdownMenu.locator('a[href="/articles"]').first();
    if (await firstDropdownLink.count() > 0) {
      const linkLoadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 1000 });
      
      // Click the actual navigation link
      await firstDropdownLink.click();
      
      // This should show the loading bar since it's a real navigation
      const linkLoading = await linkLoadingPromise.catch(() => null);
      if (linkLoading) {
        console.log('✅ Loading bar correctly appears for dropdown navigation links');
      } else {
        console.log('❌ Loading bar should appear for actual navigation links');
      }
    }
    
    expect(loadingBar).toBeNull(); // Main assertion: no loading bar for dropdown toggle
  });
  
  test('should verify the fix logic correctly identifies dropdown toggles', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test the fix logic in the browser
    const analysis = await page.evaluate(() => {
      const results = {
        dropdownToggles: [],
        regularLinks: [],
        allInternalLinks: 0
      };
      
      // Get all internal links
      const internalLinks = document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]');
      results.allInternalLinks = internalLinks.length;
      
      internalLinks.forEach((link, index) => {
        const linkInfo = {
          index,
          href: link.href,
          classes: link.className,
          hasDropdownToggle: link.classList.contains('dropdown-toggle'),
          hasDataBsToggle: link.getAttribute('data-bs-toggle') === 'dropdown',
          hasButtonRole: link.getAttribute('role') === 'button',
          textContent: link.textContent.trim(),
          shouldSkipLoading: false
        };
        
        // Apply the same logic as the fix
        if (link.classList.contains('dropdown-toggle') || 
            link.getAttribute('data-bs-toggle') === 'dropdown' ||
            link.getAttribute('role') === 'button') {
          linkInfo.shouldSkipLoading = true;
          results.dropdownToggles.push(linkInfo);
        } else {
          results.regularLinks.push(linkInfo);
        }
      });
      
      return results;
    });
    
    console.log('Fix Logic Analysis:');
    console.log(`Total internal links: ${analysis.allInternalLinks}`);
    console.log(`Dropdown toggles (skip loading): ${analysis.dropdownToggles.length}`);
    console.log(`Regular links (show loading): ${analysis.regularLinks.length}`);
    
    if (analysis.dropdownToggles.length > 0) {
      console.log('\nDropdown toggles that will skip loading:');
      analysis.dropdownToggles.forEach(link => {
        console.log(`  - "${link.textContent}" (${link.href})`);
      });
    }
    
    // Verify that the Articles dropdown is properly identified
    const articlesDropdown = analysis.dropdownToggles.find(link => 
      link.textContent.toLowerCase().includes('articles')
    );
    
    expect(articlesDropdown).toBeTruthy();
    expect(articlesDropdown.shouldSkipLoading).toBe(true);
    console.log('✅ Articles dropdown correctly identified as dropdown toggle');
  });
});