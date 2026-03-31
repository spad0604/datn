package com.example.robot_delivery.controller;

import com.example.robot_delivery.impl.RobotServiceImpl;
import com.example.robot_delivery.model.request.RobotLocationRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Controller
@RequiredArgsConstructor
public class RobotLocationController {
    private final RobotServiceImpl robotService;
    private final SimpMessagingTemplate simpMessagingTemplate;

    @Value("${robot.shared-secret:DATN_2025_2_GIAP}")
    private String serverSecret;

    @MessageMapping("/update-location")
    public void handleRobotLocation(@Payload RobotLocationRequest request) {
        if (!serverSecret.equals(request.getSecretKey())) {
            return;
        }

        String destination = "/topic/robot" + request.getRobotId();

        // Update internal state / persistence
        robotService.updateRobotLocation(request.getRobotId(), request.getLat(), request.getLng());

        // Broadcast to subscribed mobile clients (don't send secret)
        Map<String, Object> payload = Map.of(
                "robotId", request.getRobotId(),
                "lat", request.getLat(),
                "lng", request.getLng()
        );

        simpMessagingTemplate.convertAndSend(destination, (Object) payload);
    }
}
