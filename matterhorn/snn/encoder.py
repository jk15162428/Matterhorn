import torch
import torch.nn as nn


"""
脉冲神经网络的编码机制。
注意：此单元可能会改变张量形状。
"""


class Direct(nn.Module):
    def __init__(self) -> None:
        """
        直接编码，直接对传入的脉冲（事件）数据进行编码
        """
        super().__init__()
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        直接编码的前向传播函数，直接将第二个维度作为时间维度，转置到首个维度上
        @params:
            x: torch.Tensor 输入张量，形状为[B,T,...]
        @return:
            y: torch.Tensor 输出张量，形状为[T,B,...]
        """
        idx = [i for i, j in enumerate(x.shape)]
        assert len(idx) >= 2, "There is no time steps."
        idx[0], idx[1] = idx[1], idx[0]
        y = x.permute(*idx)
        return y


class Poisson(nn.Module):
    def __init__(self, time_steps: int = 64, max_value: float = 1.0, min_value: float = 0.0) -> None:
        """
        泊松编码（速率编码），将值转化为脉冲发放率（多步）
        @params:
            time_steps: int 生成的时间步长
            max_value: float 最大值
            min_value: float 最小值
        """
        super().__init__()
        assert max_value > min_value, "Max value is less than min value."
        self.time_steps = time_steps
        self.max_value = max_value
        self.min_value = min_value


    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "time_steps=%d, max=%.3f, min=%.3f" % (self.time_steps, self.max_value, self.min_value)
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        泊松编码的前向传播函数，将值$V$转化为该时间步$t$内的脉冲$O^{0}(t)$
        @params:
            x: torch.Tensor 输入张量，形状为[B,...]
        @return:
            y: torch.Tensor 输出张量，形状为[T,B,...]
        """
        x = (x - self.min_value) / (self.max_value - self.min_value)
        y_seq = []
        for t in range(self.time_steps):
            r = torch.rand_like(x)
            y_seq.append(r.le(x).to(x))
        y = torch.stack(y_seq)
        return y


class Temporal(nn.Module):
    def __init__(self, time_steps: int = 64, max_value: float = 1.0, min_value: float = 0.0, prob: float = 0.75) -> None:
        """
        时间编码，在某个时间之前不会产生脉冲，在某个时间之后随机产生脉冲
        @params:
            time_steps: int 生成的时间步长
            max_value: float 最大值
            min_value: float 最小值
        """
        super().__init__()
        assert max_value > min_value, "Max value is less than min value."
        self.time_steps = time_steps
        self.max_value = max_value
        self.min_value = min_value
        self.prob = prob


    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "time_steps=%d, max=%.3f, min=%.3f, spike_freq=%.3f" % (self.time_steps, self.max_value, self.min_value, self.prob)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        时间编码的前向传播函数，将值$V$转化为该时间步$t$内的脉冲$O^{0}(t)$
        @params:
            x: torch.Tensor 输入张量，形状为[B,...]
        @return:
            y: torch.Tensor 输出张量，形状为[T,B,...]
        """
        x = (x - self.min_value) / (self.max_value - self.min_value) * self.time_steps
        y_seq = []
        for t in range(self.time_steps):
            f = (t + 0.0 - x).ge(0.0).to(x)
            r = torch.rand_like(x).le(self.prob).to(x)
            y_seq.append(f * r)
        y = torch.stack(y_seq)
        return y