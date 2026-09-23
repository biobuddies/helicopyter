"""Demonstrate a staff-only JAM stack."""

from helicopyter.cloudflare import jam
from stacks.base import provide

provide('cloudflare/cloudflare', '5.25.0')
jam('staff@admin.example.net/')
