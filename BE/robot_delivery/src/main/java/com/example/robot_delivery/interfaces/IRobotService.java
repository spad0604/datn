package com.example.robot_delivery.interfaces;

import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.enums.RobotStatusEnum;

import java.util.List;

public interface IRobotService {
    List<Robot> findByStatus(RobotStatusEnum robotStatusEnum);

    public void updateRobotLocation(Long robotId, Double lat, Double lon);
}
