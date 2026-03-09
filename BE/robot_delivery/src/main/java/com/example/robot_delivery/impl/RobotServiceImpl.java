package com.example.robot_delivery.impl;

import com.example.robot_delivery.interfaces.IRobotService;
import com.example.robot_delivery.model.Robot;
import com.example.robot_delivery.model.enums.RobotStatusEnum;
import com.example.robot_delivery.repositorys.RobotRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RobotServiceImpl implements IRobotService {
    private final RobotRepository robotRepository;

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
        } catch (Exception e) {
            return;
        }
    }
}
