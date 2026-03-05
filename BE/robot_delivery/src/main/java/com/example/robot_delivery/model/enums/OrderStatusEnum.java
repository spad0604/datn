package com.example.robot_delivery.model.enums;

public enum OrderStatusEnum {
    WAIT_ROBOT,  // Đang đợi robot (khi không có robot rảnh)
    PENDING,     // Đã gán robot, robot đang đến lấy hàng
    DELIVERING,  // Robot đang giao hàng
    DELIVERED    // Đã giao hàng thành công
}
