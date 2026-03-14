package com.example.robot_delivery.impl;

import com.example.robot_delivery.interfaces.IRobotService;
import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.enums.OrderStatusEnum;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import com.example.robot_delivery.repositorys.OrderRepository;
import com.example.robot_delivery.repositorys.RobotRepository;
import com.example.robot_delivery.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class RobotServiceImpl implements IRobotService {
    private final RobotRepository robotRepository;
    private final OrderRepository orderRepository;
    private final NotificationService notificationService;

    @Override
    public List<Robot> findByStatus(RobotStatusEnum status) {
        try {
            return robotRepository.findByStatus(status);
        } catch (Exception e) {
            return List.of();
        }
    }

    @Override
    public void updateRobotLocation(Long robotId, Double latitude, Double longitude) {
        try {
            robotRepository.updateRobotLocation(robotId, latitude, longitude);

            Robot robot = robotRepository.findById(robotId).orElse(null);
            if (robot == null) return;

            // KIỂM TRA PENDING -> approaching pickup (báo cho người gửi)
            Optional<Order> pickupOpt = orderRepository.findByRobotAndStatus(robot, OrderStatusEnum.PENDING);
            if (pickupOpt.isPresent()) {
                Order order = pickupOpt.get();
                if (order.getStartLat() != null && order.getStartLng() != null) {
                    double dist = calculateDistance(latitude, longitude, order.getStartLat(), order.getStartLng());
                    if (dist < 0.2 && !Boolean.TRUE.equals(order.getIsPickupNotified())) {
                        notificationService.sendAndSaveNotification(
                                order.getCustomerId(),
                                "Robot đang đến!",
                                "Robot sắp đến điểm lấy hàng, vui lòng chuẩn bị hàng.",
                                "ROBOT_APPROACHING_PICKUP",
                                order.getId()
                        );
                        order.setIsPickupNotified(true);
                        orderRepository.save(order);
                    }
                }
            }

            // KIỂM TRA DELIVERING -> approaching delivery (báo cho người nhận)
            Optional<Order> deliveryOpt = orderRepository.findByRobotAndStatus(robot, OrderStatusEnum.DELIVERING);
            if (deliveryOpt.isPresent()) {
                Order order = deliveryOpt.get();
                if (order.getDeliveryLat() != null && order.getDeliveryLng() != null) {
                    double dist = calculateDistance(latitude, longitude, order.getDeliveryLat(), order.getDeliveryLng());
                    if (dist < 0.2 && !Boolean.TRUE.equals(order.getIsDeliveryNotified())) {
                        notificationService.sendAndSaveNotification(
                                order.getRecipientId(),
                                "Robot sắp đến!",
                                "Robot sắp giao hàng cho bạn, vui lòng chuẩn bị ra nhận.",
                                "ROBOT_APPROACHING_DELIVERY",
                                order.getId()
                        );
                        order.setIsDeliveryNotified(true);
                        orderRepository.save(order);
                    }
                }
            }

        } catch (Exception e) {
            System.err.println("Error updating robot location: " + e.getMessage());
        }
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        // Công thức Haversine đơn giản
        double earthRadius = 6371; // km
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return earthRadius * c;
    }
}
