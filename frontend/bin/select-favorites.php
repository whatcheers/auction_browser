<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // Allows all domains
header('Access-Control-Allow-Methods: GET, POST, OPTIONS'); // Specifies methods allowed when accessing the resource
header('Access-Control-Allow-Headers: Content-Type, Authorization'); // Specifies headers allowed

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    // Handle preflight request
    exit(0);
}

$dsn = 'mysql:host=localhost;dbname=auctions';
$user = 'whatcheer';
$password = 'meatwad';

try {
    $pdo = new PDO($dsn, $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $tables = ['backes', 'bidspotter', 'govdeals', 'gsa', 'publicsurplus', 'smc', 'wiscosurp_auctions'];
    $results = [];

    foreach ($tables as $table) {
        $query = $pdo->prepare("SELECT *, 'favorite' AS favorite_column, '$table' AS original_table FROM `$table` WHERE `favorite` = 'Y'");
        $query->execute();
        
        while ($row = $query->fetch(PDO::FETCH_ASSOC)) {
            $results[] = $row;
        }
    }

    echo json_encode($results);

} catch (PDOException $e) {
    echo json_encode(['error' => "Could not connect to the database: " . $e->getMessage()]);
}
?>
