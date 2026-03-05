package com.example.robot_delivery.controller;

import com.example.robot_delivery.interfaces.IUserService;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.request.ChangePasswordRequest;
import com.example.robot_delivery.model.request.LoginRequest;
import com.example.robot_delivery.model.request.RegisterRequest;
import com.example.robot_delivery.model.responses.LoginResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Tag(name = "Authentication", description = "Đăng ký, Đăng nhập, Refresh Token, Đổi mật khẩu")
public class AuthController {

    private final IUserService userService;

    @PostMapping("/register")
    @Operation(summary = "Đăng ký tài khoản mới")
    public ResponseEntity<ResponseData<LoginResponse>> register(@RequestBody RegisterRequest request) {
        return ResponseEntity.ok(userService.register(request));
    }

    @PostMapping("/login")
    @Operation(summary = "Đăng nhập")
    public ResponseEntity<ResponseData<LoginResponse>> login(@RequestBody LoginRequest loginRequest) {
        return ResponseEntity.ok(userService.login(loginRequest));
    }

    @PostMapping("/refresh-token")
    @Operation(summary = "Làm mới Access Token")
    public ResponseEntity<ResponseData<LoginResponse>> refreshToken(@RequestParam String refreshToken) {
        return ResponseEntity.ok(userService.refreshToken(refreshToken));
    }

    @PostMapping("/change-password")
    @Operation(summary = "Đổi mật khẩu")
    public ResponseEntity<ResponseData<Void>> changePassword(@RequestBody ChangePasswordRequest request) {
        return ResponseEntity.ok(userService.changePassword(request));
    }
}
