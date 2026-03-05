package com.example.robot_delivery;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class RobotDeliveryApplication {

	public static void main(String[] args) {
		SpringApplication.run(RobotDeliveryApplication.class, args);
	}

}
