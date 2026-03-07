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
    private Double streamLat;
    private Double streamLng;
    private Double deliveryLat;
    private Double deliveryLng;
}
