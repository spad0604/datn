package com.example.robot_delivery.service;

import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.enums.OrderStatusEnum;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class RobotOrderEventPublisher {

    private final SimpMessagingTemplate messagingTemplate;

    @Value("${robot.ws.robot-order-topic-prefix:/topic/robot-order}")
    private String robotOrderTopicPrefix;

    public void publishOrderAssigned(Order order) {
        publish(order, "ORDER_ASSIGNED", order.getStatus());
    }

    public void publishOrderCancelled(Order order) {
        publish(order, "ORDER_CANCELLED", order.getStatus());
    }

    public void publishOrderStatusChanged(Order order, OrderStatusEnum newStatus) {
        publish(order, "ORDER_STATUS_CHANGED", newStatus);
    }

    private void publish(Order order, String type, OrderStatusEnum status) {
        if (order == null) return;
        Robot robot = order.getRobot();
        if (robot == null || robot.getId() == null) return;

        String destination = robotOrderTopicPrefix + "/" + robot.getId();

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("type", type);
        payload.put("ts", Instant.now().toEpochMilli());
        payload.put("robotId", robot.getId());
        payload.put("orderId", order.getId());
        payload.put("orderCode", order.getOrderId());
        payload.put("orderStatus", status != null ? status.name() : null);
        payload.put("robotStatus", robot.getStatus() != null ? robot.getStatus().name() : null);
        payload.put("startLat", order.getStartLat());
        payload.put("startLng", order.getStartLng());
        payload.put("deliveryLat", order.getDeliveryLat());
        payload.put("deliveryLng", order.getDeliveryLng());
        payload.put("senderAddress", order.getSenderAddress());
        payload.put("deliveryAddress", order.getDeliveryAddress());

        messagingTemplate.convertAndSend(destination, (Object) payload);
    }
}
