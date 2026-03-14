package com.example.robot_delivery.service;

import com.example.robot_delivery.model.User;
import com.example.robot_delivery.repositorys.NotificationRepository;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.Message;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class NotificationService {
    private final NotificationRepository notificationRepository;

    public com.example.robot_delivery.model.Notification sendAndSaveNotification(
            User user, String title, String body, String type, Long orderId) {

        if (user == null) return null;

        // Lưu log thông báo vào CSDL
        com.example.robot_delivery.model.Notification notification =
                com.example.robot_delivery.model.Notification.builder()
                        .user(user)
                        .title(title)
                        .body(body)
                        .type(type)
                        .orderId(orderId)
                        .isRead(false)
                        .createdAt(LocalDateTime.now())
                        .build();
        com.example.robot_delivery.model.Notification saved = notificationRepository.save(notification);

        // Đẩy notify qua FCM (Firebase)
        if (user.getFcmToken() != null && !user.getFcmToken().isBlank()) {
            try {
                com.google.firebase.messaging.Notification fcmNotif =
                        com.google.firebase.messaging.Notification.builder()
                                .setTitle(title)
                                .setBody(body)
                                .build();

                Message message = Message.builder()
                        .setNotification(fcmNotif)
                        .setToken(user.getFcmToken())
                        .putData("type", type != null ? type : "")
                        .putData("orderId", orderId != null ? String.valueOf(orderId) : "")
                        .build();

                FirebaseMessaging.getInstance().send(message);
            } catch (Exception e) {
                System.err.println("Firebase Messaging Error: " + e.getMessage());
            }
        }

        return saved;
    }
}
