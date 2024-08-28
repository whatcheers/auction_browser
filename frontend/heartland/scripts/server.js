const express = require('express');
const { exec } = require('child_process');
const cors = require('cors'); // Require the cors package
const app = express();
const port = 31415;

// Use CORS middleware to allow cross-origin requests
// You can configure CORS options here as needed
app.use(cors());

// Middleware to parse JSON request bodies
app.use(express.json());

// POST endpoint to execute the shell script
app.post('/execute', (req, res) => {
    const { auctionNumber } = req.body;
    
    // Validate the auction number is a positive integer
    if (!/^\d+$/.test(auctionNumber)) {
        return res.status(400).json({ error: "Invalid auction number. Must be a positive integer." });
    }
    
    const scriptCommand = `./scrape-heartland.sh ${auctionNumber}`;

    // Execute the shell script with the auction number
    exec(scriptCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution error: ${error}`);
            return res.status(500).json({ error: `Execution error: ${error.message}` });
        }
        res.json({ stdout, stderr });
    });
});

// Start the server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
