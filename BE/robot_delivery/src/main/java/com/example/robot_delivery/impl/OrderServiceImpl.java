package com.example.robot_delivery.impl;

import com.example.robot_delivery.interfaces.IOrderService;
import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.User;
import com.example.robot_delivery.model.enums.OrderStatusEnum;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import com.example.robot_delivery.repositorys.OrderRepository;
import com.example.robot_delivery.repositorys.RobotRepository;
import com.example.robot_delivery.repositorys.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements IOrderService {

    private final OrderRepository orderRepository;
    private final RobotRepository robotRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional
    public ResponseData<Order> createOrder(Order order, String username) {
        User customer = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        order.setCustomerId(customer);
        order.setCreatedAt(java.time.LocalDateTime.now());

        // Tìm robot rảnh gần nhất
        List<Robot> idleRobots = robotRepository.findByStatus(RobotStatusEnum.IDLE);
        Robot nearestRobot = null;
        double minDistance = Double.MAX_VALUE;

        for (Robot robot : idleRobots) {
            double distance = calculateDistance(
                    robot.getLatitude(), robot.getLongitude(),
                    order.getStreamLat(), order.getStreamLng()
            );
            if (distance < minDistance) {
                minDistance = distance;
                nearestRobot = robot;
            }
        }

        if (nearestRobot != null) {
            nearestRobot.setStatus(RobotStatusEnum.PICKING_UP);
            robotRepository.save(nearestRobot);
            order.setRobot(nearestRobot);
            order.setStatus(OrderStatusEnum.PENDING);
        } else {
            // Không có robot rảnh, đơn hàng ở trạng thái đợi
            order.setRobot(null);
            order.setStatus(OrderStatusEnum.WAIT_ROBOT);
        }

        Order savedOrder = orderRepository.save(order);
        String message = (nearestRobot != null) ? "Order created and robot assigned" : "Order created. Waiting for an available robot.";
        
        return ResponseData.<Order>builder()
                .message(message)
                .data(savedOrder)
                .build();
    }

    @Override
    public ResponseData<Order> updateOrder(Long id, Order order, String username) {
        return orderRepository.findById(id).map(existing -> {
            if (!existing.getCustomerId().getUsername().equals(username)) {
                return ResponseData.<Order>builder().message("Access denied").build();
            }
            existing.setRecipientPhone(order.getRecipientPhone());
            existing.setDeliveryLat(order.getDeliveryLat());
            existing.setDeliveryLng(order.getDeliveryLng());
            return ResponseData.<Order>builder()
                    .message("Order updated")
                    .data(orderRepository.save(existing))
                    .build();
        }).orElse(ResponseData.<Order>builder().message("Order not found").build());
    }

    @Override
    public ResponseData<Void> deleteOrder(Long id, String username) {
        return orderRepository.findById(id).map(existing -> {
            if (!existing.getCustomerId().getUsername().equals(username)) {
                return ResponseData.<Void>builder().message("Access denied").build();
            }
            orderRepository.delete(existing);
            return ResponseData.<Void>builder().message("Order deleted").build();
        }).orElse(ResponseData.<Void>builder().message("Order not found").build());
    }

    @Override
    public ResponseData<List<Order>> getMyCreatedOrders(String username) {
        User user = userRepository.findByUsername(username).orElse(null);
        if (user == null) return ResponseData.<List<Order>>builder().message("User not found").build();
        
        List<Order> orders = orderRepository.findByCustomerId(user);
        return ResponseData.<List<Order>>builder().message("Success").data(orders).build();
    }

    @Override
    public ResponseData<List<Order>> getMyReceivedOrders(String username) {
        User user = userRepository.findByUsername(username).orElse(null);
        if (user == null) return ResponseData.<List<Order>>builder().message("User not found").build();

        List<Order> orders = orderRepository.findByRecipientId(user);
        return ResponseData.<List<Order>>builder().message("Success").data(orders).build();
    }

    @Override
    public ResponseData<Order> getRobotCurrentOrder(Long robotId) {
        Robot robot = robotRepository.findById(robotId).orElse(null);
        if (robot == null) return ResponseData.<Order>builder().message("Robot not found").build();

        // Tìm đơn hàng mà robot này đang đi lấy (PENDING) hoặc đang giao (DELIVERING)
        Optional<Order> order = orderRepository.findByRobotAndStatus(robot, OrderStatusEnum.PENDING);
        if (order.isEmpty()) {
            order = orderRepository.findByRobotAndStatus(robot, OrderStatusEnum.DELIVERING);
        }
        
        return order.map(value -> ResponseData.<Order>builder().message("Success").data(value).build())
                .orElseGet(() -> ResponseData.<Order>builder().message("No active order found").build());
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
