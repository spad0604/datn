package com.example.robot_delivery.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "robot")
@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder
public class Robot {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private double latitude;

    private double longitude;

    private String status;
}
