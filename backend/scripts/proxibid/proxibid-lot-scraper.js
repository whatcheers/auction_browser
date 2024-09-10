const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const moment = require('moment');

// Flag to control the scraping process
let isCancelled = false;

let stats = {
  auctions_scraped: 0,
  items_added: 0,
  items_updated: 0,
  items_removed: 0,
  items_skipped: 0,
  errors: 0,
  addresses_processed: 0,
  addresses_updated: 0,
  addresses_skipped: 0
};

/**
 * Safely log messages by removing non-ASCII characters
 * @param {string} message - The message to log
 */
function safeLog(message) {
  console.log(message.replace(/[^\x00-\x7F]/g, ""));
}

/**
 * Scrape individual auction house pages
 * @param {Object} page - Puppeteer page object
 * @param {Object} auctionHouse - Auction house data
 * @returns {Object} Updated auction house data
 */
async function scrapeAuctionHouse(page, auctionHouse) {
  safeLog(`Scraping auction house: ${auctionHouse.name}`);
  safeLog(`Navigating to URL: ${auctionHouse.url}`);
  
  await page.goto(auctionHouse.url, { waitUntil: 'networkidle2', timeout: 60000 });
  safeLog("Page loaded. Extracting auction information...");

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

  safeLog(`Scraped ${auctionInfo.upcomingAuctions.length} upcoming auctions`);

  // Load previously scraped data
  let previousData = [];
  try {
    const data = await fs.readFile('previous_auctions.json', 'utf8');
    previousData = JSON.parse(data);
  } catch (error) {
    safeLog("No previous data found. Starting fresh.");
  }

  return {
    ...auctionHouse,
    ...auctionInfo
  };
}

/**
 * Scrape lots for a given auction
 * @param {Object} page - Puppeteer page object
 * @param {string} auctionUrl - URL of the auction
 * @param {string} auctionHouseName - Name of the auction house
 * @param {string} auctionLocation - Location of the auction
 * @returns {Array} List of lots
 */
async function scrapeAuctionLots(page, auctionUrl, auctionHouseName, auctionLocation) {
  safeLog(`Navigating to auction URL: ${auctionUrl}`);
  await page.goto(auctionUrl, { waitUntil: 'networkidle2', timeout: 60000 });
  safeLog("Auction page loaded. Extracting lot information...");

  const lots = await page.evaluate(() => {
    const lotElements = document.querySelectorAll('.lot-item');
    return Array.from(lotElements).map(lot => {
      const lotNumberElement = lot.querySelector('.lot-number');
      const itemNameElement = lot.querySelector('.lot-title');
      const currentBidPriceElement = lot.querySelector('.current-bid');
      const descriptionElement = lot.querySelector('.lot-description');

      return {
        lot_number: lotNumberElement ? lotNumberElement.textContent.trim() : 'No lot number found',
        item_name: itemNameElement ? itemNameElement.textContent.trim() : 'No item name found',
        current_bid_price: currentBidPriceElement ? currentBidPriceElement.textContent.trim() : 'N/A',
        description: descriptionElement ? descriptionElement.textContent.trim() : 'No description found'
      };
    });
  });

  safeLog(`Scraped ${lots.length} lots from auction`);

  return lots;
}

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Set user agent and viewport
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
  await page.setViewport({ width: 1920, height: 1080 });
  safeLog("User agent and viewport set");

  // Navigate to the main Iowa auction houses page
  safeLog("Navigating to the Iowa auction houses page...");
  await page.goto('https://www.proxibid.com/asp/auction-companies.asp?AHName=&AHCountryID=1&AHState=Iowa', {
    waitUntil: 'networkidle2',
    timeout: 60000
  });
  safeLog("Iowa auction houses page loaded");

  // Extract auction house data from the main page
  safeLog("Extracting auction house data...");
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

  safeLog(`Found ${auctionHouseData.length} auction houses`);
  stats.total_auction_houses = auctionHouseData.length;

  const updatedAuctionHouseData = [];
  let totalAuctions = 0;
  let totalLots = 0;

  // Process each auction house
  for (let i = 0; i < auctionHouseData.length; i++) {
    if (isCancelled) {
      safeLog("Operation cancelled by user.");
      break;
    }

    const auctionHouse = auctionHouseData[i];
    safeLog(`Processing auction house ${i + 1}/${auctionHouseData.length}: ${auctionHouse.name}`);
    
    // Scrape individual auction house page
    const updatedAuctionHouse = await scrapeAuctionHouse(page, auctionHouse);
    updatedAuctionHouseData.push(updatedAuctionHouse);

    if (updatedAuctionHouse.hasUpcomingAuctions) {
      safeLog(`Found ${updatedAuctionHouse.upcomingAuctions.length} upcoming auctions for ${auctionHouse.name}`);
      stats.total_auctions += updatedAuctionHouse.upcomingAuctions.length;
      
      // Scrape lots for each upcoming auction
      for (const auction of updatedAuctionHouse.upcomingAuctions) {
        if (isCancelled) break;
        safeLog(`Scraping lots for auction: ${auction.title}`);
        const lots = await scrapeAuctionLots(page, auction.url, updatedAuctionHouse.name, auction.location);
        auction.lots = lots;
        stats.total_lots += lots.length;
        safeLog(`Scraped ${lots.length} lots for this auction`);
      }
    } else {
      safeLog(`No upcoming auctions found for ${auctionHouse.name}`);
    }
  }

  // Update statistics
  stats.auctions_scraped += updatedAuctionHouseData.length;
  stats.items_added += stats.total_lots;

  // Write the collected data to a JSON file
  safeLog("\nAll auction houses processed. Writing data to file...");
  const jsonData = JSON.stringify(updatedAuctionHouseData, null, 2);
  await fs.writeFile('iowa_auction_houses.json', jsonData);
  safeLog("Data successfully written to iowa_auction_houses.json");

  // Save statistics
  const statsJson = JSON.stringify(stats, null, 2);
  await fs.writeFile('proxibid_statistics.json', statsJson);
  safeLog("Statistics saved to proxibid_statistics.json");

  // Print summary of scraping results
  safeLog("\n--- Scraping Summary ---");
  safeLog(`Total auction houses processed: ${stats.total_auction_houses}`);
  safeLog(`Total upcoming auctions found: ${stats.total_auctions}`);
  safeLog(`Total lots scraped: ${stats.total_lots}`);

  // Close the browser
  safeLog("Closing browser...");
  await browser.close();
  safeLog("Browser closed. Script execution complete.");
})();