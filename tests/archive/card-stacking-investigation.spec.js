const { test, expect } = require('@playwright/test');

test.describe('Card Stacking Investigation', () => {
  test('should investigate card layout behavior across different screen sizes', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test various screen widths to find exact stacking points
    const testWidths = [
      320,  // Small mobile
      375,  // iPhone SE
      414,  // iPhone Pro
      480,  // Small tablet
      600,  // Medium tablet
      768,  // iPad portrait
      820,  // iPad landscape  
      1024, // Large tablet
      1200, // Small desktop
      1400, // Desktop
      1600, // Large desktop
      1920  // Full HD
    ];
    
    const layoutResults = [];
    
    for (const width of testWidths) {
      await page.setViewportSize({ width, height: 800 });
      await page.waitForTimeout(200); // Wait for layout to settle
      
      // Get the computed grid layout information
      const layoutInfo = await page.evaluate(() => {
        const grid = document.querySelector('.posts-grid-enhanced');
        if (!grid) return null;
        
        const gridStyle = getComputedStyle(grid);
        const cards = document.querySelectorAll('.post-card-dynamic');
        
        if (cards.length === 0) return null;
        
        // Get card positions to determine rows/columns
        const cardPositions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return {
            top: Math.round(rect.top),
            left: Math.round(rect.left),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          };
        });
        
        // Group cards by their top position (same row)
        const rows = {};
        cardPositions.forEach((pos, index) => {
          const roundedTop = Math.round(pos.top / 10) * 10; // Group within 10px
          if (!rows[roundedTop]) rows[roundedTop] = [];
          rows[roundedTop].push({ index, ...pos });
        });
        
        const rowCount = Object.keys(rows).length;
        const maxCardsPerRow = Math.max(...Object.values(rows).map(row => row.length));
        const actualLayout = Object.values(rows).map(row => row.length);
        
        return {
          gridTemplateColumns: gridStyle.gridTemplateColumns,
          gap: gridStyle.gap,
          cardCount: cards.length,
          rowCount,
          maxCardsPerRow,
          actualLayout,
          cardPositions,
          rows: Object.keys(rows).length
        };
      });
      
      if (layoutInfo) {
        layoutResults.push({
          width,
          ...layoutInfo
        });
        
        console.log(`Width ${width}px:`, {
          columns: layoutInfo.gridTemplateColumns,
          cardsPerRow: layoutInfo.maxCardsPerRow,
          rows: layoutInfo.rowCount,
          layout: layoutInfo.actualLayout.join(' + '),
          totalCards: layoutInfo.cardCount
        });
      }
    }
    
    // Analyze the results to find exact breakpoints
    console.log('\n=== LAYOUT ANALYSIS ===');
    
    let previousLayout = null;
    const breakpoints = [];
    
    layoutResults.forEach((result, index) => {
      if (previousLayout && previousLayout.maxCardsPerRow !== result.maxCardsPerRow) {
        breakpoints.push({
          width: result.width,
          change: `${previousLayout.maxCardsPerRow} → ${result.maxCardsPerRow} cards per row`,
          stacking: result.maxCardsPerRow < previousLayout.maxCardsPerRow ? 'STACKING' : 'EXPANDING'
        });
      }
      previousLayout = result;
    });
    
    console.log('\n=== BREAKPOINT CHANGES ===');
    breakpoints.forEach(bp => {
      console.log(`${bp.width}px: ${bp.change} (${bp.stacking})`);
    });
    
    // Find where cards stack to single column
    const singleColumnBreakpoint = layoutResults.find(r => r.maxCardsPerRow === 1);
    const twoColumnBreakpoint = layoutResults.find(r => r.maxCardsPerRow === 2);
    const threeColumnBreakpoint = layoutResults.find(r => r.maxCardsPerRow === 3);
    
    console.log('\n=== RECOMMENDED BREAKPOINTS ===');
    if (singleColumnBreakpoint) {
      console.log(`Single column starts at: ${singleColumnBreakpoint.width}px`);
    }
    if (twoColumnBreakpoint) {
      console.log(`Two columns available from: ${twoColumnBreakpoint.width}px`);
    }
    if (threeColumnBreakpoint) {
      console.log(`Three columns available from: ${threeColumnBreakpoint.width}px`);
    }
    
    // Determine optimal per_page settings
    console.log('\n=== OPTIMAL per_page SETTINGS ===');
    layoutResults.forEach(result => {
      let optimalPerPage;
      if (result.maxCardsPerRow === 1) {
        optimalPerPage = 2; // Show 2 cards (2 rows) when single column
      } else if (result.maxCardsPerRow === 2) {
        optimalPerPage = 2; // Show 2 cards (1 row) when two columns
      } else if (result.maxCardsPerRow >= 3) {
        optimalPerPage = 3; // Show 3 cards (1 row) when three+ columns
      }
      
      console.log(`${result.width}px: ${result.maxCardsPerRow} cols → per_page=${optimalPerPage}`);
    });
    
    // Test specific problematic sizes mentioned by user
    const problematicSizes = [900, 1000, 1100, 850, 950, 1050];
    
    console.log('\n=== TESTING POTENTIALLY PROBLEMATIC SIZES ===');
    for (const width of problematicSizes) {
      await page.setViewportSize({ width, height: 800 });
      await page.waitForTimeout(200);
      
      const layoutInfo = await page.evaluate(() => {
        const grid = document.querySelector('.posts-grid-enhanced');
        const cards = document.querySelectorAll('.post-card-dynamic');
        
        if (!grid || cards.length === 0) return null;
        
        const cardPositions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: Math.round(rect.top), left: Math.round(rect.left) };
        });
        
        const rows = {};
        cardPositions.forEach((pos, index) => {
          const roundedTop = Math.round(pos.top / 10) * 10;
          if (!rows[roundedTop]) rows[roundedTop] = [];
          rows[roundedTop].push(index);
        });
        
        const maxCardsPerRow = Math.max(...Object.values(rows).map(row => row.length));
        const currentPerPage = window.responsivePaginationManager ? 
          window.responsivePaginationManager.getOptimalPerPage() : 'unknown';
        
        return { maxCardsPerRow, currentPerPage, rowCount: Object.keys(rows).length };
      });
      
      if (layoutInfo) {
        const isStacking = layoutInfo.maxCardsPerRow < 3;
        console.log(`${width}px: ${layoutInfo.maxCardsPerRow} cols, per_page=${layoutInfo.currentPerPage}, rows=${layoutInfo.rowCount} ${isStacking ? '⚠️  STACKING' : '✅'}`);
      }
    }
  });
  
  test('should test exact CSS breakpoint behavior', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    console.log('\n=== CSS GRID BREAKPOINT ANALYSIS ===');
    
    // Test the exact CSS breakpoints defined in the stylesheet
    const cssBreakpoints = [
      { name: 'Mobile', min: 0, max: 767 },
      { name: 'Tablet', min: 768, max: 1199 },
      { name: 'Desktop', min: 1200, max: 9999 }
    ];
    
    for (const breakpoint of cssBreakpoints) {
      // Test lower bound
      const testWidth = breakpoint.min === 0 ? 320 : breakpoint.min;
      await page.setViewportSize({ width: testWidth, height: 800 });
      await page.waitForTimeout(200);
      
      const lowerInfo = await page.evaluate(() => {
        const grid = document.querySelector('.posts-grid-enhanced');
        if (!grid) return null;
        
        const style = getComputedStyle(grid);
        const cards = document.querySelectorAll('.post-card-dynamic');
        
        // Analyze actual card positions
        const positions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: rect.top, left: rect.left };
        });
        
        const rows = {};
        positions.forEach((pos, i) => {
          const row = Math.round(pos.top / 10);
          if (!rows[row]) rows[row] = [];
          rows[row].push(i);
        });
        
        return {
          gridColumns: style.gridTemplateColumns,
          cardsPerRow: Math.max(...Object.values(rows).map(r => r.length)),
          cardCount: cards.length
        };
      });
      
      // Test upper bound (if not infinite)
      let upperInfo = null;
      if (breakpoint.max < 9999) {
        await page.setViewportSize({ width: breakpoint.max, height: 800 });
        await page.waitForTimeout(200);
        
        upperInfo = await page.evaluate(() => {
          const grid = document.querySelector('.posts-grid-enhanced');
          if (!grid) return null;
          
          const style = getComputedStyle(grid);
          const cards = document.querySelectorAll('.post-card-dynamic');
          
          const positions = Array.from(cards).map(card => {
            const rect = card.getBoundingClientRect();
            return { top: rect.top, left: rect.left };
          });
          
          const rows = {};
          positions.forEach((pos, i) => {
            const row = Math.round(pos.top / 10);
            if (!rows[row]) rows[row] = [];
            rows[row].push(i);
          });
          
          return {
            gridColumns: style.gridTemplateColumns,
            cardsPerRow: Math.max(...Object.values(rows).map(r => r.length)),
            cardCount: cards.length
          };
        });
      }
      
      console.log(`${breakpoint.name} (${breakpoint.min}px${breakpoint.max < 9999 ? `-${breakpoint.max}px` : '+'})`);
      if (lowerInfo) {
        console.log(`  At ${testWidth}px: ${lowerInfo.cardsPerRow} cards/row, grid: ${lowerInfo.gridColumns}`);
      }
      if (upperInfo) {
        console.log(`  At ${breakpoint.max}px: ${upperInfo.cardsPerRow} cards/row, grid: ${upperInfo.gridColumns}`);
      }
    }
  });
});