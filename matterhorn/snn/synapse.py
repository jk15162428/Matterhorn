from typing import Union
import torch
from torch import Tensor
import torch.nn as nn
from torch.nn.common_types import _size_1_t, _size_2_t, _size_3_t
from torch.nn.modules.normalization import _shape_t


"""
脉冲神经网络神经元的突触，一层的前半段。输入为脉冲，输出为模拟电位值。
由突触将来自上一层神经元的脉冲信号$O_{j}^{l-1}(t)$整合成为突触后电位$X_{i}^{l}(t)$后，在胞体中进行突触后电位的累积和发放。
"""


class Linear(nn.Linear):
    def __init__(self, in_features: int, out_features: int, bias: bool = True, device = None, dtype = None) -> None:
        """
        全连接操作，输入一个大小为[B, L_{in}]的张量，输出一个大小为[B, L_{out}]的张量。
        @params:
            in_features: 输入的长度L_{in}
            out_features: 输出的长度L_{out}
            bias: bool 是否要加入偏置
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_features = in_features,
            out_features = out_features,
            bias = bias,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class Conv1d(nn.Conv1d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: _size_1_t, stride: _size_1_t = 1, padding: Union[_size_1_t, str] = 0, dilation: _size_1_t = 1, groups: int = 1, bias: bool = True, padding_mode: str = "zeros", device = None, dtype = None) -> None:
        """
        一维卷积操作，输入一个大小为[B, C_{in}, L_{in}]的张量，输出一个大小为[B, C_{out}, L_{out}]的张量。
        @params:
            in_channels: int 输入的频道数C_{in}
            out_channels: int 输出的频道C_{out}
            kernel_size: _size_1_t 卷积核的形状
            stride: _size_1_t 卷积的输出步长，决定卷积输出的形状
            padding: _size_1_t | str 在边缘填充的量（一般为卷积核大小的一半，向下取整）
            dilation: _size_1_t 卷积的输入步长
            groups: int 分组进行卷积操作的组数
            bias: bool 是否要加入偏置
            padding_mode: str 边缘填充的方式
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = padding,
            dilation = dilation,
            groups = groups,
            bias = bias,
            padding_mode = padding_mode,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class Conv2d(nn.Conv2d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: _size_2_t, stride: _size_2_t = 1, padding: Union[_size_2_t, str] = 0, dilation: _size_2_t = 1, groups: int = 1, bias: bool = True, padding_mode: str = "zeros", device = None, dtype = None) -> None:
        """
        二维卷积操作，输入一个大小为[B, C_{in}, H_{in}, W_{in}]的张量，输出一个大小为[B, C_{out}, H_{out}, W_{out}]的张量。
        @params:
            in_channels: int 输入的频道数C_{in}
            out_channels: int 输出的频道C_{out}
            kernel_size: _size_2_t 卷积核的形状
            stride: _size_2_t 卷积的输出步长，决定卷积输出的形状
            padding: _size_2_t | str 在边缘填充的量（一般为卷积核大小的一半，向下取整）
            dilation: _size_2_t 卷积的输入步长
            groups: int 分组进行卷积操作的组数
            bias: bool 是否要加入偏置
            padding_mode: str 边缘填充的方式
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = padding,
            dilation = dilation,
            groups = groups,
            bias = bias,
            padding_mode = padding_mode,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class Conv3d(nn.Conv3d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: _size_3_t, stride: _size_3_t = 1, padding: Union[_size_3_t, str] = 0, dilation: _size_3_t = 1, groups: int = 1, bias: bool = True, padding_mode: str = "zeros", device = None, dtype = None) -> None:
        """
        三维卷积操作，输入一个大小为[B, C_{in}, H_{in}, W_{in}, L_{in}]的张量，输出一个大小为[B, C_{out}, H_{out}, W_{out}, L_{out}]的张量。
        @params:
            in_channels: int 输入的频道数C_{in}
            out_channels: int 输出的频道C_{out}
            kernel_size: _size_3_t 卷积核的形状
            stride: _size_3_t 卷积的输出步长，决定卷积输出的形状
            padding: _size_3_t | str 在边缘填充的量（一般为卷积核大小的一半，向下取整）
            dilation: _size_3_t 卷积的输入步长
            groups: int 分组进行卷积操作的组数
            bias: bool 是否要加入偏置
            padding_mode: str 边缘填充的方式
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = padding,
            dilation = dilation,
            groups = groups,
            bias = bias,
            padding_mode = padding_mode,
            device = device,
            dtype = dtype
        )
    

    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class ConvTranspose1d(nn.ConvTranspose1d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: _size_1_t, stride: _size_1_t = 1, padding: _size_1_t = 0, output_padding: _size_1_t = 0, groups: int = 1, bias: bool = True, dilation: _size_1_t = 1, padding_mode: str = "zeros", device = None, dtype = None) -> None:
        """
        一维逆卷积操作，输入一个大小为[B, C_{in}, L_{in}]的张量，输出一个大小为[B, C_{out}, L_{out}]的张量。
        @params:
            in_channels: int 输入的频道数C_{in}
            out_channels: int 输出的频道C_{out}
            kernel_size: _size_1_t 卷积核的形状
            stride: _size_1_t 卷积的输出步长，决定卷积输出的形状
            padding: _size_1_t 在边缘填充的量（一般为卷积核大小的一半，向下取整）
            output_padding: _size_1_t 在输出边缘填充的量
            groups: int 分组进行卷积操作的组数
            bias: bool 是否要加入偏置
            dilation: _size_1_t 卷积的输出步长
            padding_mode: str 边缘填充的方式
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = padding,
            output_padding = output_padding,
            groups = groups,
            bias = bias,
            dilation = dilation,
            padding_mode = padding_mode,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class ConvTranspose2d(nn.ConvTranspose2d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: _size_2_t, stride: _size_2_t = 1, padding: _size_2_t = 0, output_padding: _size_2_t = 0, groups: int = 1, bias: bool = True, dilation: _size_2_t = 1, padding_mode: str = "zeros", device = None, dtype = None) -> None:
        """
        二维逆卷积操作，输入一个大小为[B, C_{in}, H_{in}, W_{in}]的张量，输出一个大小为[B, C_{out}, H_{out}, W_{out}]的张量。
        @params:
            in_channels: int 输入的频道数C_{in}
            out_channels: int 输出的频道C_{out}
            kernel_size: _size_2_t 卷积核的形状
            stride: _size_2_t 卷积的输出步长，决定卷积输出的形状
            padding: _size_2_t 在边缘填充的量（一般为卷积核大小的一半，向下取整）
            output_padding: _size_2_t 在输出边缘填充的量
            groups: int 分组进行卷积操作的组数
            bias: bool 是否要加入偏置
            dilation: _size_2_t 卷积的输出步长
            padding_mode: str 边缘填充的方式
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = padding,
            output_padding = output_padding,
            groups = groups,
            bias = bias,
            dilation = dilation,
            padding_mode = padding_mode,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class ConvTranspose3d(nn.ConvTranspose3d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: _size_3_t, stride: _size_3_t = 1, padding: _size_3_t = 0, output_padding: _size_3_t = 0, groups: int = 1, bias: bool = True, dilation: _size_3_t = 1, padding_mode: str = "zeros", device = None, dtype = None) -> None:
        """
        三维逆卷积操作，输入一个大小为[B, C_{in}, H_{in}, W_{in}, L_{in}]的张量，输出一个大小为[B, C_{out}, H_{out}, W_{out}, L_{out}]的张量。
        @params:
            in_channels: int 输入的频道数C_{in}
            out_channels: int 输出的频道C_{out}
            kernel_size: _size_3_t 卷积核的形状
            stride: _size_3_t 卷积的输出步长，决定卷积输出的形状
            padding: _size_3_t 在边缘填充的量（一般为卷积核大小的一半，向下取整）
            output_padding: _size_3_t 在输出边缘填充的量
            groups: int 分组进行卷积操作的组数
            bias: bool 是否要加入偏置
            dilation: _size_3_t 卷积的输出步长
            padding_mode: str 边缘填充的方式
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = padding,
            output_padding = output_padding,
            groups = groups,
            bias = bias,
            dilation = dilation,
            padding_mode = padding_mode,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, o: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            o: torch.Tensor 来自上一层的输入脉冲$O_{j}^{l-1}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(o)
        return x


class BatchNorm1d(nn.BatchNorm1d):
    def __init__(self, num_features: int, eps: float = 0.00001, momentum: float = 0.1, affine: bool = True, track_running_stats: bool = True, device = None, dtype = None) -> None:
        """
        一维批归一化。
        @params:
            num_features: int 需要被归一化那一维度的长度
            eps: float 参数epsilon
            momentum: float 动量参数
            affine: bool 是否启用参数gamma和beta，进行仿射变换
            track_running_stats: bool 是否需要跟踪整个训练过程来进行批归一化的学习
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            num_features = num_features,
            eps = eps,
            momentum = momentum,
            affine = affine,
            track_running_stats = track_running_stats,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, x: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(x)
        return x


class BatchNorm2d(nn.BatchNorm2d):
    def __init__(self, num_features: int, eps: float = 0.00001, momentum: float = 0.1, affine: bool = True, track_running_stats: bool = True, device = None, dtype = None) -> None:
        """
        二维批归一化。
        @params:
            num_features: int 需要被归一化那一维度的长度
            eps: float 参数epsilon
            momentum: float 动量参数
            affine: bool 是否启用参数gamma和beta，进行仿射变换
            track_running_stats: bool 是否需要跟踪整个训练过程来进行批归一化的学习
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            num_features = num_features,
            eps = eps,
            momentum = momentum,
            affine = affine,
            track_running_stats = track_running_stats,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, x: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(x)
        return x


class BatchNorm3d(nn.BatchNorm3d):
    def __init__(self, num_features: int, eps: float = 0.00001, momentum: float = 0.1, affine: bool = True, track_running_stats: bool = True, device = None, dtype = None) -> None:
        """
        三维批归一化。
        @params:
            num_features: int 需要被归一化那一维度的长度
            eps: float 参数epsilon
            momentum: float 动量参数
            affine: bool 是否启用参数gamma和beta，进行仿射变换
            track_running_stats: bool 是否需要跟踪整个训练过程来进行批归一化的学习
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            num_features = num_features,
            eps = eps,
            momentum = momentum,
            affine = affine,
            track_running_stats = track_running_stats,
            device = device,
            dtype = dtype
        )
    
    
    def forward(self, x: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(x)
        return x


class LayerNorm(nn.LayerNorm):
    def __init__(self, normalized_shape: _shape_t, eps: float = 0.00001, elementwise_affine: bool = True, device=None, dtype=None) -> None:
        """
        数据归一化。
        @params:
            normalized_shape: _shape_t 在什么数据尺度上进行归一化
            eps: float 参数epsilon
            elementwise_affine: bool 是否启用参数gamma和beta，进行仿射变换
            device: torch.device 所计算的设备
            dtype: 所计算的数据类型
        """
        super().__init__(
            normalized_shape = normalized_shape,
            eps = eps,
            elementwise_affine = elementwise_affine,
            device = device,
            dtype = dtype
        )    
    
    
    def forward(self, x: Tensor) -> Tensor:
        """
        前向传播函数。
        @params:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        @return:
            x: torch.Tensor 突触的突触后电位$X_{i}^{l}(t)$
        """
        x = super().forward(x)
        return x