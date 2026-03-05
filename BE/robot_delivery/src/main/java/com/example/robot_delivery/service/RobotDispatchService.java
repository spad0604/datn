package com.example.robot_delivery.service;

import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.enums.OrderStatusEnum;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import com.example.robot_delivery.repositorys.OrderRepository;
import com.example.robot_delivery.repositorys.RobotRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class RobotDispatchService {

    private final OrderRepository orderRepository;
    private final RobotRepository robotRepository;

    /**
     * Mỗi 10 giây quét các đơn hàng đang đợi robot rảnh
     */
    @Scheduled(fixedRate = 10000)
    @Transactional
    public void dispatchRobotsToWaitingOrders() {
        // Lấy danh sách đơn hàng đang đợi theo thứ tự thời gian (ưu tiên đơn cũ trước)
        List<Order> waitingOrders = orderRepository.findByStatusOrderByCreatedAtAsc(OrderStatusEnum.WAIT_ROBOT);
        
        if (waitingOrders.isEmpty()) {
            return;
        }

        // Lấy danh sách robot đang rảnh
        List<Robot> idleRobots = robotRepository.findByStatus(RobotStatusEnum.IDLE);
        
        if (idleRobots.isEmpty()) {
            return;
        }

        log.info("Found {} orders waiting and {} robots idle. Starting dispatching...", waitingOrders.size(), idleRobots.size());

        for (Order order : waitingOrders) {
            if (idleRobots.isEmpty()) break;

            Robot nearestRobot = null;
            double minDistance = Double.MAX_VALUE;

            // Tìm robot rảnh gần nhất cho đơn hàng này
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
                // Gán robot cho đơn hàng
                nearestRobot.setStatus(RobotStatusEnum.PICKING_UP);
                robotRepository.save(nearestRobot);
                
                order.setRobot(nearestRobot);
                order.setStatus(OrderStatusEnum.PENDING);
                orderRepository.save(order);

                // Loại robot này khỏi danh sách rảnh để không gán cho đơn hàng tiếp theo trong cùng vòng lặp
                idleRobots.remove(nearestRobot);
                
                log.info("Assigned robot ID {} to order ID {}", nearestRobot.getId(), order.getId());
            }
        }
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
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
