package com.example.robot_delivery.controller;

import com.example.robot_delivery.interfaces.IOrderService;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.request.CreateOrderRequest;
import com.example.robot_delivery.model.responses.OrderResponse;
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
    public ResponseEntity<ResponseData<OrderResponse>> createOrder(@RequestBody CreateOrderRequest request, Authentication authentication) {
        return ResponseEntity.ok(orderService.createOrder(request, authentication.getName()));
    }

    @PutMapping("/update/{id}")
    @Operation(summary = "Cập nhật thông tin đơn hàng")
    public ResponseEntity<ResponseData<OrderResponse>> updateOrder(@PathVariable Long id, @RequestBody CreateOrderRequest request, Authentication authentication) {
        return ResponseEntity.ok(orderService.updateOrder(id, request, authentication.getName()));
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "Xoá đơn hàng")
    public ResponseEntity<ResponseData<Void>> deleteOrder(@PathVariable Long id, Authentication authentication) {
        return ResponseEntity.ok(orderService.deleteOrder(id, authentication.getName()));
    }

    @GetMapping("/my-created")
    @Operation(summary = "Lấy danh sách đơn hàng mình đã tạo")
    public ResponseEntity<ResponseData<List<OrderResponse>>> getMyCreatedOrders(Authentication authentication) {
        return ResponseEntity.ok(orderService.getMyCreatedOrders(authentication.getName()));
    }

    @GetMapping("/my-received")
    @Operation(summary = "Lấy danh sách đơn hàng mình được nhận")
    public ResponseEntity<ResponseData<List<OrderResponse>>> getMyReceivedOrders(Authentication authentication) {
        return ResponseEntity.ok(orderService.getMyReceivedOrders(authentication.getName()));
    }

    @GetMapping("/current-robot-order/{robotId}")
    @Operation(summary = "Lấy thông tin đơn hàng hiện tại robot đang nhận")
    public ResponseEntity<ResponseData<OrderResponse>> getRobotCurrentOrder(@PathVariable Long robotId) {
        return ResponseEntity.ok(orderService.getRobotCurrentOrder(robotId));
    }
}
