package com.example.robot_delivery.controller;

import com.example.robot_delivery.interfaces.IOrderService;
import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.ResponseData;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
@Tag(name = "Order", description = "Quản lý đơn hàng")
public class OrderController {

    private final IOrderService orderService;

    @PostMapping("/create")
    @Operation(summary = "Tạo đơn hàng mới (tự gán robot gần nhất)")
    public ResponseEntity<ResponseData<Order>> createOrder(@RequestBody Order order, Authentication authentication) {
        return ResponseEntity.ok(orderService.createOrder(order, authentication.getName()));
    }

    @PutMapping("/update/{id}")
    @Operation(summary = "Cập nhật thông tin đơn hàng")
    public ResponseEntity<ResponseData<Order>> updateOrder(@PathVariable Long id, @RequestBody Order order, Authentication authentication) {
        return ResponseEntity.ok(orderService.updateOrder(id, order, authentication.getName()));
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "Xoá đơn hàng")
    public ResponseEntity<ResponseData<Void>> deleteOrder(@PathVariable Long id, Authentication authentication) {
        return ResponseEntity.ok(orderService.deleteOrder(id, authentication.getName()));
    }

    @GetMapping("/my-created")
    @Operation(summary = "Lấy danh sách đơn hàng mình đã tạo")
    public ResponseEntity<ResponseData<List<Order>>> getMyCreatedOrders(Authentication authentication) {
        return ResponseEntity.ok(orderService.getMyCreatedOrders(authentication.getName()));
    }

    @GetMapping("/my-received")
    @Operation(summary = "Lấy danh sách đơn hàng mình được nhận")
    public ResponseEntity<ResponseData<List<Order>>> getMyReceivedOrders(Authentication authentication) {
        return ResponseEntity.ok(orderService.getMyReceivedOrders(authentication.getName()));
    }

    @GetMapping("/current-robot-order/{robotId}")
    @Operation(summary = "Lấy thông tin đơn hàng hiện tại robot đang nhận")
    public ResponseEntity<ResponseData<Order>> getRobotCurrentOrder(@PathVariable Long robotId) {
        return ResponseEntity.ok(orderService.getRobotCurrentOrder(robotId));
    }
}
