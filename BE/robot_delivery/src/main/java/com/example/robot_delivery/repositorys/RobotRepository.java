package com.example.robot_delivery.repositorys;

import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RobotRepository extends JpaRepository<Robot, Long> {
    List<Robot> findByStatus(RobotStatusEnum status);
}
