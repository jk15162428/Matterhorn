import torch
import torch.nn as nn
import torchvision
from torchvision.datasets import MNIST
from torch.utils.data import DataLoader, Dataset


import time
import os, sys
sys.path.append(os.path.abspath("."))


import matterhorn.snn as snn


from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.progress import track
from rich.table import Table


def main():
    # 欢迎语，客套话

    print(Panel(Text("EXAMPLE 3: BUILD WITH SRM0 NEURON", justify = "center", style = "bold blue")))

    print("This is your third example. Unlike traditional neuron model, in this example, you will face with a brand new kind of neuron model, SRM0 neuron model.")

    print("In this demo, we're about to build a 2-layer multi-layer perceptron, but use SRM0 model.")

    # 设置参数

    print(Panel(Text("Hyper Parameters", justify = "center")))

    time_steps = 32
    batch_size = 256
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    epochs = 100
    learning_rate = 1e-3
    momentum = 0.9
    tau = 2.0

    hyper_param_table = Table(show_header = True, header_style = "bold blue")
    hyper_param_table.add_column("Name", justify = "center")
    hyper_param_table.add_column("Value", justify = "center")
    hyper_param_table.add_row("Time Steps", str(time_steps))
    hyper_param_table.add_row("Batch Size", str(batch_size))
    hyper_param_table.add_row("Epochs", str(epochs))
    hyper_param_table.add_row("Learning Rate", str(learning_rate))
    hyper_param_table.add_row("Momentum", str(momentum))
    hyper_param_table.add_row("Tau m", str(tau))
    print(hyper_param_table)

    # 根据参数建立模型

    print(Panel(Text("Model", justify = "center")))

    model = snn.SNNContainer(
        encoder = snn.PoissonEncoder(
            time_steps = time_steps,
        ),
        snn_model = snn.TemporalContainer(
            snn.SpatialContainer(
                snn.Flatten(),
                snn.SRM0Linear(28 * 28, 80, tau_m = tau),
                snn.SRM0Linear(80, 10, tau_m = tau)
            ),
        ),
        decoder = snn.AvgSpikeDecoder()
    )
    model = model.to(device)

    print(model)

    # 调取数据集，本次使用的数据集为MNIST

    print(Panel(Text("Dataset", justify = "center")))

    train_dataset = torchvision.datasets.MNIST(
        root = "./examples/data",
        train = True,
        transform = torchvision.transforms.ToTensor(),
        download=True
    )
    test_dataset = torchvision.datasets.MNIST(
        root = "./examples/data",
        train = False,
        transform = torchvision.transforms.ToTensor(),
        download = True
    )

    train_data_loader = DataLoader(
        dataset = train_dataset,
        batch_size = batch_size,
        shuffle = True,
        drop_last = True,
        pin_memory = True
    )
    test_data_loader = DataLoader(
        dataset = test_dataset,
        batch_size = batch_size,
        shuffle = True,
        drop_last = True,
        pin_memory = True
    )

    print(test_dataset[0][0].shape)

    # 设置学习率，优化器，学习率衰减机制等等

    print(Panel(Text("Prepare for Training", justify = "center")))

    optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)
    lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer = optimizer, T_max = epochs)

    # 开始训练

    print(Panel(Text("Training", justify = "center")))

    max_test_acc = 0.0

    for e in range(epochs):
        start_time = time.time()

        # 使用训练集进行训练

        model.train()
        train_loss = 0.0
        train_acc = 0.0
        train_samples = 0
        for x, y in track(train_data_loader, description = "Training at epoch %d" % (e,)):
            optimizer.zero_grad()
            x = x.to(device)
            y = y.to(device)
            y0 = torch.nn.functional.one_hot(y, num_classes = 10).float()

            o = model(x)
            loss = torch.nn.functional.mse_loss(o, y0)
            loss.backward()
            optimizer.step()

            train_samples += y.numel()
            train_loss += loss.item() * y.numel()
            train_acc += (o.argmax(1) == y).float().sum().item()

        train_loss /= train_samples
        train_acc /= train_samples
        
        # 使用测试集进行评估

        model.eval()
        test_loss = 0.0
        test_acc = 0.0
        test_samples = 0
        with torch.no_grad():
            for x, y in track(test_data_loader, description = "Testing at epoch %d" % (e,)):
                x = x.to(device)
                y = y.to(device)
                y0 = torch.nn.functional.one_hot(y, num_classes = 10).float()
                
                o = model(x)
                loss = torch.nn.functional.mse_loss(o, y0)

                test_samples += y.numel()
                test_loss += loss.item() * y.numel()
                test_acc += (o.argmax(1) == y).float().sum().item()
        
        test_loss /= test_samples
        test_acc /= test_samples
        if test_acc > max_test_acc:
            max_test_acc = test_acc
        
        end_time = time.time()

        # 打印测试结果

        result_table = Table(show_header = True, header_style = "bold blue")
        result_table.add_column("Name", justify = "center")
        result_table.add_column("Value", justify = "center")
        result_table.add_row("Epoch", str(e))
        result_table.add_row("Learning Rate", "%.6f" % (lr_scheduler.get_last_lr()[0],))
        result_table.add_row("Training Loss", "%.6f" % (train_loss,))
        result_table.add_row("Training Accuracy", "%.2f%%" % (100 * train_acc,))
        result_table.add_row("Testing Loss", "%.6f" % (test_loss,))
        result_table.add_row("Testing Accuracy", "%.2f%%" % (100 * test_acc,))
        result_table.add_row("Maximum Testing Accuracy", "%.2f%%" % (100 * max_test_acc,))
        result_table.add_row("Duration", "%.3fs" %(end_time - start_time,))
        print(result_table)

        lr_scheduler.step()


if __name__ == "__main__":
    main()