const { test, expect } = require('@playwright/test');

test.describe('Final Balance Verification', () => {
  test('should verify perfect balance with aligned CSS and JS breakpoints', async ({ page }) => {
    console.log('=== VERIFYING ALIGNED CSS/JS BREAKPOINTS ===');
    
    const testCases = [
      { width: 768, expectedCols: 2, expectedCards: 2, name: 'Tablet: 2 cols, 2 cards' },
      { width: 849, expectedCols: 2, expectedCards: 2, name: 'Pre-3card: 2 cols, 2 cards' },
      { width: 850, expectedCols: 3, expectedCards: 3, name: 'Large tablet: 3 cols, 3 cards' },
      { width: 900, expectedCols: 3, expectedCards: 3, name: 'Large tablet+: 3 cols, 3 cards' },
      { width: 1000, expectedCols: 3, expectedCards: 3, name: 'Laptop: 3 cols, 3 cards' },
      { width: 1200, expectedCols: 3, expectedCards: 3, name: 'Desktop: 3 cols, 3 cards' }
    ];
    
    for (const testCase of testCases) {
      await page.setViewportSize({ width: testCase.width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1500);
      
      const result = await page.evaluate(() => {
        const grid = document.querySelector('.posts-grid-enhanced');
        const cards = document.querySelectorAll('.post-card-dynamic');
        const urlParams = new URLSearchParams(window.location.search);
        const perPage = parseInt(urlParams.get('per_page')) || 3;
        
        if (!grid || cards.length === 0) return null;
        
        // Get CSS grid columns
        const gridStyle = getComputedStyle(grid);
        const gridColumns = gridStyle.gridTemplateColumns.split(' ').length;
        
        // Analyze layout
        const cardPositions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: rect.top, left: rect.left, width: rect.width };
        });
        
        // Group by rows
        const rows = {};
        cardPositions.forEach((pos, i) => {
          const row = Math.round(pos.top / 50);
          if (!rows[row]) rows[row] = [];
          rows[row].push(i);
        });
        
        const rowSizes = Object.values(rows).map(row => row.length);
        const maxCardsInRow = Math.max(...rowSizes);
        const isSingleRow = rowSizes.length === 1;
        const avgCardWidth = cardPositions.reduce((sum, pos) => sum + pos.width, 0) / cardPositions.length;
        
        // Perfect balance check
        const isPerfectBalance = isSingleRow && maxCardsInRow === perPage;
        
        return {
          perPage,
          cardCount: cards.length,
          gridColumns,
          maxCardsInRow,
          isSingleRow,
          isPerfectBalance,
          avgCardWidth: avgCardWidth.toFixed(1),
          layout: rowSizes.join(' + ')
        };
      });
      
      if (result) {
        const balanceStatus = result.isPerfectBalance ? '🟢 PERFECT' : 
                            result.isSingleRow ? '🟡 SINGLE ROW' : '🔴 STACKING';
        
        console.log(`${testCase.name} (${testCase.width}px):`);
        console.log(`  CSS: ${result.gridColumns} cols, JS: ${result.perPage} cards`);
        console.log(`  Layout: [${result.layout}], Cards: ${result.avgCardWidth}px ${balanceStatus}`);
        
        expect(result.gridColumns).toBe(testCase.expectedCols);
        expect(result.perPage).toBe(testCase.expectedCards);
        expect(result.isPerfectBalance).toBe(true);
      }
    }
  });
  
  test('should verify no stacking at any size', async ({ page }) => {
    console.log('\n=== ANTI-STACKING VERIFICATION ===');
    
    const testWidths = [768, 800, 850, 900, 950, 1000, 1100, 1200, 1400];
    
    for (const width of testWidths) {
      await page.setViewportSize({ width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      const stackingCheck = await page.evaluate(() => {
        const cards = document.querySelectorAll('.post-card-dynamic');
        if (cards.length === 0) return null;
        
        const positions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: Math.round(rect.top), left: rect.left };
        });
        
        const rows = {};
        positions.forEach((pos, i) => {
          const row = Math.round(pos.top / 50);
          if (!rows[row]) rows[row] = [];
          rows[row].push(i);
        });
        
        const rowSizes = Object.values(rows).map(row => row.length);
        const hasStacking = rowSizes.length > 1 && rowSizes.some(size => size !== rowSizes[0]);
        const isSingleRow = rowSizes.length === 1;
        
        return {
          cardCount: cards.length,
          rowCount: rowSizes.length,
          rowSizes,
          hasStacking: hasStacking && !isSingleRow, // Only bad if uneven and multi-row
          isSingleRow,
          layout: rowSizes.join(' + ')
        };
      });
      
      if (stackingCheck) {
        const status = stackingCheck.isSingleRow ? '✅ SINGLE ROW' : 
                      stackingCheck.hasStacking ? '❌ STACKING' : '✅ EVEN ROWS';
        
        console.log(`${width}px: ${stackingCheck.cardCount} cards → [${stackingCheck.layout}] ${status}`);
        expect(stackingCheck.hasStacking).toBe(false);
      }
    }
  });
});