package com.example.robot_delivery.interfaces;

import com.example.robot_delivery.model.Order;
import com.example.robot_delivery.model.ResponseData;
import java.util.List;

public interface IOrderService {
    ResponseData<Order> createOrder(Order order, String username);
    ResponseData<Order> updateOrder(Long id, Order order, String username);
    ResponseData<Void> deleteOrder(Long id, String username);
    ResponseData<List<Order>> getMyCreatedOrders(String username);
    ResponseData<List<Order>> getMyReceivedOrders(String username);
    ResponseData<Order> getRobotCurrentOrder(Long robotId);
}
