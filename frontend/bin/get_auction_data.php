<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: http://hashbrowns:3000'); 
header('Access-Control-Allow-Methods: GET, POST, OPTIONS'); 
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Credentials: true'); 

$dsn = 'mysql:host=localhost;dbname=auctions';
$user = 'whatcheer';
$password = 'meatwad';

try {
    $pdo = new PDO($dsn, $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $tables = ['backes', 'bidspotter', 'govdeals', 'gsa', 'publicsurplus', 'smc', 'proxibid', 'wiscosurp_auctions'];
    $results = [];

    $startDate = $_GET['startDate'] ?? null;
    $endDate = $_GET['endDate'] ?? null;
    $limit = $_GET['limit'] ?? 500;
    $offset = $_GET['offset'] ?? 0;

    if (!$startDate || !$endDate) {
        echo json_encode(['error' => 'Missing startDate or endDate']);
        exit;
    }

    foreach ($tables as $table) {
        $identifierColumn = 'id';
        $columnCheck = $pdo->query("SHOW COLUMNS FROM `$table` LIKE 'id'");
        if ($columnCheck->rowCount() == 0) {
            $identifierColumn = 'lot_number';
        }

        $query = $pdo->prepare("SELECT id, item_name, time_left, current_bid FROM `$table` WHERE DATE(time_left) BETWEEN :startDate AND :endDate LIMIT :limit OFFSET :offset");
        $query->bindParam(':startDate', $startDate);
        $query->bindParam(':endDate', $endDate);
        $query->bindParam(':limit', $limit, PDO::PARAM_INT);
        $query->bindParam(':offset', $offset, PDO::PARAM_INT);
        $query->execute();

        while ($row = $query->fetch(PDO::FETCH_ASSOC)) {
            $row['original_table'] = $table;
            $results[] = $row;
        }
    }

    echo json_encode($results);
} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
