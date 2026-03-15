package com.example.robot_delivery.controller;

import com.example.robot_delivery.interfaces.IUserService;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.User;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "User", description = "Quản lý người dùng")
public class UserController {

    private final IUserService userService;

    @GetMapping("/search")
    @Operation(summary = "Tìm kiếm người dùng bằng Số điện thoại (dành cho người gửi/nhận)")
    public ResponseEntity<ResponseData<User>> searchUserByPhoneNumber(@RequestParam String phoneNumber) {
        User user = userService.findUserByPhoneNumber(phoneNumber);
        if (user == null) {
            return ResponseEntity.ok(ResponseData.<User>builder()
                    .message("Không tìm thấy người dùng với số điện thoại này")
                    .data(null)
                    .build());
        }
        
        return ResponseEntity.ok(ResponseData.<User>builder()
                .message("Tìm kiếm thành công")
                .data(user)
                .build());
    }

    @PostMapping("/upload_avatar")
    @Operation(summary = "")
    public ResponseEntity<ResponseData<User>> uploadAvatar(@RequestParam("file") MultipartFile file) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body(ResponseData.<User>builder()
                    .message("Unauthorized")
                    .data(null)
                    .build());
        }

        String username = authentication.getName();
        User user = userService.findByUsername(username);


        if (user == null) {
            return ResponseEntity.status(404).body(ResponseData.<User>builder()
                    .message("User not found")
                    .data(null)
                    .build());
        }

        userService.uploadAvatar(file, username);

        return ResponseEntity.ok(ResponseData.<User>builder()
                .message("Success")
                .data(user)
                .build());
    }


    @GetMapping("/my-info")
    @Operation(summary = "Lấy thông tin tài khoản đang đăng nhập")
    public ResponseEntity<ResponseData<User>> getMyInfo() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body(ResponseData.<User>builder()
                    .message("Unauthorized")
                    .data(null)
                    .build());
        }

        String username = authentication.getName();
        User user = userService.findByUsername(username);

        if (user == null) {
            return ResponseEntity.status(404).body(ResponseData.<User>builder()
                    .message("User not found")
                    .data(null)
                    .build());
        }

        return ResponseEntity.ok(ResponseData.<User>builder()
                .message("Success")
                .data(user)
                .build());
    }
}
