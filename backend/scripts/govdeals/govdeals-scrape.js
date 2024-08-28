const puppeteer = require('../../node_modules/puppeteer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process'); // Include child_process to run Python script

const baseUrl = 'https://www.govdeals.com/search/filters';
const queryParams = '?zipcode=52403&miles=250&showMap=0&source=location-search&pn=';
const pageSize = 120; // This is assumed from your URL, adjust if necessary

// Additional utility functions for date and subprocess execution
const { format } = require('date-fns'); // Make sure to install date-fns or replace with another date formatter

async function hasNextPage(page) {
    // Check if the "Next Page" button exists
    const nextPageButtonExists = await page.evaluate(() => {
        const nextPageButton = document.querySelector('li[data-type="nextPage"] a');
        return nextPageButton !== null;
    });
    return nextPageButtonExists;
}

async function autoScroll(page){
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

async function scrapePages(baseUrl, queryParams, pageSize) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36');

    await page.goto(`${baseUrl}${queryParams}1&so=&sf=bestfit&ps=${pageSize}`, {waitUntil: 'networkidle2'});

    let currentPageNum = 1;
    let htmlFiles = [];

    while (true) { // Use an infinite loop that we will break out of when there's no next page
        console.log(`Scraping page ${currentPageNum}`);
        
        await autoScroll(page);

        const outputPath = path.resolve(__dirname, `output_page_${currentPageNum}.html`);
        const pageContent = await page.content();
        fs.writeFileSync(outputPath, pageContent);
        htmlFiles.push(outputPath);

        const hasNext = await hasNextPage(page);
        if (!hasNext) break; // If there's no next page, exit the loop

        // Increment the page number and navigate to the next page
        currentPageNum++;
        await page.goto(`${baseUrl}${queryParams}${currentPageNum}&so=&sf=bestfit&ps=${pageSize}`, {waitUntil: 'networkidle2'});
    }

    const consolidatedHtmlFile = path.resolve(__dirname, `consolidated-output-${new Date().toISOString().replace(/T.*/, '').replace(/-/g, '')}.html`);
    fs.writeFileSync(consolidatedHtmlFile, '', { encoding: 'utf-8' }); // Create or clear the file

    htmlFiles.forEach(htmlFile => {
        const content = fs.readFileSync(htmlFile, { encoding: 'utf-8' });
        fs.appendFileSync(consolidatedHtmlFile, content, { encoding: 'utf-8' });
        fs.unlinkSync(htmlFile); // Delete the individual HTML file after consolidating
    });

    console.log(`Consolidated HTML file created: ${consolidatedHtmlFile}`);

    // Execute the Python script on the consolidated HTML file
    console.log(`Starting the JSON conversion script on the file: ${consolidatedHtmlFile}`);
    exec(`python3 govdeals-extract.py ${consolidatedHtmlFile}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution error: ${error}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
        if (stderr) {
            console.error(`stderr: ${stderr}`);
        }
    });

    await page.close();
    await browser.close();
}

// Start scraping
scrapePages(baseUrl, queryParams, pageSize).catch(console.error);




