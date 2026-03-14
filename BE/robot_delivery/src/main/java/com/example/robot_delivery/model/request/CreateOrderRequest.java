package com.example.robot_delivery.model.request;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class CreateOrderRequest {
    private String recipientPhone;
    private Double startLat;
    private Double startLng;
    private Double deliveryLat;
    private Double deliveryLng;
}
