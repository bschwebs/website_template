const { test, expect } = require('@playwright/test');

test.describe('Balanced Pagination Verification', () => {
  test('should verify improved balance with new 850px breakpoint', async ({ page }) => {
    console.log('=== TESTING NEW BALANCED BREAKPOINT (850px) ===');
    
    const testCases = [
      { width: 600, expected: 2, name: 'Mobile', reason: '2 cards in 2 rows' },
      { width: 768, expected: 2, name: 'Small Tablet', reason: '2 cards in 1 row' },
      { width: 800, expected: 2, name: 'Small Tablet+', reason: '2 cards perfectly fitted' },
      { width: 849, expected: 2, name: 'Tablet Edge', reason: 'Last size with 2 cards' },
      { width: 850, expected: 3, name: 'Large Tablet', reason: '3 cards with good spacing' },
      { width: 900, expected: 3, name: 'Large Tablet+', reason: '3 cards comfortable' },
      { width: 1000, expected: 3, name: 'Laptop', reason: '3 cards with great spacing' },
      { width: 1200, expected: 3, name: 'Desktop', reason: '3 cards optimal' },
      { width: 1400, expected: 3, name: 'Large Desktop', reason: '3 cards spacious' }
    ];
    
    for (const testCase of testCases) {
      await page.setViewportSize({ width: testCase.width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1500); // Wait for any redirects
      
      const result = await page.evaluate(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const perPage = parseInt(urlParams.get('per_page')) || 3;
        const optimal = window.responsivePaginationManager?.getOptimalPerPage();
        
        const cards = document.querySelectorAll('.post-card-dynamic');
        const cardPositions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: rect.top, left: rect.left, width: rect.width };
        });
        
        // Analyze layout quality
        const rows = {};
        cardPositions.forEach((pos, i) => {
          const row = Math.round(pos.top / 50);
          if (!rows[row]) rows[row] = [];
          rows[row].push({ index: i, width: pos.width });
        });
        
        const rowSizes = Object.values(rows).map(row => row.length);
        const avgCardWidth = cardPositions.reduce((sum, card) => sum + card.width, 0) / cardPositions.length;
        
        // Calculate balance score
        const isBalanced = rowSizes.every(size => size === rowSizes[0]) || rowSizes.length === 1;
        const isComfortable = avgCardWidth >= 300; // Good card width
        const balanceScore = isBalanced && isComfortable ? 100 : 
                           isBalanced ? 75 : 
                           isComfortable ? 50 : 25;
        
        return {
          perPage,
          optimal,
          cardCount: cards.length,
          rowSizes,
          avgCardWidth: avgCardWidth.toFixed(1),
          isBalanced,
          isComfortable,
          balanceScore,
          layout: rowSizes.join(' + ')
        };
      });
      
      const balanceIcon = result.balanceScore >= 75 ? '🟢' : 
                         result.balanceScore >= 50 ? '🟡' : '🔴';
      
      console.log(`${testCase.name} (${testCase.width}px):`);
      console.log(`  Expected: ${testCase.expected}, Got: ${result.perPage} ${result.perPage === testCase.expected ? '✅' : '❌'}`);
      console.log(`  Layout: [${result.layout}], Cards: ${result.avgCardWidth}px wide`);
      console.log(`  Balance Score: ${result.balanceScore}% ${balanceIcon} - ${testCase.reason}`);
      console.log();
      
      expect(result.perPage).toBe(testCase.expected);
      expect(result.balanceScore).toBeGreaterThanOrEqual(75); // Should be well balanced
    }
  });
  
  test('should verify no stacking issues at problematic sizes', async ({ page }) => {
    console.log('=== VERIFYING NO STACKING AT PREVIOUSLY PROBLEMATIC SIZES ===');
    
    const problematicSizes = [850, 900, 950, 1000, 1050, 1100, 1150];
    
    for (const width of problematicSizes) {
      await page.setViewportSize({ width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1500);
      
      const analysis = await page.evaluate(() => {
        const cards = document.querySelectorAll('.post-card-dynamic');
        const urlParams = new URLSearchParams(window.location.search);
        const perPage = parseInt(urlParams.get('per_page')) || 3;
        
        if (cards.length === 0) return null;
        
        // Check layout structure
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
        
        const rowCount = Object.keys(rows).length;
        const cardsPerRow = Object.values(rows).map(row => row.length);
        const maxCardsInRow = Math.max(...cardsPerRow);
        const avgCardWidth = cardPositions.reduce((sum, pos) => sum + pos.width, 0) / cardPositions.length;
        
        // Determine layout quality
        const hasStacking = rowCount > 1 && cardsPerRow.some((count, i) => i === 0 && count < maxCardsInRow);
        const isOptimal = (rowCount === 1) || // Single row is always good
                         (rowCount === 2 && perPage === 2 && cards.length === 2); // 2 cards in 2 rows for mobile
        
        return {
          perPage,
          cardCount: cards.length,
          rowCount,
          cardsPerRow,
          maxCardsInRow,
          avgCardWidth: avgCardWidth.toFixed(1),
          hasStacking,
          isOptimal,
          layout: cardsPerRow.join(' + ')
        };
      });
      
      if (analysis) {
        const status = analysis.isOptimal ? '✅ OPTIMAL' : 
                      analysis.hasStacking ? '⚠️ STACKING' : '🟡 OKAY';
        
        console.log(`${width}px: ${analysis.perPage} cards, Layout=[${analysis.layout}], Cards=${analysis.avgCardWidth}px ${status}`);
        
        // Key assertions
        expect(analysis.hasStacking).toBe(false); // No unwanted stacking
        expect(parseFloat(analysis.avgCardWidth)).toBeGreaterThan(300); // Cards should be comfortable size
      }
    }
  });
  
  test('should verify visual balance and spacing', async ({ page }) => {
    console.log('\n=== TESTING VISUAL BALANCE AND SPACING ===');
    
    const keyBreakpoints = [
      { width: 768, name: 'Tablet Start', expected: 2 },
      { width: 849, name: 'Before 3-card threshold', expected: 2 },
      { width: 850, name: '3-card threshold', expected: 3 },
      { width: 1000, name: 'Laptop', expected: 3 },
      { width: 1200, name: 'Desktop', expected: 3 }
    ];
    
    for (const breakpoint of keyBreakpoints) {
      await page.setViewportSize({ width: breakpoint.width, height: 800 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1500);
      
      // Take screenshot for visual verification
      await page.screenshot({ 
        path: `tests/screenshots/balance-${breakpoint.width}px.png`,
        fullPage: false,
        clip: { x: 0, y: 0, width: breakpoint.width, height: 600 }
      });
      
      const spacingAnalysis = await page.evaluate(() => {
        const grid = document.querySelector('.posts-grid-enhanced');
        const cards = document.querySelectorAll('.post-card-dynamic');
        
        if (!grid || cards.length === 0) return null;
        
        const gridRect = grid.getBoundingClientRect();
        const cardRects = Array.from(cards).map(card => card.getBoundingClientRect());
        
        // Calculate spacing metrics
        const gridWidth = gridRect.width;
        const totalCardWidth = cardRects.reduce((sum, rect) => sum + rect.width, 0);
        const gapSpace = gridWidth - totalCardWidth;
        const gapCount = cards.length - 1;
        const avgGap = gapCount > 0 ? gapSpace / gapCount : 0;
        
        // Check if cards are evenly spaced
        const gaps = [];
        for (let i = 1; i < cardRects.length; i++) {
          const gap = cardRects[i].left - (cardRects[i-1].left + cardRects[i-1].width);
          gaps.push(gap);
        }
        
        const gapVariation = gaps.length > 0 ? 
          Math.max(...gaps) - Math.min(...gaps) : 0;
        
        const isEvenlySpaced = gapVariation < 5; // Within 5px is considered even
        
        // Calculate visual balance score
        const spaceEfficiency = (totalCardWidth / gridWidth) * 100;
        const balanceScore = isEvenlySpaced && spaceEfficiency > 70 ? 100 :
                           isEvenlySpaced ? 80 :
                           spaceEfficiency > 70 ? 60 : 40;
        
        return {
          gridWidth: gridWidth.toFixed(1),
          totalCardWidth: totalCardWidth.toFixed(1),
          avgGap: avgGap.toFixed(1),
          gapVariation: gapVariation.toFixed(1),
          isEvenlySpaced,
          spaceEfficiency: spaceEfficiency.toFixed(1),
          balanceScore
        };
      });
      
      if (spacingAnalysis) {
        const balanceIcon = spacingAnalysis.balanceScore >= 80 ? '🟢' : 
                           spacingAnalysis.balanceScore >= 60 ? '🟡' : '🔴';
        
        console.log(`${breakpoint.name} (${breakpoint.width}px):`);
        console.log(`  Grid: ${spacingAnalysis.gridWidth}px, Cards: ${spacingAnalysis.totalCardWidth}px`);
        console.log(`  Spacing: ${spacingAnalysis.avgGap}px gaps, variation: ${spacingAnalysis.gapVariation}px`);
        console.log(`  Efficiency: ${spacingAnalysis.spaceEfficiency}%, Balance: ${spacingAnalysis.balanceScore}% ${balanceIcon}`);
        console.log();
        
        expect(spacingAnalysis.balanceScore).toBeGreaterThanOrEqual(80);
        expect(spacingAnalysis.isEvenlySpaced).toBe(true);
      }
    }
  });
  
  test('should verify smooth transitions between breakpoints', async ({ page }) => {
    console.log('=== TESTING SMOOTH BREAKPOINT TRANSITIONS ===');
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test transition from 2-card to 3-card layout
    const transitionPoints = [
      { from: 820, to: 880, expectedBefore: 2, expectedAfter: 3 }
    ];
    
    for (const transition of transitionPoints) {
      // Start at smaller size
      await page.setViewportSize({ width: transition.from, height: 800 });
      await page.waitForTimeout(1000);
      
      const beforeResult = await page.evaluate(() => {
        const urlParams = new URLSearchParams(window.location.search);
        return {
          perPage: parseInt(urlParams.get('per_page')) || 3,
          optimal: window.responsivePaginationManager?.getOptimalPerPage()
        };
      });
      
      // Resize to larger size
      await page.setViewportSize({ width: transition.to, height: 800 });
      await page.waitForTimeout(1000); // Wait for resize handler
      
      const afterResult = await page.evaluate(() => {
        const urlParams = new URLSearchParams(window.location.search);
        return {
          perPage: parseInt(urlParams.get('per_page')) || 3,
          optimal: window.responsivePaginationManager?.getOptimalPerPage()
        };
      });
      
      console.log(`Transition ${transition.from}px → ${transition.to}px:`);
      console.log(`  Before: per_page=${beforeResult.perPage}, optimal=${beforeResult.optimal}`);
      console.log(`  After: per_page=${afterResult.perPage}, optimal=${afterResult.optimal}`);
      
      expect(beforeResult.optimal).toBe(transition.expectedBefore);
      expect(afterResult.optimal).toBe(transition.expectedAfter);
      
      const hasSmoothtransition = beforeResult.optimal !== afterResult.optimal;
      console.log(`  Transition detected: ${hasSmoothtransition ? '✅ YES' : '❌ NO'}`);
    }
  });
});