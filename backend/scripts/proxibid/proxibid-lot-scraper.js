const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const blessed = require('blessed');
const contrib = require('blessed-contrib');
const moment = require('moment');

// Flag to control the scraping process
let isCancelled = false;

/**
 * Safely log messages by removing non-ASCII characters
 * @param {Object} log - The log object from blessed
 * @param {string} message - The message to log
 */
function safeLog(log, message) {
  log.log(message.replace(/[^\x00-\x7F]/g, ""));
}

/**
 * Scrape individual auction house pages
 * @param {Object} page - Puppeteer page object
 * @param {Object} auctionHouse - Auction house data
 * @param {Object} log - Blessed log object
 * @returns {Object} Updated auction house data
 */
async function scrapeAuctionHouse(page, auctionHouse, log) {
  safeLog(log, `Scraping auction house: ${auctionHouse.name}`);
  safeLog(log, `Navigating to URL: ${auctionHouse.url}`);
  
  await page.goto(auctionHouse.url, { waitUntil: 'networkidle2', timeout: 60000 });
  safeLog(log, "Page loaded. Extracting auction information...");

  const auctionInfo = await page.evaluate(() => {
    const noEventsText = 'There are no current events for this seller.';
    const hasNoEvents = document.body.innerText.includes(noEventsText);

    let upcomingAuctions = [];
    if (!hasNoEvents) {
      const auctionElements = document.querySelectorAll('.auc-listings .saleItem');
      upcomingAuctions = Array.from(auctionElements).map(auction => {
        const titleElement = auction.querySelector('h2 a');
        const dateElement = auction.querySelector('.aucdates');
        const locationElement = auction.querySelector('.aucplcdate');
        const descriptionElement = auction.querySelector('.aucdescription');
        const linkElement = auction.querySelector('h2 a');

        return {
          title: titleElement ? titleElement.textContent.trim() : 'No title found',
          date: dateElement ? dateElement.textContent.trim() : 'No date found',
          location: locationElement ? locationElement.textContent.trim() : 'No location found',
          description: descriptionElement ? descriptionElement.textContent.trim() : 'No description found',
          url: linkElement ? linkElement.href : 'No URL found'
        };
      });
    }

    return {
      hasUpcomingAuctions: !hasNoEvents,
      upcomingAuctions: upcomingAuctions,
      currentUrl: window.location.href
    };
  });

  safeLog(log, `Scraped ${auctionInfo.upcomingAuctions.length} upcoming auctions`);
  return {
    ...auctionHouse,
    hasUpcomingAuctions: auctionInfo.hasUpcomingAuctions,
    upcomingAuctions: auctionInfo.upcomingAuctions,
    currentUrl: auctionInfo.currentUrl
  };
}

/**
 * Scrape lots from an individual auction, handling pagination
 * @param {Object} page - Puppeteer page object
 * @param {string} auctionUrl - URL of the auction
 * @param {string} companyName - Name of the auction company
 * @param {string} auctionLocation - Location of the auction
 * @param {Object} log - Blessed log object
 * @returns {Array} Array of lot objects
 */

async function scrapeAuctionLots(page, auctionUrl, companyName, auctionLocation, log) {
    safeLog(log, `Scraping lots for auction: ${auctionUrl}`);
    await page.goto(auctionUrl, { waitUntil: 'networkidle2', timeout: 60000 });
    safeLog(log, "Auction page loaded. Extracting lot information...");
  
    let allLots = [];
    let currentPage = 1;
    let maxPages = 1;
  
    while (true) {
      // Extract max page count if it's the first page
      if (currentPage === 1) {
        maxPages = await page.evaluate(() => {
          const maxPageInput = document.querySelector('input[name="MaxPageCount"]');
          return maxPageInput ? parseInt(maxPageInput.value, 10) : 1;
        });
        safeLog(log, `Total pages to scrape: ${maxPages}`);
      }
  
      const lots = await page.evaluate((companyName, auctionLocation) => {
        const lotElements = document.querySelectorAll('DIV.lotBorder');
        
        return Array.from(lotElements).map(lot => {
          const lotNumber = lot.querySelector('.lotListNumber A')?.textContent?.trim() || 'N/A';
          const itemNameElement = lot.querySelector('H2 A.responsive-width');
          const itemName = itemNameElement?.textContent?.trim() || 'N/A';
          const url = itemNameElement?.href || 'N/A';
          const currentBidPrice = lot.querySelector('.lotStatusValue SPAN:nth-of-type(2)')?.textContent?.trim() || 'N/A';
          const description = lot.querySelector('DIV.lotDesc')?.textContent?.trim() || '';
          
          let location = 'N/A';
          if (description) {
            const locationMatch = description.match(/Location:\s*([^.]+)/i);
            location = locationMatch ? locationMatch[1].trim() : auctionLocation || 'N/A';
          } else {
            location = auctionLocation || 'N/A';
          }
  
          const timeLeftElement = document.querySelector('#TimedArea');
          let timeLeft = 'N/A';
          if (timeLeftElement) {
            timeLeft = timeLeftElement.textContent.trim();
          }
  
          return {
            lot_number: lotNumber,
            item_name: itemName,
            url: url,
            current_bid_price: currentBidPrice,
            description: description || 'No description available',
            company_name: companyName,
            location: location,
            time_left: timeLeft
          };
        });
      }, companyName, auctionLocation);
  
      allLots = allLots.concat(lots);
      safeLog(log, `Scraped ${lots.length} lots from page ${currentPage}`);
  
      if (currentPage < maxPages) {
        // Navigate to the next page
        const nextPageUrl = new URL(page.url());
        nextPageUrl.searchParams.set('p', currentPage + 1);
        await page.goto(nextPageUrl.toString(), { waitUntil: 'networkidle2' });
        currentPage++;
      } else {
        break;
      }
    }
  
    safeLog(log, `Scraped a total of ${allLots.length} lots from the auction`);
    return allLots;
  }

/**
 * Main function to run the scraper
 */
(async () => {
  // Set up the dashboard
  const screen = blessed.screen({
    smartCSR: true,
    title: 'Proxibid Scraper Dashboard'
  });

  const grid = new contrib.grid({rows: 12, cols: 12, screen: screen});

  // Create a gauge for overall progress
  const overallProgress = grid.set(0, 0, 2, 12, contrib.gauge, {
    label: 'Overall Progress',
    stroke: 'green',
    fill: 'white',
    height: '20%'
  });

  // Create a scrollable log for displaying real-time updates
  const log = grid.set(2, 0, 6, 12, blessed.log, {
    fg: "green",
    selectedFg: "green",
    label: 'Scraper Log',
    border: {type: "line", fg: "cyan"},
    mouse: true,
    keys: true,
    vi: true,
    scrollable: true,
    scrollbar: {
      ch: '|',
      track: {
        bg: 'yellow'
      },
      style: {
        inverse: true
      }
    },
    wrap: true
  });

  // Create a scrollable table for displaying auction house statistics
  const table = grid.set(8, 0, 4, 12, contrib.table, {
    keys: true,
    fg: 'white',
    selectedFg: 'green',
    selectedBg: 'black',
    interactive: true,
    label: 'Auction House Stats',
    width: '100%',
    height: '30%',
    border: {type: "ascii"},
    columnSpacing: 3,
    columnWidth: [30, 10, 10],
    scrollbar: {
      ch: ' ',
      track: {
        bg: 'yellow'
      },
      style: {
        inverse: true
      }
    }
  });

  // Function to update table data
  function updateTable(data) {
    table.setData({
      headers: ['Auction House', 'Auctions', 'Lots'],
      data: data.map(ah => [
        ah.name.replace(/[^\x00-\x7F]/g, "").substring(0, 29),  // Remove non-ASCII characters and truncate
        ah.hasUpcomingAuctions ? ah.upcomingAuctions.length : 0,
        ah.hasUpcomingAuctions ? ah.upcomingAuctions.reduce((sum, auction) => sum + (auction.lots ? auction.lots.length : 0), 0) : 0
      ])
    });
  }

  // Render the initial dashboard
  screen.render();

  safeLog(log, "Starting the Proxibid scraper script...");
  
  // Launch a new browser instance
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars', '--window-position=0,0', '--ignore-certifcate-errors', '--ignore-certifcate-errors-spki-list'],
  });
  safeLog(log, "Browser launched successfully");

  // Create a new page
  const page = await browser.newPage();
  safeLog(log, "New page created");

  // Set user agent and viewport
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
  await page.setViewport({ width: 1920, height: 1080 });
  safeLog(log, "User agent and viewport set");

  // Navigate to the main Iowa auction houses page
  safeLog(log, "Navigating to the Iowa auction houses page...");
  await page.goto('https://www.proxibid.com/asp/auction-companies.asp?AHName=&AHCountryID=1&AHState=Iowa', {
    waitUntil: 'networkidle2',
    timeout: 60000
  });
  safeLog(log, "Iowa auction houses page loaded");

  // Extract auction house data from the main page
  safeLog(log, "Extracting auction house data...");
  const auctionHouseData = await page.evaluate(() => {
    const auctionHouses = document.querySelectorAll('.AHLine');
    return Array.from(auctionHouses).map(ah => {
      const linkElement = ah.querySelector('.AHLink');
      return {
        name: linkElement.textContent.trim(),
        url: linkElement.href
      };
    });
  });

  safeLog(log, `Found ${auctionHouseData.length} auction houses`);

  const updatedAuctionHouseData = [];
  let totalAuctions = 0;
  let totalLots = 0;

  // Process each auction house
  for (let i = 0; i < auctionHouseData.length; i++) {
    if (isCancelled) {
      safeLog(log, "Operation cancelled by user.");
      break;
    }

    const auctionHouse = auctionHouseData[i];
    // Update overall progress
    overallProgress.setPercent((i + 1) / auctionHouseData.length * 100);
    safeLog(log, `Processing auction house ${i + 1}/${auctionHouseData.length}: ${auctionHouse.name}`);
    
    // Scrape individual auction house page
    const updatedAuctionHouse = await scrapeAuctionHouse(page, auctionHouse, log);
    updatedAuctionHouseData.push(updatedAuctionHouse);

    if (updatedAuctionHouse.hasUpcomingAuctions) {
      safeLog(log, `Found ${updatedAuctionHouse.upcomingAuctions.length} upcoming auctions for ${auctionHouse.name}`);
      totalAuctions += updatedAuctionHouse.upcomingAuctions.length;
      
      // Scrape lots for each upcoming auction
      for (const auction of updatedAuctionHouse.upcomingAuctions) {
        if (isCancelled) break;
        safeLog(log, `Scraping lots for auction: ${auction.title}`);
        const lots = await scrapeAuctionLots(page, auction.url, updatedAuctionHouse.name, auction.location, log);
        auction.lots = lots;
        totalLots += lots.length;
        safeLog(log, `Scraped ${lots.length} lots for this auction`);
      }
    } else {
      safeLog(log, `No upcoming auctions found for ${auctionHouse.name}`);
    }

    // Update the table with the latest stats
    updateTable(updatedAuctionHouseData);

    // Render the updated dashboard
    screen.render();
  }

  // Write the collected data to a JSON file
  safeLog(log, "\nAll auction houses processed. Writing data to file...");
  const jsonData = JSON.stringify(updatedAuctionHouseData, null, 2);
  await fs.writeFile('iowa_auction_houses.json', jsonData);
  safeLog(log, "Data successfully written to iowa_auction_houses.json");

  // Print summary of scraping results
  safeLog(log, "\n--- Scraping Summary ---");
  safeLog(log, `Total auction houses processed: ${updatedAuctionHouseData.length}`);
  safeLog(log, `Total upcoming auctions found: ${totalAuctions}`);
  safeLog(log, `Total lots scraped: ${totalLots}`);

  // Close the browser
  safeLog(log, "Closing browser...");
  await browser.close();
  safeLog(log, "Browser closed. Script execution complete.");

  // Render the final dashboard
  screen.render();
  
  // Set up key bindings
  screen.key(['escape', 'q', 'C-c'], function(ch, key) {
    clearTimeout(exitTimer);  // Clear the auto-exit timer
    isCancelled = true;
    safeLog(log, "Cancelling operation...");
    return process.exit(0);
  });

  screen.key(['S-up', 'S-down'], function(ch, key) {
    if (key.name === 'up') {
      log.setScrollPerc(log.getScrollPerc() - 10);
    } else if (key.name === 'down') {
      log.setScrollPerc(log.getScrollPerc() + 10);
    }
    screen.render();
  });

  // Instructions for user
  safeLog(log, "\nPress 'q', 'Esc', or 'Ctrl+C' to exit.");
  safeLog(log, "Use Shift+Up and Shift+Down to scroll the log.");
  safeLog(log, "Auto-exiting in 5 seconds if no key is pressed...");

  // Set up auto-exit timer
  const exitTimer = setTimeout(() => {
    safeLog(log, "No input received. Auto-exiting...");
    process.exit(0);
  }, 5000);

  // Keep the script running
  screen.render();
})();
