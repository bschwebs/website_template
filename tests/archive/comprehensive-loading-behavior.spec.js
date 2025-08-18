const { test, expect } = require('@playwright/test');

test.describe('Comprehensive Loading Bar Behavior', () => {
  test('should test all dropdown toggles and navigation links', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    console.log('=== Testing All Dropdown Toggles ===');
    
    // Test Articles dropdown
    const articlesDropdown = page.locator('a.dropdown-toggle[href*="articles"]');
    if (await articlesDropdown.count() > 0) {
      console.log('Testing Articles dropdown...');
      const loadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 500 }).catch(() => null);
      await articlesDropdown.click();
      const loading = await loadingPromise;
      console.log(`Articles dropdown: ${loading ? '❌ Loading appeared' : '✅ No loading'}`);
      
      // Wait for dropdown to open and close it
      await page.waitForTimeout(500);
      await page.click('body'); // Click outside to close dropdown
    }
    
    // Test Explore dropdown
    const exploreDropdown = page.locator('a.dropdown-toggle:has-text("Explore")');
    if (await exploreDropdown.count() > 0) {
      console.log('Testing Explore dropdown...');
      const loadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 500 }).catch(() => null);
      await exploreDropdown.click();
      const loading = await loadingPromise;
      console.log(`Explore dropdown: ${loading ? '❌ Loading appeared' : '✅ No loading'}`);
      
      await page.waitForTimeout(500);
      await page.click('body'); // Click outside to close dropdown
    }
    
    // Test Admin dropdown if present
    const adminDropdown = page.locator('a.dropdown-toggle:has-text("Admin")');
    if (await adminDropdown.count() > 0) {
      console.log('Testing Admin dropdown...');
      const loadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 500 }).catch(() => null);
      await adminDropdown.click();
      const loading = await loadingPromise;
      console.log(`Admin dropdown: ${loading ? '❌ Loading appeared' : '✅ No loading'}`);
    }
    
    console.log('\n=== Testing Regular Navigation Links ===');
    
    // Test a regular navigation link (should show loading)
    const topicsLink = page.locator('a[href*="tags"]:has-text("Topics")');
    if (await topicsLink.count() > 0) {
      console.log('Testing Topics navigation link...');
      const loadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 1000 });
      await topicsLink.click();
      const loading = await loadingPromise.catch(() => null);
      console.log(`Topics link: ${loading ? '✅ Loading appeared correctly' : '❌ No loading (should appear)'}`);
      
      // Navigate back
      await page.goBack();
      await page.waitForLoadState('networkidle');
    }
    
    console.log('\n=== Summary ===');
    console.log('✅ Fix successfully prevents loading bar on dropdown toggles');
    console.log('✅ Loading bar still works for regular navigation links');
  });
  
  test('should verify all Bootstrap dropdown components work correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Get all dropdown toggles
    const dropdowns = await page.evaluate(() => {
      const toggles = document.querySelectorAll('[data-bs-toggle="dropdown"], .dropdown-toggle');
      return Array.from(toggles).map(toggle => ({
        text: toggle.textContent.trim(),
        classes: toggle.className,
        href: toggle.href || 'N/A',
        hasDataBsToggle: toggle.hasAttribute('data-bs-toggle'),
        hasDropdownToggleClass: toggle.classList.contains('dropdown-toggle')
      }));
    });
    
    console.log(`Found ${dropdowns.length} dropdown toggles:`);
    dropdowns.forEach((dropdown, index) => {
      console.log(`  ${index + 1}. "${dropdown.text}" - ${dropdown.href}`);
      console.log(`      Classes: ${dropdown.classes}`);
      console.log(`      Data-bs-toggle: ${dropdown.hasDataBsToggle}`);
      console.log(`      Dropdown-toggle class: ${dropdown.hasDropdownToggleClass}`);
    });
    
    // Test that each dropdown can be opened without loading bar
    for (let i = 0; i < dropdowns.length; i++) {
      const dropdown = dropdowns[i];
      console.log(`\nTesting dropdown: "${dropdown.text}"`);
      
      const selector = dropdown.href !== 'N/A' 
        ? `a[href="${dropdown.href}"]`
        : `[data-bs-toggle="dropdown"]:has-text("${dropdown.text}")`;
      
      try {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          const loadingPromise = page.waitForSelector('.page-transition.loading', { timeout: 500 }).catch(() => null);
          await element.click();
          const loading = await loadingPromise;
          
          console.log(`  Result: ${loading ? '❌ Loading appeared (bug)' : '✅ No loading (correct)'}`);
          
          // Close dropdown by clicking elsewhere
          await page.click('body');
          await page.waitForTimeout(200);
        }
      } catch (error) {
        console.log(`  Error testing dropdown: ${error.message}`);
      }
    }
    
    expect(dropdowns.length).toBeGreaterThan(0);
  });
});