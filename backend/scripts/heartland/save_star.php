<?php
// Replace with your actual connection details
$host = '192.168.1.100';
$dbname = 'auctions';
$user = 'whatcheer';
$pass = 'meatwad';

// Assuming PDO for a more secure, efficient connection
$pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
// Ensure proper error mode is set
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$lot_number = $_POST['lot_number'] ?? '';
$favorite = $_POST['favorite'] ?? '';

try {
    if ($lot_number) {
        // Toggle favorite based on the 'favorite' POST parameter
        $sql = "UPDATE heartland SET favorite = :favorite WHERE lot_number = :lot_number";
        $stmt = $pdo->prepare($sql);
        // Determine the new value for 'favorite' column ('Y' or NULL)
        $newFavoriteValue = ($favorite === 'Y') ? 'Y' : NULL;
        $stmt->execute(['lot_number' => $lot_number, 'favorite' => $newFavoriteValue]);

        echo "Record updated successfully";
    } else {
        echo "Lot number is required.";
    }
} catch (PDOException $e) {
    die("Could not update record: " . $e->getMessage());
}
?>
