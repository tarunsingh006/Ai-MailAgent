package com.bharatmarwah.mail_tool_service.Service;

import com.bharatmarwah.mail_tool_service.Model.EmailSendRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender javaMailSender;

    @Value("${spring.mail.username:noreply@example.com}")
    private String fromEmail = "tarunchauhan8832@gmail.com";


    public String sendEmail(EmailSendRequest sendRequest) {
        if (!isValidRequest(sendRequest)) {
            log.warn("Invalid email request received");
            return "Invalid email request: missing required fields";
        }

        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(fromEmail);
        message.setTo(sendRequest.getTo());
        message.setSubject(sendRequest.getSubject());
        message.setText(sendRequest.getBody());

        try {
            javaMailSender.send(message);
            log.info("Email sent successfully to {} with subject '{}'",
                    sendRequest.getTo(), sendRequest.getSubject());
            return "Email sent successfully";

        } catch (IllegalStateException e) {
            log.error("SMTP Configuration error: {}", e.getMessage());
            return "SMTP Configuration Error: " + e.getMessage();
        } catch (Exception e) {
            log.error("Failed to send email to {}: {}", sendRequest.getTo(), e.getMessage(), e);
            return "Failed to send email: " + e.getMessage();
        }
    }

    @Async
    public void sendEmailAsync(EmailSendRequest sendRequest) {
        log.debug("Processing async email request for {}", sendRequest.getTo());
        String result = sendEmail(sendRequest);
        log.info("Async email processing result: {}", result);
    }

    private boolean isValidRequest(EmailSendRequest sendRequest) {
        if (sendRequest == null) {
            return false;
        }
        if (sendRequest.getTo() == null || sendRequest.getTo().trim().isEmpty()) {
            return false;
        }
        if (sendRequest.getSubject() == null || sendRequest.getSubject().trim().isEmpty()) {
            return false;
        }
        if (sendRequest.getBody() == null || sendRequest.getBody().trim().isEmpty()) {
            return false;
        }
        return isValidEmail(sendRequest.getTo());
    }

    private boolean isValidEmail(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
    }
}
