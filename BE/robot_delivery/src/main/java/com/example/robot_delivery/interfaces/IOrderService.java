package com.example.robot_delivery.interfaces;

import com.example.robot_delivery.model.ResponseData;
import com.example.robot_delivery.model.request.CreateOrderRequest;
import com.example.robot_delivery.model.responses.OrderResponse;

import java.util.List;

public interface IOrderService {
    ResponseData<OrderResponse> createOrder(CreateOrderRequest request, String username);
    ResponseData<OrderResponse> updateOrder(Long id, CreateOrderRequest request, String username);
    ResponseData<Void> deleteOrder(Long id, String username);
    ResponseData<List<OrderResponse>> getMyCreatedOrders(String username);
    ResponseData<List<OrderResponse>> getMyReceivedOrders(String username);
    ResponseData<OrderResponse> getRobotCurrentOrder(Long robotId);
    
    ResponseData<OrderResponse> confirmSender(Long orderId, String username);
    ResponseData<OrderResponse> confirmReceiver(Long orderId, String username);
}
