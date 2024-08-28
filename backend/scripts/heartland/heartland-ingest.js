const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const initBrowser = async () => {
    return puppeteer.launch({ headless: true });
};

const scrollToEndOfPage = async (page) => {
    await page.evaluate(async () => {
        const distance = 100;
        const delay = 100;
        while (window.scrollY + window.innerHeight < document.body.scrollHeight) {
            window.scrollBy(0, distance);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    });
};

const scrapePage = async (browser, base_url, page_number, allItems) => {
    let page;
    try {
        page = await browser.newPage();
        const url = `${base_url}?page=${page_number}`;
        await page.goto(url, { waitUntil: 'networkidle0' });
        await scrollToEndOfPage(page);

        const endDate = await page.evaluate(() => {
            const endDateElement = document.querySelector('li span.text-xs.font-semibold.inline-block.py-1.px-2.my-1.rounded-full.text-white.bg-green-500');
            return endDateElement ? endDateElement.nextSibling.textContent.trim() : 'Unknown End Date';
        });

        const itemsDetails = await page.evaluate((endDate) => {
            const items = [];
            document.querySelectorAll('.background-white.rounded-md.border.border-gray-200.shadow-md.overflow-hidden').forEach((item) => {
                const itemName = item.querySelector('p')?.innerText || 'No name';
                const lotNumberDiv = item.querySelector('.font-bold.mb-2')?.innerText || 'Lot # Not Set';
                const url = item.querySelector('a[href*="/auction/"]')?.href || 'No URL';
                
                const lotNumber = lotNumberDiv.includes('Lot #') ? lotNumberDiv.replace('Lot #', '').trim() : '10000';
                
                items.push({
                    item_name: itemName, // Preserving the full name
                    location: "2860 Industrial Park Rd., Iowa City, IA 52240",
                    current_bid: 0.00,
                    lot_number: lotNumber,
                    time_left: endDate,
                    url: url
                });
            });
            return items;
        }, endDate);

        allItems.push(...itemsDetails);
        console.log(`Extracted item details from page ${page_number}.`);

        const hasNextPage = await page.evaluate(() => {
            const nextButton = document.querySelector('a[href*="page="]:not([href*="page=1"]):last-child');
            return !!nextButton && !nextButton.textContent.includes('Previous');
        });

        if (page) await page.close();
        return hasNextPage;
    } catch (error) {
        console.error(`Error scraping page ${page_number}:`, error);
        if (page) await page.close();
        return false;
    }
};

const main = async () => {
    const auctionNumber = process.argv[2];
    if (!auctionNumber) {
        console.error("Please provide an auction number as an argument.");
        process.exit(1);
    }

    const base_url = `https://www.heartlandrecoveryinc.com/auctions/${auctionNumber}`;
    console.log(`Base URL: ${base_url}`);

    const browser = await initBrowser();
    let page_number = 1;
    let continueScraping = true;
    let allItems = []; // Array to hold all items from all pages
    while (continueScraping) {
        continueScraping = await scrapePage(browser, base_url, page_number, allItems);
        page_number += 1;
    }
    await browser.close();

    fs.writeFileSync('all_items.json', JSON.stringify(allItems, null, 2)); // Write all items to a single file
    console.log(`Scraping completed. All items saved to all_items.json.`);
};

main().catch(console.error);
