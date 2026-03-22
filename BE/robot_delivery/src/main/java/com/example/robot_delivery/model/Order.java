package com.example.robot_delivery.model;

import com.example.robot_delivery.model.enums.OrderStatusEnum;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "orders")
@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String orderId;

    @ManyToOne
    @JoinColumn(name = "customer_id", referencedColumnName = "id")
    private User customerId;

    @ManyToOne
    @JoinColumn(name = "recipient_id", referencedColumnName = "id")
    private User recipientId;

    private String recipientPhone;

    private String shippingId;

    private String deliveryId;

    private Double startLat;

    private Double startLng;
    private String senderAddress;

    private Double deliveryLat;

    private Double deliveryLng;
    
    private String deliveryAddress;

    private String pinCode;


    private String senderName;

    @ManyToOne
    @JoinColumn(name = "robot_id", referencedColumnName = "id")
    private Robot robot;

    @Enumerated(EnumType.STRING)
    private OrderStatusEnum status;

    @Column(name = "created_at")
    private java.time.LocalDateTime createdAt;

    @Column(name = "is_pickup_notified")
    private Boolean isPickupNotified;

    @Column(name = "is_delivery_notified")
    private Boolean isDeliveryNotified;
}
