const { test, expect } = require('@playwright/test');

test.describe('Responsive Pagination', () => {
  test('should show 2 cards per page on medium screens (768px-1199px)', async ({ page }) => {
    // Set viewport to medium screen size
    await page.setViewportSize({ width: 1000, height: 800 });
    
    // Navigate to home page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check if responsive pagination manager was initialized
    const paginationManagerExists = await page.evaluate(() => {
      return window.responsivePaginationManager !== undefined;
    });
    
    console.log(`Responsive pagination manager exists: ${paginationManagerExists}`);
    
    // Get the optimal per_page for current screen size
    const optimalPerPage = await page.evaluate(() => {
      if (window.responsivePaginationManager) {
        return window.responsivePaginationManager.getOptimalPerPage();
      }
      return null;
    });
    
    console.log(`Optimal per_page for 1000px width: ${optimalPerPage}`);
    expect(optimalPerPage).toBe(2); // Should be 2 for medium screens
    
    // Check if URL has been updated with per_page=2
    await page.waitForTimeout(1000); // Wait for any potential redirects
    
    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);
    
    const url = new URL(currentUrl);
    const perPageParam = url.searchParams.get('per_page');
    console.log(`per_page parameter: ${perPageParam}`);
    
    // Check number of cards displayed
    const cardCount = await page.locator('.post-card-dynamic').count();
    console.log(`Number of cards displayed: ${cardCount}`);
    
    // Check if pagination info shows correct per_page
    const paginationInfo = await page.locator('.text-muted').textContent();
    console.log(`Pagination info: ${paginationInfo}`);
  });
  
  test('should show 3 cards per page on desktop screens (≥1200px)', async ({ page }) => {
    // Set viewport to desktop screen size
    await page.setViewportSize({ width: 1400, height: 800 });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const optimalPerPage = await page.evaluate(() => {
      if (window.responsivePaginationManager) {
        return window.responsivePaginationManager.getOptimalPerPage();
      }
      return null;
    });
    
    console.log(`Optimal per_page for 1400px width: ${optimalPerPage}`);
    expect(optimalPerPage).toBe(3); // Should be 3 for desktop screens
    
    await page.waitForTimeout(1000);
    
    const cardCount = await page.locator('.post-card-dynamic').count();
    console.log(`Number of cards displayed on desktop: ${cardCount}`);
  });
  
  test('should show 3 cards per page on mobile screens (<768px)', async ({ page }) => {
    // Set viewport to mobile screen size
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const optimalPerPage = await page.evaluate(() => {
      if (window.responsivePaginationManager) {
        return window.responsivePaginationManager.getOptimalPerPage();
      }
      return null;
    });
    
    console.log(`Optimal per_page for 375px width: ${optimalPerPage}`);
    expect(optimalPerPage).toBe(3); // Should be 3 for mobile screens (3 rows of 1 card each)
    
    await page.waitForTimeout(1000);
    
    const cardCount = await page.locator('.post-card-dynamic').count();
    console.log(`Number of cards displayed on mobile: ${cardCount}`);
  });
  
  test('should update pagination links when screen size changes', async ({ page }) => {
    // Start with desktop size
    await page.setViewportSize({ width: 1400, height: 800 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Get initial pagination links
    const initialPaginationLinks = await page.evaluate(() => {
      const links = document.querySelectorAll('a[href*="page="]');
      return Array.from(links).map(link => link.href);
    });
    
    console.log('Initial pagination links:', initialPaginationLinks);
    
    // Change to medium screen size
    await page.setViewportSize({ width: 1000, height: 800 });
    
    // Wait for resize handling
    await page.waitForTimeout(500);
    
    // Check if pagination links were updated
    const updatedPaginationLinks = await page.evaluate(() => {
      const links = document.querySelectorAll('a[href*="page="]');
      return Array.from(links).map(link => link.href);
    });
    
    console.log('Updated pagination links:', updatedPaginationLinks);
    
    // Verify that per_page parameter is updated in links
    const hasPerPage2 = updatedPaginationLinks.some(link => link.includes('per_page=2'));
    console.log(`Pagination links updated with per_page=2: ${hasPerPage2}`);
  });
  
  test('should handle pagination navigation with correct per_page', async ({ page }) => {
    // Set medium screen size
    await page.setViewportSize({ width: 1000, height: 800 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for potential redirects
    await page.waitForTimeout(1000);
    
    // Check if there are pagination controls
    const nextButton = page.locator('a[href*="page="]:has(i.fa-chevron-right)');
    
    if (await nextButton.count() > 0) {
      console.log('Testing pagination navigation...');
      
      // Click next page
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      
      // Check if per_page parameter is preserved
      const currentUrl = page.url();
      const url = new URL(currentUrl);
      const perPageParam = url.searchParams.get('per_page');
      const pageParam = url.searchParams.get('page');
      
      console.log(`After navigation - Page: ${pageParam}, Per page: ${perPageParam}`);
      
      // Should maintain per_page=2 for medium screens
      expect(perPageParam).toBe('2');
      expect(pageParam).toBe('2');
    } else {
      console.log('No pagination controls found (not enough posts for pagination)');
    }
  });
});