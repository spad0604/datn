package com.example.robot_delivery.model.responses;

import com.example.robot_delivery.model.enums.OrderStatusEnum;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Builder
public class OrderResponse {
    private Long id;
    private String orderId;
    private UserSummary customer;
    private UserSummary recipient;
    private String recipientPhone;
    private Double startLat;
    private Double startLng;
    private String senderAddress;
    private Double deliveryLat;
    private Double deliveryLng;
    private String deliveryAddress;
    private String pinCode;

    private String senderName;
    private Long robotId;
    private String robotName;
    private RobotStatusEnum robotStatus;
    private OrderStatusEnum status;
    private LocalDateTime createdAt;

    @Data
    @Builder
    public static class UserSummary {
        private Long id;
        private String username;
        private String fullName;
        private String phoneNumber;
    }
}
