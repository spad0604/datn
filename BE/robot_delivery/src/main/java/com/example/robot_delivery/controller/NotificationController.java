package com.example.robot_delivery.controller;

import com.example.robot_delivery.model.Notification;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.User;
import com.example.robot_delivery.repositorys.NotificationRepository;
import com.example.robot_delivery.repositorys.UserRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/notifications")
@RequiredArgsConstructor
@Tag(name = "Notification", description = "Lịch sử thông báo")
public class NotificationController {

    private final NotificationRepository notificationRepository;
    private final UserRepository userRepository;

    @GetMapping
    @Operation(summary = "Lấy danh sách thông báo của tài khoản hiện tại")
    public ResponseEntity<ResponseData<List<Notification>>> getMyNotifications(Authentication authentication) {
        User user = userRepository.findByUsername(authentication.getName()).orElse(null);
        if (user == null) {
            return ResponseEntity.ok(ResponseData.<List<Notification>>builder().message("User not found").build());
        }

        List<Notification> notifications = notificationRepository.findByUserOrderByCreatedAtDesc(user);
        return ResponseEntity.ok(ResponseData.<List<Notification>>builder()
                .message("Success")
                .data(notifications)
                .build());
    }

    @PostMapping("/{id}/read")
    @Operation(summary = "Đánh dấu thông báo đã đọc")
    public ResponseEntity<ResponseData<Void>> markAsRead(@PathVariable Long id, Authentication authentication) {
        notificationRepository.findById(id).ifPresent(n -> {
            if (n.getUser().getUsername().equals(authentication.getName())) {
                n.setRead(true);
                notificationRepository.save(n);
            }
        });
        return ResponseEntity.ok(ResponseData.<Void>builder()
                .message("Success")
                .build());
    }
}
