const { test, expect } = require('@playwright/test');

test.describe('Space Utilization Analysis', () => {
  test('should analyze actual card widths and container space', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test various screen widths to understand space utilization
    const testWidths = [
      800,   // Tablet
      900,   // Medium tablet
      1000,  // Large tablet
      1100,  // Small laptop
      1200,  // Desktop threshold
      1300,  // Desktop
      1400,  // Large desktop
      1500,  // XL desktop
      1600   // XXL desktop
    ];
    
    console.log('=== SPACE UTILIZATION ANALYSIS ===');
    console.log('Analyzing actual card dimensions and available space...\n');
    
    const spaceAnalysis = [];
    
    for (const width of testWidths) {
      await page.setViewportSize({ width, height: 800 });
      await page.waitForTimeout(300); // Wait for layout to settle
      
      const analysis = await page.evaluate(() => {
        const container = document.querySelector('.container');
        const grid = document.querySelector('.posts-grid-enhanced');
        const cards = document.querySelectorAll('.post-card-dynamic');
        
        if (!container || !grid || cards.length === 0) return null;
        
        // Get container dimensions
        const containerRect = container.getBoundingClientRect();
        const gridRect = grid.getBoundingClientRect();
        const gridStyle = getComputedStyle(grid);
        
        // Get card dimensions
        const firstCard = cards[0];
        const cardRect = firstCard.getBoundingClientRect();
        
        // Calculate grid properties
        const gap = parseInt(gridStyle.gap) || 24;
        const containerWidth = containerRect.width;
        const gridWidth = gridRect.width;
        const cardWidth = cardRect.width;
        
        // Calculate how many cards could theoretically fit
        const availableWidth = gridWidth;
        const cardWithGap = cardWidth + gap;
        const theoreticalMaxCards = Math.floor((availableWidth + gap) / cardWithGap);
        
        // Get actual CSS grid columns
        const gridColumns = gridStyle.gridTemplateColumns;
        const actualColumns = gridColumns.split(' ').length;
        
        // Analyze card positions to see actual layout
        const cardPositions = Array.from(cards).map((card, index) => {
          const rect = card.getBoundingClientRect();
          return {
            index,
            left: rect.left,
            top: rect.top,
            width: rect.width,
            height: rect.height
          };
        });
        
        // Group cards by rows
        const rows = {};
        cardPositions.forEach(pos => {
          const row = Math.round(pos.top / 50); // Group by 50px intervals
          if (!rows[row]) rows[row] = [];
          rows[row].push(pos);
        });
        
        const cardsPerRow = Object.values(rows).map(row => row.length);
        const maxCardsInRow = Math.max(...cardsPerRow);
        
        // Calculate space efficiency
        const usedWidth = maxCardsInRow * cardWidth + (maxCardsInRow - 1) * gap;
        const spaceEfficiency = (usedWidth / availableWidth) * 100;
        const unusedSpace = availableWidth - usedWidth;
        
        // Calculate if we could fit one more card
        const spaceForOneMore = unusedSpace >= (cardWidth + gap);
        
        return {
          containerWidth,
          gridWidth,
          cardWidth,
          gap,
          theoreticalMaxCards,
          actualColumns,
          maxCardsInRow,
          cardsPerRow,
          spaceEfficiency,
          unusedSpace,
          spaceForOneMore,
          gridColumns
        };
      });
      
      if (analysis) {
        spaceAnalysis.push({ width, ...analysis });
        
        const efficiency = analysis.spaceEfficiency.toFixed(1);
        const canFitMore = analysis.spaceForOneMore ? '🟢 CAN FIT MORE' : '🔴 FULL';
        
        console.log(`${width}px:`);
        console.log(`  Container: ${analysis.containerWidth}px, Grid: ${analysis.gridWidth}px`);
        console.log(`  Card: ${analysis.cardWidth}px, Gap: ${analysis.gap}px`);
        console.log(`  CSS Columns: ${analysis.actualColumns}, Actual Max/Row: ${analysis.maxCardsInRow}`);
        console.log(`  Theoretical Max: ${analysis.theoreticalMaxCards} cards`);
        console.log(`  Space Efficiency: ${efficiency}%, Unused: ${analysis.unusedSpace.toFixed(1)}px`);
        console.log(`  Layout: [${analysis.cardsPerRow.join(', ')}] ${canFitMore}`);
        console.log(`  Grid Template: ${analysis.gridColumns}\n`);
      }
    }
    
    // Analyze optimal breakpoints based on space utilization
    console.log('=== OPTIMAL CARD COUNT RECOMMENDATIONS ===');
    
    spaceAnalysis.forEach(analysis => {
      let recommendedCards;
      
      // If we can efficiently fit 3 cards (good space utilization)
      if (analysis.actualColumns >= 3 || analysis.theoreticalMaxCards >= 3) {
        recommendedCards = 3;
      }
      // If we can fit exactly 2 cards with good efficiency
      else if (analysis.actualColumns === 2 && analysis.spaceEfficiency > 70) {
        recommendedCards = 2;
      }
      // For narrow screens
      else {
        recommendedCards = 2; // Better than 1 for mobile
      }
      
      const current = analysis.maxCardsInRow;
      const statusIcon = recommendedCards > current ? '📈 INCREASE' : 
                        recommendedCards < current ? '📉 DECREASE' : 
                        '✅ OPTIMAL';
      
      console.log(`${analysis.width}px: Current=${current}, Recommended=${recommendedCards} ${statusIcon}`);
    });
    
    // Find the optimal breakpoint where we can show 3 cards without stacking
    console.log('\n=== BREAKPOINT ANALYSIS FOR 3-CARD LAYOUT ===');
    
    const canShow3Cards = spaceAnalysis.filter(a => 
      a.theoreticalMaxCards >= 3 && a.spaceEfficiency > 60
    );
    
    if (canShow3Cards.length > 0) {
      const minWidthFor3Cards = Math.min(...canShow3Cards.map(a => a.width));
      console.log(`Minimum width for 3 cards: ${minWidthFor3Cards}px`);
      
      // Test specific breakpoint candidates
      const breakpointCandidates = [900, 950, 1000, 1050, 1100];
      
      console.log('\nTesting breakpoint candidates for 3-card support:');
      for (const candidateWidth of breakpointCandidates) {
        const analysis = spaceAnalysis.find(a => a.width === candidateWidth);
        if (analysis) {
          const supports3Cards = analysis.theoreticalMaxCards >= 3 && analysis.spaceEfficiency > 60;
          const status = supports3Cards ? '✅ SUPPORTS 3 CARDS' : '❌ TOO CRAMPED';
          console.log(`  ${candidateWidth}px: Theoretical=${analysis.theoreticalMaxCards}, Efficiency=${analysis.spaceEfficiency.toFixed(1)}% ${status}`);
        }
      }
    }
  });
  
  test('should test 3-card layout at various screen sizes', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    console.log('\n=== TESTING 3-CARD LAYOUT VIABILITY ===');
    
    // Force 3 cards at different screen sizes to see how they look
    const testSizes = [800, 900, 1000, 1100, 1200, 1300, 1400];
    
    for (const width of testSizes) {
      await page.setViewportSize({ width, height: 800 });
      
      // Navigate with per_page=3 to force 3 cards
      await page.goto('/?per_page=3');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);
      
      const layoutResult = await page.evaluate(() => {
        const cards = document.querySelectorAll('.post-card-dynamic');
        const grid = document.querySelector('.posts-grid-enhanced');
        
        if (!cards.length || !grid) return null;
        
        // Analyze the layout quality
        const cardPositions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { left: rect.left, top: rect.top, width: rect.width };
        });
        
        // Check if cards are cramped (too narrow)
        const avgCardWidth = cardPositions.reduce((sum, card) => sum + card.width, 0) / cardPositions.length;
        const minComfortableWidth = 280; // Minimum width for good UX
        
        // Group by rows
        const rows = {};
        cardPositions.forEach((pos, i) => {
          const row = Math.round(pos.top / 50);
          if (!rows[row]) rows[row] = [];
          rows[row].push({ index: i, ...pos });
        });
        
        const rowSizes = Object.values(rows).map(row => row.length);
        const isSingleRow = rowSizes.length === 1;
        const maxPerRow = Math.max(...rowSizes);
        const isBalanced = rowSizes.every(size => size === maxPerRow);
        
        return {
          cardCount: cards.length,
          avgCardWidth: avgCardWidth.toFixed(1),
          isComfortable: avgCardWidth >= minComfortableWidth,
          isSingleRow,
          isBalanced,
          maxPerRow,
          layout: rowSizes.join(' + ')
        };
      });
      
      if (layoutResult) {
        const comfort = layoutResult.isComfortable ? '😊 COMFORTABLE' : '😰 CRAMPED';
        const layout = layoutResult.isSingleRow ? '✅ SINGLE ROW' : '⚠️ MULTI ROW';
        const balance = layoutResult.isBalanced ? '⚖️ BALANCED' : '⚠️ UNBALANCED';
        
        console.log(`${width}px with 3 cards:`);
        console.log(`  Card width: ${layoutResult.avgCardWidth}px ${comfort}`);
        console.log(`  Layout: [${layoutResult.layout}] ${layout} ${balance}`);
        
        // Determine if this width can handle 3 cards well
        const canHandle3Cards = layoutResult.isComfortable && 
                               (layoutResult.isSingleRow || layoutResult.isBalanced);
        console.log(`  Verdict: ${canHandle3Cards ? '✅ CAN HANDLE 3 CARDS' : '❌ STICK TO 2 CARDS'}\n`);
      }
    }
  });
  
  test('should find optimal breakpoint for 3-card transition', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    console.log('=== FINDING OPTIMAL 3-CARD BREAKPOINT ===');
    
    // Test incremental widths to find the sweet spot
    const incrementalWidths = [];
    for (let w = 850; w <= 1200; w += 50) {
      incrementalWidths.push(w);
    }
    
    const results = [];
    
    for (const width of incrementalWidths) {
      await page.setViewportSize({ width, height: 800 });
      await page.goto('/?per_page=3');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(300);
      
      const analysis = await page.evaluate(() => {
        const cards = document.querySelectorAll('.post-card-dynamic');
        const container = document.querySelector('.posts-grid-enhanced');
        
        if (!cards.length) return null;
        
        const cardWidths = Array.from(cards).map(card => card.getBoundingClientRect().width);
        const avgWidth = cardWidths.reduce((a, b) => a + b, 0) / cardWidths.length;
        
        // Check layout quality
        const positions = Array.from(cards).map(card => {
          const rect = card.getBoundingClientRect();
          return { top: rect.top, left: rect.left };
        });
        
        const rows = {};
        positions.forEach((pos, i) => {
          const row = Math.round(pos.top / 30);
          if (!rows[row]) rows[row] = [];
          rows[row].push(i);
        });
        
        const rowCount = Object.keys(rows).length;
        const cardsInFirstRow = rows[Object.keys(rows)[0]]?.length || 0;
        
        // Quality score based on multiple factors
        const minCardWidth = 280;
        const widthScore = Math.min(avgWidth / minCardWidth, 1) * 100;
        const layoutScore = rowCount === 1 ? 100 : (cardsInFirstRow === 3 ? 50 : 0);
        const overallScore = (widthScore + layoutScore) / 2;
        
        return {
          avgCardWidth: avgWidth,
          rowCount,
          cardsInFirstRow,
          widthScore: widthScore.toFixed(1),
          layoutScore,
          overallScore: overallScore.toFixed(1),
          isGood: overallScore >= 75
        };
      });
      
      if (analysis) {
        results.push({ width, ...analysis });
        
        const quality = analysis.isGood ? '🟢 GOOD' : '🟡 OKAY';
        console.log(`${width}px: Card=${analysis.avgCardWidth.toFixed(0)}px, Rows=${analysis.rowCount}, Score=${analysis.overallScore}% ${quality}`);
      }
    }
    
    // Find the optimal breakpoint
    const goodResults = results.filter(r => r.isGood);
    if (goodResults.length > 0) {
      const optimalBreakpoint = Math.min(...goodResults.map(r => r.width));
      console.log(`\n🎯 RECOMMENDED BREAKPOINT FOR 3 CARDS: ${optimalBreakpoint}px`);
      
      // Suggest new breakpoint logic
      console.log('\n📋 SUGGESTED BREAKPOINT LOGIC:');
      console.log(`• Mobile (<768px): 2 cards`);
      console.log(`• Small Tablet (768px-${optimalBreakpoint - 1}px): 2 cards`);
      console.log(`• Large Tablet/Desktop (≥${optimalBreakpoint}px): 3 cards`);
    } else {
      console.log('\n⚠️ No width in tested range can comfortably handle 3 cards');
    }
  });
});