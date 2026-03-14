package com.example.robot_delivery.repositorys;

import com.example.robot_delivery.model.Notification;
import com.example.robot_delivery.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface NotificationRepository extends JpaRepository<Notification, Long> {
    List<Notification> findByUserOrderByCreatedAtDesc(User user);
}
