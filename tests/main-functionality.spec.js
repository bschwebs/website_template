const { test, expect } = require('@playwright/test');

test.describe('Main Functionality Tests', () => {
  test('should have working dropdown navigation without loading bar', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test Articles dropdown
    const articlesDropdown = page.locator('a.dropdown-toggle[href*="articles"]');
    await expect(articlesDropdown).toBeVisible();
    
    // Check that no loading bar appears when clicking dropdown
    const loadingBarPromise = page.waitForSelector('.page-transition.loading', { timeout: 500 }).catch(() => null);
    await articlesDropdown.click();
    const loadingBar = await loadingBarPromise;
    
    expect(loadingBar).toBeNull(); // No loading bar should appear
    
    // Verify dropdown opens
    const dropdownMenu = page.locator('.dropdown-menu.show');
    await expect(dropdownMenu).toBeVisible();
  });
  
  test('should have responsive pagination working correctly', async ({ page }) => {
    // Test medium screens (2 cards)
    await page.setViewportSize({ width: 800, height: 800 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const mediumResult = await page.evaluate(() => {
      const urlParams = new URLSearchParams(window.location.search);
      const perPage = parseInt(urlParams.get('per_page')) || 3;
      const cards = document.querySelectorAll('.post-card-dynamic');
      return { perPage, cardCount: cards.length };
    });
    
    expect(mediumResult.perPage).toBe(2);
    
    // Test large screens (3 cards)
    await page.setViewportSize({ width: 1000, height: 800 });
    await page.waitForTimeout(500);
    
    const largeResult = await page.evaluate(() => {
      return window.responsivePaginationManager?.getOptimalPerPage();
    });
    
    expect(largeResult).toBe(3);
  });
  
  test('should have no card stacking issues', async ({ page }) => {
    const testWidths = [800, 900, 1000, 1200];
    
    for (const width of testWidths) {
      await page.setViewportSize({ width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      const layoutCheck = await page.evaluate(() => {
        const cards = document.querySelectorAll('.post-card-dynamic');
        if (cards.length === 0) return { isOptimal: true };
        
        const positions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: Math.round(rect.top) };
        });
        
        const rows = {};
        positions.forEach((pos, i) => {
          const row = Math.round(pos.top / 50);
          if (!rows[row]) rows[row] = [];
          rows[row].push(i);
        });
        
        const rowSizes = Object.values(rows).map(row => row.length);
        const isSingleRow = rowSizes.length === 1;
        
        return { isOptimal: isSingleRow, rowCount: rowSizes.length };
      });
      
      expect(layoutCheck.isOptimal).toBe(true);
    }
  });
});