import torch
import torch.nn as nn
from matterhorn.snn import surrogate


"""
脉冲神经网络神经元的胞体，一层的后半段。输入为模拟电位值，输出为脉冲。
由突触将来自上一层神经元的脉冲信号$O_{j}^{l-1}(t)$整合成为突触后电位$X_{i}^{l}(t)$后，在胞体中进行突触后电位的累积和发放。
"""


class PFHSkeleton(nn.Module):
    def __init__(self, tau_m: float = 1.0, u_threshold: float = 1.0, u_rest: float = 0.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Potential-Firing-History三段式神经元胞体骨架，分别为：
        （1）通过历史电位$H_{i}^{l}(t)$和输入电位$X_{i}^{l}(t)$计算当前电位$U_{i}^{l}(t)$；
        （2）通过当前电位$U_{i}^{l}(t)$计算当前脉冲$O_{i}^{l}(t)$；
        （3）通过当前电位$U_{i}^{l}(t-1)$与当前脉冲$O_{i}^{l}(t-1)$计算下一时刻的历史电位$H_{i}^{l}(t)$
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__()
        assert tau_m != 0.0, "Can't let membrane time constant tau_m be zero."
        self.tau_m = tau_m
        self.u_threshold = u_threshold
        self.u_rest = u_rest
        self.spiking_function = spiking_function
        self.reset()


    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "tau_m=%.3f, u_th=%.3f, u_rest=%.3f" % (self.tau_m, self.u_threshold, self.u_rest)
    

    def reset(self) -> None:
        """
        重置整个神经元
        """
        self.u = self.u_rest


    def init_tensor(self, u: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        校正整个电位形状
        @params:
            u: torch.Tensor 待校正的电位，可能是张量或浮点值
            x: torch.Tensor 带有正确数据类型、所在设备和形状的张量
        @return:
            u: torch.Tensor 经过校正的电位张量
        """
        if isinstance(u, float):
            u = u * torch.ones_like(x)
        return u

    
    def detach(self) -> None:
        """
        将历史电位从计算图中分离，以停止在时间上进行反向传播
        """
        if isinstance(self.u, torch.Tensor):
            self.u = self.u.detach()


    def f_potential(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过历史电位$H_{i}^{l}(t)$和输入电位$X_{i}^{l}(t)$计算当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 历史电位$H_{i}^{l}(t)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        return h + (1.0 / self.tau_m) * x
    

    def f_firing(self, u: torch.Tensor) -> torch.Tensor:
        """
        通过当前电位$U_{i}^{l}(t)$计算当前脉冲$O_{i}^{l}(t)$。
        @params:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        @return:
            o: torch.Tensor 当前脉冲$O_{i}^{l}(t)$
        """
        return self.spiking_function(u - self.u_threshold)
    

    def f_history(self, u: torch.Tensor, o: torch.Tensor) -> torch.Tensor:
        """
        通过当前电位$U_{i}^{l}(t-1)$与当前脉冲$O_{i}^{l}(t-1)$计算下一时刻的历史电位$H_{i}^{l}(t)$。
        @params:
            u: torch.Tensor 当前电位$U_{i}^{l}(t-1)$
            o: torch.Tensor 当前脉冲$O_{i}^{l}(t-1)$
        @return:
            h: torch.Tensor 下一时刻的历史电位$H_{i}^{l}(t)$
        """
        raise NotImplementedError
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播函数
        @params:
            x: torch.Tensor 来自突触的输入电位$X_{i}^{l}(t)$
        @return:
            o: torch.Tensor 胞体当前的输出脉冲$O_{i}^{l}(t)$
        """
        self.u = self.init_tensor(self.u, x)
        self.u = self.f_potential(self.u, x)
        o = self.f_firing(self.u)
        self.u = self.f_history(self.u, o)
        return o


class RFRSkeleton(nn.Module):
    def __init__(self, tau_m: float = 1.0, u_threshold: float = 1.0, u_rest: float = 0.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Response-Firing-Reset三段式神经元胞体骨架，分别为：
        （1）通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$；
        （2）通过当前电位$U_{i}^{l}(t)$计算当前脉冲$O_{i}^{l}(t)$；
        （3）通过当前脉冲$O_{i}^{l}(t)$重置当前电位$U_{i}^{l}(t)$。
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__()
        self.tau_m = tau_m
        self.u_threshold = u_threshold
        self.u_rest = u_rest
        self.spiking_function = spiking_function
        self.reset()
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "tau_m=%.3f, u_th=%.3f, u_rest=%.3f" % (self.tau_m, self.u_threshold, self.u_rest)


    def init_tensor(self, u: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        校正整个电位形状
        @params:
            u: torch.Tensor 待校正的电位，可能是张量或浮点值
            x: torch.Tensor 带有正确数据类型、所在设备和形状的张量
        @return:
            u: torch.Tensor 经过校正的电位张量
        """
        if isinstance(u, float):
            u = u * torch.ones_like(x)
        return u


    def reset(self) -> None:
        """
        重置整个神经元
        """
        self.u = self.u_rest

    
    def detach(self) -> None:
        """
        将历史电位从计算图中分离，以停止在时间上进行反向传播
        """
        if isinstance(self.u, torch.Tensor):
            self.u = self.u.detach()


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        du = (1.0 / self.tau_m) * (-(h - self.u_rest) + x)
        u = h + du
        return u


    def f_firing(self, u: torch.Tensor) -> torch.Tensor:
        """
        通过当前电位$U_{i}^{l}(t)$计算当前脉冲$O_{i}^{l}(t)$。
        @params:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        @return:
            o: torch.Tensor 当前脉冲$O_{i}^{l}(t)$
        """
        return self.spiking_function(u - self.u_threshold)


    def f_reset(self, u: torch.Tensor, o: torch.Tensor) -> torch.Tensor:
        """
        通过当前脉冲$O_{i}^{l}(t)$重置当前电位$U_{i}^{l}(t)$。
        @params:
            u: torch.Tensor 当前电位$U_{i}^{l}(t-1)$
            o: torch.Tensor 当前脉冲$O_{i}^{l}(t-1)$
        @return:
            h: torch.Tensor 经过重置之后的当前电位$U_{i}^{l}(t-1)$
        """
        h = u * (1.0 - o) + self.u_rest * o
        return h
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播函数
        @params:
            x: torch.Tensor 来自突触的输入电位$X_{i}^{l}(t)$
        @return:
            o: torch.Tensor 胞体当前的输出脉冲$O_{i}^{l}(t)$
        """
        self.u = self.init_tensor(self.u, x)
        self.u = self.f_response(self.u, x)
        o = self.f_firing(self.u)
        self.u = self.f_reset(self.u, o)
        return o
    

class IF(RFRSkeleton):
    def __init__(self, u_threshold: float = 1.0, u_rest: float = 0.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Integrate-and-Fire(IF)神经元。
        无泄漏过程，一阶电位变换公式为：
        $$\frac{du}{dt}=RI$$
        @params:
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__(
            tau_m = 1.0,
            u_threshold = u_threshold,
            u_rest = u_rest,
            spiking_function = spiking_function
        )
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "u_th=%.3f, u_rest=%.3f" % (self.u_threshold, self.u_rest)


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        u = h + x
        return u


class LIF(RFRSkeleton):
    def __init__(self, tau_m: float = 2.0, u_threshold: float = 1.0, u_rest: float = 0.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Leaky-Integrate-and-Fire(LIF)神经元。
        一阶电位变换公式为：
        $$τ\frac{du}{dt}=-(u-u_{rest})+RI$$
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__(
            tau_m = tau_m,
            u_threshold = u_threshold,
            u_rest = u_rest,
            spiking_function = spiking_function
        )


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        du = (1.0 / self.tau_m) * (-(h - self.u_rest) + x)
        u = h + du
        return u


class QIF(RFRSkeleton):
    def __init__(self, tau_m: float = 2.0, u_threshold: float = 1.0, u_rest: float = 0.0, u_c: float = 0.8, a_0: float = 1.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Quadratic Integrate-and-Fire(QIF)神经元。
        一阶电位变换公式为：
        $$τ\frac{du}{dt}=a_{0}(u-u_{rest})(u-u_{c})+RI$$
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            u_c: float 参数$u_{c}$
            a_0: float 参数$a_{0}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__(
            tau_m = tau_m,
            u_threshold = u_threshold,
            u_rest = u_rest,
            spiking_function = spiking_function
        )
        self.a_0 = a_0
        self.u_c = u_c
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "tau_m=%.3f, u_th=%.3f, u_rest=%.3f, a_0=%.3f, u_C=%.3f" % (self.tau_m, self.u_threshold, self.u_rest, self.a_0, self.u_c)


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        du = (1.0 / self.tau_m) * (-self.a_0 * (h - self.u_rest) * (h - self.u_c) + x)
        u = h + du
        return u


class EIF(RFRSkeleton):
    def __init__(self, tau_m: float = 2.0, u_threshold: float = 1.0, u_rest: float = 0.0, u_t: float = 8.0, delta_t: float = 1.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Exponential Integrate-and-Fire(EIF)神经元。
        一阶电位变换公式为：
        $$τ\frac{du}{dt}=-(u-u_{rest})+Δ_{T}e^{\frac{u-u_{T}}{Δ_{T}}}+RI$$
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            u_t: float 参数$u_{T}$
            delta_t: float 参数$Δ_{T}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__(
            tau_m = tau_m,
            u_threshold = u_threshold,
            u_rest = u_rest,
            spiking_function = spiking_function
        )
        self.delta_t = delta_t
        self.u_t = u_t
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "tau_m=%.3f, u_th=%.3f, u_rest=%.3f, u_T=%.3f, delta_T=%.3f" % (self.tau_m, self.u_threshold, self.u_rest, self.u_t, self.delta_t)


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        du = (1.0 / self.tau_m) * (-(h - self.u_rest) + self.delta_t * torch.exp((h - self.u_t) / self.delta_t) + x)
        u = h + du
        return u


class Izhikevich(RFRSkeleton):
    def __init__(self, a: float = 1.0, b: float = 1.0, u_threshold: float = 1.0, spiking_function: nn.Module = surrogate.Rectangular()) -> None:
        """
        Izhikevich神经元。
        一阶电位变换公式为：
        $$\frac{du}{dt}=0.04u^{2}+5u+140-w+I$$
        $$\frac{dw}{dt}=a(bu-w)$$
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            u_t: float 参数$u_{T}$
            delta_t: float 参数$Δ_{T}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
        """
        super().__init__(
            tau_m = 1.0,
            u_threshold = u_threshold,
            u_rest = 0.0,
            spiking_function = spiking_function
        )
        self.a = a
        self.b = b
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "a=%.3f, b=%.3f, u_th=%.3f" % (self.a, self.b, self.u_threshold)


    def reset(self) -> None:
        """
        重置整个神经元
        """
        self.u = 0.0
        self.w = 0.0

    
    def detach(self) -> None:
        """
        将历史电位从计算图中分离，以停止在时间上进行反向传播
        """
        if isinstance(self.u, torch.Tensor):
            self.u = self.u.detach()
        if isinstance(self.w, torch.Tensor):
            self.w = self.w.detach()


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        self.w = self.init_tensor(self.w, h)
        dw = self.a * (self.b * h - self.w)
        self.w = self.w + dw
        du = 0.04 * h * h + 5.0 * h + 140.0 - self.w + x
        u = h + du
        return u


class AnalogRFRSkeleton(RFRSkeleton):
    def __init__(self, tau_m: float = 1, u_threshold: float = 1, u_rest: float = 0, spiking_function: nn.Module = surrogate.Rectangular(), activation_function: nn.Module = nn.ReLU()) -> None:
        """
        带有模拟输出的Response-Firing-Reset三段式神经元胞体骨架，分别为：
        （1）通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$；
        （2）通过当前电位$U_{i}^{l}(t)$计算当前脉冲$O_{i}^{l}(t)$；
        （3）通过当前电位$U_{i}^{l}(t)$计算当前模拟输出$Y_{i}^{l}(t)$；
        （4）通过当前脉冲$O_{i}^{l}(t)$重置当前电位$U_{i}^{l}(t)$。
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
            activation_function: nn.Module 激活函数
        """
        super().__init__(tau_m, u_threshold, u_rest, spiking_function)
        self.activation_function = activation_function
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "tau_m=%.3f, u_th=%.3f, u_rest=%.3f" % (self.tau_m, self.u_threshold, self.u_rest)
    

    def f_activation(self, u: torch.Tensor) -> torch.Tensor:
        """
        通过当前电位$U_{i}^{l}(t)$计算当前模拟输出$Y_{i}^{l}(t)$。
        @params:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        @return:
            y: torch.Tensor 当前模拟输出$Y_{i}^{l}(t)$
        """
        return self.activation_function(u - self.u_rest)
    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播函数
        @params:
            x: torch.Tensor 来自突触的输入电位$X_{i}^{l}(t)$
        @return:
            o: torch.Tensor 胞体当前的输出脉冲$O_{i}^{l}(t)$
        """
        self.u = self.init_tensor(self.u, x)
        self.u = self.f_response(self.u, x)
        o = self.f_firing(self.u)
        y = self.f_activation(self.u)
        self.u = self.f_reset(self.u, o)
        return y


class LIAF(AnalogRFRSkeleton):
    def __init__(self, tau_m: float = 1, u_threshold: float = 1, u_rest: float = 0, spiking_function: nn.Module = surrogate.Rectangular(), activation_function: nn.Module = nn.ReLU()) -> None:
        """
        Leaky Integrate-and-Analog-Fire(LIAF)神经元
        @params:
            tau_m: float 膜时间常数$τ_{m}$
            u_threshold: float 阈电位$u_{th}$
            u_rest: float 静息电位$u_{rest}$
            spiking_function: nn.Module 计算脉冲时所使用的阶跃函数
            activation_function: nn.Module 激活函数
        """
        super().__init__(tau_m, u_threshold, u_rest, spiking_function, activation_function)
    

    def extra_repr(self) -> str:
        """
        额外的表达式，把参数之类的放进来
        @return:
            repr_str: str 参数表
        """
        return "tau_m=%.3f, u_th=%.3f, u_rest=%.3f" % (self.tau_m, self.u_threshold, self.u_rest)


    def f_response(self, h: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        通过上一时刻的电位$U_{i}^{l}(t-1)$和当前时刻的输入电位$X_{i}^{l}(t)$计算电位导数$dU/dt=U_{i}^{l}(t)-U_{i}^{l}(t-1)$，进而获得当前电位$U_{i}^{l}(t)$。
        @params:
            h: torch.Tensor 上一时刻的电位$U_{i}^{l}(t-1)$
            x: torch.Tensor 输入电位$X_{i}^{l}(t)$
        @return:
            u: torch.Tensor 当前电位$U_{i}^{l}(t)$
        """
        du = (1.0 / self.tau_m) * (-(h - self.u_rest) + x)
        u = h + du
        return u