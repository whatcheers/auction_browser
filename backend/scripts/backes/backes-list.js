const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function scrapeAuctions(baseUrl, queryParams, pageSize) {
    // Initialize Processed URLs Storage
    const processedUrls = new Set(fs.existsSync('processed_urls.txt') ?
        fs.readFileSync('processed_urls.txt', 'utf-8').split('\n').filter(Boolean) : []);

    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36');

    // Set the viewport size
    await page.setViewport({ width: 1920, height: 1080 });

    const url = `${baseUrl}${queryParams}`;
    console.log(`Navigating to auction list page: ${url}`);
    await page.goto(url);

    // Get all the auction tiles and their URLs
    console.log('Finding auction tiles...');
    const auctionTiles = await page.$$eval('.auction', tiles =>
        tiles.map(tile => ({
            name: tile.querySelector('.auctionTitle').textContent,
            url: tile.querySelector('.enterAuction').href
        }))
    );
    console.log(`Found ${auctionTiles.length} auction tiles.`);

    let newItemsCount = 0;

    for (const [index, auction] of auctionTiles.entries()) {
        console.log(`\nProcessing auction "${auction.name}" (${index + 1}/${auctionTiles.length})...`);

        // Duplicate Check During URL Processing
        if (processedUrls.has(auction.url)) {
            console.log(`Skipping previously processed URL: ${auction.url}`);
            continue;
        }
        newItemsCount++;

        console.log(`Navigating to auction page: ${auction.url}`);
        await page.goto(auction.url);

        console.log('Waiting for 4 seconds for auction page to load...');
        await new Promise(resolve => setTimeout(resolve, 4000));
        console.log('Auction page loaded successfully.');

        let currentPage = 1;
        const auctionPages = [];

        while (true) {
            // Save the current page as a file
            const fileName = `${auction.name.replace(/\s/g, '')}-page${currentPage}.html`;
            const filePath = path.join(__dirname, fileName);
            const pageContent = await page.content();
            fs.writeFileSync(filePath, pageContent);
            console.log(`Saved page ${currentPage} as ${fileName}`);

            auctionPages.push(filePath);

            // Check for the "Next Page" link
            const nextPageLink = await page.$('a.next[title="Next Page"]');
            if (nextPageLink) {
                console.log('Clicking "Next Page" link...');
                await nextPageLink.click();
                console.log('Waiting for 4 seconds for next page to load...');
                await new Promise(resolve => setTimeout(resolve, 4000));
                console.log('Next page loaded successfully.');
                currentPage++;
            } else {
                console.log('No more pages found.');
                break;
            }
        }

        // Combine the HTML files into a single file
        const combinedFileName = `${auction.name.replace(/\s/g, '')}.html`;
        const combinedFilePath = path.join(__dirname, combinedFileName);
        const combinedContent = auctionPages.map(file => fs.readFileSync(file, 'utf8')).join('');
        fs.writeFileSync(combinedFilePath, combinedContent);
        console.log(`Combined ${auctionPages.length} pages into ${combinedFileName}`);

        // Update Storage After Processing
        processedUrls.add(auction.url);
        fs.appendFileSync('processed_urls.txt', `${auction.url}\n`);

        // Delete the individual page files
        auctionPages.forEach(file => fs.unlinkSync(file));
        console.log('Deleted individual page files.');
    }

    // Set Exit Code
    if (newItemsCount === 0) {
        console.log("No new items found.");
        process.exit(2);
    } else {
        console.log(`Successfully processed ${newItemsCount} new items.`);
        process.exit(0);
    }

    console.log('Closing browser...');
    await browser.close();
    console.log('Done!');
}

// Example usage
const baseUrl = 'https://backes.auctioneersoftware.com/auctions?';
const queryParams = 'page=1&pageSize=100&search=&sort=null&currentDisplay=tile&websiteDisplay%5B0%5D=tile&canToggle=false';
const pageSize = 100;

scrapeAuctions(baseUrl, queryParams, pageSize);