const puppeteer = require('../../node_modules/puppeteer');
const fs = require('fs');

// Initialize the processed URLs storage
const processedUrls = new Set();

// Function to automatically scroll through the page
async function autoScroll(page) {
    await page.evaluate(async () => {
        await new Promise((resolve) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if (totalHeight >= scrollHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

(async () => {
    console.log('Starting the script...');

    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();

    const fullUrl = 'https://gsaauctions.gov/auctions/auctions-list?page=1&size=50&searchType=ALL_WORDS&status=active&zipCode=52403&radius=radius-200&advanced=true';
    console.log(`Navigating to URL: ${fullUrl}`);
    await page.goto(fullUrl, { waitUntil: 'networkidle0' });

    console.log('Scrolling through the page...');
    await autoScroll(page);

    console.log('Extracting auction details...');
    const auctionItemsSelector = '.item-search-result-wrapper .usa-card-group.ppms-card-group.icn-card .usa-card';
    const auctionDetails = await page.evaluate((selector) => {
        const baseUrl = 'https://gsaauctions.gov';
        const items = Array.from(document.querySelectorAll(selector));
        return items.map(item => {
            const item_name = item.querySelector('.auction-name') ? item.querySelector('.auction-name').textContent.replace('Lot Name', '').trim() : '';
            const location = item.querySelector('.auction-location') ? item.querySelector('.auction-location').textContent.replace('Location', '').trim() : '';
            const time_left = item.querySelector('li:nth-child(3)') ? item.querySelector('li:nth-child(3)').textContent.replace('Closing Date', '').trim() : '';
            const urlElement = item.querySelector('.usa-card__header a');
            const url = urlElement ? baseUrl + urlElement.getAttribute('href') : '';

            return { item_name, location, url, time_left };
        });
    }, auctionItemsSelector);

    // Duplicate check during URL processing
    const uniqueAuctionDetails = auctionDetails.filter(details => {
        if (!processedUrls.has(details.url)) {
            processedUrls.add(details.url);
            return true;
        }
        console.log(`Skipping URL: ${details.url} (already processed)`);
        return false;
    });

    // Writing the unique auction details to a JSON file
    const filePath = 'auctionDetails.json';
    fs.writeFile(filePath, JSON.stringify(uniqueAuctionDetails, null, 2), 'utf8', (err) => {
        if (err) {
            console.error('An error occurred while writing JSON Object to File.', err);
        } else {
            console.log(`JSON file has been saved with the latest auction details to ${filePath}.`);
        }
    });

    // Save the processed URLs to a file
    const processedUrlsFilePath = 'processed_urls.txt';
    fs.writeFile(processedUrlsFilePath, Array.from(processedUrls).join('\n'), 'utf8', (err) => {
        if (err) {
            console.error('An error occurred while writing processed URLs to File.', err);
        } else {
            console.log(`Processed URLs have been saved to ${processedUrlsFilePath}.`);
        }
    });

    await browser.close();
    console.log('Browser closed. Script execution complete.');
})();