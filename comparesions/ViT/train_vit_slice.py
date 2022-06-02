import argparse
import logging
import os
import time

import torch
import torch.nn as nn
import torch.optim as optim
from comparesions.dataloader import EuclideanDataloader
from comparesions.ViT.vit import get_args, vit_patch, vit_slice
from tqdm import tqdm
from utils.Config import Config
from utils.Result import Result
from utils.utils_net import get_lr, init_train, save_model


def train(epoch):

    st = time.time()
    running_loss = 0.0
    net.train()

    for data in tqdm(dataset["train"], desc="iter", position=1, leave=False):
        data.to(cfg.device)
        optimizer.zero_grad()
        cls = net(data.image)
        loss = loss_function(cls, data.label)
        loss.backward()
        optimizer.step()
        running_loss += loss
    ft = time.time()
    epoch_loss = running_loss / len(dataset["train"])
    logging.info("EPOCH: {}".format(epoch))
    logging.info("TRAIN_LOSS : {:.3f}, TIME: {:.1f}s".format(epoch_loss, ft - st))
    return epoch_loss


@torch.no_grad()
def eval_training(datatype):

    result[datatype].init()
    net.eval()
    for data in dataset[datatype]:
        data.to(cfg.device)
        cls = net(data.image)
        result[datatype].add(cls, data.label)
    result[datatype].stastic()
    result[datatype].print()

    return


if __name__ == "__main__":

    args = get_args(argparse.ArgumentParser())
    cfg = Config(args)
    init_train(cfg)
    loss_function = nn.CrossEntropyLoss()
    net = vit_slice().to(cfg.device)
    optimizer = optim.Adam(net.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    dataset = EuclideanDataloader(cfg)
    result = {}
    result["valid"], result["test"] = Result(cfg), Result(cfg)

    for epoch in range(1, cfg.num_epoch + 1):

        # Learning rate decay
        for param_group in optimizer.param_groups:
            param_group["lr"] = get_lr(epoch, cfg)

        # Train
        loss = train(epoch)

        # Calculate val data and test data and save failed file
        eval_training("valid")
        eval_training("test")

        # Save  model
        save_model(epoch, result, net, cfg)
