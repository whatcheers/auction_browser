<?php
// Set header to output JSON
header('Content-Type: application/json');

// Database connection parameters
$host = '192.168.1.100';
$dbname = 'auctions';
$user = 'whatcheer';
$password = 'meatwad';

try {
    // Create PDO instance to connect to the database
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Adjusted SQL query to include the favorite column
    $sql = "SELECT lot_number, item_name, category, url, time_left, favorite FROM heartland";
    $stmt = $pdo->prepare($sql);

    // Execute the query
    $stmt->execute();

    // Fetch all the results
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Encode the results to JSON and output
    echo json_encode($results);
} catch (PDOException $e) {
    // Handle error
    echo json_encode(['error' => $e->getMessage()]);
}
?>
