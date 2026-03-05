package com.example.robot_delivery.model.request;

import lombok.Builder;
import lombok.Data;

@Builder
@Data
public class ChangePasswordRequest {
    private String username;
    private String oldPassword;
    private String newPassword;
}
