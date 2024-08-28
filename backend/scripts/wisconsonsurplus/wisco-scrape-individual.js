const colors = require('colors');
const mysql = require('mysql2/promise');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Auction URL provided via command-line argument
const auctionUrl = process.argv[2];

if (!auctionUrl) {
    console.log(colors.red("Please provide an auction URL."));
    process.exit(1);
}

// Prints the starting message
console.log(colors.green('Starting the script...'));

// Function to automatically scroll through the page
async function autoScroll(page) {
    await page.evaluate(async () => {
        await new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 100;
            const timer = setInterval(() => {
                const scrollHeight = document.body.scrollHeight;
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

// Function to ensure the 'processed' column exists
async function ensureProcessedColumnExists(connection) {
    const columnCheckQuery = `
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'auctions' 
        AND TABLE_NAME = 'upcoming_wisco_list' 
        AND COLUMN_NAME = 'processed';
    `;

    const [columns] = await connection.query(columnCheckQuery);

    if (columns.length === 0) {
        console.log(colors.yellow('Processed column not found, adding it...'));
        const addColumnQuery = `
            ALTER TABLE upcoming_wisco_list
            ADD COLUMN processed BOOLEAN DEFAULT FALSE;
        `;
        await connection.query(addColumnQuery);
        console.log(colors.green('Processed column added successfully.'));
    } else {
        console.log(colors.green('Processed column already exists.'));
    }
}

// Main script execution
(async () => {
    console.log(colors.green('Starting the script...'));

    // Create a MySQL connection
    const connection = await mysql.createConnection({
        host: 'localhost',
        user: 'whatcheer',
        password: 'meatwad',
        database: 'auctions'
    });

    try {
        // Ensure the 'processed' column exists in the database
        await ensureProcessedColumnExists(connection);

        // Fetch the auction number associated with the URL
        const [rows] = await connection.query(`
            SELECT auction_number
            FROM upcoming_wisco_list
            WHERE url_to_view_items = ?
        `, [auctionUrl]);

        // Check if the auction exists
        if (rows.length === 0) {
            console.log(colors.red('Auction URL not found in the database. Exiting the script.'));
            return;
        }

        const auctionNumber = rows[0]['auction_number'];

        try {
            // Start Puppeteer browser instance
            const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
            const page = await browser.newPage();

            console.log(colors.green(`Navigating to URL: ${auctionUrl}`));
            await page.goto(auctionUrl, { waitUntil: 'networkidle2' });

            // Scroll through the page
            console.log(colors.green('Starting to scroll through the page...'));
            await autoScroll(page);

            // Save the page content to a file
            const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14); // YYYYMMDDHHMMSS
            const filename = `auction_${auctionNumber}_${timestamp}_content.html`;
            fs.writeFileSync(filename, await page.content());
            console.log(colors.green(`Page content saved to "${filename}".`));

            await browser.close();
            console.log(colors.green('Browser closed.'));

            console.log(colors.green('Calling Python script...'));
            // Pass the filename as an argument to the Python script
            execSync(`python3 wisco-scrape-extract.py --file ${filename}`, { stdio: 'inherit' });
            } catch (error) {
            console.error(colors.red(`Error processing auction ${auctionNumber}: ${error.message}`));
            console.error(colors.red(`URL provided: ${auctionUrl}`));
        } finally {
            // Update the database to mark this auction as processed, even if an error occurred
            await connection.query(`
                UPDATE upcoming_wisco_list
                SET processed = 1
                WHERE auction_number = ?
            `, [auctionNumber]);

            console.log(colors.green(`Auction ${auctionNumber} marked as processed.`));
        }
    } catch (error) {
        console.error(colors.red('Error:', error));
    } finally {
        await connection.end();
        console.log(colors.green('Script execution complete.'));
    }
})();
