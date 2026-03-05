package com.example.robot_delivery.interfaces;

import com.example.robot_delivery.model.User;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.request.ChangePasswordRequest;
import com.example.robot_delivery.model.request.LoginRequest;
import com.example.robot_delivery.model.request.RegisterRequest;
import com.example.robot_delivery.model.responses.LoginResponse;

public interface IUserService {
    ResponseData<LoginResponse> register(RegisterRequest registerRequest);
    ResponseData<LoginResponse> login(LoginRequest loginRequest);

    ResponseData<LoginResponse> refreshToken(String refreshToken);

    ResponseData<Void> changePassword(ChangePasswordRequest changePasswordRequest);

    User findByUsername(String username);

    User findByEmail(String email);
}
