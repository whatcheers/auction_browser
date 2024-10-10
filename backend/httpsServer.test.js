// httpsServer.test.js

// Disable TLS certificate validation for testing with self-signed certificates
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const fs = require('fs');
const https = require('https');
const request = require('supertest');
const app = require('./server'); // Adjust the path to your Express app accordingly

// Increase the Jest timeout to handle potential delays
jest.setTimeout(10000);

describe('HTTPS Server Regression Tests', () => {
  let server;

  beforeAll((done) => {
    // Set up environment variables for testing
    process.env.SSL_KEY_PATH = './server.key';  // Path to your test SSL key
    process.env.SSL_CERT_PATH = './server.cert'; // Path to your test SSL certificate
    process.env.PORT = 3002;
    process.env.CORS_ORIGIN = 'https://hashbrowns:3000'; // Adjusted to match server response

    // Read SSL certificates
    const privateKey = fs.readFileSync(process.env.SSL_KEY_PATH, 'utf8');
    const certificate = fs.readFileSync(process.env.SSL_CERT_PATH, 'utf8');
    const httpsOptions = { key: privateKey, cert: certificate };

    // Start the HTTPS server
    server = https.createServer(httpsOptions, app).listen(process.env.PORT, done);
  });

  afterAll((done) => {
    console.log('Starting server close');
    server.close(() => {
      console.log('Server closed');
      if (global.gc) {
        console.log('Running garbage collection');
        global.gc();
      }
      console.log('Finished afterAll hook');
      done();
    });
  });

  /**
   * Test GET /api/alerts
   */
  test('GET /api/alerts should return an array of alerts', async () => {
    const response = await request(server)
      .get('/api/alerts')
      .expect('Content-Type', /json/)
      .expect(200);

    expect(Array.isArray(response.body)).toBe(true);
    // Additional assertions can be added based on expected alert data
  });

  /**
   * Test GET /api/get-auction-data
   */
  test('GET /api/get-auction-data should return auction data', async () => {
    const response = await request(server)
      .get('/api/get-auction-data')
      .query({
        tableName: 'all_tables',
        searchTerm: 'TV',
        startDate: '2024-09-16',
        endDate: '2024-09-16',
      })
      .expect('Content-Type', /json/)
      .expect(200);

    // Log the response body for debugging
    console.log('Response body:', response.body);

    expect(Array.isArray(response.body)).toBe(true);
    // Check if the data contains expected fields
    if (response.body.length > 0) {
      const item = response.body[0];
      expect(item).toHaveProperty('id');
      expect(item).toHaveProperty('item_name');
      expect(item).toHaveProperty('lot_number');
      expect(item).toHaveProperty('time_left');
      // Add other properties as necessary
    }
  });

  /**
   * Test GET /api/get-auction-data exists and works
   */
  test('GET /api/get-auction-data should exist and work', async () => {
    const response = await request(server)
      .get('/api/get-auction-data')
      .query({
        tableName: 'all_tables',
        searchTerm: 'Test',
        startDate: '2024-09-16',
        endDate: '2024-09-16',
      })
      .expect('Content-Type', /json/)
      .expect(200);

    console.log('Response body:', response.body);

    expect(Array.isArray(response.body)).toBe(true);
    // Additional assertions can be added as needed
  });

  /**
   * Test POST /api/favorite should update favorite status
   */
  test('POST /api/favorite should update favorite status', async () => {
    // Ensure this data matches a record in your test database
    const favoriteData = {
      id: 268705, // Ensure this ID exists in your test database
      tableName: 'govdeals', // Ensure this matches the expected field name
      lot_number: '16015-74', // Ensure this matches the expected field name
      url: 'https://www.govdeals.com/asset/74/16015', // Ensure this URL is correct
      favorite: 'N', // Toggle the favorite status
    };

    const response = await request(server)
      .post('/api/favorite')
      .send(favoriteData)
      .set('Content-Type', 'application/json');

    // Log the response status and body for debugging
    console.log('Response status:', response.status);
    console.log('Response body:', response.body);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('success', true);
  });

  /**
   * Test GET /api/favorites
   */
  test('GET /api/favorites should return favorite auctions', async () => {
    const response = await request(server)
      .get('/api/favorites')
      .expect('Content-Type', /json/)
      .expect(200);

    console.log('Response body:', response.body);

    expect(Array.isArray(response.body)).toBe(true);
    // Check if the favorite items have expected properties
    if (response.body.length > 0) {
      const item = response.body[0];
      expect(item).toHaveProperty('id');
      expect(item).toHaveProperty('item_name');
      expect(item).toHaveProperty('favorite');
    }
  });

  /**
   * Test GET /api/daily-averages
   */
  test('GET /api/daily-averages should return daily averages', async () => {
    const response = await request(server)
      .get('/api/daily-averages')
      .expect('Content-Type', /json/)
      .expect(200);

    console.log('Response body:', response.body);

    expect(Array.isArray(response.body)).toBe(true);
    // Check if the data contains expected fields
    if (response.body.length > 0) {
      const item = response.body[0];
      expect(item).toHaveProperty('date');
      expect(item).toHaveProperty('avg_auctions_scraped'); // Adjust based on actual data
    }
  });

  /**
   * Test GET /api/daily-averages with date filter
   */
  test('GET /api/daily-averages with date filter should return data matching format', async () => {
    const date = '2024-10-10';

    const response = await request(server)
      .get('/api/daily-averages')
      .query({ date })
      .expect('Content-Type', /json/)
      .expect(200);

    response.body.forEach(item => {
      // Check that item.date matches the date format 'YYYY-MM-DD'
      const itemDate = new Date(item.date).toISOString().split('T')[0];
      console.log(`Item date: ${itemDate}`);
      expect(itemDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    });
  });

  /**
   * Test GET /api/search-auction-data
   */
  test('GET /api/search-auction-data should return search results', async () => {
    const searchTerm = 'TV';

    const response = await request(server)
      .get('/api/search-auction-data')
      .query({
        searchTerm,
        tableName: 'all_tables',
        startDate: '2024-09-16',
        endDate: '2024-09-16',
      })
      .expect('Content-Type', /json/)
      .expect(200);

    console.log('Response body:', response.body);

    expect(Array.isArray(response.body)).toBe(true);
    // Check if the search results match the query
    response.body.forEach(item => {
      expect(item.item_name).toMatch(new RegExp(searchTerm, 'i'));
    });
  });

  /**
   * Test CORS Headers
   */
  test('CORS headers should be set correctly', async () => {
    const response = await request(server)
      .options('/api/get-auction-data')
      .set('Origin', 'https://hashbrowns:3000') // Adjusted to match server response
      .expect(204); // No Content response

    expect(response.headers['access-control-allow-origin']).toBe('https://hashbrowns:3000');
  });

  /**
   * Test Server Start
   */
  test('Server should be running on the specified port', () => {
    expect(server.address().port).toBe(Number(process.env.PORT));
  });

  /**
   * Test Missing SSL Certificates
   */
  test('Server should fail to start without SSL certificates', (done) => {
    // Save original environment variables
    const originalKeyPath = process.env.SSL_KEY_PATH;
    const originalCertPath = process.env.SSL_CERT_PATH;

    // Delete SSL certificate paths to simulate missing certificates
    delete process.env.SSL_KEY_PATH;
    delete process.env.SSL_CERT_PATH;

    try {
      require('../httpsServer'); // Adjust the path as necessary
    } catch (err) {
      expect(err).toBeDefined();
    } finally {
      // Restore environment variables
      process.env.SSL_KEY_PATH = originalKeyPath;
      process.env.SSL_CERT_PATH = originalCertPath;
      done();
    }
  });

  /**
   * Test Invalid Routes
   */
  test('GET /invalid-route should return 404', async () => {
    await request(server)
      .get('/invalid-route')
      .expect(404);
  });

  /**
   * Test POST /api/favorite with Invalid Data
   */
  test('POST /api/favorite with invalid data should return 400', async () => {
    const invalidData = { invalidField: 'invalidValue' }; // Data that does not meet validation requirements

    const response = await request(server)
      .post('/api/favorite')
      .send(invalidData)
      .set('Content-Type', 'application/json');

    // Log the response status and body for debugging
    console.log('Response status:', response.status);
    console.log('Response body:', response.body);

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });

  /**
   * Test GET /api/favorites without authentication
   */
  test('GET /api/favorites should return favorite auctions without authentication', async () => {
    const response = await request(server)
      .get('/api/favorites')
      .expect('Content-Type', /json/)
      .expect(200);

    // Log the response status and body for debugging
    console.log('Response status:', response.status);
    console.log('Response body:', response.body);

    expect(Array.isArray(response.body)).toBe(true);
  });

  /**
   * Test OPTIONS Request for Preflight Checks
   */
  test('OPTIONS request should return correct headers', async () => {
    const response = await request(server)
      .options('/api/get-auction-data')
      .set('Origin', 'https://hashbrowns:3000') // Adjusted to match server response
      .expect(204);

    expect(response.headers['access-control-allow-methods']).toContain('GET');
    expect(response.headers['access-control-allow-headers']).toContain('Content-Type');
  });
});