package com.example.robot_delivery.model.responses;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Builder
@Data
@AllArgsConstructor
public class LoginResponse {
    private String username;
    private String fullName;
    private String token;
    private String refreshToken;
}
