package com.example.robot_delivery.impl;

import com.example.robot_delivery.interfaces.IUserService;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.User;
import com.example.robot_delivery.model.request.ChangePasswordRequest;
import com.example.robot_delivery.model.request.LoginRequest;
import com.example.robot_delivery.model.request.RegisterRequest;
import com.example.robot_delivery.model.responses.LoginResponse;
import com.example.robot_delivery.repositorys.RefreshTokenRepository;
import com.example.robot_delivery.repositorys.UserRepository;
import com.example.robot_delivery.security.JwtService;
import com.example.robot_delivery.security.RefreshToken;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements IUserService {
    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    private static final long REFRESH_TOKEN_EXPIRE_DAYS = 7;

    @Override
    @Transactional
    public ResponseData<LoginResponse> register(RegisterRequest registerRequest) {
        if (registerRequest == null || registerRequest.getUsername() == null || registerRequest.getPassword() == null) {
            throw new IllegalArgumentException("Missing username/password");
        }

        if (Boolean.TRUE.equals(userRepository.existsByUsername(registerRequest.getUsername()))) {
            throw new IllegalArgumentException("Username already exists");
        }
        if (registerRequest.getEmail() != null && Boolean.TRUE.equals(userRepository.existsByEmail(registerRequest.getEmail()))) {
            throw new IllegalArgumentException("Email already exists");
        }

        User user = User.builder()
                .username(registerRequest.getUsername())
                .password(passwordEncoder.encode(registerRequest.getPassword()))
                .firstName(registerRequest.getFirstName())
                .lastName(registerRequest.getLastName())
                .email(registerRequest.getEmail())
                .phoneNumber(registerRequest.getPhoneNumber())
                .address(registerRequest.getAddress())
                .build();

        User savedUser = userRepository.save(user);

        String accessToken = jwtService.generateToken(savedUser.getUsername(), buildFullName(savedUser), savedUser.getEmail());
        String refreshToken = createOrRotateRefreshToken(savedUser).getToken();

        LoginResponse loginResponse = LoginResponse.builder()
                .username(savedUser.getUsername())
                .fullName(buildFullName(savedUser))
                .token(accessToken)
                .refreshToken(refreshToken)
                .build();

        return ResponseData.<LoginResponse>builder()
                .message("Register success")
                .data(loginResponse)
                .build();
    }

    @Override
    public ResponseData<LoginResponse> login(LoginRequest loginRequest) {
        if (loginRequest == null || loginRequest.getUsername() == null || loginRequest.getPassword() == null) {
            throw new IllegalArgumentException("Missing username/password");
        }

        User user = userRepository.findByUsername(loginRequest.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));

        if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
            throw new IllegalArgumentException("Invalid credentials");
        }

        String accessToken = jwtService.generateToken(user.getUsername(), buildFullName(user), user.getEmail());
        String refreshToken = createOrRotateRefreshToken(user).getToken();

        LoginResponse loginResponse = LoginResponse.builder()
                .username(user.getUsername())
                .fullName(buildFullName(user))
                .token(accessToken)
                .refreshToken(refreshToken)
                .build();

        return ResponseData.<LoginResponse>builder()
                .message("Login success")
                .data(loginResponse)
                .build();
    }

    @Override
    @Transactional
    public ResponseData<LoginResponse> refreshToken(String refreshToken) {
        if (refreshToken == null || refreshToken.isBlank()) {
            throw new IllegalArgumentException("Missing refresh token");
        }

        RefreshToken storedToken = refreshTokenRepository.findByToken(refreshToken)
                .orElseThrow(() -> new IllegalArgumentException("Invalid refresh token"));

        if (storedToken.getExpiryDate() == null || storedToken.getExpiryDate().isBefore(Instant.now())) {
            refreshTokenRepository.delete(storedToken);
            throw new IllegalArgumentException("Refresh token expired");
        }

        User user = storedToken.getUser();
        if (user == null || user.getUsername() == null) {
            throw new IllegalArgumentException("Invalid refresh token");
        }

        String accessToken = jwtService.generateToken(user.getUsername(), buildFullName(user), user.getEmail());
        String newRefreshToken = createOrRotateRefreshToken(user).getToken();

        LoginResponse loginResponse = LoginResponse.builder()
                .username(user.getUsername())
                .fullName(buildFullName(user))
                .token(accessToken)
                .refreshToken(newRefreshToken)
                .build();

        return ResponseData.<LoginResponse>builder()
                .message("Refresh token success")
                .data(loginResponse)
                .build();
    }

    @Override
    @Transactional
    public ResponseData<Void> changePassword(ChangePasswordRequest changePasswordRequest) {
        if (changePasswordRequest == null
                || changePasswordRequest.getUsername() == null
                || changePasswordRequest.getOldPassword() == null
                || changePasswordRequest.getNewPassword() == null) {
            throw new IllegalArgumentException("Missing change password fields");
        }

        User user = userRepository.findByUsername(changePasswordRequest.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        if (!passwordEncoder.matches(changePasswordRequest.getOldPassword(), user.getPassword())) {
            throw new IllegalArgumentException("Old password is incorrect");
        }

        user.setPassword(passwordEncoder.encode(changePasswordRequest.getNewPassword()));
        userRepository.save(user);

        // Invalidate any existing refresh token so user must login again.
        refreshTokenRepository.deleteByUser(user);

        return ResponseData.<Void>builder()
                .message("Change password success")
                .data(null)
                .build();
    }

    @Override
    public User findByUsername(String username) {
        if (username == null) {
            return null;
        }
        return userRepository.findByUsername(username).orElse(null);
    }

    @Override
    public User findByEmail(String email) {
        if (email == null) {
            return null;
        }
        return userRepository.findByEmail(email).orElse(null);
    }

    @Override
    public User findUserByPhoneNumber(String phoneNumber) {
        if (phoneNumber == null) {
            return null;
        }
        return userRepository.findByPhoneNumber(phoneNumber).orElse(null);
    }

    private RefreshToken createOrRotateRefreshToken(User user) {
        RefreshToken token = refreshTokenRepository.findByUser(user).orElse(null);
        if (token == null) {
            token = RefreshToken.builder().user(user).build();
        }

        // Generate a longer, more secure refresh token using UUID + extra entropy
        String secureToken = UUID.randomUUID().toString() + "-" + UUID.randomUUID().toString();
        token.setToken(secureToken);
        token.setExpiryDate(Instant.now().plus(REFRESH_TOKEN_EXPIRE_DAYS, ChronoUnit.DAYS));
        return refreshTokenRepository.save(token);
    }

    private String buildFullName(User user) {
        String firstName = user.getFirstName() == null ? "" : user.getFirstName().trim();
        String lastName = user.getLastName() == null ? "" : user.getLastName().trim();
        String fullName = (firstName + " " + lastName).trim();
        return fullName.isEmpty() ? null : fullName;
    }
}
