package com.example.robot_delivery.repositorys;

import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.User;
import com.example.robot_delivery.model.enums.OrderStatusEnum;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(User customer);
    List<Order> findByRecipientId(User recipient);
    List<Order> findByStatusOrderByCreatedAtAsc(OrderStatusEnum status);
    Optional<Order> findByRobotAndStatus(Robot robot, OrderStatusEnum status);
}
