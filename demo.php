<?php
require 'vendor/autoload.php';
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $emails = $_POST['email'] ?? [];
    $senderEmail = $_POST['senderEmail'] ?? '';
    $smtpPassword = $_POST['smtpPassword'] ?? '';
    $emailSubject = $_POST['emailSubject'] ?? '';
    $emailBody = $_POST['emailBody'] ?? '';
    $uploadDir = 'uploads/';
    $response = ['success' => true, 'messages' => []];

    foreach ($emails as $email) {
        // Validate email
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $response['success'] = false;
            $response['messages'][] = "❌ Invalid email: $email";
            continue;
        }

        // Initialize PHPMailer
        $mail = new PHPMailer(true);
        try {
            // SMTP Configuration
            $mail->isSMTP();
            $mail->Host = 'smtp.gmail.com'; // Replace with your SMTP host
            $mail->SMTPAuth = true;
            $mail->Username = $senderEmail; // Use the provided sender email
            $mail->Password = $smtpPassword; // Use the provided SMTP password
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
            $mail->Port = 587;

            // Email Content
            $mail->setFrom($senderEmail, 'Your Name'); // Use the provided sender info
            $mail->addAddress($email); // Add recipient
            $mail->isHTML(true);
            $mail->Subject = $emailSubject; // Use the provided subject
            $mail->Body = $emailBody; // Use the provided body

            // Attach files for each email
            if (isset($_FILES['pdfFiles'])) {
                foreach ($_FILES['pdfFiles']['name'] as $key => $name) {
                    if ($_FILES['pdfFiles']['error'][$key] == 0) {
                        $tmpName = $_FILES['pdfFiles']['tmp_name'][$key];
                        $mail->addAttachment($tmpName, $name);
                    }
                }
            }

            // Attempt to send email
            $mail->send();
            $response['messages'][] = "✅ Email sent successfully to $email";
        } catch (Exception $e) {
            $response['success'] = false;
            echo e;
           $response['messages'][] = "❌ Could not send to $email. Mailer Error: {$mail->ErrorInfo}.";
            $response['messages'][] = "📋 Debug: Sender Email - $senderEmail, Subject - $emailSubject, Body - $emailBody";

        }
    }

    echo json_encode($response);
} else {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
}
?>
