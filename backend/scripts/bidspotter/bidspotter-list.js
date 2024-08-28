const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function scrapeAuctions(baseUrl, queryParams, pageSize) {
  const auctionDetails = [];
  const scrapedUrls = loadScrapedUrls(); // Load previously scraped URLs
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36');

  const url = `${baseUrl}${queryParams}`;
  console.log(`Navigating to auction list page: ${url}`);
  await page.goto(url, { waitUntil: 'networkidle2' });

  console.log('Finding auction tiles...');
  const auctionTiles = await page.$$eval('.auction-summary-standard', tiles =>
    tiles.map(tile => ({
      title: tile.querySelector('.auction-title a')?.textContent.trim() || '',
      date: tile.querySelector('.auction-sale-dates time')?.getAttribute('datetime') || '',
      location: tile.querySelector('.auction-location span')?.textContent.trim() || '',
      description: tile.querySelector('.auction-subtitle')?.textContent.trim() || '',
      url: `https://www.bidspotter.com${tile.querySelector('.auction-title a')?.getAttribute('href') || ''}`
    }))
  );
  console.log(`Found ${auctionTiles.length} auction tiles.`);

  for (const auction of auctionTiles) {
    const auctionUrl = auction.url;
    if (scrapedUrls.has(auctionUrl)) {
      console.log(`Skipping previously scraped auction: ${auctionUrl}`);
      continue;
    }

    console.log(`\nProcessing auction "${auction.title}"...`);
    console.log(`Navigating to auction page: ${auctionUrl}`);
    await page.goto(auctionUrl, { waitUntil: 'networkidle2' });
    console.log('Auction page loaded successfully.');

    let hasMoreLots = true;
    while (hasMoreLots) {
      const lotItems = await page.$$eval('.panel.item', (lots) =>
        lots.map(lot => ({
          item_name: lot.querySelector('.lot-title')?.textContent.trim() || '',
          location: lot.querySelector('.lotlocation strong')?.textContent.trim() || '',
          current_bid: parseFloat(lot.querySelector('.opening-price strong')?.textContent.trim() || '0'),
          lot_number: lot.querySelector('.lot-number')?.textContent.trim() || '',
          url: `https://www.bidspotter.com${lot.querySelector('.a-wrapped[data-lot-id]')?.getAttribute('href') || ''}`,
          time_left: lot.querySelector('.date.countdown')?.textContent.trim() || ''
        }))
      );

      auctionDetails.push(...lotItems);

      const nextPageButton = await page.$('.pagination-pages .prev-next-element a[rel="next"]');
      if (nextPageButton) {
        console.log('Clicking "Next Page" button...');
        await nextPageButton.click();
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
        console.log('Next page loaded successfully.');
      } else {
        console.log('No more lots found for this auction.');
        hasMoreLots = false;
      }
    }

    scrapedUrls.add(auctionUrl);
  }

  saveScrapedUrls(scrapedUrls); // Save updated set of scraped URLs
  const fileName = 'auction-details.json';
  const filePath = path.join(__dirname, fileName);
  fs.writeFileSync(filePath, JSON.stringify(auctionDetails, null, 2));
  console.log(`Saved auction details to ${fileName}`);

  console.log('Closing browser...');
  await browser.close();
  console.log('Done!');
}

function loadScrapedUrls() {
  const filePath = path.join(__dirname, 'processed_urls.txt');
  return new Set(fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf-8').split('\n').filter(Boolean) : []);
}

function saveScrapedUrls(scrapedUrls) {
  const filePath = path.join(__dirname, 'processed_urls.txt');
  fs.writeFileSync(filePath, Array.from(scrapedUrls).join('\n'));
}

// Example usage
const baseUrl = 'https://www.bidspotter.com/en-us/auction-catalogues/search-filter?';
const queryParams = 'country=US&state=IA&countyState=Iowa&pagesize=120';
const pageSize = 120;

scrapeAuctions(baseUrl, queryParams, pageSize);
