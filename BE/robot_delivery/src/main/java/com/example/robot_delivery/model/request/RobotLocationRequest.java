package com.example.robot_delivery.model.request;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@AllArgsConstructor
@NoArgsConstructor
public class RobotLocationRequest {
    private double lat;
    private double lng;
    private Long robotId;
    private String secretKey;
    private double heading;
}
