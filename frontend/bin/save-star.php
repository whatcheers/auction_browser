<?php
// Enable error reporting and logging
ini_set('display_errors', 1);
error_reporting(E_ALL);
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/php-error.log');

// Log the start of the script execution
error_log("save-star.php started execution");

// Handle CORS
header('Access-Control-Allow-Origin: http://hashbrowns:3000'); // Allow requests from your frontend origin
header('Access-Control-Allow-Methods: POST, OPTIONS'); // Allow POST and OPTIONS methods
header('Access-Control-Allow-Headers: Content-Type'); // Allow Content-Type header
header('Access-Control-Allow-Credentials: true'); // Allow credentials

// Handle preflight request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204); // No content
    exit;
}

// Get the raw input
$input = $argv[1] ?? file_get_contents('php://input');
error_log("Received data: " . $input);

// Parse JSON input
$data = json_decode($input, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400);
    error_log("Invalid JSON: " . json_last_error_msg());
    echo json_encode(["success" => false, "error" => "Invalid JSON: " . json_last_error_msg()]);
    exit;
}

// Extract data
$favorite = $data['favorite'] ?? '';
$tableName = $data['tableName'] ?? '';
$lotNumber = $data['lot_number'] ?? '';
$url = $data['url'] ?? '';
$id = $data['id'] ?? '';

// Log extracted data
error_log("Extracted data: favorite=$favorite, tableName=$tableName, lotNumber=$lotNumber, url=$url, id=$id");

// Validate input
if (empty($tableName) || empty($url)) {
    http_response_code(400);
    error_log("Missing required data: tableName=$tableName, url=$url");
    echo json_encode(["success" => false, "error" => "Missing required data: tableName or url"]);
    exit;
}

// Database connection details
$host = 'localhost';
$dbname = 'auctions';
$user = 'whatcheer';
$pass = 'meatwad';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Determine the correct identifier column and value
    $identifierColumn = 'id';
    $identifierValue = $id;

    if (in_array($tableName, ['govdeals', 'gsa', 'bidspotter', 'backes', 'smc', 'wiscosurp_auctions', 'hibid'])) {
        $identifierColumn = 'lot_number';
        $identifierValue = $lotNumber;
    } elseif ($tableName === 'publicsurplus') {
        $identifierColumn = 'lot_number';
        $identifierValue = (int)$lotNumber; // Convert to integer
    }

    // Prepare SQL statement
    $sql = "UPDATE `$tableName` SET favorite = :favorite WHERE url = :url";
    if (!empty($identifierValue)) {
        $sql .= " AND $identifierColumn = :identifierValue";
    }
    
    $stmt = $pdo->prepare($sql);

    // Bind parameters
    $stmt->bindParam(':favorite', $favorite, PDO::PARAM_STR);
    $stmt->bindParam(':url', $url, PDO::PARAM_STR);
    if (!empty($identifierValue)) {
        $stmt->bindParam(':identifierValue', $identifierValue, 
            $tableName === 'publicsurplus' ? PDO::PARAM_INT : PDO::PARAM_STR);
    }
    
    // Execute the statement
    $stmt->execute();

    // Check if any rows were affected
    if ($stmt->rowCount() > 0) {
        echo json_encode(["success" => true]);
    } else {
        echo json_encode(["success" => false, "error" => "No matching record found to update"]);
    }

} catch (PDOException $e) {
    http_response_code(500);
    error_log("Database error: " . $e->getMessage());
    echo json_encode(["success" => false, "error" => "Database error: " . $e->getMessage()]);
}

// Log the end of the script execution
error_log("save-star.php finished execution");
?>
