const { test, expect } = require('@playwright/test');

test.describe('Card Stacking Fix Verification', () => {
  test('should eliminate stacking at problematic screen sizes', async ({ page }) => {
    // Test the exact problematic sizes identified in investigation
    const problematicSizes = [850, 900, 950, 1000, 1050, 1100, 1150];
    
    console.log('=== TESTING PREVIOUSLY PROBLEMATIC SIZES ===');
    
    for (const width of problematicSizes) {
      await page.setViewportSize({ width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Wait for any potential redirects due to responsive pagination
      await page.waitForTimeout(1500);
      
      const layoutInfo = await page.evaluate(() => {
        const grid = document.querySelector('.posts-grid-enhanced');
        const cards = document.querySelectorAll('.post-card-dynamic');
        
        if (!grid || cards.length === 0) return null;
        
        // Get current per_page setting
        const urlParams = new URLSearchParams(window.location.search);
        const perPage = urlParams.get('per_page');
        
        // Get optimal per_page from the manager
        const optimalPerPage = window.responsivePaginationManager ? 
          window.responsivePaginationManager.getOptimalPerPage() : null;
        
        // Analyze card positions
        const cardPositions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: Math.round(rect.top), left: Math.round(rect.left) };
        });
        
        // Group by rows
        const rows = {};
        cardPositions.forEach((pos, index) => {
          const roundedTop = Math.round(pos.top / 10) * 10;
          if (!rows[roundedTop]) rows[roundedTop] = [];
          rows[roundedTop].push(index);
        });
        
        const rowCount = Object.keys(rows).length;
        const maxCardsPerRow = Math.max(...Object.values(rows).map(row => row.length));
        const totalCards = cards.length;
        const layout = Object.values(rows).map(row => row.length).join(' + ');
        
        // Check if we have optimal layout (no stacking)
        const isOptimal = (maxCardsPerRow >= 2 && rowCount === 1) || // 2+ columns, single row
                         (maxCardsPerRow === 1 && totalCards <= 2);   // 1 column, max 2 cards
        
        return {
          perPage,
          optimalPerPage,
          totalCards,
          rowCount,
          maxCardsPerRow,
          layout,
          isOptimal
        };
      });
      
      if (layoutInfo) {
        const status = layoutInfo.isOptimal ? '✅ OPTIMAL' : '⚠️  STACKING';
        console.log(`${width}px: ${layoutInfo.maxCardsPerRow} cols, ${layoutInfo.rowCount} rows (${layoutInfo.layout}), per_page=${layoutInfo.perPage}, optimal=${layoutInfo.optimalPerPage} ${status}`);
        
        // Assert that we have optimal layout
        expect(layoutInfo.isOptimal).toBe(true);
        expect(layoutInfo.perPage).toBe(layoutInfo.optimalPerPage?.toString());
      }
    }
  });
  
  test('should verify perfect row filling at all breakpoints', async ({ page }) => {
    const testCases = [
      { width: 400, expectedCols: 1, expectedPerPage: 2, name: 'Mobile' },
      { width: 768, expectedCols: 2, expectedPerPage: 2, name: 'Tablet Start' },
      { width: 1000, expectedCols: 2, expectedPerPage: 2, name: 'Medium Tablet' },
      { width: 1199, expectedCols: 2, expectedPerPage: 2, name: 'Tablet End' },
      { width: 1200, expectedCols: 3, expectedPerPage: 3, name: 'Desktop Start' },
      { width: 1400, expectedCols: 3, expectedPerPage: 3, name: 'Desktop' }
    ];
    
    console.log('\n=== BREAKPOINT VERIFICATION ===');
    
    for (const testCase of testCases) {
      await page.setViewportSize({ width: testCase.width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1500); // Wait for redirects
      
      const result = await page.evaluate(() => {
        const cards = document.querySelectorAll('.post-card-dynamic');
        const urlParams = new URLSearchParams(window.location.search);
        const perPage = parseInt(urlParams.get('per_page')) || 3;
        
        // Analyze layout
        const positions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: Math.round(rect.top), left: Math.round(rect.left) };
        });
        
        const rows = {};
        positions.forEach((pos, i) => {
          const row = Math.round(pos.top / 10);
          if (!rows[row]) rows[row] = [];
          rows[row].push(i);
        });
        
        const maxCardsPerRow = Math.max(...Object.values(rows).map(r => r.length));
        const rowCount = Object.keys(rows).length;
        const perfectFill = (maxCardsPerRow === perPage) || // All cards fit in one row
                           (maxCardsPerRow === 1 && perPage === 2); // Mobile with 2 cards in 2 rows
        
        return {
          perPage,
          cardCount: cards.length,
          maxCardsPerRow,
          rowCount,
          perfectFill
        };
      });
      
      console.log(`${testCase.name} (${testCase.width}px): ${result.maxCardsPerRow} cols, ${result.rowCount} rows, per_page=${result.perPage} ${result.perfectFill ? '✅' : '❌'}`);
      
      expect(result.perPage).toBe(testCase.expectedPerPage);
      expect(result.perfectFill).toBe(true);
    }
  });
  
  test('should handle screen size changes dynamically', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    console.log('\n=== DYNAMIC RESIZE TESTING ===');
    
    // Start with desktop
    await page.setViewportSize({ width: 1400, height: 800 });
    await page.waitForTimeout(1000);
    
    let result = await page.evaluate(() => {
      const urlParams = new URLSearchParams(window.location.search);
      return {
        perPage: urlParams.get('per_page'),
        optimal: window.responsivePaginationManager?.getOptimalPerPage()
      };
    });
    console.log(`Desktop (1400px): per_page=${result.perPage}, optimal=${result.optimal}`);
    
    // Resize to medium (should trigger change)
    await page.setViewportSize({ width: 1000, height: 800 });
    await page.waitForTimeout(500); // Wait for resize handler
    
    result = await page.evaluate(() => {
      const urlParams = new URLSearchParams(window.location.search);
      return {
        perPage: urlParams.get('per_page'),
        optimal: window.responsivePaginationManager?.getOptimalPerPage()
      };
    });
    console.log(`Medium (1000px): per_page=${result.perPage}, optimal=${result.optimal}`);
    
    // Resize to mobile
    await page.setViewportSize({ width: 400, height: 800 });
    await page.waitForTimeout(500);
    
    result = await page.evaluate(() => {
      const urlParams = new URLSearchParams(window.location.search);
      return {
        perPage: urlParams.get('per_page'),
        optimal: window.responsivePaginationManager?.getOptimalPerPage()
      };
    });
    console.log(`Mobile (400px): per_page=${result.perPage}, optimal=${result.optimal}`);
    
    // All should show optimal per_page
    expect(result.optimal).toBe(2); // Mobile should be 2
  });
});