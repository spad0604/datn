package com.example.robot_delivery.model;

import lombok.Builder;
import lombok.Data;

@Builder
@Data
public class ResponseData<T> {
    private String message;
    private T data;
}
