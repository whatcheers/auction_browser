const puppeteer = require('puppeteer');
const fs = require('fs');

function convertToISODate(dateString) {
  const [_, month, day, year, time, ampm] = dateString.match(/(\w{3})\s+(\d{1,2})\s+(\d{4})\s+(\d{1,2}:\d{2})\s+(\w{2})/);
  const monthMap = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 };
  const [hours, minutes] = time.split(':');
  let hour = parseInt(hours);
  if (ampm === 'PM' && hour !== 12) hour += 12;
  if (ampm === 'AM' && hour === 12) hour = 0;
  const date = new Date(year, monthMap[month], day, hour, minutes);
  return date.toISOString();
}

function loadPreviousAuctions() {
  try {
    const data = fs.readFileSync('auction_list.json', 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('No previous auction data found or error reading file.');
    return [];
  }
}

function hasNewAuctions(previousAuctions, currentAuctions) {
  if (previousAuctions.length !== currentAuctions.length) return true;

  const previousUrls = new Set(previousAuctions.map(auction => auction.auctionUrl));
  for (const auction of currentAuctions) {
    if (!previousUrls.has(auction.auctionUrl)) return true;
  }

  return false;
}

async function main() {
  let browser;
  const stats = {
    auctions_scraped: 0,
    new_auctions_found: 0,
    errors: 0,
    items_added: 0,
    items_updated: 0,
    items_removed: 0,
    items_skipped: 0,
    addresses_processed: 0,
    addresses_updated: 0,
    addresses_skipped: 0
  };

  async function updateStatistics() {
    try {
      const data = await fs.promises.readFile('smc_statistics.json', 'utf8');
      const existingStats = JSON.parse(data);
      for (const key in stats) {
        existingStats[key] = (existingStats[key] || 0) + stats[key];
      }
      await fs.promises.writeFile('smc_statistics.json', JSON.stringify(existingStats, null, 2));
    } catch (error) {
      await fs.promises.writeFile('smc_statistics.json', JSON.stringify(stats, null, 2));
    }
  }

  try {
    console.log('Starting the scraping process...');
    browser = await puppeteer.launch({ headless: true });
    console.log('Browser launched');
    const page = await browser.newPage();
    console.log('New page created');

    const mainUrl = 'https://smc.prod4.maxanet.auction/Public/Auction/All';
    console.log(`Navigating to main auction page: ${mainUrl}`);
    await page.goto(mainUrl, { waitUntil: 'networkidle0' });
    console.log('Main page loaded');

    console.log('Extracting auction information...');
    const auctionData = await page.evaluate(() => {
      const auctionItems = Array.from(document.querySelectorAll('.col-lg-8.col-md-9.col-sm-12.flex-wrap'));
      console.log(`Found ${auctionItems.length} auction items on the page`);
      return auctionItems.map(item => {
        const auctionUrl = item.querySelector('.auction-gridhead a')?.href;
        const auctionName = item.querySelector('.auction-gridhead a')?.textContent.trim();
        const endDateString = item.querySelectorAll('.local-date-time[data-auc-date]')[1]?.textContent.replace(':', '').trim();
        
        console.log(`Extracted auction: ${auctionName}, URL: ${auctionUrl}, End Date: ${endDateString}`);
        return {
          auctionUrl,
          auctionName,
          endDateString
        };
      });
    });

    if (!auctionData || auctionData.length === 0) {
      console.log('No auction data found on the page. The page structure might have changed.');
      stats.errors++;
      return;
    }

    stats.auctions_scraped = auctionData.length;
    console.log(`Found ${auctionData.length} auctions`);

    // Load previous auction data
    const previousAuctions = loadPreviousAuctions();

    // Check if there are new auctions
    if (!hasNewAuctions(previousAuctions, auctionData)) {
      console.log('No new auctions found. Exiting...');
      return;
    }

    const results = auctionData.map((auction, index) => {
      const endDate = convertToISODate(auction.endDateString);
      console.log(`Processed auction ${index + 1}/${auctionData.length}`);
      console.log(`Auction Name: ${auction.auctionName}`);
      console.log(`End Date: ${endDate}`);
      console.log(`URL: ${auction.auctionUrl}`);
      console.log('---');
      return {
        auctionName: auction.auctionName,
        endDate: endDate,
        auctionUrl: auction.auctionUrl
      };
    });

    stats.new_auctions_found = results.length - previousAuctions.length;
    console.log('Scraping completed.');

    // Save results to a JSON file
    fs.writeFileSync('auction_list.json', JSON.stringify(results, null, 2));
    console.log('Results saved to auction_list.json');

  } catch (error) {
    console.error('An error occurred during scraping:', error);
    console.error('Stack trace:', error.stack);
    stats.errors++;
  } finally {
    if (browser) {
      await browser.close();
      console.log('Browser closed.');
    }

    // Save statistics
    await updateStatistics();
    console.log('Statistics saved to smc_statistics.json');
  }
}

main().catch(error => {
  console.error('An unhandled error occurred:', error);
  console.error('Stack trace:', error.stack);
  process.exit(1);
});