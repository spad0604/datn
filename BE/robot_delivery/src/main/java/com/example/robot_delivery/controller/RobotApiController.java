package com.example.robot_delivery.controller;

import com.example.robot_delivery.interfaces.IOrderService;
import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.responses.OrderResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/robot")
@RequiredArgsConstructor
@Tag(name = "Robot API", description = "API cho Raspberry Pi/robot (secret-based)")
public class RobotApiController {

    private final IOrderService orderService;

    @Value("${robot.shared-secret:DATN_2025_2_GIAP}")
    private String serverSecret;

    @GetMapping("/{robotId}/current-order")
    @Operation(summary = "Robot lấy đơn hàng hiện tại (không cần JWT, dùng shared secret)")
    public ResponseEntity<ResponseData<OrderResponse>> getRobotCurrentOrder(
            @PathVariable Long robotId,
            @RequestHeader(value = "X-Robot-Secret", required = false) String headerSecret,
            @RequestParam(value = "secretKey", required = false) String secretKey
    ) {
        String provided = (headerSecret != null && !headerSecret.isBlank()) ? headerSecret : secretKey;
        if (provided == null || !serverSecret.equals(provided)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ResponseData.<OrderResponse>builder().message("Unauthorized").build());
        }
        return ResponseEntity.ok(orderService.getRobotCurrentOrder(robotId));
    }
}
