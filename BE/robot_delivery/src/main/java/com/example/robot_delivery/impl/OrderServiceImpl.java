package com.example.robot_delivery.impl;

import com.example.robot_delivery.interfaces.IOrderService;
import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.User;
import com.example.robot_delivery.model.request.CreateOrderRequest;
import com.example.robot_delivery.model.responses.OrderResponse;
import com.example.robot_delivery.model.enums.OrderStatusEnum;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import com.example.robot_delivery.repositorys.OrderRepository;
import com.example.robot_delivery.repositorys.RobotRepository;
import com.example.robot_delivery.repositorys.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements IOrderService {

    private final OrderRepository orderRepository;
    private final RobotRepository robotRepository;
    private final UserRepository userRepository;

    private OrderResponse.UserSummary mapToUserSummary(User user) {
        if (user == null) return null;
        return OrderResponse.UserSummary.builder()
                .id(user.getId())
                .username(user.getUsername())
                .fullName(user.getFirstName() + " " + user.getLastName())
                .phoneNumber(user.getPhoneNumber())
                .build();
    }

    private OrderResponse mapToOrderResponse(Order order) {
        return OrderResponse.builder()
                .id(order.getId())
                .orderId(order.getOrderId())
                .customer(mapToUserSummary(order.getCustomerId()))
                .recipient(mapToUserSummary(order.getRecipientId()))
                .recipientPhone(order.getRecipientPhone())
                .startLat(order.getStartLat())
                .startLng(order.getStartLng())
                .deliveryLat(order.getDeliveryLat())
                .deliveryLng(order.getDeliveryLng())
                .pinCode(order.getPinCode())
                .senderName(order.getSenderName())
                .robotId(order.getRobot() != null ? order.getRobot().getId() : null)
                .robotName(order.getRobot() != null ? order.getRobot().getRobotName() : null)
                .status(order.getStatus())
                .createdAt(order.getCreatedAt())
                .build();
    }

    @Override
    @Transactional
    public ResponseData<OrderResponse> createOrder(CreateOrderRequest request, String username) {
        User customer = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        Order order = Order.builder()
                .orderId("ORD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .customerId(customer)
                .senderName(customer.getFirstName() + " " + customer.getLastName())
                .recipientPhone(request.getRecipientPhone())
                .startLat(request.getStartLat())
                .startLng(request.getStartLng())
                .deliveryLat(request.getDeliveryLat())
                .deliveryLng(request.getDeliveryLng())
                .pinCode(generatePinCode())
                .createdAt(LocalDateTime.now())
                .build();

        // Tự động tìm recipientId theo số điện thoại
        if (request.getRecipientPhone() != null) {
            userRepository.findByPhoneNumber(request.getRecipientPhone()).ifPresent(order::setRecipientId);
        }

        // Tìm robot rảnh gần nhất
        List<Robot> idleRobots = robotRepository.findByStatus(RobotStatusEnum.IDLE);
        Robot nearestRobot = null;
        double minDistance = Double.MAX_VALUE;

        for (Robot robot : idleRobots) {
            double distance = calculateDistance(
                    robot.getLatitude(), robot.getLongitude(),
                    order.getStartLat(), order.getStartLng()
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
            order.setRobot(null);
            order.setStatus(OrderStatusEnum.WAIT_ROBOT);
        }

        Order savedOrder = orderRepository.save(order);
        String message = (nearestRobot != null) ? "Order created and robot assigned" : "Order created. Waiting for an available robot.";
        
        return ResponseData.<OrderResponse>builder()
                .message(message)
                .data(mapToOrderResponse(savedOrder))
                .build();
    }

    @Override
    public ResponseData<OrderResponse> updateOrder(Long id, CreateOrderRequest request, String username) {
        return orderRepository.findById(id).map(existing -> {
            if (!existing.getCustomerId().getUsername().equals(username)) {
                return ResponseData.<OrderResponse>builder().message("Access denied").build();
            }
            existing.setRecipientPhone(request.getRecipientPhone());
            existing.setDeliveryLat(request.getDeliveryLat());
            existing.setDeliveryLng(request.getDeliveryLng());
            
            if (request.getRecipientPhone() != null) {
                userRepository.findByPhoneNumber(request.getRecipientPhone())
                    .ifPresentOrElse(existing::setRecipientId, () -> existing.setRecipientId(null));
            }
            
            return ResponseData.<OrderResponse>builder()
                    .message("Order updated")
                    .data(mapToOrderResponse(orderRepository.save(existing)))
                    .build();
        }).orElse(ResponseData.<OrderResponse>builder().message("Order not found").build());
    }

    @Override
    @Transactional
    public ResponseData<Void> deleteOrder(Long id, String username) {
        return orderRepository.findById(id).map(existing -> {
            if (!existing.getCustomerId().getUsername().equals(username)) {
                return ResponseData.<Void>builder().message("Access denied").build();
            }

            // Nếu đơn hàng đang có robot được gán (chưa giao hàng),
            // chuyển robot về trạng thái IDLE để sẵn sàng nhận đơn mới
            if (existing.getRobot() != null &&
                    (existing.getStatus() == OrderStatusEnum.PENDING ||
                     existing.getStatus() == OrderStatusEnum.WAIT_ROBOT)) {
                Robot robot = existing.getRobot();
                robot.setStatus(RobotStatusEnum.IDLE);
                robotRepository.save(robot);
            }

            orderRepository.delete(existing);
            return ResponseData.<Void>builder().message("Order deleted").build();
        }).orElse(ResponseData.<Void>builder().message("Order not found").build());
    }

    @Override
    public ResponseData<List<OrderResponse>> getMyCreatedOrders(String username) {
        User user = userRepository.findByUsername(username).orElse(null);
        if (user == null) return ResponseData.<List<OrderResponse>>builder().message("User not found").build();
        
        List<Order> orders = orderRepository.findByCustomerId(user);
        List<OrderResponse> response = orders.stream()
                .map(this::mapToOrderResponse)
                .collect(Collectors.toList());
        return ResponseData.<List<OrderResponse>>builder().message("Success").data(response).build();
    }

    @Override
    public ResponseData<List<OrderResponse>> getMyReceivedOrders(String username) {
        User user = userRepository.findByUsername(username).orElse(null);
        if (user == null) return ResponseData.<List<OrderResponse>>builder().message("User not found").build();

        List<Order> orders = orderRepository.findByRecipientId(user);
        List<OrderResponse> response = orders.stream()
                .map(this::mapToOrderResponse)
                .collect(Collectors.toList());
        return ResponseData.<List<OrderResponse>>builder().message("Success").data(response).build();
    }

    @Override
    public ResponseData<OrderResponse> getRobotCurrentOrder(Long robotId) {
        Robot robot = robotRepository.findById(robotId).orElse(null);
        if (robot == null) return ResponseData.<OrderResponse>builder().message("Robot not found").build();

        Optional<Order> order = orderRepository.findByRobotAndStatus(robot, OrderStatusEnum.PENDING);
        if (order.isEmpty()) {
            order = orderRepository.findByRobotAndStatus(robot, OrderStatusEnum.DELIVERING);
        }
        
        return order.map(value -> ResponseData.<OrderResponse>builder().message("Success").data(mapToOrderResponse(value)).build())
                .orElse(ResponseData.<OrderResponse>builder().message("No active order for this robot").build());
    }

    @Override
    @Transactional
    public ResponseData<OrderResponse> confirmSender(Long orderId, String username) {
        return orderRepository.findById(orderId).map(order -> {
            // Verify the user is the sender
            if (!order.getCustomerId().getUsername().equals(username)) {
                return ResponseData.<OrderResponse>builder().message("Access denied. Only the sender can confirm sending.").build();
            }

            if (order.getStatus() != OrderStatusEnum.PENDING || order.getRobot() == null) {
                return ResponseData.<OrderResponse>builder().message("Order cannot be confirmed at this stage").build();
            }

            order.setStatus(OrderStatusEnum.DELIVERING);
            Robot robot = order.getRobot();
            robot.setStatus(RobotStatusEnum.DELIVERING);
            
            robotRepository.save(robot);
            Order savedOrder = orderRepository.save(order);
            
            return ResponseData.<OrderResponse>builder()
                    .message("Sender confirmed successfully")
                    .data(mapToOrderResponse(savedOrder))
                    .build();
        }).orElse(ResponseData.<OrderResponse>builder().message("Order not found").build());
    }

    @Override
    @Transactional
    public ResponseData<OrderResponse> confirmReceiver(Long orderId, String username) {
        return orderRepository.findById(orderId).map(order -> {
            // Verify the user is the receiver if recipientId is present
            if (order.getRecipientId() != null && !order.getRecipientId().getUsername().equals(username)) {
                 return ResponseData.<OrderResponse>builder().message("Access denied. Only the receiver can confirm receiving.").build();
            } else if (order.getRecipientId() == null) {
                 // Fallback if recipient ID is not mapped via phone number (e.g. user not registered)
                 // You might want a different logic or allow the sender to confirm if recipient is anonymous, or use pin code.
                 // Currently, if the system allows placing order to unregistered user, we might relax username check here 
                 // but for security we should only allow the correct user. 
                 // Assuming here the user receiving must be the mapped recipient.
                 User currentUser = userRepository.findByUsername(username).orElse(null);
                 if (currentUser == null || !currentUser.getPhoneNumber().equals(order.getRecipientPhone())) {
                      return ResponseData.<OrderResponse>builder().message("Access denied. Phone number does not match recipient.").build();
                 }
            }

            if (order.getStatus() != OrderStatusEnum.DELIVERING || order.getRobot() == null) {
                return ResponseData.<OrderResponse>builder().message("Order is not currently being delivered").build();
            }

            order.setStatus(OrderStatusEnum.DELIVERED);
            Robot robot = order.getRobot();
            robot.setStatus(RobotStatusEnum.IDLE);
            
            robotRepository.save(robot);
            Order savedOrder = orderRepository.save(order);
            
            return ResponseData.<OrderResponse>builder()
                    .message("Receiver confirmed successfully")
                    .data(mapToOrderResponse(savedOrder))
                    .build();
        }).orElse(ResponseData.<OrderResponse>builder().message("Order not found").build());
    }

    private String generatePinCode() {
        Random random = new Random();
        int pin = 100000 + random.nextInt(900000);
        return String.valueOf(pin);
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
