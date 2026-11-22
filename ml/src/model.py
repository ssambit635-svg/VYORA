"""Compact two-channel ResU-Net generator for Sentinel-1 VV/VH -> RGB-style target.

Deliberately small and stable: no GAN, diffusion or transformer. The network
returns only a 3-channel optical-style estimate. Confidence and land-cover
classes are not directly supervised by paired image targets and are therefore
not model output heads.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
        )
        self.act = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(x + self.block(x))


class Down(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            ResidualBlock(out_ch),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Up(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_ch, out_ch, 2, stride=2)
        self.net = nn.Sequential(
            nn.Conv2d(out_ch * 2, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            ResidualBlock(out_ch),
        )

    def forward(self, x: torch.Tensor, skip: torch.Tensor) -> torch.Tensor:
        x = F.interpolate(self.up(x), size=skip.shape[-2:], mode="bilinear", align_corners=False)
        return self.net(torch.cat([x, skip], dim=1))


class ResUNet(nn.Module):
    def __init__(self, base_channels: int = 24, input_channels: int = 2):
        super().__init__()
        b = base_channels
        self.input_channels = input_channels
        self.stem = nn.Sequential(
            nn.Conv2d(input_channels, b, 3, padding=1, bias=False), nn.BatchNorm2d(b), nn.ReLU(inplace=True),
            ResidualBlock(b),
        )
        self.d1 = Down(b, 2 * b)
        self.d2 = Down(2 * b, 4 * b)
        self.d3 = Down(4 * b, 8 * b)
        self.d4 = Down(8 * b, 8 * b)
        self.bottleneck = ResidualBlock(8 * b)
        self.u1 = Up(16 * b, 8 * b)
        self.u2 = Up(16 * b, 4 * b)
        self.u3 = Up(8 * b, 2 * b)
        self.u4 = Up(4 * b, b)
        self.rgb_head = nn.Sequential(nn.Conv2d(b, 3, 1), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        s0 = self.stem(x)
        s1 = self.d1(s0)
        s2 = self.d2(s1)
        s3 = self.d3(s2)
        s4 = self.d4(s3)
        z = self.bottleneck(s4)
        z = self.u1(torch.cat([z, s4], dim=1), s3)
        z = self.u2(torch.cat([z, s3], dim=1), s2)
        z = self.u3(torch.cat([z, s2], dim=1), s1)
        z = self.u4(torch.cat([z, s1], dim=1), s0)
        return self.rgb_head(z)


def build_model(base_channels: int = 24, input_channels: int = 2) -> ResUNet:
    return ResUNet(base_channels=base_channels, input_channels=input_channels)


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
